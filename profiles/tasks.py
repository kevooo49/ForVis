import itertools
import logging
import queue
import re
import time
import uuid
from subprocess import Popen, PIPE

import matplotlib.pyplot as plt
import numpy as np
from colormap import rgb2hex as rgb2hexColormap
from django.core.files import File
from igraph import *

from formulavis.celeryconf import app
from formulavis.settings import SATELITE_PATH
from profiles.communities import CommunityManager
from profiles.email import EmailService
from profiles.models import JsonFile, TextFile, Profile
from profiles.vis_tasks import vis_2clause, vis_directed, vis_dpll
from profiles.vis_tasks.i_dpll import DpllIteration
from profiles.vis_tasks.vis_dpll import DpllTree
from profiles.vis_tasks.heatmap_helpers import regrid_x, regrid_y

logger = logging.getLogger('email_on_exception_logger')


@app.task()
def create_json(obj_id, js_id, js_format, selected_vars):
    now = time.time()
    formats = {
        'sat_vis_factor': create_sat_vis_factor,
        'sat_vis_interaction': create_sat_vis_interaction,
        'sat_vis_matrix': create_sat_vis_matrix,
        'sat_vis_tree': create_sat_vis_tree,
        'sat_vis_cluster': create_sat_vis_cluster,
        'sat_vis_resolution': create_sat_vis_resolution,
        'sat_vis_distribution': create_sat_vis_distribution,
        'sat_vis_directed': create_sat_vis_directed,
        'sat_vis_2clause': create_sat_vis_2clause,
        'sat_vis_dpll': create_sat_vis_dpll,
        'sat_vis_heatmap': create_sat_vis_heatmap,
        'maxsat_vis_factor': create_maxsat_vis_factor,
        'maxsat_vis_interaction': create_maxsat_vis_interaction,
        'maxsat_vis_matrix': create_maxsat_vis_matrix,
        'maxsat_vis_tree': create_maxsat_vis_tree,
        'maxsat_vis_cluster': create_maxsat_vis_cluster,
        'maxsat_vis_resolution': create_maxsat_vis_resolution,
        'variables': create_variables_list,
        ''
        'raw': create_raw
    }
    formats.get(js_format)(obj_id, js_id, js_format, selected_vars)
    email_service = EmailService()
    user = TextFile.objects.get(id=obj_id).profile.user
    later = time.time()
    visualization = TextFile.objects.get(id=obj_id).name

    email_service.send_email(
        user.email,
        f'ForVis Virtualization {visualization}',
        f'ForVis virtualization {visualization} finished with time {int(later - now)}'
    )


@app.task()
def create_community(visualization_id, result_id):
    result = JsonFile.objects.get(pk=result_id)
    visualization = JsonFile.objects.get(pk=visualization_id)
    graph_dict = visualization.content
    communities = CommunityManager(graph_dict, result).calculate_communities()

    group = 0
    for community in communities:
        for vertex in community.vertex_list:
            [x for x in graph_dict['nodes'] if x['id'] == vertex][0]['group'] = group
        group += 1
    for edge in graph_dict['edges']:
        if 'color' in edge:
            edge['color']['color'] = 'black'

    result.content = graph_dict
    result.status = 'done'
    result.progress = 'Progress: 100.0%'
    result.save()


def create_sat_vis_heatmap(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_Heatmap")

    num_colors = 10

    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "datasets": []
    }

    text_file = TextFile.objects.get(id=obj_id)

    var_count = cl_count = None
    cl_dict = {}
    sat = None
    index_offset = 0
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index//3, lines_amount, obj)
            line = line.strip()
            if not line or line.startswith('c'):
                index_offset += 1
                continue
            if line.startswith('p'):
                index_offset += 1
                data['info'] = line.replace("\n", "").split(' ')
                init_line = line.split()
                if var_count is None:
                    var_count = int(init_line[2])
                    cl_count = int(init_line[3])
                    sat = np.zeros((cl_count, var_count), dtype=np.int8)
                continue
            # Parse clause
            if sat is not None:
                # Remove trailing 0 and split
                clause_vars = [int(i) for i in line.split() if i != '0']
                clause_idx = index - index_offset
                for variable in clause_vars:
                    if variable > 0:
                        sat[clause_idx][variable-1] = 1
                    else:
                        sat[clause_idx][-variable-1] = -1
                cl_dict[clause_idx] = np.count_nonzero(sat[clause_idx])

    print(f"Formatting cnf DONE. var_count={var_count}, cl_count={cl_count}")
    if sat is not None:
        print(f"SAT matrix after parsing:\n{sat}")
    # Number of occurrences of variable in whole formula
    if var_count is not None and sat is not None:
        val_dict = {i: np.count_nonzero(sat[:, i]) for i in range(var_count)}
    else:
        val_dict = {}
    print("Values Dict Creation DONE")

    if not cl_count or not var_count or cl_count == 0 or var_count == 0 or sat is None:
        print("No clauses or variables found. Skipping heatmap creation.")
        obj.content = {"error": "Empty or malformed file. No heatmap generated."}
        obj.status = 'done'
        obj.progress = 'Progress: 100.0%'
        obj.save()
        return obj

    heatmap = np.zeros([cl_count, var_count])

    if heatmap.size == 0:
        print("Heatmap array is empty after creation. Skipping further processing.")
        obj.content = {"error": "Empty or malformed file. No heatmap generated."}
        obj.status = 'done'
        obj.progress = 'Progress: 100.0%'
        obj.save()
        return obj

    for i in range(len(heatmap)):
        update_progress(lines_amount//3 + i//3, lines_amount, obj)
        val_ctr = -1
        for j in range(len(heatmap[i])):
            val_ctr += 1
            if cl_dict.get(i, 0) == 0:
                heatmap[i][j] = 0
            else:
                heatmap[i][j] = (val_dict.get(val_ctr, 0)/cl_dict.get(i, 1))
    print(f"Full Resolution Heatmap Creation DONE. heatmap shape: {heatmap.shape}")
    print(f"Heatmap matrix:\n{heatmap}")

    max_size = 500
    # Only regrid if heatmap is larger than max_size
    if heatmap.shape[0] > max_size:
        step_x = int(np.ceil(heatmap.shape[0]/max_size))
        heatmap = regrid_x(heatmap, step_x)
    if heatmap.shape[1] > max_size:
        step_y = int(np.ceil(heatmap.shape[1]/max_size))
        heatmap = regrid_y(heatmap, step_y)
    print(f"Scaling down DONE. heatmap shape after regrid: {heatmap.shape}")

    cmap = plt.get_cmap('inferno')

    if heatmap is None or heatmap.size == 0 or heatmap.shape[0] == 0 or heatmap.shape[1] == 0:
        print("Heatmap array is empty after regridding. Skipping further processing.")
        obj.content = {"error": "Empty or malformed file. No heatmap generated."}
        obj.status = 'done'
        obj.progress = 'Progress: 100.0%'
        obj.save()
        return obj

    max_val = heatmap.max()*1.1
    sum_of_heatmap = heatmap.flatten().sum()
    step = max_val/num_colors
    ranges = []
    for clr in range(num_colors):
        ranges.append([clr*step, (clr+1)*step])
    color_list = [cmap(x/num_colors) for x in range(num_colors)]
    color_list_hex = [rgb2hexColormap(int(255*r), int(255*g), int(255*b)) for r, g, b, _ in color_list]
    points = [[] for i in color_list]
    for row_idx, row in enumerate(heatmap):
        update_progress(2*lines_amount//3 + row_idx//3, lines_amount, obj)
        for el_idx, el in enumerate(row):
            entered = False
            for rng_index, rng in enumerate(ranges):
                if rng[0] <= el < rng[1]:
                    points[rng_index].append({"x": row_idx, "y":el_idx})
                    entered = True
            if not entered:
                points[0].append({"x": row_idx, "y": el_idx})
    update_progress(50, 100, obj)
    datasets = []
    for i in range(len(color_list_hex)):
        datasets.append({
            "label": str([np.round(ranges[i][0], 2), np.round(ranges[i][1], 2)]),
            "data": points[i],
            "backgroundColor": color_list_hex[i]
        })
    print("Vis Heatmap all DONE")
    obj.content = {"datasets": datasets}
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()
    return obj


def create_sat_vis_directed(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_Direct_Graphical_Model")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": [],
        "options": vis_directed.options
    }

    nodes_tmp = {}
    edges_tmp = {}

    clause = 0

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text, 1):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                clause += 1
                c_id = 'c_' + str(clause)
                nodes_tmp[c_id] = {"id": c_id,
                                   "color": {"border": 'rgb(0,0,0)', "background": 'rgb(169,169,169)'},
                                   "shape": 'square', "size": 15}
                for n in numbers:
                    l = abs(n)
                    p_l = 'P' + str(l)
                    n_l = 'N' + str(l)
                    nodes_tmp[p_l] = vis_directed.node_json(p_l)
                    nodes_tmp[n_l] = vis_directed.node_json(n_l)
                    p_e = (p_l, c_id)
                    n_e = (n_l, c_id)
                    if n > 0:
                        edges_tmp[p_e] = {"from": c_id, "to": p_l}
                        edges_tmp[n_e] = {"from": n_l, "to": c_id}
                    else:
                        edges_tmp[p_e] = {"from": p_l, "to": c_id}
                        edges_tmp[n_e] = {"from": c_id, "to": n_l}

    data['nodes'] = [v for _, v in nodes_tmp.items()]
    data['edges'] = [v for _, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()
    return obj


def create_sat_vis_2clause(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_2-Clauses_Interaction_Graph")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": [],
        "options": vis_2clause.options
    }

    nodes_tmp = {}
    edges_tmp = {}

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n in numbers:
                    v = abs(n)
                    nodes_tmp[v] = {"id": v, "label": str(v)}

                if len(numbers) == 2:
                    id2c = '2c' + str(sorted(numbers))
                    if numbers[0] > 0 and numbers[1] > 0:
                        ids = list(sorted(map(lambda x: abs(x), numbers)))
                        try:
                            vis_2clause.inc_edge(edges_tmp[id2c])
                        except KeyError:
                            edges_tmp[id2c] = vis_2clause.positive_positive(ids[0], ids[1])
                    elif numbers[0] < 0 and numbers[1] < 0:
                        ids = list(sorted(map(lambda x: abs(x), numbers)))
                        try:
                            vis_2clause.inc_edge(edges_tmp[id2c])
                        except KeyError:
                            edges_tmp[id2c] = vis_2clause.negative_negative(ids[0], ids[1])
                    else:
                        ids = list(map(lambda x: abs(x), sorted(numbers)))
                        try:
                            vis_2clause.inc_edge(edges_tmp[id2c])
                        except KeyError:
                            edges_tmp[id2c] = vis_2clause.negative_positive(ids[0], ids[1])
                else:
                    for p in itertools.combinations(numbers, 2):
                        p = tuple(sorted(map(lambda x: abs(x), p)))
                        try:
                            vis_2clause.inc_edge(edges_tmp[p])
                        except KeyError:
                            edges_tmp[p] = vis_2clause.gt_2clause(p[0], p[1])

    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_dpll(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_DPLL_SOLVER_VISUALIZATION")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.progress = 'DPLL Sat-Solver working...'
    obj.save()

    data = {
        "info": None,
        "moms_nodes": [],
        "moms_edges": [],
        "dlis_nodes": [],
        "dlis_edges": [],
        "jw_nodes": [],
        "jw_edges": [],
        "options": vis_dpll.options
    }

    heuristic_name_map = {1: 'DLIS', 2: 'Jeroslow Wang', 3: 'MOMS'}
    heuristic_output_drop = {1: ["dlis_nodes", "dlis_edges"], 2: ["jw_nodes", "jw_edges"],
                             3: ["moms_nodes", "moms_edges"]}

    text_file = TextFile.objects.get(id=obj_id)

    for heuristic_type in [3, 1, 2]:
        idpll = DpllIteration(text_file.content.path, heuristic_type)
        obj.progress = 'DPLL Sat-Solver working [' + heuristic_name_map[heuristic_type] + '] ...'
        obj.save()
        idpll.run()
        obj.progress = 'Building visualization tree [' + heuristic_name_map[heuristic_type] + '] ...'
        obj.save()
        dpll_tree = DpllTree(idpll.assignment_trail)
        dpll_tree.build_tree()
        dpll_tree.visualize_tree()

        data[heuristic_output_drop[heuristic_type][0]] = [v for k, v in dpll_tree.v_nodes.items()]
        data[heuristic_output_drop[heuristic_type][1]] = [v for k, v in dpll_tree.v_edges.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_distribution(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_Distribution")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "labels": [],
        "positive": [],
        "negative": []
    }

    text_file = TextFile.objects.get(id=obj_id)

    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text, 1):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                number_of_variables = int((line.split(' '))[2])
                positive = np.zeros((number_of_variables,), dtype=int)
                negative = np.zeros((number_of_variables,), dtype=int)
                labels = []

                for i in range(number_of_variables - 1):
                    labels.append(str(i + 1))

                data['info'] = line.replace("\n", "").split(' ')
                data['info'][3].replace("\n", "")
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]

                for n in numbers:
                    if n > 0:
                        positive[n - 1] += 1
                    if n < 0:
                        negative[(n * (-1)) - 1] += 1

    # if len(labels) > 10000:
    #     new_data = {}
    #
    #     for i in range (0, len(labels)):
    #         new_data[labels[i]] = positive[i]+negative[i]
    #
    #     sorted_data = sorted(new_data.items(), key=new_data.get)
    #     new_labels = []
    #     new_positive = []
    #     new_negative = []
    #
    #     for key in sorted_data:
    #         new_labels.append(key)
    #         if len(new_labels) == 10000:
    #             break
    #
    #     for i in new_labels:
    #         new_negative.append(negative[i])
    #         new_positive.append(positive[i])
    #
    #     labels = new_labels
    #     positive = new_positive
    #     negative = new_negative

    data['labels'] = labels
    data['positive'] = positive.tolist()
    data['negative'] = negative.tolist()

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()
    return obj.content


def create_sat_vis_factor(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_FACTOR")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    nodes_tmp = {}
    edges_tmp = {}

    clause = 0

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text, 1):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                clause += 1
                clause_id = -clause
                nodes_tmp['C_' + str(clause)] = {"id": clause_id, "label": 'C_' + str(clause), "group": 0}

                for n in numbers:
                    y = abs(n)
                    nodes_tmp[y] = {"id": y, "label": str(y), "group": 1}

                for n in numbers:
                    k = (abs(n), clause_id)
                    color = 'red' if n < 0 else 'green'
                    edges_tmp[k] = {"from": k[0], "to": k[1], "color": {"color": color, "opacity": 1}}

    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()
    return obj


def create_sat_vis_interaction(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_INTERACTION")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    nodes_tmp = {}
    edges_tmp = {}

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n in numbers:
                    y = abs(n)
                    nodes_tmp[y] = {"id": y, "label": str(y)}

                for k in itertools.combinations(numbers, 2):
                    k = tuple(sorted(map(lambda c: abs(c), k)))
                    try:
                        edges_tmp[k]["color"]["opacity"] += 0.1
                    except KeyError:
                        edges_tmp[k] = {"from": k[0], "to": k[1], "color": {"color": '#000000',
                                                                            "opacity": 0.1}}

    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_cluster(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_CLUSTER")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        'clusteredNetwork': {
            'edges': [],
            'nodes': []
        },
        'wholeNetwork': {
            'edges': [],
            'nodes': []
        }
    }

    edges_tmp = []

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue

                for k in itertools.combinations(numbers, 2):
                    k = tuple(sorted(map(lambda c: abs(c), k)))
                    edges_tmp.append((k[0], k[1]))

    g = Graph(edges_tmp)
    g.delete_vertices(0)
    g.simplify()

    dendogram = g.community_edge_betweenness()
    clusters = dendogram.as_clustering()
    membership = clusters.membership

    layout1 = g.layout_kamada_kawai()

    i = g.community_infomap()

    unique_membership_classes = len(set(membership))
    pal = drawing.colors.ClusterColoringPalette(unique_membership_classes)

    clustered = g.copy()
    clustered.contract_vertices(membership, combine_attrs='max')
    clustered.simplify()

    for vertex, cluster in zip(g.vs.indices, membership):
        data['wholeNetwork']['nodes'].append({
            'color': rgb2hex(pal.get(cluster)),
            'id': vertex,
            'label': str(vertex),
            'cluster': cluster
        })

    for edge in g.get_edgelist():
        data['wholeNetwork']['edges'].append({
            'color':
                {
                    'color': '#888888',
                    'opacity': 1
                },
            'from': edge[0],
            'id': f"{edge[0]}_{edge[1]}",
            'to': edge[1],
            'width': 1  # You might want to add edge width
        })

    for vertex in clustered.vs.indices:
        data['clusteredNetwork']['nodes'].append({
            'color': rgb2hex(pal.get(vertex_idx)),
            'id': vertex_idx,
            'label': f"Cluster {vertex_idx}",
            'size': 30 + (clustered.degree(vertex_idx) * 3),
            'x': clustered_layout[vertex_idx][0] * 150,
            'y': clustered_layout[vertex_idx][1] * 150
        })

    for edge in clustered.get_edgelist():
        data['clusteredNetwork']['edges'].append({
            'color':
                {
                    'color': '#888888',
                    'opacity': 1
                },
            'from': edge[0],
            'id': str(edge[0]) + '_' + str(edge[1]),
            'to': edge[1]
        })
    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_matrix(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_MATRIX")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "labels": [],
        "rows": []
    }

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
                # initialize data['rows'] and data['labels']
                numberOfVariables = int(data['info'][-2])
                for indx1 in range(numberOfVariables):
                    data['labels'].append(str(indx1))
                    tmpRow = {
                        "dependencies": []
                    }
                    for indx2 in range(numberOfVariables):
                        if indx1 != indx2:
                            tmpRow['dependencies'].append({
                                "positive": 0,
                                "negative": 0
                            })
                        else:
                            tmpRow['dependencies'].append({
                                "positive": -1,
                                "negative": -1
                            })
                    data['rows'].append(tmpRow)
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n1 in numbers:
                    for n2 in numbers:
                        if n1 == n2:
                            continue
                        if n1 > 0:
                            data['rows'][abs(n1) - 1]['dependencies'][abs(n2) - 1]['positive'] += 1
                        else:
                            data['rows'][abs(n1) - 1]['dependencies'][abs(n2) - 1]['negative'] += 1

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_tree(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_TREE")

    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    formulas = []

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):
            update_progress(index, lines_amount, obj)

            if is_comment(line):
                continue
            if is_info(line):
                data['info'] = get_info_array(line)
            else:
                formulas.append(get_numbers(line))

        tree = FormulaTree(formulas, 0)
        tree.serialize()
        data['nodes'] = tree.nodes
        data['edges'] = tree.edges

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_sat_vis_resolution(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_RESOLUTION")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    nodes_tmp = {}
    edges_tmp = {}

    variables = {}
    clause = 0

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)

        print("Working on vis resolution.")
        lines_amount = get_lines_amount_for(f)

        for index, line in enumerate(text, 1):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                clause += 1
                nodes_tmp[clause] = {"id": clause, "label": 'C_' + str(clause)}
                for n in numbers:
                    if n not in variables and (selected_vars is None or len(selected_vars) == 0 or
                                               n in selected_vars or -n in selected_vars):
                        variables[n] = []
                    if n in variables:
                        variables[n].append(clause)

        for v, clause_list_1 in variables.items():
            if v < 0:
                continue
            if -v in variables.keys():
                clause_list_2 = variables[-v]

                for c1 in clause_list_1:
                    for c2 in clause_list_2:
                        edges_tmp[(c1, c2)] = {"from": c1, "to": c2}

    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_variables_list(obj_id, js_id, js_format, selected_vars):
    print("SAT_VARIABLES")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "variables": []
    }

    variables = {}

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n in numbers:
                    if n >= 0 and n not in variables.keys():
                        variables[n] = []
                    if n < 0 and -n not in variables.keys():
                        variables[-n] = []

    data['variables'] = list(variables.keys())

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_raw(obj_id, js_id, js_format, selected_vars):
    print("RAW")
    obj = JsonFile.objects.get(id=js_id)
    text_file = TextFile.objects.get(id=obj_id)
    obj.status = 'pending'
    obj.save()
    data = {"raw": ""}
    with open(text_file.content.path) as f:
        text = File(f)
        t = text.read()
        data["raw"] = t
        obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


@app.task()
def create_minimized(obj_id, profile_id):
    print("MINIMIZING: {}".format(obj_id))
    time.sleep(5)

    base_file = TextFile.objects.get(id=obj_id)
    profile = Profile.objects.get(id=profile_id)

    base_path = base_file.content.path

    satelite_path = re.sub(r'.cnf', '_min.cnf', base_path)
    name = re.sub(r'.cnf', '_min.cnf', base_file.name)

    open(satelite_path, 'w+')
    p = Popen(
        [SATELITE_PATH, base_path, satelite_path],
        stdin=PIPE, stdout=PIPE, stderr=PIPE
    )
    output, err = p.communicate()
    print('OUTPUt {}'.format(output))
    print('ERROR {}'.format(err))
    # TODO email error to admin
    print('basse {}'.format(os.path.isfile(base_path)))
    print('satelite {}'.format(os.path.isfile(satelite_path)))

    with open(satelite_path, 'r') as f:
        text = File(f)

        TextFile.objects.create(
            profile=profile,
            name=name,
            content=text,
            minimized=True
        )

    os.remove(satelite_path)
    print("DONE: {}".format(obj_id))


def create_maxsat_vis_factor(obj_id, js_id, js_format, selected_vars):
    print("MAXSAT_VIS_FACTOR")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    nodes_tmp = {}
    edges_tmp = {}
    clause_weights = {}
    clause = 0

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                clause += 1
                clause_weights[clause] = numbers[0]
                del numbers[0]

                for n in numbers:
                    y = abs(n)
                    nodes_tmp[y] = {"id": y, "label": str(y)}

                for n in numbers:
                    k = (abs(n), -clause)
                    color = 'red' if n < 0 else 'green'
                    edges_tmp[k] = {"from": k[0], "to": k[1], "color": {"color": color, "opacity": 1}}

    min_cw = min(clause_weights.values())
    max_cw = max(clause_weights.values())
    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['nodes'].extend([get_node(-c, cw, min_cw, max_cw) for c, cw in clause_weights.items()])
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_maxsat_vis_interaction(obj_id, js_id, js_format, selected_vars):
    print("MAXSAT_VIS_INTERACTION")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    nodes_tmp = {}
    edges_tmp = {}

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n in numbers:
                    y = abs(n)
                    nodes_tmp[y] = {"id": y, "label": str(y)}

                for k in itertools.combinations(numbers, 2):
                    k = tuple(sorted(map(lambda c: abs(c), k)))
                    try:
                        edges_tmp[k]["color"]["opacity"] += 0.1
                    except KeyError:
                        edges_tmp[k] = {"from": k[0], "to": k[1], "color": {"color": '#000000',
                                                                            "opacity": 0.1}}

    data['nodes'] = [v for k, v in nodes_tmp.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_maxsat_vis_cluster(obj_id, js_id, js_format, selected_vars):
    print("SAT_VIS_CLUSTER")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        'clusteredNetwork': {
            'edges': [],
            'nodes': []
        },
        'wholeNetwork': {
            'edges': [],
            'nodes': []
        }
    }

    edges_tmp = []

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue

                for k in itertools.combinations(numbers, 2):
                    k = tuple(sorted(map(lambda c: abs(c), k)))
                    edges_tmp.append((k[0], k[1]))

    g = Graph(edges_tmp)
    g.delete_vertices(0)
    g.simplify()

    dendogram = g.community_edge_betweenness()
    clusters = dendogram.as_clustering()
    membership = clusters.membership

    layout1 = g.layout_kamada_kawai()

    i = g.community_infomap()
    pal = drawing.colors.ClusterColoringPalette(len(i))

    clustered = g.copy()
    clustered.contract_vertices(membership, combine_attrs='max')
    clustered.simplify()

    for vertex, cluster in zip(g.vs.indices, membership):
        data['wholeNetwork']['nodes'].append({
            'color': rgb2hex(pal.get(cluster)),
            'id': vertex,
            'label': str(vertex),
            'cluster': cluster
        })

    for edge in g.get_edgelist():
        data['wholeNetwork']['edges'].append({
            'color':
                {
                    'color': '#888888',
                    'opacity': 1
                },
            'from': edge[0],
            'id': str(edge[0]) + '_' + str(edge[1]),
            'to': edge[1]
        })

    for vertex in clustered.vs.indices:
        data['clusteredNetwork']['nodes'].append({
            'color': rgb2hex(pal.get(vertex)),
            'id': vertex,
            'label': str(vertex),
        })

    for edge in clustered.get_edgelist():
        data['clusteredNetwork']['edges'].append({
            'color':
                {
                    'color': '#888888',
                    'opacity': 1
                },
            'from': edge[0],
            'id': str(edge[0]) + '_' + str(edge[1]),
            'to': edge[1]
        })
    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_maxsat_vis_matrix(obj_id, js_id, js_format, selected_vars):
    print("MAXSAT_VIS_MATRIX")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "labels": [],
        "rows": []
    }

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
                # initialize data['rows'] and data['labels']
                numberOfVariables = int(data['info'][-2])
                for indx1 in range(numberOfVariables):
                    data['labels'].append(str(indx1))
                    tmpRow = {
                        "dependencies": []
                    }
                    for indx2 in range(numberOfVariables):
                        if indx1 != indx2:
                            tmpRow['dependencies'].append({
                                "positive": 0,
                                "negative": 0
                            })
                        else:
                            tmpRow['dependencies'].append({
                                "positive": -1,
                                "negative": -1
                            })
                    data['rows'].append(tmpRow)
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                for n1 in numbers:
                    for n2 in numbers:
                        if n1 == n2:
                            continue
                        if n1 > 0:
                            data['rows'][abs(n1) - 1]['dependencies'][abs(n2) - 1]['positive'] += 1
                        else:
                            data['rows'][abs(n1) - 1]['dependencies'][abs(n2) - 1]['negative'] += 1

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_maxsat_vis_tree(obj_id, js_id, js_format, selected_vars):
    print("MAXSAT_VIS_TREE")

    obj = JsonFile.objects.get(id=js_id)

    obj.stJsonFileatus = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    formulas = []

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(f):

            update_progress(index, lines_amount, obj)

            if is_comment(line):
                continue
            if is_info(line):
                data['info'] = get_info_array(line)
            else:
                formulas.append(get_numbers(line))
        tree = FormulaTree(formulas, 0)
        tree.serialize()
        data['nodes'] = tree.nodes
        data['edges'] = tree.edges

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def create_maxsat_vis_resolution(obj_id, js_id, js_format, selected_vars):
    print("MAXSAT_VIS_RESOLUTION")
    obj = JsonFile.objects.get(id=js_id)

    obj.status = 'pending'
    obj.save()

    data = {
        "info": None,
        "nodes": [],
        "edges": []
    }

    clause_weights = {}
    nodes_tmp = {}
    edges_tmp = {}

    variables = {}
    clause = 0

    text_file = TextFile.objects.get(id=obj_id)
    with open(text_file.content.path) as f:
        text = File(f)
        lines_amount = get_lines_amount_for(f)
        for index, line in enumerate(text):

            update_progress(index, lines_amount, obj)

            if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
                continue
            if line.startswith('p'):
                data['info'] = line.replace("\n", "").split(' ')
            else:
                numbers = [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]
                if not numbers:
                    continue
                clause += 1
                clause_weights[clause] = numbers[0]
                del numbers[0]
                for n in numbers:
                    if n not in variables and (selected_vars is None or len(
                            selected_vars) == 0 or n in selected_vars or -n in selected_vars):
                        variables[n] = []
                    if n in variables:
                        variables[n].append(clause)

    for v, clause_list_1 in variables.items():
        if v < 0:
            continue
        if -v in variables.keys():
            clause_list_2 = variables[-v]

            for c1 in clause_list_1:
                for c2 in clause_list_2:
                    edges_tmp[(c1, c2)] = {"from": c1, "to": c2}

    min_cw = min(clause_weights.values())
    max_cw = max(clause_weights.values())
    data['nodes'] = [get_node(c, cw, min_cw, max_cw) for c, cw in clause_weights.items()]
    data['edges'] = [v for k, v in edges_tmp.items()]

    obj.content = data
    obj.status = 'done'
    obj.progress = 'Progress: 100.0%'
    obj.save()


def get_node(clause, clause_weight, min_cw, max_cw):
    return {"id": clause, "color": {"background": get_clause_color(clause_weight, min_cw, max_cw)},
            "label": 'C_{}'.format(abs(clause))}


def get_clause_color(cw, min_cw, max_cw):
    normalized_cw = normalize_value(cw, min_cw, max_cw)
    return "rgba(255, {}, {})".format(normalized_cw, normalized_cw)


def normalize_value(v, min_v, max_v):
    return int((v - min_v) * 255 / (max_v - min_v))


def is_comment(line):
    if line.startswith('c') or line.startswith('C') or line in ['', ' ']:
        return True
    return False


def is_info(line):
    if line.startswith('p'):
        return True
    return False


def get_info_array(line):
    return line.split(' ')


def get_numbers(line):
    return [int(x) for x in list(filter(lambda x: x != '', line.strip().split(' ')))[:-1]]


def join_lists(lst):
    result = []
    [result.extend(el) for el in lst]
    return result


def most_common(lst):
    if not lst or lst == [[]]:
        return None
    joined = join_lists(lst)
    return max(joined, key=joined.count)


def get_lines_amount_for(file):
    linesAmount = 0
    for line in file:
        linesAmount += 1
    return linesAmount


def update_progress(index, linesAmount, obj):
    progress = float(index) / float(linesAmount) * float(100)
    obj.progress = "Progress: " + str(round(progress, 2)) + "%"
    obj.save()


class FormulaNode(object):
    def __init__(self, formula_list, level):
        self.children = []
        self.id = str(uuid.uuid4())
        self.level = level

        self.data = most_common(formula_list)
        self.formula_list = formula_list

        for formula in self.formula_list:
            formula.remove(self.data)

        [self.add_child(child) for child in FormulaTree(formula_list, level + 1).roots]

    def add_child(self, obj):
        self.children.append(obj)

    def set_level(self, level):
        self.level = level

    def set_id(self, id):
        self.id = id


class FormulaTree(object):
    def __init__(self, formula_list, start_level):
        self.nodes = []
        self.edges = []

        self.roots = []
        self.grouped_formula = []
        self.formula_list = self.group_formulas(formula_list)

        for formula in self.grouped_formula:
            if (formula != [[]]):
                self.roots.append(FormulaNode(formula, start_level))

    def group_formulas(self, lst):
        formulas = []
        tmp = []
        f = []
        root = most_common(lst)
        if not root:
            return formulas
        for formula in lst:
            if root in formula:
                f.append(formula)
            else:
                tmp.append(formula)
        self.grouped_formula.append(f)
        return self.group_formulas(tmp)

    def serialize(self):
        q = queue.Queue()

        for root in self.roots:
            q.put(root)

        for root in self.roots:
            root.set_level(0)

        while not q.empty():
            node = q.get()
            for child in node.children:
                self.edges.append({"from": node.id, "to": child.id, "color": {"color": '#ff383f'}})
                q.put(child)

            self.nodes.append({"id": node.id, "label": str(node.data), "level": node.level})


def rgb2hex(rgb):
    return '#%02x%02x%02x' % (tuple(int(value * 255) for value in rgb)[0:-1])

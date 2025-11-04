options = {
    "nodes": {
        "color": {"border": 'rgb(0,0,0)', "background": 'rgb(169,169,169)'},
        "font": {
            "color": "rgb(0,0,0)"
        }
    },
    "edges": {
        "enabled": True
    },
    "physics": {
        "enabled": True,
        "barnesHut": {
            "avoidOverlap": 1,
            "centralGravity": 3.5
        },
        "maxVelocity": 1,
        "minVelocity": 1
    }
}


def inc_edge(e):
    e['label'] = str(int(e['label']) + 1)
    if e['width'] < 20:
        e['width'] += 1


def edge_2clause_json_2arrow(a, b, color, _type, roundness):
    return {"from": a, "to": b, "color": {"color": color, "opacity": 0.5}, "label": '1', "width": 1,
            "arrows": {"to": {"enabled": True, "scaleFactor": 1, "type": "arrow"},
                       "from": {"enabled": True, "scaleFactor": 1, "type": "arrow"}},
            "smooth": {"type": _type, "roundness": roundness}
            }


def edge_2clause_json_1arrow(a, b, color, _type, roundness):
    return {"from": a, "to": b, "color": {"color": color, "opacity": 0.5}, "label": '1', "width": 1,

            "arrows": {"to": {"enabled": True, "scaleFactor": 1, "type": "arrow"}},
            "smooth": {"type": _type, "roundness": roundness}
            }


def gt_2clause(a, b):
    return {"from": a, "to": b, "color": {"color": 'rgb(0,0,0)', "opacity": 0.5}, "label": '1', "width": 1,
            "smooth": {"type": 'curvedCW', "roundness": 0}}


def positive_positive(a, b):
    return edge_2clause_json_2arrow(a, b, 'rgb(255,0,0)', 'curvedCW', 0.2)


def negative_positive(a, b):
    return edge_2clause_json_1arrow(a, b, 'rgb(0,0,255)', 'curvedCW', 0.5)


def negative_negative(a, b):
    return edge_2clause_json_2arrow(a, b, 'rgb(0,128,0)', 'curvedCCW', 0.2)

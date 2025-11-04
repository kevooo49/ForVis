from profiles.vis_tasks.i_dpll import DpllIteration

options = {
    "nodes": {
        "color": {"border": 'rgb(0,0,0)', "background": 'rgb(30,144,255)'},
        "font": {
            "color": "rgb(0,0,0)"
        }
    },
    "edges": {
        "enabled": True,
        "arrows": {
            "to": {
                "enabled": True,
                "scaleFactor": 1,
                "type": "arrow"
            }
        }
    },
    "physics": {
        "enabled": True,
        "barnesHut": {
            "avoidOverlap": 1,
            "centralGravity": 3.5
        },
        "maxVelocity": 1,
        "minVelocity": 1
    },
    "layout": {
        "hierarchical": {
            "direction": "UD",
            "nodeSpacing": 150
        }
    }
}

NORMAL = 0
DECISION = 1
CONFLICT = 2
SAT = 3
UNSAT = 4
NORMAL_COLOR = 'rgb(135,206,250)'
DECISION_COLOR = 'rgb(147,112,219)'
CONFLICT_COLOR = 'rgb(255,165,0)'
SAT_COLOR = 'rgb(50,205,50)'
UNSAT_COLOR = 'rgb(255,0,0)'
ZERO_EDGE_COLOR = 'rgb(255,0,0)'
ONE_EDGE_COLOR = 'rgb(0,255,0)'


class DpllTreeAttr:
    def __init__(self):
        self.prev = None
        self.dec_node = False
        self.conf_node = False
        self.prev_val = False
        self.back_to = False
        self.ntype = NORMAL


class DpllNode:
    def __init__(self, nid, parent, level, ntype, tree_nodes: list):
        self.nid = nid
        self.parent = parent
        self.level = level
        self.zero = None
        self.one = None
        self.ntype = ntype
        tree_nodes.append(self)


def get_var(nid: str):
    return nid.split('.')[0]


def create_v_node(n: DpllNode):
    if n.ntype == DECISION:
        ncolor = DECISION_COLOR
    elif n.ntype == CONFLICT:
        ncolor = CONFLICT_COLOR
    elif n.ntype == SAT:
        ncolor = SAT_COLOR
    elif n.ntype == UNSAT:
        ncolor = UNSAT_COLOR
    else:
        ncolor = NORMAL_COLOR
    return {"id": n.nid, "label": get_var(n.nid), "level": n.level, "color": {"background": ncolor}}


class DpllTree:
    def __init__(self, assignment_trail):
        self.root = None
        self.trail = assignment_trail
        self.repeat_counter = {}
        self.v_nodes = {}
        self.v_edges = {}
        self.attr = DpllTreeAttr()
        self.tree_nodes = []

    def put_repeat_counter(self, v):
        if v in self.repeat_counter:
            self.repeat_counter[v] += 1
        else:
            self.repeat_counter[v] = 1

    def build_id(self, n):
        return str(n) + '.' + str(self.repeat_counter[n])

    def set_root(self):
        while self.trail:
            lit = self.trail.pop(0)
            if lit == 'd':
                self.attr.ntype = DECISION
                continue
            elif lit == 'sat':
                self.root = DpllNode("SAT", None, 0, SAT, self.tree_nodes)
                break
            elif lit == 'unsat':
                self.root = DpllNode("SAT", None, 0, UNSAT, self.tree_nodes)
                break
            else:
                lit = int(lit)
                v = abs(lit)
                self.put_repeat_counter(v)
                self.root = DpllNode(self.build_id(v), None, 0, self.attr.ntype, self.tree_nodes)
                self.attr.prev = self.root
                self.attr.prev_val = lit > 0
                break

    def sat(self):
        n = DpllNode('SAT', self.attr.prev, self.attr.prev.level + 1, SAT, self.tree_nodes)
        if self.attr.prev_val:
            self.attr.prev.one = n
        else:
            self.attr.prev.zero = n

    def unsat(self):
        n = DpllNode('UNSAT', self.attr.prev, self.attr.prev.level + 1, UNSAT, self.tree_nodes)
        if self.attr.prev_val:
            self.attr.prev.one = n
        else:
            self.attr.prev.zero = n

    def back_to(self):
        if self.attr.conf_node:
            self.put_repeat_counter('CONF')
            n = DpllNode(self.build_id('CONF'), self.attr.prev, self.attr.prev.level + 1, CONFLICT, self.tree_nodes)
            if self.attr.prev_val:
                self.attr.prev.one = n
            else:
                self.attr.prev.zero = n
        self.attr.conf_node = False
        self.attr.back_to = True

    def build_tree(self):
        self.set_root()  # ustawianie roota

        while self.trail:
            lit = self.trail.pop(0)
            if lit == 'd':
                self.attr.dec_node = True
            elif lit == 'c':
                self.attr.conf_node = True
            elif lit == 'b':
                self.back_to()
            elif lit == 'sat':
                self.sat()
                break
            elif lit == 'unsat':
                self.unsat()
                break
            else:
                lit = int(lit)
                v = abs(lit)
                if self.attr.back_to:
                    while get_var(self.attr.prev.nid) != str(v):
                        self.attr.prev = self.attr.prev.parent
                    self.attr.prev_val = not lit > 0
                    self.attr.back_to = False
                    continue
                self.attr.ntype = NORMAL
                if self.attr.dec_node:
                    self.attr.ntype = DECISION
                    self.attr.dec_node = False
                if str(v) == get_var(self.attr.prev.nid):
                    continue
                self.put_repeat_counter(v)
                n = DpllNode(self.build_id(v), self.attr.prev, self.attr.prev.level + 1, self.attr.ntype,
                             self.tree_nodes)
                if self.attr.prev_val:
                    self.attr.prev.one = n
                else:
                    self.attr.prev.zero = n
                self.attr.prev = n
                self.attr.prev_val = lit > 0

    def fill_vis_struct(self, p: DpllNode, n: DpllNode, value):
        self.v_nodes[n.nid] = create_v_node(n)
        if value == 1:
            ecolor = ONE_EDGE_COLOR
        else:
            ecolor = ZERO_EDGE_COLOR
        self.v_edges[str(p.nid) + '-' + str(n.nid) + ':' + str(value)] = {"from": p.nid, "to": n.nid,
                                                                          "color": {"color": ecolor}}

    def visualize_tree(self):
        self.v_nodes[self.root.nid] = create_v_node(self.root)
        # self.visualize_tree_body(self.root)
        for n in self.tree_nodes[1:]:
            if n == n.parent.one:
                self.fill_vis_struct(n.parent, n, 1)
            else:
                self.fill_vis_struct(n.parent, n, 0)

    def visualize_tree_body(self, n: DpllNode):
        if n.one:
            self.fill_vis_struct(n, n.one, 1)
            self.visualize_tree_body(n.one)
        if n.zero:
            self.fill_vis_struct(n, n.zero, 0)
            self.visualize_tree_body(n.zero)

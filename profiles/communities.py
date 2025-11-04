import heapq
from itertools import combinations


class Matrix:

    def __init__(self):
        self.matrix_dict = {}

    @staticmethod
    def _get_key(u_id, v_id):
        u = str(u_id)
        v = str(v_id)
        return f'{u}_{v}'

    def put_edge(self, u_id, v_id):
        key = self._get_key(u_id, v_id)
        self.matrix_dict[key] = True
        key = self._get_key(v_id, u_id)
        self.matrix_dict[key] = True

    def get(self, u_id, v_id):
        key = self._get_key(u_id, v_id)
        if key in self.matrix_dict and self.matrix_dict[key]:
            return True
        return False


class CommunityData:
    vertex_list: [int]
    modularity: float
    neighbour_list: []

    def __init__(self, community_manager, vertex_list):
        self.vertex_list = vertex_list
        self.neighbour_list = []
        # self.modularity = community_manager.calculate_modularity([self.vertex_list])

    def add_neighbour(self, item):
        self.neighbour_list.append(item)

    def remove_neighbour(self, item):
        try:
            self.neighbour_list.remove(item)
        except ValueError:
            pass


class ModularityDeltaData:

    def __init__(self, comm1, comm2, modularity_delta):
        self.comm1 = comm1
        self.comm2 = comm2
        self.modularity_delta = modularity_delta

    def __gt__(self, other):
        return self.modularity_delta < other.modularity_delta

    def __lt__(self, other):
        return self.modularity_delta > other.modularity_delta

    def __eq__(self, other):
        return self.modularity_delta == other.modularity_delta


class PriorityQueue:

    def __init__(self):
        self.h = []

    def push(self, item: ModularityDeltaData):
        heapq.heappush(self.h, item)

    def pop(self):
        return heapq.heappop(self.h)

    def is_empty(self):
        return len(self.h) == 0

    def size(self):
        return len(self.h)


def update_progress(index, linesAmount, obj):
    if obj is not None and linesAmount != 0:
        progress = float(index) / float(linesAmount) * float(100)
        obj.progress = "Progress: " + str(round(progress, 2)) + "%"
        obj.save()


class CommunityManager:

    """
        'https://www.inesc-id.pt/ficheiros/publicacoes/5176.pdf'
    """

    def __init__(self, graph_dict, result=None):
        assert 'nodes' in graph_dict
        assert 'edges' in graph_dict
        self.graph_dict = graph_dict
        self.result = result
        self.vertex_list = self._get_vertex_list()
        self.degree_list = {}
        self.m = len(self.graph_dict['edges'])
        # matrix = A
        self.matrix = self.create_matrix()

    def _get_vertex_list(self):
        return set(x['id'] for x in self.graph_dict['nodes'])

    def create_matrix(self):
        matrix = Matrix()
        for edge in self.graph_dict['edges']:
            matrix.put_edge(edge['from'], edge['to'])
            if edge['from'] not in self.degree_list:
                self.degree_list[edge['from']] = 0
            if edge['to'] not in self.degree_list:
                self.degree_list[edge['to']] = 0
            self.degree_list[edge['from']] += 1
            self.degree_list[edge['to']] += 1
        return matrix

    def calculate_modularity(self, community_list):
        """
            community_list is a list of vertex_id int list e.g:
                [ [1,-1,2], [2,3,-3] ]
        """
        assert self.degree_list
        modularity = 0
        for community in community_list:
            for v in community:
                for u in community:
                    if u == v:
                        continue
                    a = 1 if self.matrix.get(u, v) else 0
                    modularity += a - ((self.degree_list[u] * self.degree_list[v]) / (2*self.m))
        return modularity / (2*self.m)

    def _init_data(self, communities, community_dict, queue):
        # Create community list (every vertex is new community at the beginning)
        for vertex in self.vertex_list:
            community = CommunityData(
                self, vertex_list=[vertex]
            )
            communities.append(community)
            community_dict[vertex] = community

        # Set neighbours to community list
        for community in communities:
            vertex = community.vertex_list[0]
            neighbour = [x['from'] for x in self.graph_dict['edges'] if x['to'] == vertex] \
                        + [x['to'] for x in self.graph_dict['edges'] if x['from'] == vertex]
            for n in neighbour:
                community.add_neighbour(community_dict[n])

        # Init cheap H
        for u, v in combinations(self.vertex_list, 2):
            if v != u and self.matrix.get(u, v):
                queue.push(
                    ModularityDeltaData(community_dict[u], community_dict[v], 0)
                )

    def calculate_communities(self) -> [[int]]:
        queue = PriorityQueue()
        communities = []
        community_dict = {}
        self._init_data(communities, community_dict, queue)

        x = 0
        while not queue.is_empty():
            x = x + 1
            if x % 1000 == 0:
                update_progress(1, queue.size(), self.result)
            c = queue.pop()
            cx = c.comm1
            cy = c.comm2
            if c.modularity_delta < 0 or not (cx in communities and cy in communities):
                continue

            cz = CommunityData(
                self, vertex_list=cx.vertex_list + cy.vertex_list
            )
            communities.remove(cx)
            communities.remove(cy)
            communities.append(cz)

            neighbours = set(cy.neighbour_list + cx.neighbour_list)
            neighbours.remove(cx)
            neighbours.remove(cy)

            for n in neighbours:
                self._update_neighbours(cz, cx, cy, n)

                c = communities.copy()
                c.remove(n)
                c.remove(cz)
                c.append(CommunityData(
                    self, vertex_list=n.vertex_list + cz.vertex_list
                ))

                modularity_delta = self.calculate_modularity(self.get_community_list(c)) \
                                   - self.calculate_modularity(self.get_community_list(communities))
                modularity_data = ModularityDeltaData(cz, n, modularity_delta)
                queue.push(modularity_data)
        return communities

    @staticmethod
    def get_community_list(data):
        return [x.vertex_list for x in data]

    @staticmethod
    def _update_neighbours(cz, cx, cy, n: CommunityData):
        n.remove_neighbour(cx)
        n.remove_neighbour(cy)
        n.add_neighbour(cz)
        cz.add_neighbour(n)

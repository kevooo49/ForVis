import time
from itertools import combinations
from tempfile import TemporaryFile
from unittest import TestCase
from unittest.mock import Mock

import django
from django.contrib.auth.models import User
from django.core.files.base import ContentFile, File
from django.db.models import Q

from profiles.communities import CommunityManager
from profiles.models import TextFile, Profile, JsonFile
from profiles.tasks import create_json, create_sat_vis_factor
from profiles.views import start_community_task


class TestTasks(TestCase):

    def setUp(self):
        super().setUp()

    def test_calculate_modularity(self):
        graph = self._create_graph().content
        vertexes = [[-1, -2, -3, 1, 2, 3, 4]]
        x = CommunityManager(graph).calculate_modularity(vertexes)
        self.assertEqual(x, 0.15625)
        x = CommunityManager(graph).calculate_modularity([[4]])
        self.assertEqual(x, 0.0)

        x = CommunityManager(graph)
        modularity_dict = {}
        for v in vertexes[0]:
            for u in vertexes[0]:
                if u == v:
                    continue
                modularity_dict[f'{v}_{u}'] = x.calculate_modularity([[u, v]])
        self.assertEqual(1, 1)

    def test_calculate_communities(self):
        graph = {
            'nodes': [
                {'id': 1},
                {'id': 2},
                {'id': 3},
                {'id': 4},
                {'id': 5},
                {'id': 6},
            ],
            'edges': [
                {'from': 1, 'to': 3},
                {'from': 1, 'to': 2},
                {'from': 2, 'to': 3},
                {'from': 3, 'to': 6},
                {'from': 4, 'to': 5},
                {'from': 5, 'to': 6},
                {'from': 4, 'to': 6}
            ]
        }
        x = CommunityManager(graph).calculate_communities()
        self.assertEqual(len(x), 2)
        self.assertEqual(x[0].vertex_list, [1, 2, 3])
        self.assertEqual(x[1].vertex_list, [5, 6, 4])

    def test_calculate_communities_performance(self):
        # 100 25 sec
        vertex_number = 1000
        vertex_list = list(range(1, vertex_number))
        graph = {
            'nodes': [{'id': x} for x in vertex_list],
            'edges': [{'from': x[0], 'to': x[1]} for x in list(combinations(vertex_list, 2))]
        }
        now = time.time()
        x = CommunityManager(graph).calculate_communities()
        later = time.time()
        self.assertEqual(int(later - now), 1)

    def test_start_community_task(self):
        json_file = self._create_graph()
        start_community_task(None, json_file.id)
        graph_dict = JsonFile.objects.filter(~Q(id=json_file.id)).get().content
        self.assertEqual(len(graph_dict['nodes']), 7)

    @staticmethod
    def _create_graph():
        name = 'x.cnf'
        selected_vars = [1]
        profile = Profile.objects.create(
            user=User.objects.create(
                first_name='First',
                last_name='Last',
                email='Email'
            )
        )
        graph = None
        with open(f'./_files/{name}') as f:
            text_file = TextFile.objects.create(
                profile=profile,
                name='Test Text File',
                content=File(f),
                kind='Kind'
            )
            json_file, j_c = JsonFile.objects.get_or_create(
                text_file=text_file,
                json_format='sat_vis_factor',
                selected_vars=selected_vars
            )
            return create_sat_vis_factor(text_file.id, json_file.id, json_file.json_format, selected_vars)

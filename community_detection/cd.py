# cd.py
#
# Copyright 2022 Martin Pobaschnig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http: //www.gnu.org/licenses/>.

from collections import defaultdict
from typing import List, Optional
from itertools import combinations

from cdhf.data import Data

import igraph as ig
import numpy as np


class CD:
    graph: Optional[ig.Graph] = None
    communities: Optional[ig.VertexClustering] = None
    layout: Optional[ig.Layout] = None
    data: Data = None

    def set_data(self, data) -> None:
        self.data = data

    def __init__(self) -> None:
        self.graph = ig.Graph()

    def __calc_channel_thresholds(self) -> None:
        channel_sizes = []
        for t in self.data.teams:
            for c in t.channels:
                channel_sizes.append(len(c.channel_members))

        mean = np.mean(channel_sizes)
        sd = np.std(channel_sizes)

        self.__channel_members_upper = mean + 3 * sd
        self.__channel_members_lower = 2

    def __create_graph(self) -> None:
        graph_connections = defaultdict(int)

        for team in self.data.teams:
            for channel in team.channels:
                if len(channel.channel_members) > self.__channel_members_upper:
                    continue

                if len(channel.channel_members) < self.__channel_members_lower:
                    continue

                user_ids = [
                    member.user_id for member in channel.channel_members
                ]

                connections = list(combinations(set(user_ids), 2))

                for (source, target) in connections:
                    if source < target:
                        graph_connections[(source, target)] += 1
                    else:
                        graph_connections[(target, source)] += 1

        tuple_list = []
        for ((source, target), weight) in list(graph_connections.items()):
            tuple_list.append((source, target, weight))

        self.graph = ig.Graph.TupleList(tuple_list, weights=True)

    def __threshold_remove_nodes(self) -> None:
        node_degrees_list = self.graph.degree(self.graph.vs)

        mean = np.mean(node_degrees_list)
        sd = np.std(node_degrees_list)

        self.__node_degree_upper = mean + sd * 3
        self.__node_degree_lower = 2

        to_remove: List[ig.Vertex] = []
        for v in self.graph.vs:
            if self.graph.degree(v) < self.__node_degree_lower:
                to_remove.append(v)
            if self.graph.degree(v) > self.__node_degree_upper:
                to_remove.append(v)
        self.graph.delete_vertices(to_remove)

        self.graph = self.graph.clusters().giant()

    def __find_communities(self) -> None:
        self.communities = self.graph.community_infomap(edge_weights="weight")
        self.modularity = self.communities.modularity

    def find(self) -> None:
        self.__calc_channel_thresholds()
        self.__create_graph()
        self.__threshold_remove_nodes()
        self.__find_communities()

    def plot_graph(self) -> ig.Plot:
        if self.layout == None:
            self.layout = self.graph.layout(layout="lgl", maxiter=2000)

        p = ig.plot(self.graph,
                    target=f"igraph.png",
                    layout=self.layout,
                    edge_color="rgba(0,0,0,0.005)",
                    vertex_size=15,
                    bbox=(2750, 2750))

        return p

    def plot_graph_with_communities(self) -> ig.Plot:
        if self.layout == None:
            self.layout = self.graph.layout(layout="lgl", maxiter=2000)

        pal = ig.drawing.colors.ClusterColoringPalette(self.communities.n)
        g_colored = ig.Graph.copy(self.graph)
        g_colored.vs['color'] = pal.get_many(self.communities.membership)
        pc = ig.plot(g_colored,
                     target=f"igraph_cd.png",
                     layout=self.layout,
                     edge_color="rgba(0,0,0,0.005)",
                     vertex_size=15,
                     bbox=(2750, 2750))

        return pc

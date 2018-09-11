"""
The algorithm
greedily builds a tour by recalculating the traveling salesman
tour of the so-far selected nodes plus each possible candidate node
and picking the candidate that is the most cost-effective. We
"""

from math import sqrt, hypot
from Location import Locations


class SingleTourOrienteering:
    """
    G: graph
    B: budget
    s: start and end node
    p: tour
    T_p: visit time
    """
    def __init__(self, locations, time_budget, start_end_node):
        self.locations = locations
        self.time_budget = time_budget
        self.start_end_node = start_end_node

    def compute_path(self):
        p_star = Route()
        p_star.append(Node(self.start_end_node))
        while True:
            p = p_star
            best_margin = 0
            p_star = None
            for v in self.locations.getLocations():
                tsp = TSPSolver(p.append(v))
                p_apos = tsp.compute_tour()
                margin = (p_apos.calculate_tour_importance() - p_star.calculate_tour_importance()) / \
                         (p_apos.calculate_tour_duration() - p_star.calculate_tour_duration())
                if (margin > best_margin) & (p_apos.calculate_tour_duration() < self.time_budget):
                    best_margin = margin
                    p_star = p_apos
            if p_star is not None:
                break

        tau_p = p.create_tour_visit_time()
        return p, tau_p


class TSPSolver:
    """
    Args:
        data: a list of triples of ints.
                [
                    (nodeid, x, y),
                    (nodeid, x, y),
                    ...
                    (nodeid, x, y)
                ]
    Returns:
        best_path: list of (nodeid, x, y) triples in the order in which nodes
            should be visited.
    """
    def __init__(self, loc_attributes):
        self.loc_attributes = loc_attributes
        self.data = []
        for loc in loc_attributes:
            self.data.append(loc[0], loc[1], loc[2])

    def compute_tour(self):
        p = self.greedy_solution()
        p_star = self.run_2opt(p)
        return p_star

    def greedy_solution(self):
        best_path = None
        min_dist = None

        for start_node in self.data:
            total_distance = 0
            visited_nodes = [start_node]
            remaining_nodes = [node for node in self.data if node is not start_node]

            while len(remaining_nodes) > 0:
                nearest_node, distance = self.getNearestNode(remaining_nodes, visited_nodes[-1])
                visited_nodes.append(nearest_node)
                remaining_nodes.remove(nearest_node)
                total_distance += distance

            # account for distance from last node to first node
            _, firstx, firsty = visited_nodes[0]
            _, lastx, lasty = visited_nodes[-1]
            total_distance += sqrt(self.dist2(firstx, firsty, lastx, lasty))

            if min_dist is None or total_distance < min_dist:
                best_path = visited_nodes
                min_dist = total_distance
                # print("starting at node {i} gives a distance of {d}".format(i=start_node[0], d=total_distance))

        route = Route()
        for loc in best_path:
            lid = loc[0]
            route.append(Node(self.loc_attributes[lid]))

        return route

    def dist2(self, x1, y1, x2, y2):
        """
        Computes Euclidean distance squared
        """
        return (x2 - x1)**2 + (y2 - y1)**2

    def getNearestNode(self, remaining_nodes, current_node):
        """
        Args:
            remaining_nodes: list of (nodeid, x, y) triples
            current_node: the "current" node; (nodeid, x, y)
        Returns:
            1. nearest node: the (nodeid, x, y) triple closest to the current node
            2. the distance between this nearest node and the current node
        """
        _, cur_x, cur_y = current_node
        # dict that maps {dist2(a, b) -> b} where a is the "current" node.
        dist_to_node = {self.dist2(cur_x, cur_y, x, y): (nodeid, x, y) for nodeid, x, y in remaining_nodes}
        return dist_to_node[min(dist_to_node)], sqrt(min(dist_to_node))

    def run_2opt(self, route):
        """
        improves an existing route using the 2-opt swap until no improved route is found
        best path found will differ depending of the start node of the list of nodes
            representing the input tour
        returns the best path found
        route - route to improve
        """
        improvement = True
        best_route = route
        best_distance = self.route_distance(route)
        while improvement:
            improvement = False
            for i in range(len(best_route) - 1):
                for k in range(i+1, len(best_route)):
                    new_route = self.swap_2opt(best_route, i, k)
                    new_distance = self.route_distance(new_route)
                    if new_distance < best_distance:
                        best_distance = new_distance
                        best_route = new_route
                        improvement = True
                        break #improvement found, return to the top of the while loop
                if improvement:
                    break
        assert len(best_route) == len(route)
        return best_route

    def route_distance(self, route):
        """
        returns the distance traveled for a given tour
        route - sequence of nodes traveled, does not include
                start node at the end of the route
        """
        dist = 0
        prev = route[-1]
        for node in route:
            dist += node.euclidean_dist(prev)
            prev = node
        return dist

    def swap_2opt(self, route, i, k):
        """
        swaps the endpoints of two edges by reversing a section of nodes,
            ideally to eliminate crossovers
        returns the new route created with a the 2-opt swap
        route - route to apply 2-opt
        i - start index of the portion of the route to be reversed
        k - index of last node in portion of route to be reversed
        pre: 0 <= i < (len(route) - 1) and i < k < len(route)
        post: length of the new route must match length of the given route
        """
        assert i >= 0 and i < (len(route) - 1)
        assert k > i and k < len(route)
        new_route = route[0:i]
        new_route.extend(reversed(route[i:k + 1]))
        new_route.extend(route[k+1:])
        assert len(new_route) == len(route)
        return new_route


class Route:
    def __init__(self):
        self.route = []

    def append(self, node):
        self.route.append(node)

    def calculate_tour_utility(self):
        importance = None
        duration = None
        for node in self.route:
            importance += node.importance
            duration += node.duration
        return importance

    def calculate_tour_duration(self, p):
        duration = None
        for node in self.route:
            duration += node.duration
        return duration

    def get_edges_from_route(self):
        edges_pair = []
        for i in range(len(self.route)):
            if i % 2 != 0:
                edges_pair.append((self.route[i], self.route[i + 1]))
        return edges_pair

    def create_tour_visit_time(self):
        tau_p = []
        for node_u, node_v in self.route.get_edges_from_route():
            tau_p.append(node_u.duration + sqrt((node_v.x - node_u.x)**2 + (node_v.y - node_u.y)**2))
        return tau_p


class Node:
    """
    represents a node in a TSP tour
    """
    def __init__(self, loc_attributes):
        self.lid = loc_attributes[0] # start position in a route's order
        self.x = loc_attributes[1]   # x coordinate
        self.y = loc_attributes[2]   # y coordinate
        self.importance = loc_attributes[3]
        self.duration = loc_attributes[4]

    def euclidean_dist(self, other):
        """
        returns the Euclidean distance between this Node and other Node
        other - other node
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return hypot(dx, dy)


if __name__ == '__main__':
    locations = Locations()
    tsp_solver = TSPSolver(locations.get_locations_attributes())
    p = tsp_solver.greedy_solotion()
    print(p)
    p_star = tsp_solver.run_2opt(p)
    print(p_star)

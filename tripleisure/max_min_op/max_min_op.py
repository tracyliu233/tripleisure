from .single_tour_op import Route, Node, SingleTourOrienteering


class MaxMinOrienteering:
    def __init__(self, locations, time_budget, required_tours, start_end_node, target_importance):
        self.locations = locations
        self.time_budget = time_budget
        self.required_tours = required_tours
        self.start_end_node = start_end_node
        self.target_importance = target_importance

    def compute_path(self):
        # Stage 1
        tour_list = []
        tau_list = []
        for location_attribute in self.locations.get_locations_attributes():
            if location_attribute[3] > self.target_importance:
                route = Route()
                route.append(self.start_end_node)
                route.append(Node(location_attribute))
                tour_list.append(route)
                tau_list.append(route.create_tour_visit_time())
                del self.locations[location_attribute[0]]
        if len(tour_list) > self.required_tours:
            return tour_list, tau_list

        # Stage 2
        for i in range(self.required_tours - len(tour_list ) + 1):
            sto = SingleTourOrienteering(self.locations, self.time_budget, self.start_end_node)
            tour, tau = sto.compute_path()
            tour, tar = sto.truncate_tour(tour, tau)
            if tour.calculate_tour_utility >= self.target_importance:
                tour_list.append(tour)
                tau_list.append(tau)
                for node in tour:
                    del self.locations[node.lid]

        # Stage 3
        return tour_list, tau_list

    def truncate_tour(self, tour, tau):
        for id, node in enumerate(tour):
            del tour[id]
            del tau[id]
            if tour.calculate_tour_utility() <= 2*self.target_importance:
                break
        return tour, tau



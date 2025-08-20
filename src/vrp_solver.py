from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def solve_vrp(vehicle_count, capacity, depot, customers, distance_matrix, discharge_mode=False):
    all_points = [(depot["X"], depot["Y"])] + list(zip(customers["X"], customers["Y"]))
    demands = [0] + list(customers["Demand"])
    
    routing.AddDisjunction([manager.NodeToIndex(node)], -penalty)

    # Assign a reward/penalty for discharging stations
    penalties = [0]
    for _, row in customers.iterrows():
        if discharge_mode and row["NodeType"].lower() == "dischargestation":
            penalties.append(-10)  # Negative reward = profit
        else:
            penalties.append(0)

    manager = pywrapcp.RoutingIndexManager(len(all_points), vehicle_count, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_idx):
        from_node = manager.IndexToNode(from_idx)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [capacity] * vehicle_count,
        True,
        "Capacity"
    )

    # Optional: add discharging incentives as soft constraints
    if discharge_mode:
        for node in range(1, len(all_points)):
            penalty = penalties[node]
            if penalty < 0:
                routing.AddDisjunction([manager.NodeToIndex(node)], -penalty)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    output = []
    if solution:
        for vehicle_id in range(vehicle_count):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(0)
            if len(route) > 2:
                output.append((vehicle_id, route))
    return output

    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_idx):
        from_node = manager.IndexToNode(from_idx)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [capacity] * vehicle_count,
        True,
        "Capacity"
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    output = []
    if solution:
        for vehicle_id in range(vehicle_count):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)
                index = solution.Value(routing.NextVar(index))
            route.append(0)
            if len(route) > 2:
                output.append((vehicle_id, route))
    return output

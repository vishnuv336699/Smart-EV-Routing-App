import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import math
import os
from io import StringIO
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# --- Config ---
st.set_page_config(page_title="Smart EV Routing App", layout="wide")

# --- Helpers ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2)**2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def simulate_grid_status():
    demand_levels = ['Low', 'Medium', 'High']
    incentives = {'Low': 2.5, 'Medium': 5.0, 'High': 7.5}
    level = np.random.choice(demand_levels)
    return level, incentives[level]

def should_discharge(battery, distance_to_station, deliveries_left, delivery_reward, incentive, return_dist):
    delivery_profit = deliveries_left * delivery_reward
    discharge_profit = max((battery - (deliveries_left * 5 + return_dist * 0.2)), 0) * 0.5 * incentive
    return battery > 50 and discharge_profit > delivery_profit

# --- Sidebar ---
st.sidebar.title("Smart EV Routing")
mode = st.sidebar.radio("Select Input Mode", ["Use Test Case", "Upload Your Own File"])
uploaded_file = None

if mode == "Use Test Case":
    test_dir = "Test_Case_CSV_Files"
    test_files = sorted([f for f in os.listdir(test_dir) if f.endswith(".csv")])
    selected_file = st.sidebar.selectbox("Choose Test Case", ["-- Select a test case --"] + test_files)
    if selected_file != "-- Select a test case --":
        with open(os.path.join(test_dir, selected_file), "r") as f:
            uploaded_file = StringIO(f.read())
        st.sidebar.success(f"Loaded: {selected_file}")
elif mode == "Upload Your Own File":
    uploaded_file = st.sidebar.file_uploader("Upload EV routing CSV", type="csv")

st.title(" Smart EV Routing App ")
discharge_mode = st.sidebar.checkbox("Enable Smart Discharge Strategy")
grid_demand, incentive = simulate_grid_status()
st.sidebar.metric("Grid Demand", grid_demand)
st.sidebar.metric("Incentive ₹/kWh", incentive)

# --- Solver ---
def solve_vrp(vehicle_count, capacity, depot, customers, distance_matrix, discharge_mode=False, fixed_costs=None):
    all_points = [(depot["Latitude"], depot["Longitude"])] + list(zip(customers["Latitude"], customers["Longitude"]))
    demands = [0] + list(customers["Demand"])
    manager = pywrapcp.RoutingIndexManager(len(all_points), vehicle_count, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return int(distance_matrix[from_node][to_node] * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_idx):
        from_node = manager.IndexToNode(from_idx)
        return int(demands[from_node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, [capacity] * vehicle_count, True, "Capacity"
    )

    # 🔥 Apply fixed costs if provided
    if fixed_costs:
        for i in range(vehicle_count):
            routing.SetFixedCostOfVehicle(fixed_costs[i], i)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)

    output = []
    scores = []

    if solution:
        for v_id in range(vehicle_count):
            index = routing.Start(v_id)
            route, score, battery = [], 0, 100
            energy_used, energy_discharged = 0, 0
            delivery_reward = 10

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)

                if node != 0:
                    row = customers.iloc[node - 1]
                    lat1, lon1 = all_points[route[-2]] if len(route) > 1 else all_points[0]
                    lat2, lon2 = all_points[node]
                    dist = haversine(lat1, lon1, lat2, lon2)
                    energy_used += dist * 0.2
                    battery -= dist * 0.2

                    if row["NodeType"].lower() == "dischargestation" and discharge_mode:
                        remaining_customers = customers[customers["NodeType"].str.lower() == "customer"]
                        remaining_deliveries = len(remaining_customers)
                        return_dist = haversine(lat2, lon2, depot["Latitude"], depot["Longitude"])
                        if should_discharge(battery, dist, remaining_deliveries, delivery_reward, incentive, return_dist):
                            discharged = battery * 0.5
                            battery *= 0.5
                            energy_discharged += discharged
                            score += 10
                    elif row["NodeType"].lower() == "customer":
                        score += delivery_reward

                index = solution.Value(routing.NextVar(index))

            route.append(0)

            if len(route) > 2:
                output.append((v_id, route))
                scores.append((score, energy_used, energy_discharged))

    return output, scores

# --- Main Logic ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        expected_cols = {"ID", "Latitude", "Longitude", "Demand", "NodeType"}
        if not expected_cols.issubset(df.columns):
            st.error(f"Missing required columns: {expected_cols}")
        else:
            depot = df[df["NodeType"].str.lower() == "depot"].iloc[0]
            customers = df[df["NodeType"].str.lower() != "depot"]
            all_points = [(depot["Latitude"], depot["Longitude"])] + list(zip(customers["Latitude"], customers["Longitude"]))
            distance_matrix = [[haversine(x1, y1, x2, y2) for (x2, y2) in all_points] for (x1, y1) in all_points]
            vehicle_count = 3
            capacity = 100
            solution, scores = solve_vrp(vehicle_count, capacity, depot, customers, distance_matrix, discharge_mode)

            m = folium.Map(location=[depot["Latitude"], depot["Longitude"]], zoom_start=12)
            for i, (v_id, route) in enumerate(solution):
                st.subheader(f"Vehicle Route:")
                labels = []
                for idx in route:
                    if idx == 0:
                        label = "Depot"
                        lat, lon = depot["Latitude"], depot["Longitude"]
                        color = "blue"
                    else:
                        row = customers.iloc[idx - 1]
                        node_id = row["ID"]
                        node_type = row["NodeType"]
                        label = f"{node_id} ({node_type})"
                        lat, lon = row["Latitude"], row["Longitude"]
                        color = "green" if node_type.lower() == "customer" else "red"
                    labels.append(label)
                    folium.Marker([lat, lon], tooltip=label, icon=folium.Icon(color=color)).add_to(m)

                # Custom display format with Location names
                display_labels = []
                for idx in route:
                    if idx == 0:
                        display_labels.append("Depot")
                    else:
                        row = customers.iloc[idx - 1]
                        node_type = row["NodeType"]
                        location_name = row["Location"]  # <-- Make sure CSV has this column
                        display_labels.append(f"{location_name} ({node_type})")
                
                st.write(" → ".join(display_labels))

                score, used, discharged = scores[i]
                st.metric("Driver Score", f"{score}")
                st.metric("Energy Used (kWh)", f"{used:.2f}")
                st.metric("Energy Discharged (kWh)", f"{discharged:.2f}")
                st.metric("Earnings (₹)", f"{discharged * incentive:.2f}")
            st_folium(m, width=700)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a file or select a test case.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align:center;">
    <strong>Developed by Team-Mind_Mesh</strong><br>
    Developers: Amrutha D , Vishnu V<br>
    REVA University, Bangalore
</div>
""", unsafe_allow_html=True)



import pandas as pd

def parse_solomon_dataset(file_path: str):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    vehicle_info = lines[4].split()
    vehicle_count = int(vehicle_info[0])
    capacity = int(vehicle_info[1])

    data_lines = lines[9:]
    data = []

    for line in data_lines:
        parts = line.split()
        if len(parts) == 7:
            data.append([int(p) if p.isdigit() else float(p) for p in parts])

    df = pd.DataFrame(data, columns=[
        'CustomerID', 'X', 'Y', 'Demand', 'ReadyTime', 'DueDate', 'ServiceTime'
    ])

    depot = df.iloc[0]
    customers = df.iloc[1:].reset_index(drop=True)
    return vehicle_count, capacity, depot, customers

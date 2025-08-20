import pandas as pd

def parse_csv_dataset(file_path: str, vehicle_count: int, capacity: int):
    df = pd.read_csv(file_path)
    depot = df[df['CustomerID'] == 0].iloc[0]
    customers = df[df['CustomerID'] != 0].reset_index(drop=True)
    return vehicle_count, capacity, depot, customers

import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

"""Port Log Generator
-------------------
Simulates daily port operations using train transport logs (train_log.xlsx). 
Generates arrivals, departures, and storage metrics for Coal, Limestone, and Steel.
"""

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DEFAULT_TRANSPORT_LOG = os.path.join(OUTPUT_DIR, "train_log.xlsx")
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "port_log.xlsx")

# ---------------- PORTS ----------------
PORTS = ['Haldia Port', 'Paradip Port', 'Visakhapatnam Port', 'Kolkata Port']

# ---------------- THRESHOLDS & RANGES ----------------
COAL_TRIGGER = 20000
COAL_MAX_STORAGE = 50000
COAL_SHIP_RANGE = (25000, 40000)

LIMESTONE_TRIGGER = 20000
LIMESTONE_MAX_STORAGE = 40000
LIMESTONE_SHIP_RANGE = (12000, 35000)

STEEL_TRIGGER = 25000
STEEL_MAX_STORAGE = 50000
STEEL_SHIP_RANGE = (10000, 20000)

# ---------------- HELPERS ----------------
def get_random_arrival(quantity_range, max_add):
    return min(random.uniform(*quantity_range), max_add)

def get_weather_index():
    return random.choices([0, 1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.15, 0.1, 0.04, 0.01], k=1)[0]

# ---------------- MAIN GENERATOR ----------------
def generate_port_log(transport_log_path=DEFAULT_TRANSPORT_LOG, output_path=DEFAULT_OUTPUT_LOG):
    print("STATUS: Simulating Port Logistics and Storage.")
    print(f"STATUS: Fetching scheduled train data from transport log: {transport_log_path}")
    
    if not os.path.exists(transport_log_path):
        print(f"ERROR: Transport log file not found at {transport_log_path}. Please run the train log generator first.")
        sys.exit(1)
    
    df_transport = pd.read_excel(transport_log_path)
    df_transport['departure_time'] = pd.to_datetime(df_transport['departure_time'])
    df_transport['arrival_time'] = pd.to_datetime(df_transport['arrival_time'])
    
    min_date = df_transport['departure_time'].dt.date.min()
    max_date = df_transport['arrival_time'].dt.date.max()
    all_dates = pd.date_range(start=min_date, end=max_date).date

    print("STATUS: Analyzing total scheduled movements to constrain generated ship movements.")
    
    # Pre-calculate total scheduled departures per port
    total_scheduled_departures = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    for port in PORTS:
        port_departures = df_transport[df_transport['source'] == port]
        total_scheduled_departures[port]['Coal'] = port_departures[port_departures['material']=='Coal']['quantity_tonnes'].sum()
        total_scheduled_departures[port]['Limestone'] = port_departures[port_departures['material']=='Limestone']['quantity_tonnes'].sum()
        total_scheduled_departures[port]['Steel'] = port_departures[port_departures['material']=='Steel']['quantity_tonnes'].sum()

    # Initialize storage and trackers
    storage = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    total_received = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    total_shipped = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}

    port_logs = []
    last_day = all_dates[-1]

    print(f"STATUS: Simulating daily operations from {min_date} to {max_date}...")

    for date in all_dates:
        is_last_day = (date == last_day)

        for port in PORTS:
            cargo_arrived = 0.0
            cargo_departed = 0.0

            daily_log = {
                'date': date,
                'port_name': port,
                'coal_bod_storage_tonnes': storage[port]['Coal'],
                'limestone_bod_storage_tonnes': storage[port]['Limestone'],
                'steel_bod_storage_tonnes': storage[port]['Steel'],
                'coal_arrived_tonnes': 0.0,
                'limestone_arrived_tonnes': 0.0,
                'coal_departed_tonnes': 0.0,
                'limestone_departed_tonnes': 0.0,
                'steel_arrived_tonnes': 0.0,
                'steel_shipped_tonnes': 0.0,
                'coal_eod_storage_tonnes': 0.0,
                'limestone_eod_storage_tonnes': 0.0,
                'steel_eod_storage_tonnes': 0.0
            }

            # Process departures
            departures_today = df_transport[df_transport['departure_time'].dt.date == date]
            for _, row in departures_today.iterrows():
                mat = row['material']
                qty = row['quantity_tonnes']
                src = row['source']
                if src != port:
                    continue

                if mat in ['Coal', 'Limestone']:
                    max_allowed = total_scheduled_departures[port][mat] - total_received[port][mat]
                    if max_allowed > 0:
                        range_ = COAL_SHIP_RANGE if mat == 'Coal' else LIMESTONE_SHIP_RANGE
                        max_storage = COAL_MAX_STORAGE if mat == 'Coal' else LIMESTONE_MAX_STORAGE
                        arrival_qty = min(get_random_arrival(range_, max_allowed), max_storage - storage[port][mat])
                        storage[port][mat] += arrival_qty
                        daily_log[f'{mat.lower()}_arrived_tonnes'] += arrival_qty
                        total_received[port][mat] += arrival_qty
                        cargo_arrived += arrival_qty

                # Deduct departure quantity
                storage[port][mat] -= qty
                if mat in ['Coal', 'Limestone']:
                    daily_log[f'{mat.lower()}_departed_tonnes'] += qty
                else:
                    daily_log['steel_shipped_tonnes'] += qty
                total_shipped[port][mat] += qty
                cargo_departed += qty

            # Process arrivals
            arrivals_today = df_transport[df_transport['arrival_time'].dt.date == date]
            for _, row in arrivals_today.iterrows():
                mat = row['material']
                qty = row['quantity_tonnes']
                dest = row['destination']
                if dest != port:
                    continue

                storage[port][mat] += qty
                if mat == 'Steel':
                    daily_log['steel_arrived_tonnes'] += qty
                else:
                    daily_log[f'{mat.lower()}_arrived_tonnes'] += qty
                total_received[port][mat] += qty
                cargo_arrived += qty

            # Trigger inbound replenishments
            for mat, trigger, range_, max_storage in [
                ('Coal', COAL_TRIGGER, COAL_SHIP_RANGE, COAL_MAX_STORAGE),
                ('Limestone', LIMESTONE_TRIGGER, LIMESTONE_SHIP_RANGE, LIMESTONE_MAX_STORAGE)
            ]:
                if storage[port][mat] < trigger:
                    max_allowed = total_scheduled_departures[port][mat] - total_received[port][mat]
                    if max_allowed > 0:
                        qty = min(get_random_arrival(range_, max_allowed), max_storage - storage[port][mat])
                        storage[port][mat] += qty
                        daily_log[f'{mat.lower()}_arrived_tonnes'] += qty
                        total_received[port][mat] += qty
                        cargo_arrived += qty

            # Trigger steel shipments
            shipment_trigger = 0 if is_last_day else STEEL_TRIGGER
            if storage[port]['Steel'] >= shipment_trigger:
                if is_last_day:
                    qty = storage[port]['Steel']
                else:
                    min_ship_req = STEEL_SHIP_RANGE[0]
                    if storage[port]['Steel'] >= min_ship_req:
                        qty = random.uniform(*STEEL_SHIP_RANGE)
                        qty = min(qty, storage[port]['Steel'])
                    else:
                        qty = 0
                if qty > 0:
                    storage[port]['Steel'] -= qty
                    daily_log['steel_shipped_tonnes'] += qty
                    cargo_departed += qty

            # Capture EOD storage
            daily_log['coal_eod_storage_tonnes'] = storage[port]['Coal']
            daily_log['limestone_eod_storage_tonnes'] = storage[port]['Limestone']
            daily_log['steel_eod_storage_tonnes'] = storage[port]['Steel']
            daily_log['total_cargo_flow_today_tonnes'] = round(cargo_arrived + cargo_departed, 2)
            daily_log['weather_delay_index'] = get_weather_index()
            daily_log['steel_storage_utilization_percent'] = round((storage[port]['Steel']/STEEL_MAX_STORAGE)*100,2)

            # Round all floats
            rounded_log = {k: round(v,2) if isinstance(v,float) else v for k,v in daily_log.items()}
            port_logs.append(rounded_log)

    # ---------------- EXPORT ----------------
    df_port_log = pd.DataFrame(port_logs).sort_values(by=['date','port_name'])
    
    print(f"STATUS: Writing final port log data to Excel file: {output_path}")
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df_port_log.to_excel(writer, index=False, sheet_name='Port Logs')
            wb, ws = writer.book, writer.sheets['Port Logs']
            fmt_dec = wb.add_format({'num_format':'0.00'})
            ws.set_column('C:Z', 18, fmt_dec)
        print(f"SUCCESS: Port log dataset successfully saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)

# if __name__ == "__main__":                                           #***Commented to prevent accidental run***
#     generate_port_log(DEFAULT_TRANSPORT_LOG, DEFAULT_OUTPUT_LOG)

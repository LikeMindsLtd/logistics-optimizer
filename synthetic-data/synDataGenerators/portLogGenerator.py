import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

'''This generator simulates the daily activity at the port, creating a log of all
    vessel arrivals, loading operations, and departures. It uses the daily steel
    export figures from plant_log.xlsx to determine the total material requiring
    shipment. It then simulates vessel movements with varying capacities and randomly
    generates key port metrics, including berthing time, loading duration, and total
    steel loaded for each vessel, ensuring the cumulative steel loaded matches the
    cumulative steel exported by the plants.'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

DEFAULT_TRANSPORT_LOG = os.path.join(OUTPUT_DIR, "train_log.xlsx")
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "port_log.xlsx")

# ---------------- PORTS ----------------
PORTS = ['Haldia Port', 'Paradip Port', 'Visakhapatnam Port', 'Kolkata Port']

# ---------------- THRESHOLDS & SHIP RANGES ----------------
COAL_TRIGGER = 20000
COAL_MAX_STORAGE = 50000
COAL_SHIP_RANGE = (25000, 40000)

LIMESTONE_TRIGGER = 20000
LIMESTONE_MAX_STORAGE = 40000
LIMESTONE_SHIP_RANGE = (12000, 35000)

STEEL_TRIGGER = 25000 
STEEL_MAX_STORAGE = 50000
STEEL_SHIP_RANGE = (10000, 20000) 

# ---------------- HELPER FUNCTIONS----------------
def get_random_arrival(quantity_range, max_add):
    # Ensuring the generated quantity is within the range and doesn't exceed the max allowed
    return min(random.uniform(*quantity_range), max_add)

def get_weather_index():
    #Simulating a random weather severity index (0=clear, 5=severe delay).
    return random.choices([0, 1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.15, 0.1, 0.04, 0.01], k=1)[0]


# ---------------- MAIN GENERATOR ----------------
def generate_port_log(transport_log_path=DEFAULT_TRANSPORT_LOG, output_path=DEFAULT_OUTPUT_LOG):
    
    print("STATUS: Simulating Port Logistics and Storage.")
    print(f"STATUS: Fetching scheduled train data from transport log: {transport_log_path}")
    
    if not os.path.exists(transport_log_path):
        print(f"ERROR: Transport log file not found at {transport_log_path}. Please run the train log generator first.")
        sys.exit(1)
        
    df_transport = pd.read_excel(transport_log_path)
    df_transport['Departure_Time'] = pd.to_datetime(df_transport['Departure_Time'])
    df_transport['Arrival_Time'] = pd.to_datetime(df_transport['Arrival_Time'])

    min_date = df_transport['Departure_Time'].dt.date.min()
    max_date = df_transport['Arrival_Time'].dt.date.max()
    all_dates = pd.date_range(start=min_date, end=max_date).date

    print("STATUS: Analyzing total scheduled movements to constrain generated ship movements.")
    
    # Pre-calculating total scheduled movements from the transport log
    total_scheduled_departures = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    for port in PORTS:
        port_departures = df_transport[df_transport['Source'] == port]
        total_scheduled_departures[port]['Coal'] = port_departures[port_departures['Material']=='Coal']['Quantity (tonnes)'].sum()
        total_scheduled_departures[port]['Limestone'] = port_departures[port_departures['Material']=='Limestone']['Quantity (tonnes)'].sum()
        total_scheduled_departures[port]['Steel'] = port_departures[port_departures['Material']=='Steel']['Quantity (tonnes)'].sum()

    # Initializing storage and trackers
    storage = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    
    # Trackers for scheduled movements to ensure we don't exceed the total defined in df_transport
    total_scheduled_received_so_far = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    total_scheduled_shipped_so_far = {port: {'Coal':0, 'Limestone':0, 'Steel':0} for port in PORTS}
    
    port_logs = []
    
    # Identify the last day of the simulation
    last_day = all_dates[-1]

    print(f"STATUS: Simulating daily operations from {min_date} to {max_date}...")

    for date in all_dates:
        is_last_day = (date == last_day)
        
        for port in PORTS:
            
            cargo_arrived = 0.0
            cargo_departed = 0.0
            daily_log = {
                'Date': date,
                'Port': port,
                'Coal_BOD_Storage(tonnes)': storage[port]['Coal'],
                'Limestone_BOD_Storage(tonnes)': storage[port]['Limestone'],
                'Steel_BOD_Storage(tonnes)': storage[port]['Steel'],
                'Coal_Arrived(tonnes)': 0.0,
                'Limestone_Arrived(tonnes)': 0.0,
                'Coal_Departed(tonnes)': 0.0,
                'Limestone_Departed(tonnes)': 0.0,
                'Steel_Arrived(tonnes)': 0.0,
                'Steel_Shipped(tonnes)': 0.0,
                'Coal_EOD_Storage(tonnes)': 0.0,
                'Limestone_EOD_Storage(tonnes)': 0.0,
                'Steel_EOD_Storage(tonnes)': 0.0
            }

            departures_today = df_transport[df_transport['Departure_Time'].dt.date == date]
            for _, row in departures_today.iterrows():
                mat = row['Material']
                qty = row['Quantity (tonnes)']
                src = row['Source']
                
                if src != port:
                    continue

                if mat in ['Coal', 'Limestone'] and storage[port][mat] < qty:
                    
                    max_allowed = total_scheduled_departures[port][mat] - total_scheduled_received_so_far[port][mat]
                    
                    if max_allowed > 0:
                        range_ = COAL_SHIP_RANGE if mat == 'Coal' else LIMESTONE_SHIP_RANGE
                        max_storage = COAL_MAX_STORAGE if mat == 'Coal' else LIMESTONE_MAX_STORAGE
                        
                        arrival_qty = min(get_random_arrival(range_, max_allowed),
                                          max_storage - storage[port][mat])
                        
                        storage[port][mat] += arrival_qty
                        daily_log[f'{mat}_Arrived(tonnes)'] += arrival_qty
                        total_scheduled_received_so_far[port][mat] += arrival_qty
                        cargo_arrived += arrival_qty

                storage[port][mat] -= qty
                daily_log[f'{mat}_Departed(tonnes)' if mat in ['Coal', 'Limestone'] else 'Steel_Shipped(tonnes)'] += qty
                total_scheduled_shipped_so_far[port][mat] += qty
                cargo_departed += qty

            arrivals_today = df_transport[df_transport['Arrival_Time'].dt.date == date]
            for _, row in arrivals_today.iterrows():
                mat = row['Material']
                qty = row['Quantity (tonnes)']
                dest = row['Destination']
                
                if dest != port:
                    continue
                    
                storage[port][mat] += qty
                daily_log[f'{mat}_Arrived(tonnes)' if mat != 'Steel' else 'Steel_Arrived(tonnes)'] += qty 
                total_scheduled_received_so_far[port][mat] += qty
                cargo_arrived += qty

            for mat, trigger, range_, max_storage in [
                ('Coal', COAL_TRIGGER, COAL_SHIP_RANGE, COAL_MAX_STORAGE),
                ('Limestone', LIMESTONE_TRIGGER, LIMESTONE_SHIP_RANGE, LIMESTONE_MAX_STORAGE)
            ]:
                if storage[port][mat] < trigger:
                    
                    max_allowed = total_scheduled_departures[port][mat] - total_scheduled_received_so_far[port][mat]
                    
                    if max_allowed > 0:
                        qty = min(get_random_arrival(range_, max_allowed),
                                  max_storage - storage[port][mat])
                        
                        storage[port][mat] += qty
                        daily_log[f'{mat}_Arrived(tonnes)'] += qty
                        total_scheduled_received_so_far[port][mat] += qty
                        cargo_arrived += qty

            shipment_trigger = 0 if is_last_day else STEEL_TRIGGER
            
            if storage[port]['Steel'] >= shipment_trigger:
                
                if is_last_day:
                    qty = storage[port]['Steel'] # Cleaning up all remaining steel on the last day
                else:
                    min_ship_req = STEEL_SHIP_RANGE[0]
                    
                    if storage[port]['Steel'] >= min_ship_req:
                        qty = random.uniform(STEEL_SHIP_RANGE[0], STEEL_SHIP_RANGE[1])
                        qty = min(qty, storage[port]['Steel'])
                    else:
                        qty = 0 
                
                if qty > 0:
                    storage[port]['Steel'] -= qty
                    daily_log['Steel_Shipped(tonnes)'] += qty
                    cargo_departed += qty
            
            # Capturing the final storage level for the end of the day
            daily_log['Coal_EOD_Storage(tonnes)'] = storage[port]['Coal']
            daily_log['Limestone_EOD_Storage(tonnes)'] = storage[port]['Limestone']
            daily_log['Steel_EOD_Storage(tonnes)'] = storage[port]['Steel']
            daily_log['Total_Cargo_Flow_Today(tonnes)'] = round(cargo_arrived + cargo_departed, 2)
            daily_log['Weather_Delay_Index'] = get_weather_index()
            daily_log['Steel_Storage_Utilization(%)'] = round(
                (storage[port]['Steel'] / STEEL_MAX_STORAGE) * 100, 2)

            rounded_log = {}
            for k, v in daily_log.items():
                if isinstance(v, float):
                    rounded_log[k] = round(v, 2)
                else:
                    rounded_log[k] = v
                    
            port_logs.append(rounded_log)

    # ---------------- EXPORT ----------------
    df_port_log = pd.DataFrame(port_logs).sort_values(by=['Date', 'Port'])
    
    print(f"STATUS: Writing final port log data to Excel file: {output_path}")
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df_port_log.to_excel(writer, index=False, sheet_name='Port Logs')
            workbook = writer.book
            worksheet = writer.sheets['Port Logs']
            two_dec = workbook.add_format({'num_format':'0.00'})
            worksheet.set_column('C:Z', 18, two_dec)      # Apply formatting to all data columns
            
        print(f"SUCCESS: Port log dataset successfully saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)
        
# ---------------- MAIN ----------------
# if __name__ == "__main__":                                           ***Commented to prevent accidental run***
#     generate_port_log(DEFAULT_TRANSPORT_LOG, DEFAULT_OUTPUT_LOG)
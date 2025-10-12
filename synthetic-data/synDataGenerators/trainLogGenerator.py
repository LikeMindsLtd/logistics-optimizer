import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

'''This generator will create a detailed log of all inbound material trains and outbound
    steel export trains based on the daily requirements and arrivals in plant_log.xlsx.
    It simulates individual train trips by breaking down the daily total quantities (Coal,
    Limestone, and Steel) into discrete train shipments with randomized capacities.
    It generates key details for each train, including the Train_ID, Material_Type,
    Origin/Destination, and the estimated Departure and Arrival Timestamps, ensuring
    the sum of all individual train capacities matches the daily requirement for each plant.'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets") 

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
DEFAULT_PLANT_LOG = os.path.join(OUTPUT_DIR, "plant_log.xlsx")
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "train_log.xlsx") 

# ---------------- PLANT SOURCES ----------------
PLANT_PORTS = {
    'Bhilai Steel Plant': {
        'coal_sources': [('Dalli Rajhara Mine', 35), ('Haldia Port', 650), ('Visakhapatnam Port', 560)],
        'limestone_sources': [('Bhilai Limestone Mine', 25), ('Paradip Port', 500)],
        'export_ports': [('Haldia Port', 650), ('Visakhapatnam Port', 560)]
    },
    'Durgapur Steel Plant': {
        'coal_sources': [('Raniganj Coalfields', 40), ('Haldia Port', 160), ('Visakhapatnam Port', 700)],
        'limestone_sources': [('Chotonagpur Limestone', 60), ('Paradip Port', 400)],
        'export_ports': [('Kolkata Port', 160), ('Haldia Port', 180)]
    },
    'Rourkela Steel Plant': {
        'coal_sources': [('Chiria Coal Mine', 45), ('Paradip Port', 330), ('Visakhapatnam Port', 600)],
        'limestone_sources': [('Rourkela Limestone Mine', 30), ('Haldia Port', 350)],
        'export_ports': [('Paradip Port', 330), ('Visakhapatnam Port', 600)]
    },
    'Bokaro Steel Plant': {
        'coal_sources': [('Jharia Coalfields', 35), ('Haldia Port', 300), ('Paradip Port', 550)],
        'limestone_sources': [('Bokaro Limestone Mine', 25), ('Visakhapatnam Port', 500)],
        'export_ports': [('Haldia Port', 300), ('Paradip Port', 550)]
    },
    'IISCO Steel Plant': {
        'coal_sources': [('Raniganj Coalfields', 30), ('Haldia Port', 180), ('Visakhapatnam Port', 600)],
        'limestone_sources': [('Burnpur Limestone Mine', 20), ('Paradip Port', 400)],
        'export_ports': [('Haldia Port', 180), ('Visakhapatnam Port', 600)]
    }
}

# ---------------- TRAIN CAPACITIES & SPEED ----------------
TRAIN_CAPACITY = {'Coal': 10000, 'Limestone': 8000, 'Steel': 5000}
DEFAULT_SPEED_KMPH = 40

# ---------------- LOADING/UNLOADING RATES (hrs/tonne) ----------------
LOADING_RATE = {'Coal': 0.0006, 'Limestone': 0.0005, 'Steel': 0.0010}
UNLOADING_RATE = {'Coal': 0.0005, 'Limestone': 0.0004, 'Steel': 0.0008}

# ---------------- COST CONFIGURATION (In RUPEES) ----------------
# Base Rail Freight (₹/tonne/km)
BASE_RAIL_FREIGHT_RATE = {'Coal': 4.5, 'Limestone': 3.5, 'Steel': 6.0} 
# Handling Cost at Port (₹/tonne)
BASE_PORT_HANDLING_COST = {'Coal': 200, 'Limestone': 150, 'Steel': 300}

# ---------------- RAKE MANAGEMENT SYSTEM CONFIG ----------------
NUM_RAKES = 50

RAKE_IDS = []
while len(RAKE_IDS) < NUM_RAKES:
    new_id = str(random.randint(100000, 999999)) 
    if new_id not in RAKE_IDS:
        RAKE_IDS.append(new_id)

ALL_LOCATIONS = list(PLANT_PORTS.keys()) + [loc[0] for p in PLANT_PORTS.values() for s in p['coal_sources']+p['limestone_sources']+p['export_ports'] for loc in [s]]
ALL_LOCATIONS = list(set(ALL_LOCATIONS)) 

RAKE_TRACKER = {
    rake_id: {
        'location': random.choice(ALL_LOCATIONS),
        'available_time': datetime.min, 
        'status': 'Available'
    } 
    for rake_id in RAKE_IDS
}

# ---------------- HELPER FUNCTIONS ----------------
def split_into_trains(quantity, max_capacity):
    loads = []
    remaining = quantity
    while remaining > 0:
        load = min(random.uniform(0.8, 1.0) * max_capacity, remaining)
        loads.append(round(load, 2))
        remaining -= load
    return loads

def choose_weighted_source(sources):
    weights = [0.7 if 'Mine' in s[0] or 'Plant' in s[0] else 0.3 for s in sources]
    return random.choices(sources, weights=weights, k=1)[0]

def calculate_times(qty, dist, material, speed=DEFAULT_SPEED_KMPH):
    base_time_h = dist / speed
    delay_h = random.uniform(1, 24) 
    loading_h = qty * LOADING_RATE[material] * random.uniform(0.9, 1.1)
    unloading_h = qty * UNLOADING_RATE[material] * random.uniform(0.9, 1.1)
    total_time_h = base_time_h + delay_h + loading_h + unloading_h
    return base_time_h, delay_h, loading_h, unloading_h, total_time_h

def calculate_costs(qty, dist, material, is_port_source):
    
    rail_freight_per_tonne = BASE_RAIL_FREIGHT_RATE[material] * dist * random.uniform(0.95, 1.05)
    port_handling_per_tonne = BASE_PORT_HANDLING_COST[material] * random.uniform(0.9, 1.1) if is_port_source else 0.0
    
    total_cost_per_tonne = rail_freight_per_tonne + port_handling_per_tonne
    total_trip_cost = total_cost_per_tonne * qty

    return rail_freight_per_tonne, port_handling_per_tonne, total_trip_cost

def random_time_in_day(date):
    """Return a datetime on the given date with random time"""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.combine(date, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)

def assign_rake(source_location, departure_time):

    # Number of currently available rakes *at the source*
    local_available_count = sum(1 for r_data in RAKE_TRACKER.values() 
                                 if r_data['location'] == source_location and r_data['available_time'] <= departure_time)
    
    # Rake Availability Index (High Index = High Availability/Low Congestion)
    # Rake Availability Index = (Local Available / Total Rakes) * 10
    rake_availability_index = round((local_available_count / NUM_RAKES) * 10, 2)
    
    best_rake_id = None
    
    # 1. Prioritizing Rakes at the source and available on time
    available_local_rakes = [
        r_id for r_id, r_data in RAKE_TRACKER.items()
        if r_data['location'] == source_location and r_data['available_time'] <= departure_time
    ]
    
    if available_local_rakes:
        best_rake_id = random.choice(available_local_rakes)
    else:
        # 2. Checking for any available rake globally
        available_anywhere_rakes = [
            r_id for r_id, r_data in RAKE_TRACKER.items()
            if r_data['available_time'] <= departure_time
        ]
        
        if available_anywhere_rakes:
            best_rake_id = random.choice(available_anywhere_rakes)
        else:
            # 3. NO rake is available: forces a delay
            earliest_time = datetime.max
            earliest_rake_id = None
            for r_id, r_data in RAKE_TRACKER.items():
                if r_data['available_time'] < earliest_time:
                    earliest_time = r_data['available_time']
                    earliest_rake_id = r_id
                
            best_rake_id = earliest_rake_id
            # Adjusting the departure time to be no earlier than the rake's availability
            departure_time = max(departure_time, earliest_time) 
    
    if best_rake_id:
        RAKE_TRACKER[best_rake_id]['status'] = 'In Transit'
        RAKE_TRACKER[best_rake_id]['location'] = source_location 
    
    return best_rake_id, departure_time, rake_availability_index

# ---------------- MAIN GENERATOR ----------------
def generate_train_log(plant_log_path, output_path):
    
    global RAKE_TRACKER
    
    print("STATUS: Simulating Indian Railways Freight Movements.")
    print(f"STATUS: Fetching daily material demand from plant log: {plant_log_path}")
    
    if not os.path.exists(plant_log_path):
        print(f"ERROR: Plant log file not found at {plant_log_path}. Please run the plant log generator first.")
        sys.exit(1)

    df = pd.read_excel(plant_log_path)
    transport_logs = []
    trip_counters = {plant: 1 for plant in PLANT_PORTS.keys()}
    
    df = df.sort_values(by='Date').reset_index(drop=True) 

    print("STATUS: Generating individual train trips, calculating costs, and managing rake pool...")
    
    for idx, row in df.iterrows():
        plant_date = pd.to_datetime(row['Date']).date() 
        plant = row['Plant_Name']

        for material in ['Coal', 'Limestone', 'Steel']:
            
            # ---------------- DETERMINE FLOW AND QUANTITY ----------------
            if material == 'Coal':
                qty_col = 'Coal_Arrived(in tonnes)'
                sources_list = PLANT_PORTS[plant]['coal_sources']
                dest = plant
                flow = 'Inbound'
            elif material == 'Limestone':
                qty_col = 'Limestone_Arrived(in tonnes)'
                sources_list = PLANT_PORTS[plant]['limestone_sources']
                dest = plant
                flow = 'Inbound'
            else: # Steel Export
                qty_col = 'Steel_Exported(in tonnes)'
                sources_list = PLANT_PORTS[plant]['export_ports']
                dest = None # Destination is a Port for export, which is determined later
                flow = 'Outbound'

            qty = row.get(qty_col, 0)
            if qty <= 0:
                continue

            trips = split_into_trains(qty, TRAIN_CAPACITY[material])
            
            for q in trips:
                
                trip_id = f"{plant[:3].upper()}_{trip_counters[plant]:04d}"
                trip_counters[plant] += 1
                
                # ---------------- DETERMINE SOURCE/DESTINATION AND DEPARTURE TIME ----------------
                if flow == 'Inbound':
                    source_loc, dist = choose_weighted_source(sources_list)
                    destination_loc = dest
                    # Inbound train departure must occur *before* the plant needed the material (Arrival_Time in plant log)
                    departure_time_default = random_time_in_day(plant_date) - timedelta(days=random.randint(2, 5)) 
                    is_port_source = 'Port' in source_loc or 'Mine' in source_loc
                else: # Outbound Steel
                    source_loc = plant
                    destination_loc, dist = random.choice(sources_list) # Steel goes to a Port
                    # Outbound train departure should happen on the day the steel was produced/exported
                    departure_time_default = random_time_in_day(plant_date) 
                    is_port_source = False # Source is the Plant

                # ---------------- RAKE ASSIGNMENT AND DELAY CHECK ----------------
                rake_id, final_departure_time, rake_availability_index = assign_rake(source_loc, departure_time_default)
                
                # ---------------- CALCULATE TIME AND COST METRICS ----------------
                base_time_h, delay_h, loading_h, unloading_h, total_time_h = calculate_times(
                    q, dist, material, DEFAULT_SPEED_KMPH 
                )
                
                # Calculating Costs
                rail_freight_per_tonne, port_handling_per_tonne, total_trip_cost = calculate_costs(
                    q, dist, material, is_port_source
                )

                arrival_time = final_departure_time + timedelta(hours=total_time_h)
                
                # ---------------- UPDATE RAKE TRACKER ----------------
                if rake_id:
                    # Rake becomes available at the destination location (plant or port)
                    RAKE_TRACKER[rake_id]['location'] = destination_loc 
                    # Available time is immediately after the train has been unloaded/loaded
                    RAKE_TRACKER[rake_id]['available_time'] = arrival_time 
                    RAKE_TRACKER[rake_id]['status'] = 'Available'
                
                transport_logs.append({
                    'Trip_ID': trip_id,
                    'Rake_ID': rake_id if rake_id else 'N/A', 
                    'Material_Flow': flow,
                    'Material': material,
                    'Source': source_loc,
                    'Destination': destination_loc,
                    'Quantity (tonnes)': float(f"{q:.2f}"),
                    'Distance_km': float(f"{dist:.2f}"),
                    
                    # --- TIME METRICS ---
                    'Rake_Availability_Index': float(f"{rake_availability_index:.2f}"), 
                    'Base_Time_h': float(f"{base_time_h:.2f}"),
                    'Loading_Time_h': float(f"{loading_h:.2f}"),
                    'Unloading_Time_h': float(f"{unloading_h:.2f}"),
                    'Delay_h': float(f"{delay_h:.2f}"),
                    'Total_Time_h': float(f"{total_time_h:.2f}"),
                    'Departure_Time': final_departure_time,
                    'Arrival_Time': arrival_time,
                    
                    # --- COST METRICS ---
                    'Rail_Freight_(₹/tonne)': float(f"{rail_freight_per_tonne:.2f}"), 
                    'Port_Handling_(₹/tonne)': float(f"{port_handling_per_tonne:.2f}"), 
                    'Total_Trip_Cost (₹)': float(f"{total_trip_cost:.2f}"),
                })

    df_out = pd.DataFrame(transport_logs)
    
    # --- WRITING TO EXCEL PRINT ---
    print(f"STATUS: Writing final train log data to Excel file: {output_path}")
    
    # Helper function to convert column index to Excel column name (A, B, C...)
    def colnum_to_colname(n):
        name = ''
        while n >= 0:
            name = chr(n % 26 + 65) + name
            n = n // 26 - 1
        return name

    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df_out.to_excel(writer, index=False, sheet_name='Train Logs')
            workbook = writer.book
            worksheet = writer.sheets['Train Logs']
            
            # Formating
            two_dec = workbook.add_format({'num_format':'0.00'})
            text_format = workbook.add_format({'num_format':'@'}) 
            inr_format = workbook.add_format({'num_format': '₹#,##0.00'})
            
            # Formating Rake_ID column as Text to prevent scientific notation conversion
            rake_id_col_index = df_out.columns.get_loc('Rake_ID') 
            rake_id_col_letter = colnum_to_colname(rake_id_col_index)
            worksheet.set_column(f'{rake_id_col_letter}:{rake_id_col_letter}', 18, text_format) 

            cost_cols = ['Rail_Freight_(₹/tonne)', 'Port_Handling_(₹/tonne)', 'Total_Trip_Cost (₹)']
            for col_name in cost_cols:
                col_index = df_out.columns.get_loc(col_name)
                col_letter = colnum_to_colname(col_index)
                worksheet.set_column(f'{col_letter}:{col_letter}', 22, inr_format)
                
            numeric_cols_start_index = df_out.columns.get_loc('Quantity (tonnes)')
            numeric_cols_end_index = df_out.columns.get_loc('Total_Time_h')
            worksheet.set_column(colnum_to_colname(numeric_cols_start_index) + ':' + colnum_to_colname(numeric_cols_end_index), 18, two_dec) 
            
        print(f"SUCCESS: Train log dataset successfully saved to {output_path}") 
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)

# ---------------- MAIN ----------------
# if __name__ == "__main__":                                              ***Commented to prevent accidental run***
#     generate_train_log(DEFAULT_PLANT_LOG, DEFAULT_OUTPUT_LOG)
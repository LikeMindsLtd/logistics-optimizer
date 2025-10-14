import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

"""
Train Log Generator
------------------
Generates detailed inbound (Coal, Limestone) and outbound (Steel) train logs
based on daily plant logs (plant_log.xlsx). Each material quantity is split
into discrete train trips with randomized capacities, times, and costs.
Outputs a stylized Excel file (train_log.xlsx) with all metrics.
"""

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets") 
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

# ---------------- TRAIN CAPACITY & SPEED ----------------
TRAIN_CAPACITY = {'Coal': 10000, 'Limestone': 8000, 'Steel': 5000}
DEFAULT_SPEED_KMPH = 40

# ---------------- LOADING/UNLOADING RATES ----------------
LOADING_RATE = {'Coal': 0.0006, 'Limestone': 0.0005, 'Steel': 0.0010}
UNLOADING_RATE = {'Coal': 0.0005, 'Limestone': 0.0004, 'Steel': 0.0008}

# ---------------- COST CONFIG ----------------
BASE_RAIL_FREIGHT_RATE = {'Coal': 4.5, 'Limestone': 3.5, 'Steel': 6.0} 
BASE_PORT_HANDLING_COST = {'Coal': 200, 'Limestone': 150, 'Steel': 300}

# ---------------- RAKE MANAGEMENT ----------------
NUM_RAKES = 50
RAKE_IDS = random.sample([str(i) for i in range(100000, 999999)], NUM_RAKES)
ALL_LOCATIONS = list(set(
    list(PLANT_PORTS.keys()) +
    [loc for p in PLANT_PORTS.values() for s in p['coal_sources'] + p['limestone_sources'] + p['export_ports'] for loc in [s[0]]]
))
RAKE_TRACKER = {
    rake_id: {'location': random.choice(ALL_LOCATIONS), 'available_time': datetime.min, 'status': 'Available'}
    for rake_id in RAKE_IDS
}

# ---------------- HELPER FUNCTIONS ----------------
def split_into_trains(quantity, max_capacity):
    loads, remaining = [], quantity
    while remaining > 0:
        load = min(random.uniform(0.8, 1.0) * max_capacity, remaining)
        loads.append(round(load, 2))
        remaining -= load
    return loads

def choose_weighted_source(sources):
    weights = [0.7 if 'Mine' in s[0] or 'Plant' in s[0] else 0.3 for s in sources]
    return random.choices(sources, weights=weights, k=1)[0]

def calculate_times(qty, dist, material):
    base_time_h = dist / DEFAULT_SPEED_KMPH
    delay_h = random.uniform(1, 24)
    loading_h = qty * LOADING_RATE[material] * random.uniform(0.9, 1.1)
    unloading_h = qty * UNLOADING_RATE[material] * random.uniform(0.9, 1.1)
    total_time_h = base_time_h + delay_h + loading_h + unloading_h
    return base_time_h, delay_h, loading_h, unloading_h, total_time_h

def calculate_costs(qty, dist, material, is_port_source):
    rail_freight_per_tonne = BASE_RAIL_FREIGHT_RATE[material] * dist * random.uniform(0.95, 1.05)
    port_handling_per_tonne = BASE_PORT_HANDLING_COST[material] * random.uniform(0.9, 1.1) if is_port_source else 0.0
    total_trip_cost = (rail_freight_per_tonne + port_handling_per_tonne) * qty
    return rail_freight_per_tonne, port_handling_per_tonne, total_trip_cost

def random_time_in_day(date):
    return datetime.combine(date, datetime.min.time()) + timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

def assign_rake(source, departure_time):
    available_local = [r for r, d in RAKE_TRACKER.items() if d['location'] == source and d['available_time'] <= departure_time]
    rake_av_index = round((len(available_local) / NUM_RAKES) * 10, 2)

    if available_local:
        rake_id = random.choice(available_local)
    else:
        available_anywhere = [r for r, d in RAKE_TRACKER.items() if d['available_time'] <= departure_time]
        if available_anywhere:
            rake_id = random.choice(available_anywhere)
        else:
            rake_id = min(RAKE_TRACKER, key=lambda r: RAKE_TRACKER[r]['available_time'])
            departure_time = RAKE_TRACKER[rake_id]['available_time']

    RAKE_TRACKER[rake_id]['status'] = 'In Transit'
    RAKE_TRACKER[rake_id]['location'] = source
    return rake_id, departure_time, rake_av_index

def colnum_to_colname(n):
    name = ''
    while n >= 0:
        name = chr(n % 26 + 65) + name
        n = n // 26 - 1
    return name

def try_set_column_by_name(df, worksheet, col_name, fmt, width=18):
    try:
        idx = df.columns.get_loc(col_name)
        worksheet.set_column(f'{colnum_to_colname(idx)}:{colnum_to_colname(idx)}', width, fmt)
    except KeyError:
        pass

# ---------------- MAIN GENERATOR ----------------
def generate_train_log(plant_log_path, output_path):
    print("STATUS: Simulating Indian Railways Freight Movements.")
    print(f"STATUS: Fetching daily material demand from plant log: {plant_log_path}")

    if not os.path.exists(plant_log_path):
        print(f"ERROR: Plant log not found at {plant_log_path}. Run plant generator first.")
        sys.exit(1)

    df = pd.read_excel(plant_log_path).sort_values(by='date').reset_index(drop=True)
    transport_logs = []
    trip_counter = {p: 1 for p in PLANT_PORTS}

    print("STATUS: Generating individual train trips, calculating costs, and managing rake pool...")

    for _, row in df.iterrows():
        plant, date = row['plant_name'], pd.to_datetime(row['date']).date()
        for material in ['Coal', 'Limestone', 'Steel']:
            qty_col = {'Coal': 'coal_arrived_tonnes',
                       'Limestone': 'limestone_arrived_tonnes',
                       'Steel': 'steel_exported_tonnes'}[material]
            qty = row.get(qty_col, 0)
            if qty <= 0:
                continue

            sources = (PLANT_PORTS[plant]['coal_sources'] if material == 'Coal'
                       else PLANT_PORTS[plant]['limestone_sources'] if material == 'Limestone'
                       else PLANT_PORTS[plant]['export_ports'])
            dest = plant if material in ['Coal', 'Limestone'] else None
            flow = 'Inbound' if material in ['Coal', 'Limestone'] else 'Outbound'

            for q in split_into_trains(qty, TRAIN_CAPACITY[material]):
                trip_id = f"{plant[:3].upper()}_{trip_counter[plant]:04d}"
                trip_counter[plant] += 1

                if flow == 'Inbound':
                    src, dist = choose_weighted_source(sources)
                    dest_loc, is_port = dest, 'Port' in src or 'Mine' in src
                    dep_time = random_time_in_day(date) - timedelta(days=random.randint(2, 5))
                else:
                    src, (dest_loc, dist) = plant, random.choice(sources)
                    dep_time, is_port = random_time_in_day(date), False

                rake_id, dep_time, rake_idx = assign_rake(src, dep_time)
                base, delay, load, unload, total = calculate_times(q, dist, material)
                rail, port, cost = calculate_costs(q, dist, material, is_port)
                arr_time = dep_time + timedelta(hours=total)

                RAKE_TRACKER[rake_id].update({'location': dest_loc, 'available_time': arr_time, 'status': 'Available'})

                transport_logs.append({
                    'trip_id': trip_id, 
                    'rake_id': rake_id,
                    'material_flow': flow, 
                    'material': material,
                    'source': src, 
                    'destination': dest_loc,
                    'quantity_tonnes': q, 
                    'distance_km': dist,
                    'rake_availability_index': rake_idx,
                    'base_time_h': base, 
                    'loading_time_h': load,
                    'unloading_time_h': unload, 
                    'delay_h': delay,
                    'total_time_h': total, 
                    'departure_time': dep_time,
                    'arrival_time': arr_time,
                    'rail_freight_inr_tonne': rail, 
                    'port_handling_inr_tonne': port,
                    'total_trip_cost_inr': cost
                })

    df_out = pd.DataFrame(transport_logs)

    print(f"STATUS: Writing final train log data to Excel file: {output_path}")

    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df_out.to_excel(writer, index=False, sheet_name='Train Logs')
            wb, ws = writer.book, writer.sheets['Train Logs']

            fmt_dec = wb.add_format({'num_format': '0.00'})
            fmt_txt = wb.add_format({'num_format': '@'})
            fmt_inr = wb.add_format({'num_format': '#,##0.00'})

            try_set_column_by_name(df_out, ws, 'rake_id', fmt_txt, 18)
            for c in ['rail_freight_inr_tonne', 'port_handling_inr_tonne', 'total_trip_cost_inr']:
                try_set_column_by_name(df_out, ws, c, fmt_inr, 22)

            try:
                s = df_out.columns.get_loc('quantity_tonnes')
                e = df_out.columns.get_loc('total_time_h')
                ws.set_column(f'{colnum_to_colname(s)}:{colnum_to_colname(e)}', 18, fmt_dec)
            except KeyError:
                pass

        print(f"SUCCESS: Train log successfully saved → {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)


# if __name__ == "__main__":                                        #***Commented to prevent accidental run***
#     generate_train_log(DEFAULT_PLANT_LOG, DEFAULT_OUTPUT_LOG)

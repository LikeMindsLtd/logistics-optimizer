import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

'''
Generates historical vessel delay logs based on daily port operations and vessel contracts.
Uses original port log columns directly without renaming.
'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

DEFAULT_PORT_LOG = os.path.join(OUTPUT_DIR, "port_log.xlsx")
DEFAULT_VESSEL_COST_LOG = os.path.join(OUTPUT_DIR, "vessel_cost.xlsx")
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "vessel_delay_history.xlsx")

# ---------------- SIMULATION PARAMETERS ----------------
NUM_HISTORICAL_DAYS = 730
VESSEL_ARRIVAL_PROBABILITY = 0.4
MAX_CRANES = 5

# ---------------- HELPER FUNCTIONS ----------------
def get_crane_availability():
    return random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.3, 0.3, 0.2], k=1)[0]

def get_past_delay_avg():
    return round(random.uniform(10, 40), 2)

def calculate_delay_and_times(eta, utilization, weather, cranes, past_avg):
    congestion_delay = (utilization / 100) * random.uniform(5, 30)
    weather_delay = weather * random.uniform(2, 12)
    crane_penalty = (MAX_CRANES - cranes) * random.uniform(5, 15)
    past_factor = past_avg * random.uniform(0.1, 0.5)

    delay_hours = max(1.0, congestion_delay + weather_delay + crane_penalty + past_factor)
    delay_hours = round(min(delay_hours, 240.0), 2)
    actual_berth_time = eta + timedelta(hours=delay_hours)
    return delay_hours, actual_berth_time

# ---------------- MAIN GENERATOR ----------------
def generate_vessel_delay_history(port_log_path, vessel_cost_path, output_path):
    print("STATUS: Generating vessel delay history...")

    try:
        df_port = pd.read_excel(port_log_path)
        df_vessel = pd.read_excel(vessel_cost_path)
    except FileNotFoundError as e:
        print(f"ERROR: Required file missing: {e}")
        sys.exit(1)

    df_port['date'] = pd.to_datetime(df_port['date']).dt.date
    ports_list = df_port['port_name'].unique()

    historical_logs = []

    start_date = df_port['date'].min() - timedelta(days=365)
    end_date = df_port['date'].max()
    all_dates = pd.date_range(start=start_date, end=end_date).date

    for date in all_dates:
        if random.random() < VESSEL_ARRIVAL_PROBABILITY:
            arrival_port = random.choice(ports_list)
            eta_datetime = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=random.randint(0, 23), minutes=random.randint(0, 59)
            )

            # Select a vessel randomly for this port
            valid_vessels = df_vessel[
                (df_vessel['load_port'].str.contains(arrival_port)) |
                (df_vessel['discharge_port'].str.contains(arrival_port))
            ]
            if valid_vessels.empty:
                continue

            vessel_info = valid_vessels.sample(1).iloc[0]

            vessel_id = vessel_info['vessel_id']
            parcel_size = vessel_info['contract_quantity_tonnes']
            laydays_limit = vessel_info['laydays_allowed_hours']
            demurrage_rate = vessel_info['demurrage_rate_inr_hr']

            # Port metrics
            port_row = df_port[(df_port['date'] == date) & (df_port['port_name'] == arrival_port)]
            if not port_row.empty:
                utilization = port_row.iloc[0]['steel_eod_storage_tonnes']
                weather_score = port_row.iloc[0]['weather_delay_index']
            else:
                utilization = random.uniform(50, 80)
                weather_score = random.randint(0, 2)

            queue_length = sum(
                1 for log in historical_logs if log['eta_datetime'].date() == date
            ) + random.randint(0, 3)

            cranes = get_crane_availability()
            past_avg = get_past_delay_avg()
            delay_hours, actual_berth_time = calculate_delay_and_times(
                eta=eta_datetime, utilization=utilization,
                weather=weather_score, cranes=cranes, past_avg=past_avg
            )
            demurrage_cost = round(delay_hours * demurrage_rate, 2)

            historical_logs.append({
                'vessel_name': vessel_id,
                'port_name': arrival_port,
                'eta_datetime': eta_datetime,
                'actual_berth_time': actual_berth_time,
                'parcel_size_tonnes': parcel_size,
                'laydays_start': eta_datetime - timedelta(days=random.randint(1, 3)),
                'laydays_end': eta_datetime + timedelta(days=random.randint(7, 10)),
                'queue_length': queue_length,
                'weather_score': weather_score,
                'crane_availability': cranes,
                'past_delay_avg_hours': past_avg,
                'laydays_limit_hours': laydays_limit,
                'delay_hours': delay_hours,
                'demurrage_cost_inr': demurrage_cost
            })

    df = pd.DataFrame(historical_logs).sort_values(by=['eta_datetime', 'port_name'])
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Vessel Delay History')
        print(f"SUCCESS: Vessel delay history saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Could not save Excel file: {e}")
        sys.exit(1)


# if __name__ == "__main__":                                                                        #***Commented to prevent accidental run***
#     generate_vessel_delay_history(DEFAULT_PORT_LOG, DEFAULT_VESSEL_COST_LOG, DEFAULT_OUTPUT_LOG)

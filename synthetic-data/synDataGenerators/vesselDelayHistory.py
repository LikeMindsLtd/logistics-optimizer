import pandas as pd
import random
import os
from datetime import datetime, timedelta
import sys

'''This generator creates a historical record of common causes and durations of vessel
    delays at the port. It simulates a variety of delay events such as bad weather,
    equipment breakdown, documentation issues, or berth congestion. Each simulated
    delay entry includes the cause, duration, and the affected vessel type, providing
    a dataset necessary for analyzing and predicting future supply chain disruptions.'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Dependencies (MUST run port_log and vessel_cost first)
DEFAULT_PORT_LOG = os.path.join(OUTPUT_DIR, "port_log.xlsx")
DEFAULT_VESSEL_COST_LOG = os.path.join(OUTPUT_DIR, "vessel_cost.xlsx")

DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "vessel_delay_history.xlsx")

# ---------------- SIMULATION PARAMETERS ----------------
NUM_HISTORICAL_DAYS = 730 
VESSEL_ARRIVAL_PROBABILITY = 0.4 
MAX_CRANES = 5

# ---------------- HELPER FUNCTIONS ----------------

def get_crane_availability():
    #Simulates the number of available cranes (out of MAX_CRANES)
    return random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.15, 0.3, 0.3, 0.2], k=1)[0]

def get_past_delay_avg():
    #Simulates a base average historical delay for a route/port pair (in hours).
    return round(random.uniform(10, 40), 2)

def calculate_delay_and_times(eta, utilization, weather, cranes, past_avg):
    """Calculates the Actual Berth Time and Delay Hours based on conditions.
    Delay = Congestion + Weather Impact + Crane Penalty + Past Risk"""
    
    # 1. Congestion/Utilization Factor (0 to 30 hours)
    congestion_delay = (utilization / 100) * random.uniform(5, 30)
    
    # 2. Weather Impact (0 to 60 hours)
    weather_delay = weather * random.uniform(2, 12)
    
    # 3. Crane Efficiency Penalty (Less cranes = higher penalty)
    crane_penalty = (MAX_CRANES - cranes) * random.uniform(5, 15) 
    
    # 4. Past Performance Factor
    past_factor = past_avg * random.uniform(0.1, 0.5)

    # Total Delay Hours (The core prediction target)
    delay_hours = max(1.0, congestion_delay + weather_delay + crane_penalty + past_factor)
    delay_hours = round(min(delay_hours, 240.0), 2) # Clamp at 10 days max
    
    # Calculate Actual Berth Time
    actual_berth_time = eta + timedelta(hours=delay_hours)
    
    return delay_hours, actual_berth_time

# ---------------- MAIN GENERATOR ----------------
def generate_vessel_delay_history(port_log_path, vessel_cost_path, output_path):
    print("--- Historical Vessel Delay Log Generator Initialized ---")
    print("STATUS: Creating detailed AI training data with operational features.")
    
    # --- LOADing DEPENDENCIES ---
    try:
        df_port = pd.read_excel(port_log_path)
        df_port_metrics = df_port.rename(columns={
            'Steel_Storage_Utilization(%)': 'Port_Stock_Utilization(%)',
            'Weather_Delay_Index': 'Weather_Score'
        })[['Date', 'Port', 'Port_Stock_Utilization(%)', 'Weather_Score']]
        df_port_metrics['Date'] = pd.to_datetime(df_port_metrics['Date']).dt.date
        
        df_vessel_costs = pd.read_excel(vessel_cost_path)
        
        # Determining simulation period
        start_date = df_port_metrics['Date'].min() - timedelta(days=365)
        end_date = df_port_metrics['Date'].max()
        all_dates = pd.date_range(start=start_date, end=end_date).date
        
    except FileNotFoundError as e:
        print(f"ERROR: Dependent file not found: {e}. Ensure all previous logs are generated.")
        sys.exit(1)
    
    historical_logs = []
    ports_list = df_port_metrics['Port'].unique()
    
    print(f"STATUS: Simulating {len(all_dates)} days of vessel arrivals...")
    
    for date in all_dates:
        
        if random.random() < VESSEL_ARRIVAL_PROBABILITY:
            
            arrival_port = random.choice(ports_list)
            eta_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # Get vessel contract info
            valid_vessels = df_vessel_costs[
                (df_vessel_costs['Discharge_Port'].str.contains(arrival_port)) | 
                (df_vessel_costs['Load_Port'].str.contains(arrival_port))
            ]
            
            if valid_vessels.empty:
                   continue

            vessel_info = valid_vessels.sample(1).iloc[0]
            vessel_id = vessel_info['Vessel_ID']
            demurrage_rate_inr_hr = vessel_info['Demurrage_Rate_(₹/hr)']
            parcel_size = vessel_info['Contract_Quantity(tonnes)']
            laydays_limit = vessel_info['Laydays_Allowed(hours)']
            
            # Laydays Start/End Window (Simulated Contract Window)
            laydays_start = eta_datetime - timedelta(days=random.randint(1, 3))
            laydays_end = laydays_start + timedelta(days=random.randint(7, 10))

            # --- FEATURE LOOKUP (Current Day's Conditions) ---
            port_row = df_port_metrics[(df_port_metrics['Date'] == date) & (df_port_metrics['Port'] == arrival_port)]
            if not port_row.empty:
                utilization = port_row.iloc[0]['Port_Stock_Utilization(%)']
                weather_score = port_row.iloc[0]['Weather_Score']
            else:
                utilization = random.uniform(50, 80)
                weather_score = random.randint(0, 2)

            # --- CRITICAL FIX for KeyError 'Date' ---
            current_date_str = date.strftime('%Y-%m-%d')
            
            # Calculate queue length by checking the date part of the existing 'ETA_Datetime' logs
            queue_length = sum(
                1 for log in historical_logs 
                if log['ETA_Datetime'].strftime('%Y-%m-%d') == current_date_str
            ) + random.randint(0, 3) # Add a small random element for daily fluctuation
            
            crane_availability = get_crane_availability()
            past_delay_avg = get_past_delay_avg()
            
            # --- CALCULATE TARGET VARIABLES ---
            delay_hours, actual_berth_time = calculate_delay_and_times(
                eta=eta_datetime, 
                utilization=utilization, 
                weather=weather_score, 
                cranes=crane_availability,
                past_avg=past_delay_avg
            )
            
            # --- CALCULATE COST IMPACT ---
            # Demurrage Cost (₹) = Delay Hours * Demurrage Rate (₹/hr)
            demurrage_cost_inr = round(delay_hours * demurrage_rate_inr_hr, 2)
            
            # --- LOG THE DATA POINT ---
            historical_logs.append({
                'Vessel_Name': vessel_id,
                'Port_Name': arrival_port,
                'ETA_Datetime': eta_datetime,
                'Actual_Berth_Time': actual_berth_time,
                'Parcel_Size(tonnes)': parcel_size,
                'Laydays_Start': laydays_start,
                'Laydays_End': laydays_end,
                'Queue_Length': queue_length,
                'Weather_Score': weather_score,
                'Crane_Availability': crane_availability,
                'Past_Delay_Avg(hours)': past_delay_avg,
                'Laydays_Limit(hours)': laydays_limit,
                'Delay_Hours': delay_hours,
                'Demurrage_Cost(₹)': demurrage_cost_inr,
            })
            
    df = pd.DataFrame(historical_logs).sort_values(by=['ETA_Datetime', 'Port_Name'])
    
    print(f"STATUS: Writing final historical log data to Excel file: {output_path}")
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Vessel Delay History')
            
            # Format numeric columns for consistency and INR for cost
            workbook = writer.book
            worksheet = writer.sheets['Vessel Delay History']
            two_dec = workbook.add_format({'num_format':'0.00'})
            inr_format = workbook.add_format({'num_format': '₹#,##0.00'})
            
            # Apply 2-decimal format to all numeric/hour columns
            worksheet.set_column('F:L', 20, two_dec) 
            worksheet.set_column('N:O', 20, two_dec) 
            
            # Apply INR format to the cost column
            cost_col_index = df.columns.get_loc('Demurrage_Cost(₹)')
            colnum_to_colname = lambda n: ''.join(chr(n % 26 + 65) for n in iter(lambda: n // 26 - 1, -1))
            cost_col_letter = colnum_to_colname(cost_col_index)
            worksheet.set_column(f'{cost_col_letter}:{cost_col_letter}', 28, inr_format)
            
        print(f"SUCCESS: Vessel delay history successfully saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)
        
# if __name__ == "__main__":                                                                            ***Commented to prevent accidental run***
#     generate_vessel_delay_history(DEFAULT_PORT_LOG, DEFAULT_VESSEL_COST_LOG, DEFAULT_OUTPUT_LOG)
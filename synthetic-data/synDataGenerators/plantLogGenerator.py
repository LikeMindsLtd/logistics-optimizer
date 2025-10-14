import pandas as pd
from datetime import datetime, timedelta
import random
import os
import sys

'''This generator will simulate the working of all 5 plants, and generates logs based on the
   provided coal, limestone arrived across the year and total steel exported annually.
   Then the generator randomly simulates arrival of materials, export of steel, production
   but based on the past output of these plants already provided. We take the propotion of
   past exports and reflect in the generator to reflect the same ratio. The coal and 
   limestone is randomly arrived at the plants when the stock goes beyond a level. The steel
   is expoted on a daily basis. This generator also generates key indicators like stock utilization,
   cumulative capacity utilization of a plant'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "plant_log.xlsx")

# ---------------------- Plant Information ----------------------
PLANTS = [
    {'id': 'P001', 'name': 'Bhilai Steel Plant', 'capacity_mtp': 4.0, 'past_export': 3.4},
    {'id': 'P002', 'name': 'Durgapur Steel Plant', 'capacity_mtp': 2.0, 'past_export': 1.6},
    {'id': 'P003', 'name': 'Rourkela Steel Plant', 'capacity_mtp': 2.8, 'past_export': 2.7},
    {'id': 'P004', 'name': 'Bokaro Steel Plant', 'capacity_mtp': 3.0, 'past_export': 2.9},
    {'id': 'P005', 'name': 'IISCO Steel Plant', 'capacity_mtp': 1.8, 'past_export': 1.6}
]

# ---------------------- Helper Functions ----------------------
def proportionate_exports(plants, total_export):
    total_past = sum([p['past_export'] for p in plants])
    for p in plants:
        p['yearly_export'] = round(total_export * p['past_export'] / total_past, 2)
    return plants

def generate_daily_steel_export(yearly_export, num_days):
    daily_exports = []
    remaining = yearly_export
    for i in range(num_days):
        avg_daily = remaining / (num_days - i)
        daily = round(random.uniform(0.9*avg_daily, 1.1*avg_daily), 2)
        daily = min(daily, remaining)
        daily_exports.append(daily)
        remaining -= daily
    if remaining != 0:
        daily_exports[-1] = round(daily_exports[-1] + remaining, 2)
    return daily_exports

def generate_train_arrivals(total_required, num_days, min_per_train=5000, max_per_train=10000):
    arrivals = [0]*num_days
    remaining = total_required

    while remaining > 0:
        day = random.randint(0, num_days-1)
        train_qty = round(random.uniform(min_per_train, max_per_train),2)
        train_qty = min(train_qty, remaining)
        arrivals[day] += train_qty
        remaining -= train_qty

    arrivals = [round(a,2) for a in arrivals]
    
    # Ensuring the sum is exactly the total required (small float adjustments)
    current_sum = sum(arrivals)
    diff = total_required - current_sum
    if abs(diff) > 0.01:
        arrivals[-1] = round(arrivals[-1] + diff, 2)
        
    return arrivals

# ---------------------- Main Generator ----------------------
def generate_plant_logs():
    
    print("STATUS: Gathering overall material quantities for simulation setup.")
    
    try:
        total_coal = float(input("Enter total coal for the year (million tonnes): ").strip() or 10.0) * 1_000_000
        total_limestone = float(input("Enter total limestone for the year (million tonnes): ").strip() or 4.0) * 1_000_000
        total_steel = float(input("Enter total steel exported across all plants (million tonnes): ").strip() or 6.0) * 1_000_000
    except ValueError:
        print("ALERT: Invalid input detected. Using default values (10M Coal, 4M Limestone, 6M Steel).")
        total_coal = 10_000_000
        total_limestone = 4_000_000
        total_steel = 6_000_000

    start_date = datetime(2023,1,1)
    end_date = datetime(2024,1,1)
    num_days = (end_date - start_date).days

    print("STATUS: Calculating yearly export share and material requirements per plant.")
    
    plants = proportionate_exports(PLANTS, total_steel)
    all_logs = []

    # Spliting coal/limestone proportionally by yearly steel export
    total_export_for_split = sum([p['yearly_export'] for p in plants])
    for p in plants:
        share = p['yearly_export']/total_export_for_split
        p['yearly_coal'] = round(total_coal * share,2)
        p['yearly_limestone'] = round(total_limestone * share,2)

    # Initializing max stock and random initial stock
    min_stock_ratio = 0.2
    for p in plants:
        avg_daily_steel = p['yearly_export'] / num_days
        p['max_coal_stock'] = avg_daily_steel * 10
        p['max_limestone_stock'] = avg_daily_steel * 0.43 * 10 
        p['coal_stock'] = round(random.uniform(0.3,0.7)*p['max_coal_stock'],2)
        p['limestone_stock'] = round(random.uniform(0.3,0.7)*p['max_limestone_stock'],2)

    # Generating daily steel export and train arrivals
    print("STATUS: Distributing yearly requirements into 365 daily figures.")
    for p in plants:
        p['daily_steel'] = generate_daily_steel_export(p['yearly_export'], num_days)
        p['coal_arrivals'] = generate_train_arrivals(p['yearly_coal'], num_days)
        p['limestone_arrivals'] = generate_train_arrivals(p['yearly_limestone'], num_days)

    print("STATUS: Executing daily simulation loop and calculating stock levels.")
    
    # Generating daily logs
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        for p in plants:
            steel_export = p['daily_steel'][day]
            if 'cumulative_export' not in p:
                p['cumulative_export'] = 0
            
            p['cumulative_export'] += steel_export
            yearly_max_capacity = p['capacity_mtp'] * 1_000_000
            cumulative_utilization = (p['cumulative_export'] / yearly_max_capacity) * 100

            # Daily consumption calculation
            coal_required = round(steel_export * 1.0, 2)
            limestone_required = round(steel_export * 0.43, 2)
            
            # Actual consumed materials based on random variance
            consumed_coal = round(coal_required * random.uniform(0.95,1.05), 2)
            consumed_limestone = round(limestone_required * random.uniform(0.95,1.05), 2)


            # Updating stocks
            coal_stock_bod = p['coal_stock']
            limestone_stock_bod = p['limestone_stock']
            min_stock_target = p['max_coal_stock'] * random.uniform(min_stock_ratio, 0.3) 
            
            p['coal_stock'] = min(p['coal_stock'] + p['coal_arrivals'][day], p['max_coal_stock'])
            p['coal_stock'] = max(p['coal_stock'] - consumed_coal, min_stock_target)

            p['limestone_stock'] = min(p['limestone_stock'] + p['limestone_arrivals'][day], p['max_limestone_stock'])
            p['limestone_stock'] = max(p['limestone_stock'] - consumed_limestone, p['max_limestone_stock']*min_stock_ratio)

            stock_utilization = ((p['coal_stock'] + p['limestone_stock']) / 
                                 (p['max_coal_stock'] + p['max_limestone_stock']))*100

            all_logs.append({
                'date': current_date.strftime('%Y-%m-%d'), 
                'plant_id': p['id'],
                'plant_name': p['name'],
                'max_operating_capacity_mtpa': round(p['capacity_mtp'], 2),
                'cumulative_capacity_utilization_percent': round(cumulative_utilization, 2),
                'stock_utilization_percent': round(stock_utilization, 2),
                'min_stock_target_tonnes': round(min_stock_target, 2),
                'coal_bod_stock_tonnes': round(coal_stock_bod, 2),
                'limestone_bod_stock_tonnes': round(limestone_stock_bod, 2),
                'coal_required_tonnes': round(coal_required, 2),
                'limestone_required_tonnes': round(limestone_required, 2),
                'consumed_coal_tonnes': round(consumed_coal, 2),
                'consumed_limestone_tonnes': round(consumed_limestone, 2),
                'coal_arrived_tonnes': round(p['coal_arrivals'][day], 2),
                'limestone_arrived_tonnes': round(p['limestone_arrivals'][day], 2),
                'coal_eod_stock_tonnes': round(p['coal_stock'], 2),
                'limestone_eod_stock_tonnes': round(p['limestone_stock'], 2),
                'steel_exported_tonnes': round(steel_export, 2)
            })

    export_path = DEFAULT_OUTPUT_LOG
    print(f"STATUS: Writing final plant log data to Excel file: {export_path}")

    df = pd.DataFrame(all_logs)
    try:
        with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Plant Logs')
            workbook = writer.book
            worksheet = writer.sheets['Plant Logs']
            two_dec = workbook.add_format({'num_format':'0.00'})
            worksheet.set_column('C:Z', 18, two_dec)        # Applying formatting to all data columns
        
        print(f"SUCCESS: Synthetic plant logs successfully saved to {export_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel file. Details: {e}")
        # Exiting if file write fails
        sys.exit(1)

# if __name__ == "__main__":            #***Commented to prevent accidental run***
#     generate_plant_logs()
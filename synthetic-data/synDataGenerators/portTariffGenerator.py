import pandas as pd
import random
import os
import sys

'''This generator creates a reference dataset for all port-related tariffs and charges
    for different vessel sizes and types of cargo. It simulates common port fees
    including Pilotage, Towage, Berthing, and Wharfage costs, often categorized by
    Vessel Tonnage (DWT) or Gross Tonnage (GT). This data is essential for calculating
    the total port-side charges incurred during a vessel's stay.'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "port_tariffs.xlsx")

# ---------------- PORT & MATERIAL INFO ----------------
PORTS = ['Haldia Port', 'Paradip Port', 'Visakhapatnam Port', 'Kolkata Port']
MATERIALS = ['Coal', 'Limestone', 'Steel']

# ---------------- COST RANGES (IN RUPEES) ----------------
# Handling Cost (₹/tonne): Cost to load/unload at the port (labor, equipment, etc.)
HANDLING_RANGE = {'Coal': (200.00, 350.00), 'Limestone': (150.00, 300.00), 'Steel': (250.00, 400.00)} 
# Storage Cost (₹/tonne/day): Cost for inventory sitting in the port yard
STORAGE_RANGE = {'Coal': (8.00, 12.00), 'Limestone': (5.00, 8.00), 'Steel': (10.00, 15.00)} 
# Max Throughput (T/Day): Soft capacity limit for daily cargo processing
THROUGHPUT_RANGE = {'Coal': (20000, 30000), 'Limestone': (15000, 25000), 'Steel': (10000, 20000)}

# ---------------- MAIN GENERATOR ----------------
def generate_port_tariffs_data(output_path):
    print("STATUS: Generating static port handling, storage, and throughput data in INR.")
    
    tariff_data = []
    
    for port in PORTS:
        port_base_factor = random.uniform(0.9, 1.1) 
        
        for material in MATERIALS:
            # 1. HANDLING COST (₹/tonne)
            h_low, h_high = HANDLING_RANGE[material]
            handling_cost = round(random.uniform(h_low, h_high) * port_base_factor, 2)
            
            # 2. STORAGE COST (₹/tonne/day)
            s_low, s_high = STORAGE_RANGE[material]
            storage_cost = round(random.uniform(s_low, s_high) * port_base_factor, 2)
            
            # 3. MAX THROUGHPUT (T/Day)
            t_low, t_high = THROUGHPUT_RANGE[material]
            max_throughput = round(random.uniform(t_low, t_high), -2)
            
            tariff_data.append({
                'Port_Name': port,
                'Material': material,
                'Handling_Cost_(₹/tonne)': handling_cost,
                'Storage_Cost_(₹/tonne/day)': storage_cost,
                'Max_Throughput_T/Day': max_throughput,
            })

    df = pd.DataFrame(tariff_data)
    
    print(f"STATUS: Writing static data to Excel file: {output_path}")
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Port Tariffs')
            workbook = writer.book
            worksheet = writer.sheets['Port Tariffs']
            two_dec = workbook.add_format({'num_format':'0.00'})
            worksheet.set_column('C:E', 25, two_dec)        # Apply formatting to all numeric columns
            
        print(f"SUCCESS: Port tariffs data successfully saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)
        
# if __name__ == "__main__":                             ***Commented to prevent accidental run***
#     generate_port_tariffs_data(DEFAULT_OUTPUT_LOG)
import pandas as pd
import random
import os
import sys

'''This generator creates a master dataset detailing the operational and fixed costs
    associated with various vessel types used for steel transport. It generates typical
    cost components such as daily charter rates, fuel consumption rates, insurance, and
    crew costs. The vessel cost data is designed to be used in conjunction with the
    portLogGenerator.py data to calculate the total cost and efficiency for
    different shipping routes and vessels.'''

# ---------------- CONFIG ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "..", "synDatasets")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
DEFAULT_OUTPUT_LOG = os.path.join(OUTPUT_DIR, "vessel_cost.xlsx")

# Using a realistic conversion factor for USD to INR
USD_TO_INR = 83.0

# ---------------- GEOPOLITICAL PORT INFO ----------------
INDIAN_PORTS = ['Haldia Port', 'Paradip Port', 'Visakhapatnam Port']

# INBOUND MATERIAL SOURCES (Load Ports)
COAL_SOURCE_PORTS = ['Hay Point (AUS)', 'Gladstone (AUS)', 'Newcastle (AUS)', 'Durban (SAF)', 'Baltimore (USA)']
LIMESTONE_SOURCE_PORTS = ['Port of Salalah (OMN)', 'Jebel Ali (UAE)', 'Vung Tau (VNM)']

# OUTBOUND MATERIAL DESTINATIONS (Discharge Ports)
STEEL_DESTINATION_PORTS = ['Jebel Ali (UAE)', 'Singapore', 'Hamburg (GER)', 'Tokyo (JPN)']

MATERIALS = ['Coal', 'Limestone', 'Steel']
NUM_VESSELS = 25

# ---------------- COST RANGES (IN USD - will be converted to INR) ----------------
# Ocean Freight ($/tonne)
FREIGHT_RANGE_USD = {'Coal': (20.00, 28.00), 'Limestone': (15.00, 22.00), 'Steel': (35.00, 50.00)} 
# Demurrage Rate ($/hr)
DEMURRAGE_RANGE_USD = (800.00, 1500.00)
# Contract Quantity (tonnes)
QTY_RANGE = {'Coal': (30000, 50000), 'Limestone': (25000, 40000), 'Steel': (15000, 25000)}
# Laydays Allowed (hours)
LAYDAYS = [72, 96, 120] 

# ---------------- MAIN GENERATOR ----------------
def generate_vessel_cost_data(output_path):
    print("STATUS: Generating static vessel cost and contract constraint data in INR, using geopolitical flow logic.")
    
    vessel_data = []
    
    for i in range(1, NUM_VESSELS + 1):
        vessel_id = f"V{i:03d}"
        
        num_contracts = random.randint(3, 5) 
        
        for _ in range(num_contracts):
            material = random.choice(MATERIALS)
            
            # --- APPLY GEOPOLITICAL FLOW LOGIC ---
            if material == 'Steel':
                # Steel is exported from India
                load_port = random.choice(INDIAN_PORTS)
                discharge_port = random.choice(STEEL_DESTINATION_PORTS)
            elif material == 'Coal':
                # Coal is imported to India
                load_port = random.choice(COAL_SOURCE_PORTS)
                discharge_port = random.choice(INDIAN_PORTS)
            else: # Limestone is imported to India
                load_port = random.choice(LIMESTONE_SOURCE_PORTS)
                discharge_port = random.choice(INDIAN_PORTS)
                
            # 1. OCEAN FREIGHT COST (Converted to INR)
            freight_usd = random.uniform(*FREIGHT_RANGE_USD[material])
            freight_inr = round(freight_usd * USD_TO_INR, 2)
            
            # 2. DEMURRAGE RATE (Converted to INR)
            demurrage_usd = random.uniform(*DEMURRAGE_RANGE_USD)
            demurrage_inr = round(demurrage_usd * USD_TO_INR, 2)
            
            # 3. CONTRACT CONSTRAINTS
            quantity = round(random.uniform(*QTY_RANGE[material]), -2)
            laydays = random.choice(LAYDAYS)
            
            vessel_data.append({
                'vessel_id': vessel_id,
                'load_port': load_port,
                'discharge_port': discharge_port,
                'material': material,
                'ocean_freight_inr_tonne': freight_inr,
                'demurrage_rate_inr_hr': demurrage_inr,
                'contract_quantity_tonnes': quantity,
                'laydays_allowed_hours': laydays,
            })

    df = pd.DataFrame(vessel_data)
    
    print(f"STATUS: Writing static data to Excel file: {output_path}")
    
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Vessel Costs')
            workbook = writer.book
            worksheet = writer.sheets['Vessel Costs']
            two_dec = workbook.add_format({'num_format':'0.00'})
            worksheet.set_column('E:H', 22, two_dec)
            
        print(f"SUCCESS: Vessel cost data successfully saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save Excel. Details: {e}")
        sys.exit(1)
        
# if __name__ == "__main__":                                      #***Commented to prevent accidental run***
#     generate_vessel_cost_data(DEFAULT_OUTPUT_LOG)
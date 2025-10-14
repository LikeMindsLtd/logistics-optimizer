import os
import sys
import subprocess
from datetime import datetime

'''Please avoid rerunning this file, if runned dont push it into production.
   But you can feel free to try generating this, only if you have a copy of already generated original logs.
   Then after generating and trying out, please replace the newly generated files with the original ones'''

# ---------------- CONFIG ----------------
GENERATOR_SCRIPTS = [

    "plantLogGenerator.py",    # Creates plant_log.xlsx 
    "trainLogGenerator.py",    # Creates train_log.xlsx 
    "portLogGenerator.py",     # Creates port_log.xlsx 
    "vesselCostGenerator.py",  # Creates vessel_cost.xlsx
    "portTariffGenerator.py", # Creates port_tariffs.xlsx
    "vesselDelayHistory.py",  # Creates vessel_delay_history.xlsx
]

def run_script(script_name):
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    
    if not os.path.exists(script_path):
        print(f"\n ERROR: Dependency script not found: {script_name}. Please ensure all generator files are in the same directory.")
        return False
        
    print(f"\n--- Running Script: {script_name} ---")
    
    try:
        subprocess.run(
            [sys.executable, script_path], 
            check=True, 
            capture_output=False, 
            text=True
        )
        print(f"--- Script {script_name} finished successfully. ---")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n FATAL ERROR in {script_name}: The script returned a non-zero exit code.")
        print(f"  Check the output above for specific errors.")
        return False
    except Exception as e:
        print(f"\n UNEXPECTED ERROR while running {script_name}: {e}")
        return False


def run_all_generators():
        
    start_time = datetime.now()
    print("===================================================================")
    print(f"STARTING MASTER DATA GENERATION at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Running {len(GENERATOR_SCRIPTS)} scripts in the sequence: Plant -> Train -> Port -> Costs -> Delays.")
    print("===================================================================")

    for script in GENERATOR_SCRIPTS:
        success = run_script(script)
        
        if not success:
            print("\n===================================================================")
            print("PROCESS ABORTED due to failure in a dependency script.")
            print("===================================================================")
            return
            
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n===================================================================")
    print("MASTER GENERATION COMPLETE! All 6 datasets have been created.")
    print(f"Total time taken: {duration}")
    print("===================================================================")


# if __name__ == "__main__":          #***Commented to prevent accidental run***
#     run_all_generators()
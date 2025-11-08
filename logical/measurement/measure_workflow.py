
import os
import subprocess
import sys
from datetime import datetime

class MeasurementWorkflow:
    def __init__(self, output_dir="measurement_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def run_reference_measurement(self):
        print("\nStep 2: Measuring taper structures...")
        
        reference_csv = os.path.join(self.output_dir, "reference.csv")
        if not os.path.exists(reference_csv):
            print("Reference measurement not found! Run reference measurement first.")
            return False
        
        success_count = 0
        for taper_length in taper_lengths:
            print(f"Measuring {taper_length}µm taper...")
            
            result = subprocess.run([
                sys.executable, "measure_taper.py",
                "--taper-length", str(taper_length),
                "--reference-csv", reference_csv
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {taper_length}µm taper measurement completed")
                success_count += 1
                
                for file in [f"taper_{taper_length}um.csv", 
                           f"taper_{taper_length}um_metadata.json",
                           f"taper_{taper_length}um_analysis.png"]:
                    if os.path.exists(file):
                        os.rename(file, os.path.join(self.output_dir, file))
            else:
                print(f"✗ {taper_length}µm taper measurement failed: {result.stderr}")
        
        return success_count > 0
    
    def run_analysis(self):
        
        report_file = os.path.join(self.output_dir, "measurement_workflow_report.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"Workflow report saved to: {report_file}")
        print(report)
        
        return report
    
    def run_complete_workflow(self):
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete measurement workflow')
    parser.add_argument('--output-dir', default='measurement_data',
                       help='Output directory for measurement data')
    
    args = parser.parse_args()
    
    workflow = MeasurementWorkflow(args.output_dir)
    workflow.run_complete_workflow()

if __name__ == "__main__":
    main()
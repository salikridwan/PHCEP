#!/usr/bin/env python3
"""
Complete Measurement Workflow
Orchestrates reference and taper measurements in correct sequence
"""

import os
import subprocess
import sys
from datetime import datetime

class MeasurementWorkflow:
    def __init__(self, output_dir="measurement_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def run_reference_measurement(self):
        """Run reference waveguide measurement"""
        print("Step 1: Measuring reference waveguide...")
        
        # Run reference measurement script
        result = subprocess.run([
            sys.executable, "measure_reference.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Reference measurement completed successfully")
            
            # Move files to output directory
            for file in ["reference.csv", "reference_metadata.json", "reference_measurement.png"]:
                if os.path.exists(file):
                    os.rename(file, os.path.join(self.output_dir, file))
                    
            return True
        else:
            print(f"✗ Reference measurement failed: {result.stderr}")
            return False
    
    def run_taper_measurements(self, taper_lengths=[5, 10, 20]):
        """Run taper measurements for specified lengths"""
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
                
                # Move files to output directory
                for file in [f"taper_{taper_length}um.csv", 
                           f"taper_{taper_length}um_metadata.json",
                           f"taper_{taper_length}um_analysis.png"]:
                    if os.path.exists(file):
                        os.rename(file, os.path.join(self.output_dir, file))
            else:
                print(f"✗ {taper_length}µm taper measurement failed: {result.stderr}")
        
        return success_count > 0
    
    def run_analysis(self):
        """Run post-measurement analysis"""
        print("\nStep 3: Running analysis...")
        
        # Run taper analysis
        result = subprocess.run([
            sys.executable, "taper_loss_analysis.py",
            os.path.join(self.output_dir, "reference.csv"),
            os.path.join(self.output_dir, "taper_5um.csv")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Taper analysis completed")
            
            # Move analysis results
            for file in ["taper_5um_analysis.png", "taper_5um_results.json"]:
                if os.path.exists(file):
                    os.rename(file, os.path.join(self.output_dir, file))
                    
            return True
        else:
            print(f"✗ Analysis failed: {result.stderr}")
            return False
    
    def generate_report(self):
        """Generate measurement workflow report"""
        report = f"""
=== MEASUREMENT WORKFLOW REPORT ===
Timestamp: {datetime.now().isoformat()}
Output directory: {self.output_dir}

FILES GENERATED:
Reference measurement:
- reference.csv: Reference waveguide transmission data
- reference_metadata.json: Measurement metadata
- reference_measurement.png: Transmission plot

Taper measurements:
- taper_5um.csv: 5µm taper transmission data
- taper_10um.csv: 10µm taper transmission data  
- taper_20um.csv: 20µm taper transmission data
- taper_Xum_metadata.json: Taper measurement metadata
- taper_Xum_analysis.png: Taper analysis plots

Analysis results:
- taper_5um_results.json: Insertion loss results
- taper_5um_analysis.png: Comprehensive analysis plot

NEXT STEPS:
1. Verify measurement quality in the plots
2. Check insertion loss values in the results files
3. Compare different taper lengths for optimization
4. Use the data for further photonic circuit design

MEASUREMENT PROTOCOL:
1. Always measure reference waveguide first
2. Ensure proper fiber coupling alignment
3. Use TE polarization for all measurements
4. Maintain consistent laser power settings
5. Save all raw data files for reproducibility
        """
        
        report_file = os.path.join(self.output_dir, "measurement_workflow_report.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"Workflow report saved to: {report_file}")
        print(report)
        
        return report
    
    def run_complete_workflow(self):
        """Run the complete measurement workflow"""
        print("=== COMPLETE MEASUREMENT WORKFLOW ===")
        print(f"Output directory: {self.output_dir}")
        print()
        
        # Step 1: Reference measurement
        if not self.run_reference_measurement():
            print("Workflow failed at reference measurement")
            return False
        
        # Step 2: Taper measurements
        if not self.run_taper_measurements():
            print("Workflow failed at taper measurements")
            return False
        
        # Step 3: Analysis
        if not self.run_analysis():
            print("Workflow failed at analysis")
            return False
        
        # Step 4: Report
        self.generate_report()
        
        print("\n✅ MEASUREMENT WORKFLOW COMPLETE!")
        print(f"All data and results saved to: {self.output_dir}")
        
        return True

def main():
    """Main workflow execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete measurement workflow')
    parser.add_argument('--output-dir', default='measurement_data',
                       help='Output directory for measurement data')
    
    args = parser.parse_args()
    
    workflow = MeasurementWorkflow(args.output_dir)
    workflow.run_complete_workflow()

if __name__ == "__main__":
    main()
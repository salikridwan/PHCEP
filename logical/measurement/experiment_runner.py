
import os
import glob
import json
import pandas as pd
from datetime import datetime
import subprocess
import sys

class ExperimentRunner:
    def __init__(self, data_directory="data/fab_test"):
        self.data_dir = data_directory
        self.results_summary = {}
        self.analysis_scripts = {
            'cutback': 'cutback_analysis.py',
            'taper': 'taper_loss_analysis.py', 
            'ring': 'ring_q_analysis.py',
            'pcm': 'pcm_correlation.py'
        }
    
    def discover_data_files(self):
        print("Running cut-back analysis...")
        
        for file_path in cutback_files:
            try:
                result = subprocess.run([
                    sys.executable, 'cutback_analysis.py', file_path, '--no-plot'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ {os.path.basename(file_path)}")
                    result_file = file_path.replace('.csv', '_results.json')
                    if os.path.exists(result_file):
                        with open(result_file, 'r') as f:
                            self.results_summary[os.path.basename(file_path)] = json.load(f)
                else:
                    print(f"✗ {os.path.basename(file_path)}: {result.stderr}")
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def run_taper_analysis(self, taper_files):
        pairs = []
        
        for taper_file in taper_files:
            ref_candidates = []
            for file in glob.glob(os.path.join(os.path.dirname(taper_file), "*reference*")):
                if 'taper' not in file.lower():
                    ref_candidates.append(file)
            
            if ref_candidates:
                pairs.append((taper_file, ref_candidates[0]))
            else:
                pairs.append((taper_file, None))
                print(f"Warning: No reference found for {taper_file}")
        
        return pairs
    
    def run_ring_analysis(self, ring_files):
        print("Running PCM correlation analysis...")
        
        try:
            result = subprocess.run([
                sys.executable, 'pcm_correlation.py', '--data-dir', self.data_dir
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ PCM correlation analysis")
            else:
                print(f"✗ PCM correlation: {result.stderr}")
                
        except Exception as e:
            print(f"Error running PCM correlation: {e}")
    
    def generate_summary_report(self):
        stats = report['summary_statistics']
        
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY REPORT")
        print("="*60)
        
        if stats['propagation_loss']['mean']:
            print(f"Propagation Loss: {stats['propagation_loss']['mean']:.3f} ± {stats['propagation_loss']['std']:.3f} dB/cm")
        
        if stats['q_factors']['mean']:
            print(f"Q-factor: {stats['q_factors']['mean']:.0f} ± {stats['q_factors']['std']:.0f}")
        
        if stats['insertion_loss']['mean']:
            print(f"Taper Insertion Loss: {stats['insertion_loss']['mean']:.3f} ± {stats['insertion_loss']['std']:.3f} dB")
        
        print(f"Total analyses: {len(report['analyses_performed'])}")
        print("="*60)
    
    def run_complete_analysis(self):

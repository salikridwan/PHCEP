#!/usr/bin/env python3
"""
Experiment Runner - Automated Analysis Orchestration
Collects CSV files, runs appropriate analyses, and generates summary reports
"""

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
        """Discover all data files in the directory structure"""
        data_files = {
            'cutback': [],
            'taper': [],
            'ring': [],
            'pcm': [],
            'other': []
        }
        
        # Find all CSV files
        csv_files = glob.glob(os.path.join(self.data_dir, "**", "*.csv"), recursive=True)
        
        for file_path in csv_files:
            filename = os.path.basename(file_path).lower()
            
            if any(keyword in filename for keyword in ['cutback', 'straight', 'length']):
                data_files['cutback'].append(file_path)
            elif any(keyword in filename for keyword in ['taper', 'wide', 'narrow']):
                data_files['taper'].append(file_path)
            elif any(keyword in filename for keyword in ['ring', 'resonance', 'spectrum']):
                data_files['ring'].append(file_path)
            elif any(keyword in filename for keyword in ['pcm', 'doping', 'etch', 'width']):
                data_files['pcm'].append(file_path)
            else:
                data_files['other'].append(file_path)
        
        return data_files
    
    def run_cutback_analysis(self, cutback_files):
        """Run cut-back analysis on discovered files"""
        print("Running cut-back analysis...")
        
        for file_path in cutback_files:
            try:
                result = subprocess.run([
                    sys.executable, 'cutback_analysis.py', file_path, '--no-plot'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ {os.path.basename(file_path)}")
                    # Extract results from output or result file
                    result_file = file_path.replace('.csv', '_results.json')
                    if os.path.exists(result_file):
                        with open(result_file, 'r') as f:
                            self.results_summary[os.path.basename(file_path)] = json.load(f)
                else:
                    print(f"✗ {os.path.basename(file_path)}: {result.stderr}")
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def run_taper_analysis(self, taper_files):
        """Run taper analysis (requires reference files)"""
        print("Running taper analysis...")
        
        # Group taper files with their references
        taper_pairs = self._pair_taper_files(taper_files)
        
        for taper_file, reference_file in taper_pairs:
            if reference_file:
                try:
                    result = subprocess.run([
                        sys.executable, 'taper_loss_analysis.py', reference_file, taper_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✓ {os.path.basename(taper_file)}")
                        result_file = taper_file.replace('.csv', '_results.json')
                        if os.path.exists(result_file):
                            with open(result_file, 'r') as f:
                                self.results_summary[os.path.basename(taper_file)] = json.load(f)
                    else:
                        print(f"✗ {os.path.basename(taper_file)}: {result.stderr}")
                        
                except Exception as e:
                    print(f"Error analyzing {taper_file}: {e}")
    
    def _pair_taper_files(self, taper_files):
        """Pair taper files with their reference measurements"""
        pairs = []
        
        for taper_file in taper_files:
            # Look for corresponding reference file
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
        """Run ring resonator analysis"""
        print("Running ring resonator analysis...")
        
        for file_path in ring_files:
            try:
                result = subprocess.run([
                    sys.executable, 'ring_q_analysis.py', file_path
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
    
    def run_pcm_correlation(self):
        """Run PCM correlation analysis"""
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
        """Generate comprehensive summary report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_directory': self.data_dir,
            'analyses_performed': list(self.results_summary.keys()),
            'results': self.results_summary
        }
        
        # Calculate summary statistics
        propagation_losses = []
        q_factors = []
        insertion_losses = []
        
        for filename, results in self.results_summary.items():
            if 'propagation_loss_dB_cm' in results:
                propagation_losses.append(results['propagation_loss_dB_cm'])
            if 'resonance_results' in results and results['resonance_results']:
                q_factors.extend([r['Q_factor'] for r in results['resonance_results']])
            if 'mean_insertion_loss' in results:
                insertion_losses.append(results['mean_insertion_loss'])
        
        report['summary_statistics'] = {
            'propagation_loss': {
                'mean': np.mean(propagation_losses) if propagation_losses else None,
                'std': np.std(propagation_losses) if propagation_losses else None,
                'min': min(propagation_losses) if propagation_losses else None,
                'max': max(propagation_losses) if propagation_losses else None
            },
            'q_factors': {
                'mean': np.mean(q_factors) if q_factors else None,
                'std': np.std(q_factors) if q_factors else None
            },
            'insertion_loss': {
                'mean': np.mean(insertion_losses) if insertion_losses else None,
                'std': np.std(insertion_losses) if insertion_losses else None
            }
        }
        
        # Save report
        report_file = os.path.join(self.data_dir, f"experiment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nSummary report saved to: {report_file}")
        
        # Print quick summary
        self.print_quick_summary(report)
        
        return report
    
    def print_quick_summary(self, report):
        """Print a quick human-readable summary"""
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
        """Run complete analysis pipeline"""
        print("=== EXPERIMENT RUNNER ===")
        print(f"Data directory: {self.data_dir}")
        print("Discovering data files...")
        
        data_files = self.discover_data_files()
        
        print(f"Found:")
        print(f"  - Cut-back files: {len(data_files['cutback'])}")
        print(f"  - Taper files: {len(data_files['taper'])}")
        print(f"  - Ring files: {len(data_files['ring'])}")
        print(f"  - PCM files: {len(data_files['pcm'])}")
        print(f"  - Other files: {len(data_files['other'])}")
        
        # Run analyses
        if data_files['cutback']:
            self.run_cutback_analysis(data_files['cutback'])
        
        if data_files['taper']:
            self.run_taper_analysis(data_files['taper'])
        
        if data_files['ring']:
            self.run_ring_analysis(data_files['ring'])
        
        if data_files['pcm']:
            self.run_pcm_correlation()
        
        # Generate summary
        self.generate_summary_report()
        
        print("\n=== ANALYSIS COMPLETE ===")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated experiment analysis runner')
    parser.add_argument('--data-dir', default='data/fab_test', help='Data directory path')
    
    args = parser.parse_args()
    
    runner = ExperimentRunner(args.data_dir)
    runner.run_complete_analysis()

if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import argparse
import os

class CutbackAnalyzer:
    def __init__(self):
        self.results = {}
        
    def load_data(self, csv_file):
        lengths_cm = df['waveguide_length_um'] / 10000
        
        if reference_power is None:
            reference_power = df['transmitted_power_dBm'].max()
        
        transmission_loss = reference_power - df['transmitted_power_dBm']
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            lengths_cm, transmission_loss
        )
        
        alpha = slope
        
        results = {
            'propagation_loss_dB_cm': alpha,
            'r_squared': r_value**2,
            'std_error': std_err,
            'lengths_cm': lengths_cm.tolist(),
            'measured_loss': transmission_loss.tolist(),
            'fitted_loss': (slope * lengths_cm + intercept).tolist()
        }
        
        return results
    
    def plot_analysis(self, df, results, output_file=None):
        print(f"Analyzing cut-back data: {csv_file}")
        
        df = self.load_data(csv_file)
        print(f"Loaded {len(df)} measurements")
        
        results = self.calculate_propagation_loss(df, reference_power)
        
        print("\n=== CUT-BACK ANALYSIS RESULTS ===")
        print(f"Propagation loss: {results['propagation_loss_dB_cm']:.3f} dB/cm")
        print(f"R² value: {results['r_squared']:.4f}")
        print(f"Standard error: {results['std_error']:.4f}")
        
        if plot:
            plot_file = csv_file.replace('.csv', '_analysis.png')
            self.plot_analysis(df, results, plot_file)
        
        results_file = csv_file.replace('.csv', '_results.json')
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Cut-back loss analysis')
    parser.add_argument('csv_file', help='Input CSV file with length and power measurements')
    parser.add_argument('--reference', type=float, help='Reference power in dBm (optional)')
    parser.add_argument('--no-plot', action='store_true', help='Skip plotting')
    
    args = parser.parse_args()
    
    analyzer = CutbackAnalyzer()
    analyzer.analyze_cutback(args.csv_file, args.reference, not args.no_plot)

if __name__ == "__main__":
    main()
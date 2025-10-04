#!/usr/bin/env python3
"""
Cut-back Loss Analysis Script
Analyzes straight waveguide measurements to extract propagation loss
"""

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
        """Load cut-back measurement data"""
        df = pd.read_csv(csv_file)
        required_cols = ['waveguide_length_um', 'transmitted_power_dBm']
        
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
            
        return df
    
    def calculate_propagation_loss(self, df, reference_power=None):
        """Calculate propagation loss using linear regression"""
        # Convert lengths to cm
        lengths_cm = df['waveguide_length_um'] / 10000
        
        # Use provided reference power or find maximum power as reference
        if reference_power is None:
            reference_power = df['transmitted_power_dBm'].max()
        
        # Calculate transmission loss relative to reference
        transmission_loss = reference_power - df['transmitted_power_dBm']
        
        # Linear regression: loss = α * length
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            lengths_cm, transmission_loss
        )
        
        # Propagation loss coefficient (dB/cm)
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
        """Create visualization of cut-back analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot 1: Raw transmission vs length
        ax1.plot(df['waveguide_length_um'] / 1000, df['transmitted_power_dBm'], 
                'bo-', linewidth=2, markersize=8, label='Measured')
        ax1.set_xlabel('Waveguide Length (mm)')
        ax1.set_ylabel('Transmitted Power (dBm)')
        ax1.set_title('Transmission vs Waveguide Length')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Loss vs length with linear fit
        lengths_cm = np.array(results['lengths_cm'])
        ax2.plot(lengths_cm, results['measured_loss'], 'ro', 
                markersize=8, label='Measured loss')
        ax2.plot(lengths_cm, results['fitted_loss'], 'b-', 
                linewidth=2, label=f'Linear fit (α={results["propagation_loss_dB_cm"]:.3f} dB/cm)')
        ax2.set_xlabel('Waveguide Length (cm)')
        ax2.set_ylabel('Propagation Loss (dB)')
        ax2.set_title('Cut-back Loss Analysis')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Add R² annotation
        ax2.text(0.05, 0.95, f'R² = {results["r_squared"]:.4f}', 
                transform=ax2.transAxes, fontsize=12,
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {output_file}")
        else:
            plt.show()
    
    def analyze_cutback(self, csv_file, reference_power=None, plot=True):
        """Complete cut-back analysis"""
        print(f"Analyzing cut-back data: {csv_file}")
        
        # Load data
        df = self.load_data(csv_file)
        print(f"Loaded {len(df)} measurements")
        
        # Calculate propagation loss
        results = self.calculate_propagation_loss(df, reference_power)
        
        # Display results
        print("\n=== CUT-BACK ANALYSIS RESULTS ===")
        print(f"Propagation loss: {results['propagation_loss_dB_cm']:.3f} dB/cm")
        print(f"R² value: {results['r_squared']:.4f}")
        print(f"Standard error: {results['std_error']:.4f}")
        
        # Create plot
        if plot:
            plot_file = csv_file.replace('.csv', '_analysis.png')
            self.plot_analysis(df, results, plot_file)
        
        # Save results
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
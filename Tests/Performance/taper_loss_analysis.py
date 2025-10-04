#!/usr/bin/env python3
"""
Taper Insertion Loss Analysis
Calculates insertion loss from taper measurements
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse

class TaperAnalyzer:
    def __init__(self):
        self.results = {}
    
    def load_taper_data(self, reference_csv, taper_csv):
        """Load reference and taper measurement data"""
        ref_df = pd.read_csv(reference_csv)
        taper_df = pd.read_csv(taper_csv)
        
        # Ensure wavelength alignment
        if 'wavelength_nm' not in ref_df.columns or 'wavelength_nm' not in taper_df.columns:
            raise ValueError("CSV files must contain 'wavelength_nm' column")
        
        return ref_df, taper_df
    
    def calculate_insertion_loss(self, ref_df, taper_df, wavelength_range=None):
        """Calculate taper insertion loss across wavelength range"""
        # Merge data on wavelength
        merged = pd.merge(ref_df, taper_df, on='wavelength_nm', 
                         suffixes=('_ref', '_taper'))
        
        # Filter wavelength range if specified
        if wavelength_range:
            wl_min, wl_max = wavelength_range
            merged = merged[(merged['wavelength_nm'] >= wl_min) & 
                          (merged['wavelength_nm'] <= wl_max)]
        
        # Calculate insertion loss: IL = P_ref - P_taper
        if 'power_dBm_ref' in merged.columns and 'power_dBm_taper' in merged.columns:
            merged['insertion_loss_dB'] = merged['power_dBm_ref'] - merged['power_dBm_taper']
        else:
            # Try to find power columns automatically
            power_cols_ref = [col for col in merged.columns if 'power' in col.lower() and 'ref' in col]
            power_cols_taper = [col for col in merged.columns if 'power' in col.lower() and 'taper' in col]
            
            if power_cols_ref and power_cols_taper:
                merged['insertion_loss_dB'] = merged[power_cols_ref[0]] - merged[power_cols_taper[0]]
            else:
                raise ValueError("Could not find power measurement columns")
        
        results = {
            'wavelengths': merged['wavelength_nm'].tolist(),
            'insertion_loss': merged['insertion_loss_dB'].tolist(),
            'mean_insertion_loss': merged['insertion_loss_dB'].mean(),
            'min_insertion_loss': merged['insertion_loss_dB'].min(),
            'max_insertion_loss': merged['insertion_loss_dB'].max(),
            'std_insertion_loss': merged['insertion_loss_dB'].std()
        }
        
        return results, merged
    
    def plot_taper_performance(self, results, output_file=None):
        """Plot taper insertion loss vs wavelength"""
        plt.figure(figsize=(10, 6))
        
        plt.plot(results['wavelengths'], results['insertion_loss'], 
                'b-', linewidth=2, label='Insertion Loss')
        
        # Add mean line
        plt.axhline(y=results['mean_insertion_loss'], color='r', linestyle='--',
                   label=f'Mean: {results["mean_insertion_loss"]:.3f} dB')
        
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Insertion Loss (dB)')
        plt.title('Taper Insertion Loss Analysis')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Add statistics box
        textstr = '\n'.join([
            f'Mean: {results["mean_insertion_loss"]:.3f} dB',
            f'Min: {results["min_insertion_loss"]:.3f} dB',
            f'Max: {results["max_insertion_loss"]:.3f} dB',
            f'Std: {results["std_insertion_loss"]:.3f} dB'
        ])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {output_file}")
        else:
            plt.show()
    
    def analyze_taper(self, reference_csv, taper_csv, wavelength_range=None):
        """Complete taper analysis"""
        print(f"Analyzing taper: {taper_csv} vs reference: {reference_csv}")
        
        # Load data
        ref_df, taper_df = self.load_taper_data(reference_csv, taper_csv)
        print(f"Reference data points: {len(ref_df)}")
        print(f"Taper data points: {len(taper_df)}")
        
        # Calculate insertion loss
        results, merged_data = self.calculate_insertion_loss(ref_df, taper_df, wavelength_range)
        
        # Display results
        print("\n=== TAPER ANALYSIS RESULTS ===")
        print(f"Mean insertion loss: {results['mean_insertion_loss']:.3f} dB")
        print(f"Minimum insertion loss: {results['min_insertion_loss']:.3f} dB")
        print(f"Maximum insertion loss: {results['max_insertion_loss']:.3f} dB")
        print(f"Standard deviation: {results['std_insertion_loss']:.3f} dB")
        
        # Create plot
        plot_file = taper_csv.replace('.csv', '_analysis.png')
        self.plot_taper_performance(results, plot_file)
        
        # Save results
        results_file = taper_csv.replace('.csv', '_results.json')
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save merged data
        merged_file = taper_csv.replace('.csv', '_merged.csv')
        merged_data.to_csv(merged_file, index=False)
        
        print(f"Results saved to {results_file}")
        print(f"Merged data saved to {merged_file}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Taper insertion loss analysis')
    parser.add_argument('reference_csv', help='Reference measurement CSV (no taper)')
    parser.add_argument('taper_csv', help='Taper measurement CSV')
    parser.add_argument('--wavelength-range', nargs=2, type=float, 
                       help='Wavelength range [min max] in nm')
    
    args = parser.parse_args()
    
    analyzer = TaperAnalyzer()
    
    if args.wavelength_range:
        analyzer.analyze_taper(args.reference_csv, args.taper_csv, args.wavelength_range)
    else:
        analyzer.analyze_taper(args.reference_csv, args.taper_csv)

if __name__ == "__main__":
    main()
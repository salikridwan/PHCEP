
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse

class TaperAnalyzer:
    def __init__(self):
        self.results = {}
    
    def load_taper_data(self, reference_csv, taper_csv):
        merged = pd.merge(ref_df, taper_df, on='wavelength_nm', 
                         suffixes=('_ref', '_taper'))
        
        if wavelength_range:
            wl_min, wl_max = wavelength_range
            merged = merged[(merged['wavelength_nm'] >= wl_min) & 
                          (merged['wavelength_nm'] <= wl_max)]
        
        if 'power_dBm_ref' in merged.columns and 'power_dBm_taper' in merged.columns:
            merged['insertion_loss_dB'] = merged['power_dBm_ref'] - merged['power_dBm_taper']
        else:
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
        print(f"Analyzing taper: {taper_csv} vs reference: {reference_csv}")
        
        ref_df, taper_df = self.load_taper_data(reference_csv, taper_csv)
        print(f"Reference data points: {len(ref_df)}")
        print(f"Taper data points: {len(taper_df)}")
        
        results, merged_data = self.calculate_insertion_loss(ref_df, taper_df, wavelength_range)
        
        print("\n=== TAPER ANALYSIS RESULTS ===")
        print(f"Mean insertion loss: {results['mean_insertion_loss']:.3f} dB")
        print(f"Minimum insertion loss: {results['min_insertion_loss']:.3f} dB")
        print(f"Maximum insertion loss: {results['max_insertion_loss']:.3f} dB")
        print(f"Standard deviation: {results['std_insertion_loss']:.3f} dB")
        
        plot_file = taper_csv.replace('.csv', '_analysis.png')
        self.plot_taper_performance(results, plot_file)
        
        results_file = taper_csv.replace('.csv', '_results.json')
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
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
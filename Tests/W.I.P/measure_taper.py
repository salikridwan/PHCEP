#!/usr/bin/env python3
"""
Taper Insertion Loss Measurement
Measure 5µm taper performance relative to reference waveguide
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import json

class TaperMeasurement:
    def __init__(self, instrument_simulated=True):
        self.instrument_simulated = instrument_simulated
        self.measurement_data = []
        
    def simulate_taper_measurement(self, wavelength_nm, taper_length=5):
        """Simulate taper measurement (replace with actual instrument API calls)"""
        # Base transmission (same as reference)
        base_transmission = -25  # dBm baseline
        
        # Taper-specific parameters
        if taper_length == 5:
            insertion_loss = 0.4  # dB for 5µm taper
            ripple = 0.05  # wavelength-dependent ripple
        elif taper_length == 10:
            insertion_loss = 0.25  # dB for 10µm taper  
            ripple = 0.03
        else:  # 20µm taper
            insertion_loss = 0.1  # dB for 20µm taper
            ripple = 0.02
            
        # Wavelength-dependent effects
        wavelength_variation = ripple * np.sin(2 * np.pi * (wavelength_nm - 1550) / 30)
        
        # Random noise
        noise = np.random.normal(0, 0.1)
        
        power_dBm = base_transmission - insertion_loss + wavelength_variation + noise
        
        return power_dBm
    
    def measure_taper_sweep(self, taper_length=5, start_wavelength=1500, 
                          stop_wavelength=1600, num_points=201):
        """Perform wavelength sweep on taper structure"""
        taper_id = f"taper_{taper_length}um"
        print(f"Measuring taper: {taper_id}")
        print(f"Wavelength range: {start_wavelength}-{stop_wavelength} nm")
        
        wavelengths = np.linspace(start_wavelength, stop_wavelength, num_points)
        powers = []
        
        for i, wl in enumerate(wavelengths):
            if self.instrument_simulated:
                power = self.simulate_taper_measurement(wl, taper_length)
            else:
                # Replace with actual instrument command:
                # power = self.actual_instrument.get_power_at_wavelength(wl)
                power = self.simulate_taper_measurement(wl, taper_length)
                
            powers.append(power)
            
            # Progress indicator
            if i % 20 == 0:
                print(f"  Progress: {i}/{num_points} points")
                
            # Small delay to simulate measurement time
            if not self.instrument_simulated:
                time.sleep(0.1)
        
        # Create DataFrame
        df = pd.DataFrame({
            'wavelength_nm': wavelengths,
            'power_dBm': powers,
            'taper_length_um': taper_length,
            'taper_id': taper_id,
            'timestamp': datetime.now().isoformat()
        })
        
        self.measurement_data = df
        return df
    
    def calculate_insertion_loss(self, reference_csv="reference.csv"):
        """Calculate insertion loss relative to reference measurement"""
        try:
            # Load reference data
            ref_df = pd.read_csv(reference_csv)
            
            # Merge with taper data on wavelength
            merged = pd.merge(self.measurement_data, ref_df, on='wavelength_nm', 
                            suffixes=('_taper', '_ref'))
            
            # Calculate insertion loss: IL = P_ref - P_taper
            merged['insertion_loss_dB'] = merged['power_dBm_ref'] - merged['power_dBm_taper']
            
            # Calculate statistics
            mean_il = merged['insertion_loss_dB'].mean()
            std_il = merged['insertion_loss_dB'].std()
            min_il = merged['insertion_loss_dB'].min()
            max_il = merged['insertion_loss_dB'].max()
            
            results = {
                'taper_length_um': self.measurement_data['taper_length_um'].iloc[0],
                'mean_insertion_loss_dB': mean_il,
                'std_insertion_loss_dB': std_il,
                'min_insertion_loss_dB': min_il,
                'max_insertion_loss_dB': max_il,
                'wavelength_range_nm': [merged['wavelength_nm'].min(), merged['wavelength_nm'].max()],
                'num_points': len(merged)
            }
            
            return results, merged
            
        except FileNotFoundError:
            print(f"Reference file {reference_csv} not found!")
            return None, None
        except Exception as e:
            print(f"Error calculating insertion loss: {e}")
            return None, None
    
    def save_measurement(self, filename=None):
        """Save taper measurement to CSV"""
        if self.measurement_data is None or len(self.measurement_data) == 0:
            print("No measurement data to save!")
            return
            
        if filename is None:
            taper_length = self.measurement_data['taper_length_um'].iloc[0]
            filename = f"taper_{taper_length}um.csv"
            
        self.measurement_data.to_csv(filename, index=False)
        print(f"Taper measurement saved to {filename}")
        
        # Also save metadata
        metadata = {
            'measurement_type': 'taper_insertion_loss',
            'taper_id': self.measurement_data['taper_id'].iloc[0],
            'taper_length_um': self.measurement_data['taper_length_um'].iloc[0],
            'wavelength_range': [self.measurement_data['wavelength_nm'].min(), 
                               self.measurement_data['wavelength_nm'].max()],
            'num_points': len(self.measurement_data),
            'timestamp': self.measurement_data['timestamp'].iloc[0],
            'instrument_simulated': self.instrument_simulated
        }
        
        metadata_file = filename.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_file}")
        
        return filename
    
    def plot_measurement(self, reference_csv="reference.csv"):
        """Plot taper measurement with reference comparison"""
        if self.measurement_data is None or len(self.measurement_data) == 0:
            print("No measurement data to plot!")
            return
            
        # Load reference data if available
        ref_df = None
        try:
            ref_df = pd.read_csv(reference_csv)
        except:
            print("Reference data not available for comparison")
        
        plt.figure(figsize=(12, 8))
        
        # Plot 1: Raw power comparison
        plt.subplot(2, 1, 1)
        if ref_df is not None:
            plt.plot(ref_df['wavelength_nm'], ref_df['power_dBm'], 
                    'b-', linewidth=2, label='Reference waveguide')
        
        plt.plot(self.measurement_data['wavelength_nm'], self.measurement_data['power_dBm'],
                'r-', linewidth=2, label=f'Taper {self.measurement_data["taper_length_um"].iloc[0]}µm')
        
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Transmitted Power (dBm)')
        plt.title('Taper vs Reference Waveguide Transmission')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Plot 2: Insertion loss
        plt.subplot(2, 1, 2)
        if ref_df is not None:
            results, merged = self.calculate_insertion_loss(reference_csv)
            if results is not None:
                plt.plot(merged['wavelength_nm'], merged['insertion_loss_dB'],
                        'g-', linewidth=2, label='Insertion Loss')
                plt.axhline(y=results['mean_insertion_loss_dB'], color='r', linestyle='--',
                           label=f'Mean: {results["mean_insertion_loss_dB"]:.3f} dB')
                
                plt.xlabel('Wavelength (nm)')
                plt.ylabel('Insertion Loss (dB)')
                plt.title('Taper Insertion Loss')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Add statistics box
                textstr = '\n'.join([
                    f'Mean: {results["mean_insertion_loss_dB"]:.3f} dB',
                    f'Std: {results["std_insertion_loss_dB"]:.3f} dB',
                    f'Min: {results["min_insertion_loss_dB"]:.3f} dB',
                    f'Max: {results["max_insertion_loss_dB"]:.3f} dB'
                ])
                props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
                plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
                        verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plot_file = f"taper_{self.measurement_data['taper_length_um'].iloc[0]}um_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Analysis plot saved to {plot_file}")
        plt.show()

def main():
    """Main taper measurement procedure"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Taper insertion loss measurement')
    parser.add_argument('--taper-length', type=int, default=5, choices=[5, 10, 20],
                       help='Taper length in microns (5, 10, or 20)')
    parser.add_argument('--reference-csv', default='reference.csv',
                       help='Reference measurement CSV file')
    parser.add_argument('--real-instrument', action='store_true',
                       help='Use real instrument (instead of simulation)')
    
    args = parser.parse_args()
    
    print("=== TAPER INSERTION LOSS MEASUREMENT ===")
    print(f"Measuring {args.taper_length}µm taper relative to reference")
    print()
    
    # Initialize measurement system
    measurement = TaperMeasurement(instrument_simulated=not args.real_instrument)
    
    # Perform wavelength sweep
    df = measurement.measure_taper_sweep(
        taper_length=args.taper_length,
        start_wavelength=1500,
        stop_wavelength=1600,
        num_points=201
    )
    
    # Save measurement
    filename = measurement.save_measurement()
    
    # Calculate insertion loss
    results, merged_data = measurement.calculate_insertion_loss(args.reference_csv)
    
    if results is not None:
        print("\n=== INSERTION LOSS RESULTS ===")
        print(f"Taper length: {results['taper_length_um']} µm")
        print(f"Mean insertion loss: {results['mean_insertion_loss_dB']:.3f} dB")
        print(f"Standard deviation: {results['std_insertion_loss_dB']:.3f} dB")
        print(f"Minimum loss: {results['min_insertion_loss_dB']:.3f} dB")
        print(f"Maximum loss: {results['max_insertion_loss_dB']:.3f} dB")
        
        # Save results
        results_file = filename.replace('.csv', '_results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")
    
    # Plot results
    measurement.plot_measurement(args.reference_csv)
    
    print(f"\n✅ Taper measurement complete!")
    print(f"   Data saved to: {filename}")
    print(f"   Use with taper_loss_analysis.py for detailed analysis")

if __name__ == "__main__":
    main()
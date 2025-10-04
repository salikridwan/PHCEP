#!/usr/bin/env python3
"""
Reference Waveguide Measurement
Measure straight waveguide (no taper) across 1500-1600 nm for baseline calibration
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import json

class ReferenceMeasurement:
    def __init__(self, instrument_simulated=True):
        self.instrument_simulated = instrument_simulated
        self.measurement_data = []
        
    def simulate_instrument_measurement(self, wavelength_nm, waveguide_type="straight_0.22um"):
        """Simulate instrument measurement (replace with actual instrument API calls)"""
        # Simulate realistic transmission data
        base_transmission = -25  # dBm baseline
        
        if waveguide_type == "straight_0.22um":
            # Simulate straight waveguide transmission
            propagation_loss = 2.4  # dB/cm
            length = 0.2  # cm (2 mm test structure)
            length_loss = propagation_loss * length
            
            # Wavelength-dependent variation
            wavelength_variation = 0.1 * np.sin(2 * np.pi * (wavelength_nm - 1550) / 50)
            
            # Random noise
            noise = np.random.normal(0, 0.1)
            
            power_dBm = base_transmission - length_loss + wavelength_variation + noise
            
        else:
            # Default simulation
            power_dBm = base_transmission + np.random.normal(0, 0.5)
            
        return power_dBm
    
    def measure_wavelength_sweep(self, start_wavelength=1500, stop_wavelength=1600, 
                               num_points=201, waveguide_id="ref_straight_0.22um"):
        """Perform wavelength sweep measurement"""
        print(f"Measuring reference waveguide: {waveguide_id}")
        print(f"Wavelength range: {start_wavelength}-{stop_wavelength} nm")
        print(f"Number of points: {num_points}")
        
        wavelengths = np.linspace(start_wavelength, stop_wavelength, num_points)
        powers = []
        
        for i, wl in enumerate(wavelengths):
            if self.instrument_simulated:
                power = self.simulate_instrument_measurement(wl, waveguide_id)
            else:
                # Replace with actual instrument command:
                # power = self.actual_instrument.get_power_at_wavelength(wl)
                power = self.simulate_instrument_measurement(wl, waveguide_id)
                
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
            'waveguide_type': waveguide_id,
            'timestamp': datetime.now().isoformat()
        })
        
        self.measurement_data = df
        return df
    
    def save_measurement(self, filename="reference.csv"):
        """Save reference measurement to CSV"""
        if self.measurement_data is None or len(self.measurement_data) == 0:
            print("No measurement data to save!")
            return
            
        self.measurement_data.to_csv(filename, index=False)
        print(f"Reference measurement saved to {filename}")
        
        # Also save metadata
        metadata = {
            'measurement_type': 'reference_waveguide',
            'waveguide_id': self.measurement_data['waveguide_type'].iloc[0],
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
    
    def plot_measurement(self):
        """Plot the reference measurement"""
        if self.measurement_data is None or len(self.measurement_data) == 0:
            print("No measurement data to plot!")
            return
            
        plt.figure(figsize=(10, 6))
        plt.plot(self.measurement_data['wavelength_nm'], self.measurement_data['power_dBm'], 
                'b-', linewidth=2, label='Reference waveguide')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Transmitted Power (dBm)')
        plt.title('Reference Waveguide Measurement\n(Straight 0.22×0.18 µm waveguide)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Add measurement info
        plt.text(0.02, 0.98, f"Waveguide: {self.measurement_data['waveguide_type'].iloc[0]}\n"
                f"Points: {len(self.measurement_data)}", 
                transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('reference_measurement.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main reference measurement procedure"""
    print("=== REFERENCE WAVEGUIDE MEASUREMENT ===")
    print("Measuring straight waveguide (no taper) for baseline calibration")
    print()
    
    # Initialize measurement system
    measurement = ReferenceMeasurement(instrument_simulated=True)  # Set to False for real instrument
    
    # Perform wavelength sweep
    df = measurement.measure_wavelength_sweep(
        start_wavelength=1500,
        stop_wavelength=1600,
        num_points=201,
        waveguide_id="straight_0.22um"
    )
    
    # Save measurement
    measurement.save_measurement("reference.csv")
    
    # Plot results
    measurement.plot_measurement()
    
    # Display summary
    print("\n=== MEASUREMENT SUMMARY ===")
    print(f"Wavelength range: {df['wavelength_nm'].min():.1f} - {df['wavelength_nm'].max():.1f} nm")
    print(f"Power range: {df['power_dBm'].min():.2f} - {df['power_dBm'].max():.2f} dBm")
    print(f"Average power: {df['power_dBm'].mean():.2f} dBm")
    
    print("\n✅ Reference measurement complete!")
    print("   Use reference.csv for taper loss calculations")

if __name__ == "__main__":
    main()
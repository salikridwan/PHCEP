
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
        print(f"Measuring reference waveguide: {waveguide_id}")
        print(f"Wavelength range: {start_wavelength}-{stop_wavelength} nm")
        print(f"Number of points: {num_points}")
        
        wavelengths = np.linspace(start_wavelength, stop_wavelength, num_points)
        powers = []
        
        for i, wl in enumerate(wavelengths):
            if self.instrument_simulated:
                power = self.simulate_instrument_measurement(wl, waveguide_id)
            else:
                power = self.simulate_instrument_measurement(wl, waveguide_id)
                
            powers.append(power)
            
            if i % 20 == 0:
                print(f"  Progress: {i}/{num_points} points")
                
            if not self.instrument_simulated:
                time.sleep(0.1)
        
        df = pd.DataFrame({
            'wavelength_nm': wavelengths,
            'power_dBm': powers,
            'waveguide_type': waveguide_id,
            'timestamp': datetime.now().isoformat()
        })
        
        self.measurement_data = df
        return df
    
    def save_measurement(self, filename="reference.csv"):
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
        
        plt.text(0.02, 0.98, f"Waveguide: {self.measurement_data['waveguide_type'].iloc[0]}\n"
                f"Points: {len(self.measurement_data)}", 
                transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('reference_measurement.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():

#!/usr/bin/env python3
"""
Measurement Data Logger Template
Standardized CSV format for all fab test measurements
"""

import pandas as pd
import datetime
import json
import os

class MeasurementLogger:
    def __init__(self, experiment_name, wafer_id, operator):
        self.experiment_name = experiment_name
        self.wafer_id = wafer_id
        self.operator = operator
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory structure
        self.base_dir = f"data/fab_test/{experiment_name}/{wafer_id}"
        os.makedirs(self.base_dir, exist_ok=True)
        
    def log_cutback_measurement(self, waveguide_lengths, transmitted_powers, 
                               laser_wavelength=1550, polarization='TE'):
        """Log cut-back loss measurements"""
        metadata = {
            'experiment': self.experiment_name,
            'wafer': self.wafer_id,
            'operator': self.operator,
            'timestamp': self.timestamp,
            'measurement_type': 'cutback_loss',
            'laser_wavelength_nm': laser_wavelength,
            'polarization': polarization,
            'units': {'length': 'µm', 'power': 'dBm'}
        }
        
        data = {
            'waveguide_length_um': waveguide_lengths,
            'transmitted_power_dBm': transmitted_powers
        }
        
        df = pd.DataFrame(data)
        filename = f"{self.base_dir}/cutback_{self.timestamp}.csv"
        df.to_csv(filename, index=False)
        
        # Save metadata
        with open(f"{self.base_dir}/cutback_{self.timestamp}_meta.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Cut-back data saved to {filename}")
        return df
        
    def log_ring_spectrum(self, wavelengths, powers, ring_id='R10'):
        """Log ring resonator spectral scan"""
        metadata = {
            'experiment': self.experiment_name,
            'wafer': self.wafer_id,
            'operator': self.operator,
            'timestamp': self.timestamp,
            'measurement_type': 'ring_spectrum',
            'ring_id': ring_id,
            'wavelength_range_nm': [min(wavelengths), max(wavelengths)],
            'points': len(wavelengths)
        }
        
        data = {
            'wavelength_nm': wavelengths,
            'power_dBm': powers
        }
        
        df = pd.DataFrame(data)
        filename = f"{self.base_dir}/ring_{ring_id}_{self.timestamp}.csv"
        df.to_csv(filename, index=False)
        
        with open(f"{self.base_dir}/ring_{ring_id}_{self.timestamp}_meta.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Ring spectrum saved to {filename}")
        return df

# Example usage
if __name__ == "__main__":
    # Initialize logger
    logger = MeasurementLogger("TE_doping_study", "W001", "operator_name")
    
    # Example cut-back measurement
    lengths = [1000, 5000, 10000]
    powers = [-25.3, -32.1, -38.7]  # dBm
    logger.log_cutback_measurement(lengths, powers)
    
    # Example ring measurement
    wavelengths = np.linspace(1540, 1560, 2000)
    powers_ring = -30 + 5 * np.random.random(2000)  # Mock data
    logger.log_ring_spectrum(wavelengths, powers_ring)
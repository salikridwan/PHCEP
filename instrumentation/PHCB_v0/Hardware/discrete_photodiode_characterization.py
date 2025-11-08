import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import stats
import csv
from datetime import datetime

mpl.rcParams.update({
    'font.size': 8,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'figure.figsize': [5.5, 4.0],
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.6,
    'grid.linewidth': 0.4,
    'lines.linewidth': 1.0,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6
})

class DiscretePhotodiodeCharacterization:
    
    def __init__(self):
        self.test_conditions = {
            'photodiode_parameters': {
                'quantum_efficiency': 0.85,
            }
        }
        
        self.results = {}
        
    def quantum_efficiency_model(self, wavelength):
        wavelength = np.asarray(wavelength)
        scalar_input = False
        if wavelength.ndim == 0:
            scalar_input = True
        
        
        qe_peak = 0.85
        
        qe = qe_peak * np.exp(-((wavelength - lambda_peak) / sigma) ** 2)
        
        cutoff_mask = wavelength > lambda_cutoff
        if np.any(cutoff_mask):
            qe[cutoff_mask] = qe[cutoff_mask] * np.exp(-(wavelength[cutoff_mask] - lambda_cutoff) / 100)
        
        qe = np.clip(qe, 0, qe_peak)
        
        return qe[0] if scalar_input else qe
    
    def responsivity_calculation(self, wavelength):
        
        wavelength_m = wavelength * 1e-9
        quantum_efficiency = self.quantum_efficiency_model(wavelength)
        
        responsivity = (q * wavelength_m * quantum_efficiency) / (h * c)
        return responsivity
    
    def dark_current_model(self, voltage, temperature):
        V_bias = np.abs(voltage)
        T = temperature
        
        
        temp_factor = 2 ** ((T - T_ref) / 10)
        
        voltage_factor = 1 + 0.1 * np.minimum(V_bias, V_sat)
        
        I_dark = I_dark_base * temp_factor * voltage_factor
        
        return I_dark
    
    def photocurrent_calculation(self, optical_power, wavelength, voltage, temperature):
        R = self.responsivity_calculation(wavelength)
        I_photo_ideal = R * optical_power
        
        V_applied = np.abs(voltage)
        
        T_norm = temperature / 293
        
        I_photo = I_photo_ideal * collection_efficiency * temperature_factor
        
        return I_photo
    
    def total_current(self, optical_power, wavelength, voltage, temperature):
        I_photo = self.photocurrent_calculation(optical_power, wavelength, voltage, temperature)
        I_dark = self.dark_current_model(voltage, temperature)
        
        I_total = I_photo + I_dark
        
        return I_total
    
    def noise_analysis(self, optical_power, wavelength, voltage, temperature, bandwidth=1e6):
        I_total = self.total_current(optical_power, wavelength, voltage, temperature)
        I_dark = self.dark_current_model(voltage, temperature)
        
        q = 1.602e-19
        k = 1.38e-23
        R_shunt = self.test_conditions['photodiode_parameters']['shunt_resistance']
        
        i_shot_rms = np.sqrt(2 * q * (I_total + I_dark) * bandwidth)
        
        i_thermal_rms = np.sqrt(4 * k * temperature * bandwidth / R_shunt)
        
        i_total_rms = np.sqrt(i_shot_rms**2 + i_thermal_rms**2)
        
        snr = I_total / i_total_rms if i_total_rms > 0 else 0
        
        return {
            'shot_noise': i_shot_rms,
            'thermal_noise': i_thermal_rms,
            'total_noise': i_total_rms,
            'signal_to_noise': snr
        }
    
    def perform_characterization(self):
        print("Initiating discrete photodiode characterization protocol...")
        
        characterization_data = []
        
        
        for wavelength in self.test_conditions['wavelength_range']:
            responsivity = self.responsivity_calculation(wavelength)
            quantum_efficiency = self.quantum_efficiency_model(wavelength)
            photocurrent = self.photocurrent_calculation(optical_power_ref, wavelength, voltage_ref, temperature_ref)
            noise_data = self.noise_analysis(optical_power_ref, wavelength, voltage_ref, temperature_ref)
            
            characterization_data.append({
                'test_type': 'wavelength_sweep',
                'wavelength_nm': wavelength,
                'optical_power_W': optical_power_ref,
                'voltage_V': voltage_ref,
                'temperature_K': temperature_ref,
                'responsivity_A_W': responsivity,
                'quantum_efficiency': quantum_efficiency,
                'photocurrent_A': photocurrent,
                'dark_current_A': self.dark_current_model(voltage_ref, temperature_ref),
                'shot_noise_A': noise_data['shot_noise'],
                'thermal_noise_A': noise_data['thermal_noise'],
                'total_noise_A': noise_data['total_noise'],
                'signal_to_noise_ratio': noise_data['signal_to_noise']
            })
        
        for optical_power in self.test_conditions['optical_power_range']:
            responsivity = self.responsivity_calculation(wavelength_peak)
            photocurrent = self.photocurrent_calculation(optical_power, wavelength_peak, voltage_ref, temperature_ref)
            noise_data = self.noise_analysis(optical_power, wavelength_peak, voltage_ref, temperature_ref)
            
            characterization_data.append({
                'test_type': 'power_sweep',
                'wavelength_nm': wavelength_peak,
                'optical_power_W': optical_power,
                'voltage_V': voltage_ref,
                'temperature_K': temperature_ref,
                'responsivity_A_W': responsivity,
                'quantum_efficiency': self.quantum_efficiency_model(wavelength_peak),
                'photocurrent_A': photocurrent,
                'dark_current_A': self.dark_current_model(voltage_ref, temperature_ref),
                'shot_noise_A': noise_data['shot_noise'],
                'thermal_noise_A': noise_data['thermal_noise'],
                'total_noise_A': noise_data['total_noise'],
                'signal_to_noise_ratio': noise_data['signal_to_noise']
            })
        
        for voltage in self.test_conditions['reverse_bias_voltage']:
            photocurrent = self.photocurrent_calculation(optical_power_ref, wavelength_peak, voltage, temperature_ref)
            noise_data = self.noise_analysis(optical_power_ref, wavelength_peak, voltage, temperature_ref)
            
            characterization_data.append({
                'test_type': 'voltage_sweep',
                'wavelength_nm': wavelength_peak,
                'optical_power_W': optical_power_ref,
                'voltage_V': voltage,
                'temperature_K': temperature_ref,
                'responsivity_A_W': self.responsivity_calculation(wavelength_peak),
                'quantum_efficiency': self.quantum_efficiency_model(wavelength_peak),
                'photocurrent_A': photocurrent,
                'dark_current_A': self.dark_current_model(voltage, temperature_ref),
                'shot_noise_A': noise_data['shot_noise'],
                'thermal_noise_A': noise_data['thermal_noise'],
                'total_noise_A': noise_data['total_noise'],
                'signal_to_noise_ratio': noise_data['signal_to_noise']
            })
        
        self.results['characterization_data'] = characterization_data
        print("Characterization protocol completed successfully.")
        
        return characterization_data
    
    def save_results_to_csv(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photodiode_characterization_{timestamp}.csv"
        
        if not self.results:
            print("No characterization data available. Please run perform_characterization() first.")
            return
        
        df = pd.DataFrame(self.results['characterization_data'])
        
        metadata = [
        ]
        
        with open(filename, 'w', newline='') as csvfile:
            for line in metadata:
                csvfile.write(line + '\n')
            
            df.to_csv(csvfile, index=False)
        
        print(f"Characterization data saved to {filename}")
        return filename
    
    def generate_characterization_plots(self):
        if not self.results:
            print("No characterization data available. Please run perform_characterization() first.")
            return
        
        df = pd.DataFrame(self.results['characterization_data'])
        
        fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.5))
        fig.suptitle('Discrete Photodiode Characterization Analysis\nPHCEP Experimental Validation', 
                    fontsize=10, y=0.98)
        
        wavelength_data = df[df['test_type'] == 'wavelength_sweep']
        axes[0,0].plot(wavelength_data['wavelength_nm'], wavelength_data['responsivity_A_W'], 
                      'b-', linewidth=1.2)
        axes[0,0].set_xlabel('Wavelength (nm)')
        axes[0,0].set_ylabel('Responsivity (A/W)')
        axes[0,0].set_title('Spectral Responsivity', fontsize=9)
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].set_xlim(400, 1700)
        
        power_data = df[df['test_type'] == 'power_sweep']
        axes[0,1].loglog(power_data['optical_power_W'], np.abs(power_data['photocurrent_A']), 
                        'r-', linewidth=1.2)
        axes[0,1].set_xlabel('Optical Power (W)')
        axes[0,1].set_ylabel('Photocurrent (A)')
        axes[0,1].set_title('Power Transfer Characteristic', fontsize=9)
        axes[0,1].grid(True, alpha=0.3)
        
        voltage_data = df[df['test_type'] == 'voltage_sweep']
        axes[1,0].semilogy(voltage_data['voltage_V'], np.abs(voltage_data['dark_current_A']), 
                          'g-', linewidth=1.2, label='Dark Current')
        axes[1,0].semilogy(voltage_data['voltage_V'], np.abs(voltage_data['photocurrent_A']), 
                          'm-', linewidth=1.2, label='Photocurrent')
        axes[1,0].set_xlabel('Reverse Bias Voltage (V)')
        axes[1,0].set_ylabel('Current (A)')
        axes[1,0].set_title('Voltage Dependence', fontsize=9)
        axes[1,0].legend(fontsize=7)
        axes[1,0].grid(True, alpha=0.3)
        
        axes[1,1].semilogx(power_data['optical_power_W'], power_data['signal_to_noise_ratio'], 
                          'k-', linewidth=1.2)
        axes[1,1].set_xlabel('Optical Power (W)')
        axes[1,1].set_ylabel('Signal-to-Noise Ratio')
        axes[1,1].set_title('Detection Sensitivity', fontsize=9)
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('photodiode_characterization_plots.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        fig2, ax2 = plt.subplots(figsize=(5.0, 3.5))
        ax2.loglog(power_data['optical_power_W'], power_data['shot_noise_A'], 
                  'b-', linewidth=1.2, label='Shot Noise')
        ax2.loglog(power_data['optical_power_W'], power_data['thermal_noise_A'], 
                  'r-', linewidth=1.2, label='Thermal Noise')
        ax2.loglog(power_data['optical_power_W'], power_data['total_noise_A'], 
                  'k--', linewidth=1.5, label='Total Noise')
        ax2.set_xlabel('Optical Power (W)')
        ax2.set_ylabel('Noise Current (A/√Hz)')
        ax2.set_title('Noise Analysis vs Optical Power', fontsize=9)
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('photodiode_noise_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_summary_report(self):
        if not self.results:
            print("No characterization data available.")
            return
        
        df = pd.DataFrame(self.results['characterization_data'])
        
        print("\n" + "="*70)
        print("PHOTODIODE CHARACTERIZATION SUMMARY REPORT")
        print("PHCEP Experimental Validation Platform")
        print("="*70)
        
        wavelength_data = df[df['test_type'] == 'wavelength_sweep']
        peak_responsivity_idx = wavelength_data['responsivity_A_W'].idxmax()
        peak_responsivity = wavelength_data.loc[peak_responsivity_idx]
        
        power_data = df[df['test_type'] == 'power_sweep']
        voltage_data = df[df['test_type'] == 'voltage_sweep']
        
        print(f"\nKEY PERFORMANCE METRICS:")
        print(f"Peak Responsivity: {peak_responsivity['responsivity_A_W']:.3f} A/W at {peak_responsivity['wavelength_nm']:.0f} nm")
        print(f"Peak Quantum Efficiency: {peak_responsivity['quantum_efficiency']:.1%}")
        
        dark_current_5v = voltage_data[voltage_data['voltage_V'] == 5]['dark_current_A'].values[0]
        print(f"Dark Current (@5V, 293K): {dark_current_5v:.2e} A")
        
        dynamic_range = power_data['optical_power_W'].max() / power_data['optical_power_W'].min()
        print(f"Linear Dynamic Range: >{dynamic_range:.0e}")
        
        min_noise = power_data['total_noise_A'].min()
        avg_responsivity = power_data['responsivity_A_W'].mean()
        NEP = min_noise / avg_responsivity if avg_responsivity > 0 else float('inf')
        
        print(f"Noise Equivalent Power: {NEP:.2e} W/√Hz")
        
        max_snr = power_data['signal_to_noise_ratio'].max()
        print(f"Maximum SNR: {max_snr:.0f}")
        
        print(f"\nTEST CONDITIONS:")
        print(f"Wavelength Range: {self.test_conditions['wavelength_range'].min():.0f}-{self.test_conditions['wavelength_range'].max():.0f} nm")
        print(f"Optical Power Range: {self.test_conditions['optical_power_range'].min():.2e}-{self.test_conditions['optical_power_range'].max():.2e} W")
        print(f"Bias Voltage Range: {self.test_conditions['reverse_bias_voltage'].min()}-{self.test_conditions['reverse_bias_voltage'].max()} V")
        print(f"Temperature Range: {self.test_conditions['temperature_range'].min()}-{self.test_conditions['temperature_range'].max()} K")
        
        print(f"\nVALIDATION CHECKS:")
            print(f"✓ Dark current within realistic range")
        else:
            print(f"✗ Dark current unrealistically high")
            
            print(f"✓ SNR performance acceptable")
        else:
            print(f"✗ SNR performance below expectations")
            
            print(f"✓ Responsivity within expected range")
        else:
            print(f"✗ Responsivity unexpectedly low")
        
        print("\n" + "="*70)

def main():
    print("Initializing Discrete Photodiode Characterization...")
    print("PHCEP Experimental Validation Platform")
    print("-" * 50)
    
    characterization = DiscretePhotodiodeCharacterization()
    
    characterization.perform_characterization()
    
    csv_filename = characterization.save_results_to_csv()
    
    characterization.generate_characterization_plots()
    
    characterization.generate_summary_report()
    
    print(f"\nCharacterization protocol completed.")
    print(f"Data exported to: {csv_filename}")
    print(f"Visualizations saved as PNG files.")

if __name__ == "__main__":
    main()
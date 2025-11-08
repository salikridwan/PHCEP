import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import stats
from scipy import signal
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

class LaserDriverCharacterization:
    
    def __init__(self):
        self.test_conditions = {
            'laser_parameters': {
            },
            'driver_parameters': {
                'modulation_efficiency': 0.95,
            }
        }
        
        self.results = {}
        
    def laser_power_characteristic(self, bias_current, modulation_current, temperature):
        I_th = self.test_conditions['laser_parameters']['threshold_current']
        
        
        
        
        if I_total < I_th_temp:
            optical_power = 0
        else:
            optical_power = η_slope * (I_total - I_th_temp) * (1 - thermal_derating)
        
    
    def modulation_response(self, frequency, bias_current, modulation_current):
        f_3dB_nom = self.test_conditions['laser_parameters']['modulation_bandwidth']
        
        I_th = self.test_conditions['laser_parameters']['threshold_current']
        if bias_current > I_th:
            bandwidth_enhancement = np.sqrt((bias_current - I_th) / I_th)
        else:
            bandwidth_enhancement = 0.1
        
        
        normalized_freq = frequency / f_3dB
        response = 1 / np.sqrt((1 - normalized_freq**2)**2 + (2*damping_factor*normalized_freq)**2)
        
        return response
    
    def rise_fall_time_calculation(self, bias_current, modulation_current):
        f_3dB_nom = self.test_conditions['laser_parameters']['modulation_bandwidth']
        I_th = self.test_conditions['laser_parameters']['threshold_current']
        
        if bias_current > I_th:
            f_3dB = f_3dB_nom * np.sqrt((bias_current - I_th) / I_th)
        else:
            f_3dB = f_3dB_nom * 0.1
        
        
        rise_time = 0.35 / f_3dB
        
        fall_time = rise_time * 1.1
        
        return rise_time, fall_time
    
    def relative_intensity_noise(self, frequency, bias_current, optical_power):
        f_3dB = self.test_conditions['laser_parameters']['modulation_bandwidth']
        
        frequency = np.asarray(frequency)
        scalar_input = frequency.ndim == 0
        if scalar_input:
            frequency = frequency[None]
        
        
        hf_noise = 1e-13 * np.ones_like(frequency)
        
        I_th = self.test_conditions['laser_parameters']['threshold_current']
        if bias_current > I_th:
            f_ro = f_3dB * np.sqrt((bias_current - I_th) / I_th)
        else:
            f_ro = f_3dB * 0.1
            
        resonance_peak = 1e-11 * np.exp(-((frequency - f_ro) / (f_ro * 0.3))**2)
        
        total_rin = lf_noise + hf_noise + resonance_peak
        
        rin_dB = 10 * np.log10(total_rin)
        
        return rin_dB[0] if scalar_input else rin_dB
    
    def power_consumption(self, bias_current, modulation_current, supply_voltage):
        
        if I_total > 0:
        else:
        
        laser_power = V_laser * I_total
        
        if driver_efficiency > 0:
            driver_loss = laser_power * (1 - driver_efficiency) / driver_efficiency
        else:
            driver_loss = 0
            
        total_power = laser_power + driver_loss
        
        return total_power, driver_efficiency
    
    def perform_characterization(self):
        print("Initiating laser driver characterization protocol...")
        
        characterization_data = []
        
        for bias_current in self.test_conditions['bias_current_range']:
            optical_power = self.laser_power_characteristic(bias_current, 0, temperature_ref)
            total_power, efficiency = self.power_consumption(bias_current, 0, 3.3)
            
            characterization_data.append({
                'test_type': 'dc_characterization',
                'bias_current_mA': bias_current,
                'modulation_current_mA': 0,
                'frequency_Hz': 0,
                'temperature_K': temperature_ref,
                'supply_voltage_V': 3.3,
                'modulation_response_dB': 0,
                'rise_time_ps': 0,
                'fall_time_ps': 0,
                'rin_dB_Hz': 0,
                'total_power_W': total_power,
                'driver_efficiency': efficiency,
                'threshold_exceedance': bias_current - self.test_conditions['laser_parameters']['threshold_current']
            })
        
        for mod_current in self.test_conditions['modulation_current_range']:
            optical_power_avg = self.laser_power_characteristic(bias_ref, mod_current, temperature_ref)
            mod_response = self.modulation_response(frequency_ref, bias_ref, mod_current)
            rise_time, fall_time = self.rise_fall_time_calculation(bias_ref, mod_current)
            total_power, efficiency = self.power_consumption(bias_ref, mod_current, 3.3)
            
            characterization_data.append({
                'test_type': 'modulation_characterization',
                'bias_current_mA': bias_ref,
                'modulation_current_mA': mod_current,
                'frequency_Hz': frequency_ref,
                'temperature_K': temperature_ref,
                'supply_voltage_V': 3.3,
                'optical_power_mW': optical_power_avg,
                'modulation_response_dB': 20 * np.log10(mod_response),
                'rise_time_ps': rise_time * 1e12,
                'fall_time_ps': fall_time * 1e12,
                'rin_dB_Hz': 0,
                'total_power_W': total_power,
                'driver_efficiency': efficiency,
                'threshold_exceedance': bias_ref - self.test_conditions['laser_parameters']['threshold_current']
            })
        
        for frequency in self.test_conditions['frequency_range']:
            mod_response = self.modulation_response(frequency, bias_ref, mod_ref)
            rin_dB = self.relative_intensity_noise(np.array([frequency]), bias_ref, 
                                                 self.laser_power_characteristic(bias_ref, mod_ref, temperature_ref))
            total_power, efficiency = self.power_consumption(bias_ref, mod_ref, 3.3)
            
            characterization_data.append({
                'test_type': 'frequency_response',
                'bias_current_mA': bias_ref,
                'modulation_current_mA': mod_ref,
                'frequency_Hz': frequency,
                'temperature_K': temperature_ref,
                'supply_voltage_V': 3.3,
                'optical_power_mW': self.laser_power_characteristic(bias_ref, mod_ref, temperature_ref),
                'modulation_response_dB': 20 * np.log10(mod_response),
                'rise_time_ps': 0,
                'fall_time_ps': 0,
                'rin_dB_Hz': rin_dB[0],
                'total_power_W': total_power,
                'driver_efficiency': efficiency,
                'threshold_exceedance': bias_ref - self.test_conditions['laser_parameters']['threshold_current']
            })
        
        for temperature in self.test_conditions['temperature_range']:
            optical_power = self.laser_power_characteristic(bias_ref, mod_ref, temperature)
            total_power, efficiency = self.power_consumption(bias_ref, mod_ref, 3.3)
            
            characterization_data.append({
                'test_type': 'temperature_dependence',
                'bias_current_mA': bias_ref,
                'modulation_current_mA': mod_ref,
                'frequency_Hz': frequency_ref,
                'temperature_K': temperature,
                'supply_voltage_V': 3.3,
                'optical_power_mW': optical_power,
                'modulation_response_dB': 20 * np.log10(self.modulation_response(frequency_ref, bias_ref, mod_ref)),
                'rise_time_ps': 0,
                'fall_time_ps': 0,
                'rin_dB_Hz': 0,
                'total_power_W': total_power,
                'driver_efficiency': efficiency,
                'threshold_exceedance': bias_ref - self.test_conditions['laser_parameters']['threshold_current']
            })
        
        self.results['characterization_data'] = characterization_data
        print("Laser driver characterization protocol completed successfully.")
        
        return characterization_data
    
    def save_results_to_csv(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"laser_driver_characterization_{timestamp}.csv"
        
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
        fig.suptitle('Laser Driver Characterization Analysis\nPHCEP Experimental Validation', 
                    fontsize=10, y=0.98)
        
        dc_data = df[df['test_type'] == 'dc_characterization']
        axes[0,0].plot(dc_data['bias_current_mA'], dc_data['optical_power_mW'], 
                      'b-', linewidth=1.2, label='Optical Power')
        axes[0,0].axvline(x=self.test_conditions['laser_parameters']['threshold_current'], 
                         color='r', linestyle='--', linewidth=1.0, label='Threshold Current')
        axes[0,0].set_xlabel('Bias Current (mA)')
        axes[0,0].set_ylabel('Optical Power (mW)')
        axes[0,0].set_title('L-I Characteristic', fontsize=9)
        axes[0,0].legend(fontsize=7)
        axes[0,0].grid(True, alpha=0.3)
        
        freq_data = df[df['test_type'] == 'frequency_response']
        axes[0,1].semilogx(freq_data['frequency_Hz'], freq_data['modulation_response_dB'], 
                          'r-', linewidth=1.2)
        axes[0,1].axhline(y=-3, color='k', linestyle='--', linewidth=1.0, label='-3 dB')
        axes[0,1].set_xlabel('Frequency (Hz)')
        axes[0,1].set_ylabel('Modulation Response (dB)')
        axes[0,1].set_title('Frequency Response', fontsize=9)
        axes[0,1].legend(fontsize=7)
        axes[0,1].grid(True, alpha=0.3)
        
        mod_data = df[df['test_type'] == 'modulation_characterization']
        axes[1,0].plot(mod_data['optical_power_mW'], mod_data['total_power_W'] * 1000, 
                      'g-', linewidth=1.2, label='Total Power')
        axes[1,0].set_xlabel('Optical Power (mW)')
        axes[1,0].set_ylabel('Total Power (mW)')
        axes[1,0].set_title('Power Consumption', fontsize=9)
        axes[1,0].grid(True, alpha=0.3)
        
        axes[1,1].semilogx(freq_data['frequency_Hz'], freq_data['rin_dB_Hz'], 
                          'm-', linewidth=1.2)
        axes[1,1].set_xlabel('Frequency (Hz)')
        axes[1,1].set_ylabel('RIN (dB/Hz)')
        axes[1,1].set_title('Relative Intensity Noise', fontsize=9)
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].set_ylim(-170, -130)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('laser_driver_characterization_plots.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        temp_data = df[df['test_type'] == 'temperature_dependence']
        fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0))
        
        ax1.plot(temp_data['temperature_K'] - 273, temp_data['optical_power_mW'], 
                'b-', linewidth=1.2)
        ax1.set_xlabel('Temperature (°C)')
        ax1.set_ylabel('Optical Power (mW)')
        ax1.set_title('Temperature Dependence', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(temp_data['temperature_K'] - 273, temp_data['driver_efficiency'] * 100, 
                'r-', linewidth=1.2)
        ax2.set_xlabel('Temperature (°C)')
        ax2.set_ylabel('Driver Efficiency (%)')
        ax2.set_title('Efficiency vs Temperature', fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('laser_driver_temperature_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0))
        
        ax1.plot(mod_data['modulation_current_mA'], mod_data['rise_time_ps'], 
                'g-', linewidth=1.2, label='Rise Time')
        ax1.plot(mod_data['modulation_current_mA'], mod_data['fall_time_ps'], 
                'm-', linewidth=1.2, label='Fall Time')
        ax1.set_xlabel('Modulation Current (mA)')
        ax1.set_ylabel('Time (ps)')
        ax1.set_title('Switching Performance', fontsize=9)
        ax1.legend(fontsize=7)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(mod_data['modulation_current_mA'], mod_data['optical_power_mW'], 
                'b-', linewidth=1.2)
        ax2.set_xlabel('Modulation Current (mA)')
        ax2.set_ylabel('Optical Power (mW)')
        ax2.set_title('Power vs Modulation', fontsize=9)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('laser_driver_modulation_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_summary_report(self):
        if not self.results:
            print("No characterization data available.")
            return
        
        df = pd.DataFrame(self.results['characterization_data'])
        
        print("\n" + "="*70)
        print("LASER DRIVER CHARACTERIZATION SUMMARY REPORT")
        print("PHCEP Experimental Validation Platform")
        print("="*70)
        
        dc_data = df[df['test_type'] == 'dc_characterization']
        freq_data = df[df['test_type'] == 'frequency_response']
        mod_data = df[df['test_type'] == 'modulation_characterization']
        temp_data = df[df['test_type'] == 'temperature_dependence']
        
        bandwidth_mask = freq_data['modulation_response_dB'] >= -3
        if bandwidth_mask.any():
            bandwidth_3dB = freq_data[bandwidth_mask]['frequency_Hz'].max()
        else:
            bandwidth_3dB = 0
        
        avg_rise_time = mod_data['rise_time_ps'].mean()
        avg_fall_time = mod_data['fall_time_ps'].mean()
        
        max_optical_power = dc_data['optical_power_mW'].max()
        max_efficiency = dc_data['driver_efficiency'].max() * 100
        
        print(f"\nKEY PERFORMANCE METRICS:")
        print(f"Threshold Current: {self.test_conditions['laser_parameters']['threshold_current']:.1f} mA")
        print(f"Maximum Optical Power: {max_optical_power:.1f} mW")
        print(f"Modulation Bandwidth (-3dB): {bandwidth_3dB/1e9:.1f} GHz")
        print(f"Average Rise Time: {avg_rise_time:.1f} ps")
        print(f"Average Fall Time: {avg_fall_time:.1f} ps")
        print(f"Peak Driver Efficiency: {max_efficiency:.1f}%")
        print(f"RIN Performance: {freq_data['rin_dB_Hz'].mean():.1f} dB/Hz")
        
        print(f"\nTEST CONDITIONS:")
        print(f"Bias Current Range: {self.test_conditions['bias_current_range'].min():.0f}-{self.test_conditions['bias_current_range'].max():.0f} mA")
        print(f"Modulation Current Range: {self.test_conditions['modulation_current_range'].min():.0f}-{self.test_conditions['modulation_current_range'].max():.0f} mA")
        print(f"Frequency Range: {self.test_conditions['frequency_range'].min()/1e6:.0f} MHz - {self.test_conditions['frequency_range'].max()/1e9:.0f} GHz")
        print(f"Temperature Range: {self.test_conditions['temperature_range'].min()-273:.0f}-{self.test_conditions['temperature_range'].max()-273:.0f} °C")
        
        print(f"\nVALIDATION CHECKS:")
            print(f"✓ Modulation bandwidth suitable for high-speed operation")
        else:
            print(f"✗ Modulation bandwidth may limit high-speed performance")
            
            print(f"✓ Switching speed adequate for photonic computing")
        else:
            print(f"✗ Switching speed may limit computational throughput")
            
            print(f"✓ Driver efficiency within acceptable range")
        else:
            print(f"✗ Driver efficiency lower than optimal")
            
            print(f"✓ Optical power sufficient for photonic circuits")
        else:
            print(f"✗ Optical power may be marginal for some applications")
        
        print("\n" + "="*70)

def main():
    print("Initializing Laser Driver Characterization...")
    print("PHCEP Experimental Validation Platform")
    print("-" * 50)
    
    characterization = LaserDriverCharacterization()
    
    characterization.perform_characterization()
    
    csv_filename = characterization.save_results_to_csv()
    
    characterization.generate_characterization_plots()
    
    characterization.generate_summary_report()
    
    print(f"\nCharacterization protocol completed.")
    print(f"Data exported to: {csv_filename}")
    print(f"Visualizations saved as PNG files.")

if __name__ == "__main__":
    main()
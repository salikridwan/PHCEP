#!/usr/bin/env python3
"""
Ring Resonator Q-Factor Analysis
Lorentzian fitting for precise Q-factor and FSR extraction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
import argparse
import warnings
warnings.filterwarnings('ignore')

class RingResonanceAnalyzer:
    def __init__(self):
        self.results = {}
    
    def load_ring_data(self, csv_file):
        """Load ring resonator spectral data"""
        df = pd.read_csv(csv_file)
        
        if 'wavelength_nm' not in df.columns or 'power_dBm' not in df.columns:
            raise ValueError("CSV must contain 'wavelength_nm' and 'power_dBm' columns")
        
        return df
    
    def lorentzian(self, x, A, x0, gamma, offset):
        """Lorentzian function for resonance fitting"""
        return offset + A * (gamma**2) / ((x - x0)**2 + gamma**2)
    
    def find_resonances(self, wavelengths, powers, min_depth=3, min_separation=0.1):
        """Automatically find resonance dips in transmission spectrum"""
        # Smooth data to reduce noise
        smoothed = savgol_filter(powers, 11, 3)
        
        # Find dips (resonances are power minima)
        dips, properties = find_peaks(-smoothed, height=min_depth, 
                                     distance=min_separation/0.001)
        
        return dips, properties
    
    def fit_single_resonance(self, wavelengths, powers, resonance_idx, window=1.0):
        """Fit Lorentzian to a single resonance"""
        center_wl = wavelengths[resonance_idx]
        
        # Extract region around resonance
        mask = (wavelengths >= center_wl - window) & (wavelengths <= center_wl + window)
        wl_region = wavelengths[mask]
        power_region_linear = 10**(np.array(powers[mask])/10)  # Convert to linear scale
        
        if len(wl_region) < 10:
            return None
        
        # Initial parameter guesses
        A_guess = (np.max(power_region_linear) - np.min(power_region_linear)) * 0.1
        x0_guess = center_wl
        gamma_guess = 0.05  # nm
        offset_guess = np.min(power_region_linear)
        
        try:
            popt, pcov = curve_fit(self.lorentzian, wl_region, power_region_linear,
                                 p0=[A_guess, x0_guess, gamma_guess, offset_guess],
                                 maxfev=5000)
            
            # Calculate Q-factor and other parameters
            resonance_wl = popt[1]
            fwhm = 2 * popt[2]  # Full width at half maximum
            Q = resonance_wl / fwhm
            
            # Calculate extinction ratio
            transmission_min = np.min(power_region_linear)
            transmission_max = np.max(power_region_linear)
            extinction_ratio = -10 * np.log10(transmission_min/transmission_max)
            
            return {
                'resonance_wavelength': resonance_wl,
                'fwhm_nm': fwhm,
                'fwhm_pm': fwhm * 1000,
                'Q_factor': Q,
                'extinction_ratio_dB': extinction_ratio,
                'fit_parameters': popt.tolist(),
                'fit_region': [wl_region.min(), wl_region.max()]
            }
        except Exception as e:
            print(f"Fit failed for resonance at {center_wl:.3f} nm: {e}")
            return None
    
    def calculate_fsr(self, resonance_wavelengths):
        """Calculate Free Spectral Range from resonance spacing"""
        if len(resonance_wavelengths) < 2:
            return None, None
        
        sorted_wl = sorted(resonance_wavelengths)
        fsr_values = np.diff(sorted_wl)
        
        avg_fsr = np.mean(fsr_values)
        std_fsr = np.std(fsr_values)
        
        return avg_fsr, std_fsr
    
    def calculate_effective_index(self, fsr, radius=10):
        """Calculate effective index from FSR and ring radius"""
        # FSR = λ² / (n_g * L) where L = 2πR
        circumference = 2 * np.pi * radius  # µm
        n_g = (1550**2) / (fsr * circumference * 1e-3)  # Group index
        
        # Approximate effective index (n_eff ≈ n_g for small dispersion)
        n_eff = n_g
        
        return n_eff, n_g
    
    def analyze_ring_spectrum(self, csv_file, ring_radius=10):
        """Complete ring resonator analysis"""
        print(f"Analyzing ring resonator data: {csv_file}")
        
        # Load data
        df = self.load_ring_data(csv_file)
        wavelengths = df['wavelength_nm'].values
        powers = df['power_dBm'].values
        
        print(f"Loaded {len(df)} spectral points")
        
        # Find resonances
        resonance_indices, properties = self.find_resonances(wavelengths, powers)
        print(f"Found {len(resonance_indices)} resonances")
        
        # Fit each resonance
        resonance_results = []
        valid_resonances = []
        
        for i, idx in enumerate(resonance_indices):
            result = self.fit_single_resonance(wavelengths, powers, idx)
            if result:
                resonance_results.append(result)
                valid_resonances.append(result['resonance_wavelength'])
                print(f"Resonance {i+1}: λ={result['resonance_wavelength']:.3f} nm, "
                      f"Q={result['Q_factor']:.0f}, ER={result['extinction_ratio_dB']:.1f} dB")
        
        # Calculate FSR and effective index
        if len(valid_resonances) >= 2:
            avg_fsr, std_fsr = self.calculate_fsr(valid_resonances)
            n_eff, n_g = self.calculate_effective_index(avg_fsr, ring_radius)
            
            print(f"\nFree Spectral Range: {avg_fsr:.2f} ± {std_fsr:.2f} nm")
            print(f"Effective index: {n_eff:.3f}")
            print(f"Group index: {n_g:.3f}")
        else:
            avg_fsr = std_fsr = n_eff = n_g = None
            print("Insufficient resonances for FSR calculation")
        
        # Compile results
        results = {
            'ring_radius_um': ring_radius,
            'resonances_found': len(resonance_indices),
            'resonances_fitted': len(resonance_results),
            'resonance_results': resonance_results,
            'fsr_nm': avg_fsr,
            'fsr_std_nm': std_fsr,
            'effective_index': n_eff,
            'group_index': n_g,
            'wavelength_range': [wavelengths.min(), wavelengths.max()]
        }
        
        # Create visualization
        self.plot_ring_analysis(wavelengths, powers, resonance_results, results, csv_file)
        
        # Save results
        results_file = csv_file.replace('.csv', '_results.json')
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")
        
        return results
    
    def plot_ring_analysis(self, wavelengths, powers, resonance_results, results, csv_file):
        """Create comprehensive ring resonator analysis plot"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Full spectrum with identified resonances
        ax1.plot(wavelengths, powers, 'b-', alpha=0.7, linewidth=1, label='Raw data')
        ax1.set_xlabel('Wavelength (nm)')
        ax1.set_ylabel('Transmission (dBm)')
        ax1.set_title('Ring Resonator Transmission Spectrum')
        ax1.grid(True, alpha=0.3)
        
        # Mark resonances
        resonance_wls = [r['resonance_wavelength'] for r in resonance_results]
        resonance_powers = [np.interp(wl, wavelengths, powers) for wl in resonance_wls]
        ax1.plot(resonance_wls, resonance_powers, 'ro', markersize=6, label='Resonances')
        ax1.legend()
        
        # Plot 2: Individual resonance fits
        for i, result in enumerate(resonance_results):
            wl_fit = np.linspace(result['fit_region'][0], result['fit_region'][1], 100)
            power_fit_linear = self.lorentzian(wl_fit, *result['fit_parameters'])
            power_fit_dB = 10 * np.log10(power_fit_linear)
            
            # Extract original data in fit region
            mask = (wavelengths >= result['fit_region'][0]) & (wavelengths <= result['fit_region'][1])
            wl_region = wavelengths[mask]
            power_region = powers[mask]
            
            ax2.plot(wl_region, power_region, 'o', markersize=4, label=f'Res {i+1} data')
            ax2.plot(wl_fit, power_fit_dB, '-', linewidth=2, label=f'Res {i+1} fit (Q={result["Q_factor"]:.0f})')
        
        ax2.set_xlabel('Wavelength (nm)')
        ax2.set_ylabel('Transmission (dBm)')
        ax2.set_title('Lorentzian Fits to Resonances')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Q-factor distribution
        if resonance_results:
            q_factors = [r['Q_factor'] for r in resonance_results]
            ax3.hist(q_factors, bins=min(10, len(q_factors)), alpha=0.7, edgecolor='black')
            ax3.axvline(np.mean(q_factors), color='r', linestyle='--', label=f'Mean Q: {np.mean(q_factors):.0f}')
            ax3.set_xlabel('Q-factor')
            ax3.set_ylabel('Count')
            ax3.set_title('Q-factor Distribution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Summary statistics
        ax4.axis('off')
        if resonance_results:
            textstr = '\n'.join([
                f'Resonances found: {results["resonances_fitted"]}',
                f'Mean Q-factor: {np.mean([r["Q_factor"] for r in resonance_results]):.0f}',
                f'Mean ER: {np.mean([r["extinction_ratio_dB"] for r in resonance_results]):.1f} dB',
                f'FSR: {results["fsr_nm"]:.2f} nm' if results["fsr_nm"] else 'FSR: N/A',
                f'n_eff: {results["effective_index"]:.3f}' if results["effective_index"] else 'n_eff: N/A'
            ])
            ax4.text(0.1, 0.9, textstr, transform=ax4.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plot_file = csv_file.replace('.csv', '_analysis.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Analysis plot saved to {plot_file}")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Ring resonator Q-factor analysis')
    parser.add_argument('csv_file', help='Ring resonator spectral data CSV')
    parser.add_argument('--radius', type=float, default=10, help='Ring radius in microns')
    
    args = parser.parse_args()
    
    analyzer = RingResonanceAnalyzer()
    analyzer.analyze_ring_spectrum(args.csv_file, args.radius)

if __name__ == "__main__":
    main()
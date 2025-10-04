#!/usr/bin/env python3
"""
Ring Resonance Analysis Script
Lorentzian fitting for precise Q-factor extraction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

class RingResonanceAnalyzer:
    def __init__(self, wavelength_nm, power_dBm):
        self.wavelength_nm = np.array(wavelength_nm)
        self.power_dBm = np.array(power_dBm)
        self.power_linear = 10**(np.array(power_dBm)/10)  # Convert to mW
        
    def lorentzian(self, x, A, x0, gamma, offset):
        """Lorentzian function for resonance fitting"""
        return offset + A * (gamma**2) / ((x - x0)**2 + gamma**2)
    
    def find_resonances(self, min_depth=3, min_separation=0.5):
        """Automatically find resonance dips"""
        # Smooth data to reduce noise
        from scipy.signal import savgol_filter
        smoothed = savgol_filter(self.power_dBm, 11, 3)
        
        # Find dips (resonances)
        from scipy.signal import find_peaks
        dips, _ = find_peaks(-smoothed, height=min_depth, distance=min_separation/0.001)
        
        return dips
    
    def fit_resonance(self, resonance_idx, window=1.0):
        """Fit Lorentzian to a single resonance"""
        # Extract region around resonance
        center_wl = self.wavelength_nm[resonance_idx]
        mask = (self.wavelength_nm >= center_wl - window) & (self.wavelength_nm <= center_wl + window)
        
        if np.sum(mask) < 10:
            return None
            
        wl_region = self.wavelength_nm[mask]
        power_region = self.power_linear[mask]
        
        # Initial guess
        A_guess = (np.max(power_region) - np.min(power_region)) * 0.1
        x0_guess = center_wl
        gamma_guess = 0.05  # nm
        offset_guess = np.min(power_region)
        
        try:
            popt, pcov = curve_fit(self.lorentzian, wl_region, power_region, 
                                 p0=[A_guess, x0_guess, gamma_guess, offset_guess],
                                 maxfev=5000)
            
            # Calculate Q-factor
            resonance_wl = popt[1]
            fwhm = 2 * popt[2]  # Full width at half maximum
            Q = resonance_wl / fwhm
            
            return {
                'resonance_wavelength': resonance_wl,
                'fwhm': fwhm,
                'Q_factor': Q,
                'depth_dB': -10 * np.log10((popt[3] + popt[0])/popt[3]),
                'fit_parameters': popt,
                'covariance': pcov
            }
        except:
            return None
    
    def analyze_all_resonances(self):
        """Complete resonance analysis"""
        resonance_indices = self.find_resonances()
        results = []
        
        print("=== RING RESONANCE ANALYSIS ===")
        print(f"Found {len(resonance_indices)} resonances")
        print("\nResonance | Wavelength (nm) | FWHM (pm) | Q-factor | Depth (dB)")
        print("-" * 65)
        
        for i, idx in enumerate(resonance_indices):
            result = self.fit_resonance(idx)
            if result:
                results.append(result)
                print(f"{i+1:9} | {result['resonance_wavelength']:14.3f} | {result['fwhm']*1000:9.1f} | {result['Q_factor']:8.0f} | {result['depth_dB']:10.2f}")
        
        # Calculate FSR from resonance spacing
        if len(results) > 1:
            wavelengths = [r['resonance_wavelength'] for r in results]
            fsr_values = np.diff(sorted(wavelengths))
            avg_fsr = np.mean(fsr_values)
            print(f"\nAverage FSR: {avg_fsr:.2f} nm")
            
            # Calculate effective index
            ring_radius = 10  # µm - UPDATE WITH ACTUAL VALUE
            n_eff = (avg_fsr * 2 * np.pi * ring_radius) / (1550**2 * 1e-3)
            print(f"Effective index: {n_eff:.3f}")
        
        return results
    
    def plot_resonances(self, results):
        """Plot raw data and fitted resonances"""
        plt.figure(figsize=(12, 8))
        
        # Plot raw data
        plt.subplot(2, 1, 1)
        plt.plot(self.wavelength_nm, self.power_dBm, 'b-', alpha=0.7, label='Raw data')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Power (dBm)')
        plt.title('Ring Resonator Transmission Spectrum')
        plt.grid(True, alpha=0.3)
        
        # Mark identified resonances
        resonance_indices = self.find_resonances()
        plt.plot(self.wavelength_nm[resonance_indices], self.power_dBm[resonance_indices], 
                'ro', markersize=8, label='Identified resonances')
        plt.legend()
        
        # Plot fitted Lorentzians
        plt.subplot(2, 1, 2)
        plt.plot(self.wavelength_nm, self.power_linear, 'b-', alpha=0.5, label='Raw data')
        
        for i, result in enumerate(results):
            wl_fit = np.linspace(result['resonance_wavelength'] - 1, 
                               result['resonance_wavelength'] + 1, 100)
            power_fit = self.lorentzian(wl_fit, *result['fit_parameters'])
            plt.plot(wl_fit, power_fit, 'r-', linewidth=2, 
                    label=f'Resonance {i+1} (Q={result["Q_factor"]:.0f})')
        
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Power (mW)')
        plt.title('Lorentzian Fits')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ring_resonance_analysis.png', dpi=300)
        plt.show()

# Usage example
def analyze_ring_data(csv_file):
    """Load CSV and analyze ring resonances"""
    df = pd.read_csv(csv_file)
    analyzer = RingResonanceAnalyzer(df['wavelength_nm'], df['power_dBm'])
    results = analyzer.analyze_all_resonances()
    analyzer.plot_resonances(results)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('ring_analysis_results.csv', index=False)
    print(f"\nResults saved to ring_analysis_results.csv")

if __name__ == "__main__":
    # Example usage
    print("Ring Resonance Analyzer - Ready")
    print("Usage: analyze_ring_data('your_ring_data.csv')")
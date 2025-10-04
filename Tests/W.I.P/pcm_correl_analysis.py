#!/usr/bin/env python3
"""
PCM Correlation Analysis
Links process control monitor measurements to optical results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import glob
import os
from scipy import stats

class PCMCorrelator:
    def __init__(self, data_directory="data/fab_test"):
        self.data_dir = data_directory
        self.results = {}
    
    def load_pcm_data(self):
        """Load PCM measurement data (SIMS, SEM, AFM, etc.)"""
        pcm_files = glob.glob(os.path.join(self.data_dir, "**", "*pcm*.csv"), recursive=True)
        pcm_files += glob.glob(os.path.join(self.data_dir, "**", "*pcm*.json"), recursive=True)
        
        pcm_data = {}
        
        for file in pcm_files:
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                    pcm_data[os.path.basename(file)] = df
                elif file.endswith('.json'):
                    with open(file, 'r') as f:
                        data = json.load(f)
                    pcm_data[os.path.basename(file)] = data
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        return pcm_data
    
    def load_optical_results(self):
        """Load optical measurement results"""
        optical_files = glob.glob(os.path.join(self.data_dir, "**", "*results.json"), recursive=True)
        
        optical_data = {}
        
        for file in optical_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                # Extract key parameters
                if 'cutback' in file.lower():
                    optical_data[os.path.basename(file)] = {
                        'type': 'cutback',
                        'propagation_loss': data.get('propagation_loss_dB_cm'),
                        'r_squared': data.get('r_squared')
                    }
                elif 'ring' in file.lower():
                    optical_data[os.path.basename(file)] = {
                        'type': 'ring',
                        'q_factor': data.get('resonance_results', [{}])[0].get('Q_factor') if data.get('resonance_results') else None,
                        'effective_index': data.get('effective_index')
                    }
                elif 'taper' in file.lower():
                    optical_data[os.path.basename(file)] = {
                        'type': 'taper',
                        'insertion_loss': data.get('mean_insertion_loss')
                    }
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        return optical_data
    
    def correlate_doping_vs_loss(self, pcm_data, optical_data):
        """Correlate TE doping concentration with optical loss"""
        doping_results = []
        loss_results = []
        
        # Extract doping concentrations and corresponding losses
        for pcm_file, pcm_info in pcm_data.items():
            if 'doping' in pcm_file.lower() or 'te' in pcm_file.lower():
                # Look for corresponding optical measurement
                for optical_file, optical_info in optical_data.items():
                    if optical_info['type'] == 'cutback':
                        # Simple filename matching (could be improved)
                        if any(substr in optical_file for substr in ['1E18', '5E18', '1E19', '5E19']):
                            # Extract doping concentration from filename or data
                            doping_conc = self._extract_doping_concentration(pcm_file, pcm_info)
                            if doping_conc and optical_info['propagation_loss']:
                                doping_results.append(doping_conc)
                                loss_results.append(optical_info['propagation_loss'])
        
        return doping_results, loss_results
    
    def _extract_doping_concentration(self, filename, data):
        """Extract doping concentration from PCM data"""
        # Try to extract from filename first
        import re
        match = re.search(r'(\d+\.?\d*)[Ee](\d+)', filename)
        if match:
            mantissa = float(match.group(1))
            exponent = int(match.group(2))
            return mantissa * (10 ** exponent)
        
        # Try to extract from data structure
        if isinstance(data, dict):
            if 'doping_concentration' in data:
                return data['doping_concentration']
        
        return None
    
    def analyze_correlations(self):
        """Perform comprehensive PCM-optical correlation analysis"""
        print("Loading PCM and optical data...")
        
        pcm_data = self.load_pcm_data()
        optical_data = self.load_optical_results()
        
        print(f"Loaded {len(pcm_data)} PCM datasets")
        print(f"Loaded {len(optical_data)} optical results")
        
        # Doping vs propagation loss correlation
        doping_conc, propagation_loss = self.correlate_doping_vs_loss(pcm_data, optical_data)
        
        if len(doping_conc) >= 2:
            correlation = stats.pearsonr(np.log10(doping_conc), propagation_loss)
            print(f"\nDoping vs Propagation Loss Correlation:")
            print(f"  Samples: {len(doping_conc)}")
            print(f"  Pearson r: {correlation[0]:.3f}")
            print(f"  p-value: {correlation[1]:.3f}")
            
            # Create correlation plot
            self.plot_doping_loss_correlation(doping_conc, propagation_loss, correlation)
        
        # Additional correlations can be added here
        # - Etch depth vs confinement
        # - Roughness vs scattering loss
        # - Width variation vs mode properties
        
        return {
            'doping_concentrations': doping_conc,
            'propagation_losses': propagation_loss,
            'correlation_coefficient': correlation[0] if len(doping_conc) >= 2 else None
        }
    
    def plot_doping_loss_correlation(self, doping_conc, propagation_loss, correlation):
        """Plot doping concentration vs propagation loss"""
        plt.figure(figsize=(10, 6))
        
        plt.semilogx(doping_conc, propagation_loss, 'bo-', linewidth=2, markersize=8)
        plt.xlabel('TE Doping Concentration (atoms/cm³)')
        plt.ylabel('Propagation Loss (dB/cm)')
        plt.title('TE Doping Concentration vs Propagation Loss')
        plt.grid(True, alpha=0.3)
        
        # Add correlation info
        plt.text(0.05, 0.95, f'Pearson r = {correlation[0]:.3f}\np-value = {correlation[1]:.3f}',
                transform=plt.gca().transAxes, fontsize=12,
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
        
        # Add trendline if significant
        if correlation[1] < 0.05:
            z = np.polyfit(np.log10(doping_conc), propagation_loss, 1)
            p = np.poly1d(z)
            x_fit = np.logspace(np.log10(min(doping_conc)), np.log10(max(doping_conc)), 100)
            y_fit = p(np.log10(x_fit))
            plt.semilogx(x_fit, y_fit, 'r--', linewidth=2, label='Trendline')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig('pcm_correlation_analysis.png', dpi=300, bbox_inches='tight')
        print("Correlation plot saved to pcm_correlation_analysis.png")
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='PCM-optical correlation analysis')
    parser.add_argument('--data-dir', default='data/fab_test', help='Data directory path')
    
    args = parser.parse_args()
    
    correlator = PCMCorrelator(args.data_dir)
    results = correlator.analyze_correlations()
    
    print(f"\n=== PCM CORRELATION ANALYSIS COMPLETE ===")
    print(f"Analyzed {len(results['doping_concentrations'])} doping-loss pairs")

if __name__ == "__main__":
    main()
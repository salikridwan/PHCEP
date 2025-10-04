#!/usr/bin/env python3
"""
Tellurium Doping Optimization Analysis
Models Te concentration vs refractive index and absorption loss
"""

import numpy as np
import matplotlib.pyplot as plt

class TelluriumAnalyzer:
    def __init__(self):
        self.te_concentrations = np.linspace(1e18, 1e21, 50)  # atoms/cm³
        
    def te_index_change(self, concentration):
        """Model refractive index change vs Te concentration"""
        # Based on Sellmeier equation modifications for doped silicon
        n_si = 3.47  # Pure silicon at 1.55μm
        delta_n = 0.3 * (concentration / 1e20) ** 0.7  # Empirical model
        return n_si + delta_n
    
    def te_absorption_loss(self, concentration):
        """Model absorption loss vs Te concentration"""
        # Free carrier absorption model
        base_loss = 0.1  # dB/cm for pure silicon
        te_loss = 2.0 * (concentration / 1e20) ** 0.9  # Te-induced loss
        return base_loss + te_loss
    
    def find_optimal_concentration(self, target_index_min=3.4, target_index_max=3.6, max_loss=1.0):
        """Find optimal Te concentration range"""
        indices = [self.te_index_change(c) for c in self.te_concentrations]
        losses = [self.te_absorption_loss(c) for c in self.te_concentrations]
        
        optimal_mask = (np.array(indices) >= target_index_min) & \
                      (np.array(indices) <= target_index_max) & \
                      (np.array(losses) <= max_loss)
        
        optimal_concentrations = self.te_concentrations[optimal_mask]
        optimal_indices = np.array(indices)[optimal_mask]
        optimal_losses = np.array(losses)[optimal_mask]
        
        return optimal_concentrations, optimal_indices, optimal_losses
    
    def plot_optimization(self):
        """Plot Te concentration trade-off"""
        concentrations_cm3 = self.te_concentrations
        concentrations_log = np.log10(concentrations_cm3)
        
        indices = [self.te_index_change(c) for c in concentrations_cm3]
        losses = [self.te_absorption_loss(c) for c in concentrations_cm3]
        
        # Find optimal range
        opt_conc, opt_idx, opt_loss = self.find_optimal_concentration()
        
        plt.figure(figsize=(12, 5))
        
        # Plot 1: Index vs Concentration
        plt.subplot(1, 2, 1)
        plt.semilogx(concentrations_cm3, indices, 'b-', linewidth=2, label='Refractive Index')
        if len(opt_conc) > 0:
            plt.fill_between(opt_conc, min(indices), max(indices), 
                           alpha=0.3, color='green', label='Optimal Range')
        plt.axhline(y=3.4, color='r', linestyle='--', alpha=0.7, label='Target Range')
        plt.axhline(y=3.6, color='r', linestyle='--', alpha=0.7)
        plt.xlabel('Te Concentration (atoms/cm³)')
        plt.ylabel('Refractive Index @ 1.55μm')
        plt.title('Te Doping vs Refractive Index')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Loss vs Concentration
        plt.subplot(1, 2, 2)
        plt.semilogx(concentrations_cm3, losses, 'r-', linewidth=2, label='Propagation Loss')
        if len(opt_conc) > 0:
            plt.fill_between(opt_conc, min(losses), max(losses), 
                           alpha=0.3, color='green', label='Optimal Range')
        plt.axhline(y=1.0, color='g', linestyle='--', alpha=0.7, label='Max Loss Target')
        plt.xlabel('Te Concentration (atoms/cm³)')
        plt.ylabel('Propagation Loss (dB/cm)')
        plt.title('Te Doping vs Optical Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('te_doping_optimization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return opt_conc, opt_idx, opt_loss

def main():
    print("=== Tellurium Doping Optimization Analysis ===")
    print("Target: n = 3.4-3.6 with loss ≤ 1 dB/cm\n")
    
    analyzer = TelluriumAnalyzer()
    opt_conc, opt_idx, opt_loss = analyzer.plot_optimization()
    
    if len(opt_conc) > 0:
        print("✅ OPTIMAL CONCENTRATION RANGE FOUND:")
        print(f"   Concentration: {opt_conc[0]:.2e} to {opt_conc[-1]:.2e} atoms/cm³")
        print(f"   Refractive Index: {opt_idx[0]:.3f} to {opt_idx[-1]:.3f}")
        print(f"   Propagation Loss: {opt_loss[0]:.3f} to {opt_loss[-1]:.3f} dB/cm")
        
        # Recommend specific concentration
        best_idx = np.argmin(opt_loss)
        best_conc = opt_conc[best_idx]
        best_index = opt_idx[best_idx]
        best_loss = opt_loss[best_idx]
        
        print(f"\n🎯 RECOMMENDED OPERATING POINT:")
        print(f"   Te Concentration: {best_conc:.2e} atoms/cm³")
        print(f"   Expected Index: {best_index:.3f}")
        print(f"   Expected Loss: {best_loss:.3f} dB/cm")
    else:
        print("❌ No optimal concentration found within constraints")
        print("   Consider relaxing index or loss requirements")
        
    print("\n🔬 EXPERIMENTAL VALIDATION NEEDED:")
    print("   - Ellipsometry for refractive index measurement")
    print("   - Cut-back method for loss characterization")
    print("   - SIMS for actual doping concentration")

if __name__ == "__main__":
    main()
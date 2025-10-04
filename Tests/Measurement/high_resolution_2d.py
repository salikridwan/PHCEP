#!/usr/bin/env python3
"""
High-Resolution 2D Parameter Sweep (Radius × Confinement)
Generates comprehensive CSV data for bend optimization
"""

import numpy as np
import pandas as pd
from tqdm import tqdm

class HighResBendSweep:
    def __init__(self):
        self.radii = np.linspace(1.0, 20.0, 100)  # 100 points
        self.confinements = np.linspace(0.05, 0.5, 50)  # 50 points
        self.results = []
    
    def circular_bend_loss(self, radius, confinement):
        """High-accuracy circular bend loss model"""
        if radius <= 0:
            return 100.0
            
        # Enhanced model with physical basis
        critical_radius = 0.5 / (confinement + 0.01)  # Physical cutoff
        if radius < critical_radius:
            # Radiation-dominated regime
            return 10.0 * np.exp(-confinement * radius / 2.0)
        else:
            # Low-loss regime
            return 0.1 * (critical_radius / radius) ** 3
    
    def euler_bend_loss(self, radius, confinement, num_segments=2000):
        """High-resolution Euler bend loss calculation"""
        if radius <= 0:
            return 100.0
            
        # Euler bend curvature profile
        s_values = np.linspace(0, 1, num_segments)
        curvatures = s_values / radius  # Linear curvature increase
        
        total_loss = 0.0
        ds = 1.0 / num_segments
        
        for i, s in enumerate(s_values):
            if i == 0:
                continue
                
            local_radius = 1.0 / curvatures[i] if curvatures[i] > 0 else 1e6
            segment_loss = self.circular_bend_loss(local_radius, confinement) * ds
            total_loss += segment_loss
        
        # Length normalization (Euler bend is longer)
        euler_length = 2.0 * radius  # Approximation
        circular_length = np.pi * radius / 2  # 90° bend
        length_ratio = euler_length / circular_length
        
        return total_loss * length_ratio
    
    def calculate_flux(self, loss_dB):
        """Convert loss in dB to power transmission (flux)"""
        return 10 ** (-loss_dB / 10)
    
    def run_sweep(self):
        """Execute high-resolution parameter sweep"""
        print("Running high-resolution 2D sweep...")
        total_points = len(self.radii) * len(self.confinements)
        
        with tqdm(total=total_points) as pbar:
            for radius in self.radii:
                for confinement in self.confinements:
                    # Calculate losses
                    loss_circ = self.circular_bend_loss(radius, confinement)
                    loss_euler = self.euler_bend_loss(radius, confinement)
                    
                    # Calculate flux (power transmission)
                    flux_circ = self.calculate_flux(loss_circ)
                    flux_euler = self.calculate_flux(loss_euler)
                    
                    # Improvement percentage
                    if loss_circ > 0:
                        improvement = ((loss_circ - loss_euler) / loss_circ) * 100
                    else:
                        improvement = 0
                    
                    self.results.append({
                        'radius_um': radius,
                        'confinement': confinement,
                        'flux_circular': flux_circ,
                        'flux_euler': flux_euler,
                        'loss_circular_dB': loss_circ,
                        'loss_euler_dB': loss_euler,
                        'improvement_percent': improvement
                    })
                    
                    pbar.update(1)
        
        return pd.DataFrame(self.results)
    
    def analyze_critical_cases(self, df):
        """Identify critical cases for 3D FDTD verification"""
        # Find tightest radii with significant improvement
        tight_cases = df[df['radius_um'] <= 5.0]
        best_improvement = tight_cases.nlargest(3, 'improvement_percent')
        
        # Find cases near design target (0.40×0.36 µm waveguide)
        target_confinement = 0.2  # Estimated for our geometry
        target_cases = df[np.abs(df['confinement'] - target_confinement) < 0.05]
        target_cases = target_cases.nsmallest(3, 'radius_um')
        
        critical_cases = pd.concat([best_improvement, target_cases]).drop_duplicates()
        
        print("\n🎯 CRITICAL CASES FOR 3D FDTD VERIFICATION:")
        print("Radius(µm) | Confinement | Loss_Circ(dB) | Loss_Euler(dB) | Improv(%)")
        print("-" * 70)
        
        for _, case in critical_cases.iterrows():
            print(f"{case['radius_um']:9.1f} | {case['confinement']:11.3f} | "
                  f"{case['loss_circular_dB']:12.3f} | {case['loss_euler_dB']:11.3f} | "
                  f"{case['improvement_percent']:8.1f}")
        
        return critical_cases

def main():
    """Execute comprehensive parameter sweep"""
    print("=== High-Resolution 2D Parameter Sweep ===")
    print("Radius × Confinement analysis for bend optimization\n")
    
    sweep = HighResBendSweep()
    df = sweep.run_sweep()
    
    # Save comprehensive CSV
    csv_filename = 'bend_sweep_high_resolution.csv'
    df.to_csv(csv_filename, index=False)
    print(f"\n💾 Sweep results saved to: {csv_filename}")
    
    # Basic statistics
    print(f"\n📊 SWEEP STATISTICS:")
    print(f"   Total data points: {len(df):,}")
    print(f"   Radius range: {df['radius_um'].min():.1f} to {df['radius_um'].max():.1f} µm")
    print(f"   Confinement range: {df['confinement'].min():.3f} to {df['confinement'].max():.3f}")
    print(f"   Max improvement: {df['improvement_percent'].max():.1f}%")
    print(f"   Avg improvement: {df['improvement_percent'].mean():.1f}%")
    
    # Identify critical cases for 3D FDTD
    critical_cases = sweep.analyze_critical_cases(df)
    
    # Save critical cases for FDTD input
    critical_cases.to_csv('critical_cases_fdtd.csv', index=False)
    print(f"💾 Critical cases for FDTD saved to: critical_cases_fdtd.csv")
    
    # Generate summary plots
    generate_sweep_plots(df)

def generate_sweep_plots(df):
    """Generate comprehensive visualization of sweep results"""
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    
    # Pivot data for 2D plots
    pivot_loss_circ = df.pivot(index='confinement', columns='radius_um', values='loss_circular_dB')
    pivot_loss_euler = df.pivot(index='confinement', columns='radius_um', values='loss_euler_dB')
    pivot_improvement = df.pivot(index='confinement', columns='radius_um', values='improvement_percent')
    
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Circular bend loss
    plt.subplot(1, 3, 1)
    im1 = plt.contourf(pivot_loss_circ.columns, pivot_loss_circ.index, pivot_loss_circ, 
                      levels=100, cmap='hot_r', norm=LogNorm())
    plt.colorbar(im1, label='Loss (dB/90°)')
    plt.xlabel('Radius (µm)')
    plt.ylabel('Confinement Factor')
    plt.title('Circular Bend Loss')
    
    # Plot 2: Euler bend loss
    plt.subplot(1, 3, 2)
    im2 = plt.contourf(pivot_loss_euler.columns, pivot_loss_euler.index, pivot_loss_euler, 
                      levels=100, cmap='hot_r', norm=LogNorm())
    plt.colorbar(im2, label='Loss (dB/90°)')
    plt.xlabel('Radius (µm)')
    plt.ylabel('Confinement Factor')
    plt.title('Euler Bend Loss')
    
    # Plot 3: Improvement percentage
    plt.subplot(1, 3, 3)
    im3 = plt.contourf(pivot_improvement.columns, pivot_improvement.index, pivot_improvement, 
                      levels=100, cmap='viridis')
    plt.colorbar(im3, label='Improvement (%)')
    plt.xlabel('Radius (µm)')
    plt.ylabel('Confinement Factor')
    plt.title('Euler Bend Improvement')
    
    plt.tight_layout()
    plt.savefig('high_res_sweep_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
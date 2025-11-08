
import numpy as np
import pandas as pd
from tqdm import tqdm

class HighResBendSweep:
    def __init__(self):
        self.results = []
    
    def circular_bend_loss(self, radius, confinement):
        if radius <= 0:
            return 100.0
            
        s_values = np.linspace(0, 1, num_segments)
        
        total_loss = 0.0
        ds = 1.0 / num_segments
        
        for i, s in enumerate(s_values):
            if i == 0:
                continue
                
            local_radius = 1.0 / curvatures[i] if curvatures[i] > 0 else 1e6
            segment_loss = self.circular_bend_loss(local_radius, confinement) * ds
            total_loss += segment_loss
        
        length_ratio = euler_length / circular_length
        
        return total_loss * length_ratio
    
    def calculate_flux(self, loss_dB):
        print("Running high-resolution 2D sweep...")
        total_points = len(self.radii) * len(self.confinements)
        
        with tqdm(total=total_points) as pbar:
            for radius in self.radii:
                for confinement in self.confinements:
                    loss_circ = self.circular_bend_loss(radius, confinement)
                    loss_euler = self.euler_bend_loss(radius, confinement)
                    
                    flux_circ = self.calculate_flux(loss_circ)
                    flux_euler = self.calculate_flux(loss_euler)
                    
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
    print("=== High-Resolution 2D Parameter Sweep ===")
    print("Radius × Confinement analysis for bend optimization\n")
    
    sweep = HighResBendSweep()
    df = sweep.run_sweep()
    
    csv_filename = 'bend_sweep_high_resolution.csv'
    df.to_csv(csv_filename, index=False)
    print(f"\n💾 Sweep results saved to: {csv_filename}")
    
    print(f"\n📊 SWEEP STATISTICS:")
    print(f"   Total data points: {len(df):,}")
    print(f"   Radius range: {df['radius_um'].min():.1f} to {df['radius_um'].max():.1f} µm")
    print(f"   Confinement range: {df['confinement'].min():.3f} to {df['confinement'].max():.3f}")
    print(f"   Max improvement: {df['improvement_percent'].max():.1f}%")
    print(f"   Avg improvement: {df['improvement_percent'].mean():.1f}%")
    
    critical_cases = sweep.analyze_critical_cases(df)
    
    critical_cases.to_csv('critical_cases_fdtd.csv', index=False)
    print(f"💾 Critical cases for FDTD saved to: critical_cases_fdtd.csv")
    
    generate_sweep_plots(df)

def generate_sweep_plots(df):

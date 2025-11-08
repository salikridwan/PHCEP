
import numpy as np
import matplotlib.pyplot as plt
import math

class WaveguideAnalyzer:
    def __init__(self, width=0.5, height=0.22, wavelength=1.55, n_core=3.7, n_clad=1.44):
        self.width = width
        self.height = height
        self.wavelength = wavelength
        self.n_core = n_core
        self.n_clad = n_clad
        
    def effective_index_approximation(self):
        delta_n = self.n_core - self.n_clad
        
        area = self.width * self.height
        lambda_sq = self.wavelength ** 2
        
        return n_eff, Gamma
    
    def propagation_loss_models(self, length_mm, roughness_nm=2, te_doping_factor=1.2):
        
        
        doping_loss_dB_cm = base_loss_dB_cm * te_doping_factor
        
        scattering_loss_dB_cm = 0.5 * roughness_factor
        
        total_loss_dB_cm = doping_loss_dB_cm + scattering_loss_dB_cm
        
        total_loss_dB_cm = max(0.1, min(20.0, total_loss_dB_cm))
        
        length_cm = length_mm / 10.0
        transmission = 10 ** (-total_loss_dB_cm * length_cm / 10.0)
        
        n_eff, Gamma = self.effective_index_approximation()
        
        return {
            'effective_index': n_eff,
            'confinement_factor': Gamma,
            'scattering_loss_dB_cm': scattering_loss_dB_cm,
            'material_loss_dB_cm': doping_loss_dB_cm,
            'total_loss_dB_cm': total_loss_dB_cm,
            'transmission': transmission,
            'loss_per_mm': total_loss_dB_cm / 10.0
        }
    
    def bending_loss_calculation(self, radius_um):
        if radius_um >= 20:
            loss_dB = 0.05
        elif radius_um >= 10:
            loss_dB = 0.1 + (20 - radius_um) * 0.1
        elif radius_um >= 5:
            loss_dB = 1.0 + (10 - radius_um) * 0.5
        elif radius_um >= 3:
            loss_dB = 5.0 + (5 - radius_um) * 5.0
        else:
            
        return max(0.01, loss_dB)
    
    def straight_waveguide_simulation(self, length_mm=8.0):
        positions = np.linspace(0, length_mm, 100)
        
        loss_params = self.propagation_loss_models(length_mm)
        loss_per_mm = loss_params['loss_per_mm']
        
        power = 10 ** (-loss_per_mm * positions / 10.0)
        
        return positions, power
    
    def analyze_bending_radius_sweep(self, min_radius=1, max_radius=50, num_points=20):
        radii = np.linspace(min_radius, max_radius, num_points)
        bending_losses = []
        
        for radius in radii:
            loss = self.bending_loss_calculation(radius)
            bending_losses.append(loss)
            
        return radii, np.array(bending_losses)

def main():
    print("=== Tellurium-doped Silicon Waveguide Analysis ===")
    print("Waveguide dimensions: 0.5 μm × 0.22 μm")
    print("Operating wavelength: 1.55 μm") 
    print("Te-doped Si refractive index: 3.7\n")
    
    analyzer = WaveguideAnalyzer(width=0.5, height=0.22, wavelength=1.55, n_core=3.7)
    
    print("1. PROPAGATION LOSS ANALYSIS")
    print("-" * 40)
    
    length_mm = 8.0
    positions, power = analyzer.straight_waveguide_simulation(length_mm=length_mm)
    loss_params = analyzer.propagation_loss_models(length_mm)
    
    print(f"Effective index: {loss_params['effective_index']:.4f}")
    print(f"Confinement factor: {loss_params['confinement_factor']:.4f}")
    print(f"Scattering loss: {loss_params['scattering_loss_dB_cm']:.2f} dB/cm")
    print(f"Material loss: {loss_params['material_loss_dB_cm']:.2f} dB/cm")
    print(f"Total propagation loss: {loss_params['total_loss_dB_cm']:.2f} dB/cm")
    print(f"Transmission over {length_mm}mm: {loss_params['transmission']*100:.2f}%")
    
    print("\n2. BENDING LOSS ANALYSIS") 
    print("-" * 40)
    
    radii, bending_losses = analyzer.analyze_bending_radius_sweep()
    
    viable_mask = bending_losses < 0.5
    if np.any(viable_mask):
        min_viable_radius = radii[viable_mask][0]
    else:
        min_viable_radius = radii[-1]
    
    print(f"Minimum viable bend radius: {min_viable_radius:.1f} μm")
    print(f"Bending loss at 5μm radius: {analyzer.bending_loss_calculation(5):.3f} dB/90°")
    print(f"Bending loss at 10μm radius: {analyzer.bending_loss_calculation(10):.3f} dB/90°")
    print(f"Bending loss at 20μm radius: {analyzer.bending_loss_calculation(20):.3f} dB/90°")
    
    print("\n3. PERFORMANCE ASSESSMENT")
    print("-" * 40)
    
    if loss_params['total_loss_dB_cm'] < 3.0:
        loss_rating = "EXCELLENT"
    elif loss_params['total_loss_dB_cm'] < 5.0:
        loss_rating = "GOOD" 
    else:
        loss_rating = "MARGINAL"
        
    if min_viable_radius < 5.0:
        bend_rating = "EXCELLENT"
    elif min_viable_radius < 10.0:
        bend_rating = "GOOD"
    else:
        bend_rating = "MARGINAL"
        
    print(f"Propagation Loss: {loss_rating} ({loss_params['total_loss_dB_cm']:.2f} dB/cm)")
    print(f"Bend Performance: {bend_rating} (min viable radius: {min_viable_radius:.1f} μm)")
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(positions, power * 100)
    plt.xlabel('Position (mm)')
    plt.ylabel('Power Transmission (%)')
    plt.title('Waveguide Propagation')
    plt.grid(True)
    plt.ylim(0, 100)
    
    plt.subplot(1, 3, 2)
    plt.plot(radii, bending_losses)
    plt.axhline(y=0.5, color='r', linestyle='--', label='0.5 dB threshold')
    plt.xlabel('Bend Radius (μm)')
    plt.ylabel('Bending Loss (dB/90°)')
    plt.title('Bending Loss vs Radius')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 3)
    losses = [loss_params['scattering_loss_dB_cm'], loss_params['material_loss_dB_cm']]
    labels = [f'Scattering\n{losses[0]:.2f} dB/cm', f'Material\n{losses[1]:.2f} dB/cm']
    
    plt.pie(valid_losses, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('Loss Contribution Breakdown')
    
    plt.tight_layout()
    plt.savefig('waveguide_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n4. DESIGN RECOMMENDATIONS")
    print("-" * 40)
    
    if loss_rating == "EXCELLENT" and bend_rating == "EXCELLENT":
        print("✅ Waveguide design is EXCELLENT for photonic circuits")
        print("✅ Suitable for dense integration with low loss")
    elif loss_rating == "GOOD" and bend_rating == "GOOD":
        print("✅ Waveguide design is GOOD for most applications")
        print("✅ Consider optimization for high-performance circuits")
    else:
        print("⚠️  Waveguide design needs optimization")
        if loss_rating == "MARGINAL":
            print("   - Focus on reducing propagation loss")
        if bend_rating == "MARGINAL":
            print("   - Consider larger bend radii or improved confinement")
    
    return analyzer, positions, power, radii, bending_losses

if __name__ == "__main__":
    try:
        analyzer, positions, flux_data, radii, bending_losses = main()
        print("\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Error in analysis: {e}")
        print("Please check the waveguide parameters and try again.")
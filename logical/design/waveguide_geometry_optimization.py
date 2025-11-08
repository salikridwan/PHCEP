
import numpy as np
import matplotlib.pyplot as plt

class WaveguideOptimizer:
    def __init__(self):
        
    def confinement_factor_rectangular(self, width, height, n_core=3.5, n_clad=1.44, wavelength=1.55):
        base_confinement = self.confinement_factor_rectangular(width, height, n_core, n_clad)
        return min(0.98, base_confinement * rib_enhancement)
    
    def bending_loss_vs_confinement(self, confinement, radius):
        best_designs = []
        
        for width in self.widths:
            for height in self.heights:
                aspect_ratio = width / height
                if aspect_ratio > max_aspect_ratio or aspect_ratio < 1/max_aspect_ratio:
                    continue
                    
                confinement = self.confinement_factor_rectangular(width, height)
                
                if confinement >= target_confinement:
                    bend_5um = self.bending_loss_vs_confinement(confinement, 5)
                    bend_10um = self.bending_loss_vs_confinement(confinement, 10)
                    
                    best_designs.append({
                        'width': width,
                        'height': height,
                        'confinement': confinement,
                        'bend_5um': bend_5um,
                        'bend_10um': bend_10um,
                        'aspect_ratio': aspect_ratio
                    })
        
        best_designs.sort(key=lambda x: x['confinement'], reverse=True)

def main():
    print("=== Waveguide Geometry Optimization ===")
    print("Testing different cross-sections for improved confinement\n")
    
    optimizer = WaveguideOptimizer()
    best_designs = optimizer.optimize_geometry(target_confinement=0.2)
    
    if best_designs:
        print("✅ TOP WAVEGUIDE DESIGNS FOUND:")
        print("Width(μm) Height(μm) AspectRatio Confinement Bend@5μm(dB) Bend@10μm(dB)")
        print("-" * 70)
        
        for i, design in enumerate(best_designs[:5]):
            print(f"{design['width']:8.2f} {design['height']:10.2f} {design['aspect_ratio']:12.2f} "
                  f"{design['confinement']:11.3f} {design['bend_5um']:14.3f} {design['bend_10um']:15.3f}")
        
        widths = [d['width'] for d in best_designs]
        heights = [d['height'] for d in best_designs]
        confinements = [d['confinement'] for d in best_designs]
        
        plt.figure(figsize=(10, 8))
        
        scatter = plt.scatter(widths, heights, c=confinements, 
                            cmap='viridis', s=100, alpha=0.7)
        plt.colorbar(scatter, label='Confinement Factor')
        plt.xlabel('Waveguide Width (μm)')
        plt.ylabel('Waveguide Height (μm)')
        plt.title('Optimal Waveguide Geometries\n(Color = Confinement Factor)')
        plt.grid(True, alpha=0.3)
        
        best = best_designs[0]
        plt.scatter(best['width'], best['height'], s=200, 
                   facecolors='none', edgecolors='red', linewidth=2, label='Best Design')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('waveguide_optimization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n🎯 RECOMMENDED DESIGN:")
        print(f"   Width: {best['width']:.2f} μm, Height: {best['height']:.2f} μm")
        print(f"   Confinement Factor: {best['confinement']:.3f} (vs original 0.0438)")
        print(f"   Expected Bend Loss @ 10μm: {best['bend_10um']:.3f} dB/90°")
        
    else:
        print("❌ No designs found meeting target confinement of 0.2")
        print("   Consider increasing target or exploring rib waveguides")

if __name__ == "__main__":
    main()
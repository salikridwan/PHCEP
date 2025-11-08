
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

class CorrectedEulerBend:
    def __init__(self, target_radius, confinement=0.2, wavelength=1.55):
        self.target_radius = target_radius
        self.confinement = confinement
        self.wavelength = wavelength
        
    def circular_bend_radiation_loss(self, radius):
        return s_normalized / self.target_radius
    
    def euler_bend_radiation_loss(self, num_segments=1000):
        circular_loss = self.circular_bend_radiation_loss(self.target_radius)
        euler_loss = self.euler_bend_radiation_loss()
        
        improvement = ((circular_loss - euler_loss) / circular_loss) * 100 if circular_loss > 0 else 0
        
        return {
            'target_radius': self.target_radius,
            'confinement': self.confinement,
            'circular_loss': circular_loss,
            'euler_loss': euler_loss,
            'improvement_percent': improvement,
            'euler_length_factor': self.length_factor
        }

def analyze_bend_performance():
    confinements = sorted(set(r['confinement'] for r in results))
    radii = sorted(set(r['target_radius'] for r in results))
    
    plt.figure(figsize=(14, 10))
    
    plt.subplot(2, 2, 1)
    for confinement in [0.05, 0.2, 0.5]:
        conf_results = [r for r in results if r['confinement'] == confinement]
        radii_conf = [r['target_radius'] for r in conf_results]
        circular_losses = [r['circular_loss'] for r in conf_results]
        euler_losses = [r['euler_loss'] for r in conf_results]
        
        plt.semilogy(radii_conf, circular_losses, 'o-', label=f'Circular, Γ={confinement}')
        plt.semilogy(radii_conf, euler_losses, 's--', label=f'Euler, Γ={confinement}')
    
    plt.xlabel('Bend Radius (μm)')
    plt.ylabel('Radiation Loss (dB/90°)')
    plt.title('Bend Loss vs Radius and Confinement')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    for confinement in [0.05, 0.2, 0.5]:
        conf_results = [r for r in results if r['confinement'] == confinement]
        radii_conf = [r['target_radius'] for r in conf_results]
        improvements = [r['improvement_percent'] for r in conf_results]
        
        plt.plot(radii_conf, improvements, 'o-', label=f'Γ={confinement}')
    
    plt.xlabel('Bend Radius (μm)')
    plt.ylabel('Improvement Over Circular Bend (%)')
    plt.title('Euler Bend Improvement vs Radius')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    X = [r['target_radius'] for r in results]
    Y = [r['confinement'] for r in results]
    Z = [r['improvement_percent'] for r in results]
    
    scatter = ax.scatter(X, Y, Z, c=Z, cmap='viridis')
    ax.set_xlabel('Bend Radius (μm)')
    ax.set_ylabel('Confinement Factor')
    ax.set_zlabel('Improvement (%)')
    ax.set_title('Euler Bend Improvement Surface')
    
    plt.subplot(2, 2, 4)
    critical_radii = []
    confinements_sorted = sorted(confinements)
    
    for confinement in confinements_sorted:
        conf_results = [r for r in results if r['confinement'] == confinement]
        low_loss_radii = [r['target_radius'] for r in conf_results if r['circular_loss'] < 0.5]
        critical_radius = min(low_loss_radii) if low_loss_radii else max([r['target_radius'] for r in conf_results])
        critical_radii.append(critical_radius)
    
    plt.plot(confinements_sorted, critical_radii, 'ro-', linewidth=2)
    plt.xlabel('Confinement Factor')
    plt.ylabel('Critical Radius (μm)')
    plt.title('Minimum Radius for < 0.5 dB Loss (Circular)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('corrected_euler_bend_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():

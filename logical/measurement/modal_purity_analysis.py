
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh
from scipy.sparse import diags
import pandas as pd

class WaveguideModeSolver:
    def __init__(self, width=0.40, height=0.36, wavelength=1.55, n_core=3.5, n_clad=1.44):
        self.n_core = n_core
        self.n_clad = n_clad
        self.dy = 0.01
        
    def create_index_profile(self, simulation_size=2.0):
        simulation_size = max(self.width, self.height) * 3
        x, y, n_profile = self.create_index_profile(simulation_size)
        
        nx, ny = n_profile.shape
        k0 = 2 * np.pi / self.wavelength
        
        diag_main = (n_profile.flatten()**2 * k0**2 - 
                     2/self.dx**2 - 2/self.dy**2)
        
        diag_x = np.ones(nx * ny) / self.dx**2
        diag_y = np.ones(nx * ny) / self.dy**2
        
        A = diags([diag_main, diag_x, diag_x, diag_y, diag_y], 
                  [0, 1, -1, nx, -nx])
        
        print("Solving for waveguide modes...")
        print("Note: For production, use dedicated mode solver like Lumerical MODE")
        
        return self.analytical_mode_cutoff()
    
    def analytical_mode_cutoff(self):
        x, y, n_profile = self.create_index_profile()
        
        X, Y = np.meshgrid(x, y)
        sigma_x = self.width / 3
        sigma_y = self.height / 3
        mode_profile = np.exp(-(X**2/(2*sigma_x**2) + Y**2/(2*sigma_y**2)))
        
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 3, 1)
        plt.imshow(n_profile, extent=[x.min(), x.max(), y.min(), y.max()], 
                  cmap='jet', origin='lower')
        plt.colorbar(label='Refractive Index')
        plt.title('Waveguide Index Profile')
        plt.xlabel('x (µm)')
        plt.ylabel('y (µm)')
        
        plt.subplot(1, 3, 2)
        plt.imshow(mode_profile, extent=[x.min(), x.max(), y.min(), y.max()],
                  cmap='hot', origin='lower')
        plt.colorbar(label='Field Intensity')
        plt.title('Estimated Fundamental Mode')
        plt.xlabel('x (µm)')
        plt.ylabel('y (µm)')
        
        plt.subplot(1, 3, 3)
        plt.plot(x, mode_profile[len(y)//2, :], 'b-', label='Horizontal cut')
        plt.plot(y, mode_profile[:, len(x)//2], 'r-', label='Vertical cut')
        plt.xlabel('Position (µm)')
        plt.ylabel('Field Intensity')
        plt.title('Mode Field Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('waveguide_mode_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def validate_single_mode_operation():

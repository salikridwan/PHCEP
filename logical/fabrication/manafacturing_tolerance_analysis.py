
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class CorrectedToleranceAnalyzer:
    def __init__(self, nominal_width=0.26, nominal_height=0.22, nominal_index=3.5):
        self.nominal_width = nominal_width
        self.nominal_height = nominal_height  
        self.nominal_index = nominal_index
        self.n_clad = 1.44
        self.wavelength = 1.55
        
    def calculate_v_parameters(self, width, height, n_core):
        Vx, Vy = self.calculate_v_parameters(width, height, n_core)
        return Vx < np.pi and Vy < np.pi
    
        results = []
        
        for dw in width_variation:
            for dh in height_variation:
                new_width = self.nominal_width + dw
                new_height = self.nominal_height + dh
                
                single_mode = self.is_single_mode(new_width, new_height, self.nominal_index)
                
                area_original = self.nominal_width * self.nominal_height
                area_new = new_width * new_height
                confinement_change = (area_new - area_original) / area_original
                
                Vx, Vy = self.calculate_v_parameters(new_width, new_height, self.nominal_index)
                
                results.append({
                    'width_variation_um': dw,
                    'height_variation_um': dh,
                    'new_width': new_width,
                    'new_height': new_height,
                    'confinement_change': confinement_change,
                    'remains_single_mode': single_mode,
                    'V_parameter_x': Vx,
                    'V_parameter_y': Vy
                })
        
        return pd.DataFrame(results)
    
    def analyze_single_mode_geometries(self):
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.plot(roughness_df['roughness_nm'], roughness_df['scattering_loss_dB_cm'], 'ro-', linewidth=2)
    plt.axvline(x=3, color='g', linestyle='--', label='3nm spec limit', linewidth=2)
    plt.xlabel('Sidewall Roughness (nm RMS)')
    plt.ylabel('Scattering Loss (dB/cm)')
    plt.title('Sidewall Roughness Impact')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    colors = ['green' if sm else 'red' for sm in sm_geometries['single_mode']]
    bars = plt.bar(sm_geometries['name'], sm_geometries['Vx'], color=colors, alpha=0.7)
    plt.axhline(y=np.pi, color='r', linestyle='--', label='V = π (single-mode limit)')
    plt.ylabel('V-Parameter')
    plt.title('Single-Mode Condition Check')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    scatter = plt.scatter(etch_df['width_variation_um']*1000, 
                         etch_df['height_variation_um']*1000,
                         c=etch_df['remains_single_mode'], cmap='coolwarm', alpha=0.6)
    plt.colorbar(scatter, label='Remains Single-Mode')
    plt.xlabel('Width Variation (nm)')
    plt.ylabel('Height Variation (nm)')
    plt.title('Etch Variation Impact on Single-Mode')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    widths = np.linspace(0.2, 0.5, 50)
    heights = np.linspace(0.15, 0.4, 50)
    W, H = np.meshgrid(widths, heights)
    
    single_mode_region = np.zeros_like(W)
    analyzer = CorrectedToleranceAnalyzer()
    
    for i in range(len(widths)):
        for j in range(len(heights)):
            single_mode_region[j, i] = analyzer.is_single_mode(widths[i], heights[j], 3.5)
    
    plt.contourf(W, H, single_mode_region, levels=[-0.5, 0.5, 1.5], colors=['red', 'green'], alpha=0.3)
    plt.contour(W, H, single_mode_region, levels=[0.5], colors='black', linewidths=2)
    
    for _, geo in sm_geometries.iterrows():
        color = 'green' if geo['single_mode'] else 'red'
        marker = 'o' if geo['single_mode'] else 'x'
        plt.scatter(geo['width'], geo['height'], color=color, marker=marker, s=100, 
                   label=geo['name'] if geo['name'] == 'Conservative SM' else "")
    
    plt.xlabel('Waveguide Width (µm)')
    plt.ylabel('Waveguide Height (µm)')
    plt.title('Single-Mode Operating Region')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('corrected_tolerance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
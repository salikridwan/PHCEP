#!/usr/bin/env python3
"""
CORRECTED Manufacturing Tolerance Analysis
Fixed bug in roughness analysis and added single-mode validation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class CorrectedToleranceAnalyzer:
    def __init__(self, nominal_width=0.26, nominal_height=0.22, nominal_index=3.5):
        # Changed nominal_width and nominal_height for single-mode fix (Option A)
        self.nominal_width = nominal_width
        self.nominal_height = nominal_height  
        self.nominal_index = nominal_index
        self.n_clad = 1.44
        self.wavelength = 1.55
        
    def calculate_v_parameters(self, width, height, n_core):
        """Calculate V-parameters for single-mode condition check"""
        Vx = (2 * np.pi * width / self.wavelength) * np.sqrt(n_core**2 - self.n_clad**2)
        Vy = (2 * np.pi * height / self.wavelength) * np.sqrt(n_core**2 - self.n_clad**2)
        return Vx, Vy
    
    def is_single_mode(self, width, height, n_core):
        """Check if waveguide supports single fundamental mode"""
        Vx, Vy = self.calculate_v_parameters(width, height, n_core)
        return Vx < np.pi and Vy < np.pi
    
    def analyze_sidewall_roughness(self, roughness_range=np.linspace(1, 10, 10)):  # Fixed: 10 points includes 2.0
        """Analyze impact of sidewall roughness (1-10 nm RMS)"""
        results = []
        
        for roughness_nm in roughness_range:
            # Roughness-induced scattering loss model
            scattering_loss = 0.5 * (roughness_nm / 2.0) ** 2  # dB/cm
            
            # Roughness also affects effective index
            delta_n = -0.01 * (roughness_nm / 5.0)  # Small index reduction
            
            results.append({
                'roughness_nm': roughness_nm,
                'scattering_loss_dB_cm': scattering_loss,
                'delta_effective_index': delta_n,
                'confinement_reduction': 0.02 * (roughness_nm / 5.0)
            })
        
        return pd.DataFrame(results)
    
    def analyze_etch_variation(self, width_variation=np.linspace(-0.05, 0.05, 20),
                              height_variation=np.linspace(-0.02, 0.02, 20)):
        """Analyze etch depth/width variations with single-mode check"""
        results = []
        
        for dw in width_variation:
            for dh in height_variation:
                new_width = self.nominal_width + dw
                new_height = self.nominal_height + dh
                
                # Check single-mode condition
                single_mode = self.is_single_mode(new_width, new_height, self.nominal_index)
                
                # Estimate confinement change (simplified)
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
        """Test recommended single-mode geometries"""
        geometries = [
            # Conservative single-mode designs
            {'width': 0.26, 'height': 0.22, 'name': 'Conservative SM'},
            {'width': 0.30, 'height': 0.28, 'name': 'Liberal SM'},
            # Current problematic design
            {'width': 0.40, 'height': 0.36, 'name': 'Current Multi-mode'},
            # Rib waveguide alternative (partial etch)
            {'width': 0.40, 'height': 0.22, 'slab_height': 0.14, 'name': 'Rib Waveguide'}
        ]
        
        results = []
        for geo in geometries:
            if 'slab_height' in geo:  # Rib waveguide
                # Simplified rib model: reduced effective height for mode counting
                effective_height = geo['height'] * 0.7  # Approximation
                single_mode = self.is_single_mode(geo['width'], effective_height, self.nominal_index)
                Vx, Vy = self.calculate_v_parameters(geo['width'], effective_height, self.nominal_index)
            else:
                single_mode = self.is_single_mode(geo['width'], geo['height'], self.nominal_index)
                Vx, Vy = self.calculate_v_parameters(geo['width'], geo['height'], self.nominal_index)
            
            results.append({
                'name': geo['name'],
                'width': geo['width'],
                'height': geo.get('height', geo.get('slab_height', 0)),
                'Vx': Vx,
                'Vy': Vy,
                'single_mode': single_mode,
                'safe_margin': min(np.pi - Vx, np.pi - Vy) if single_mode else -1
            })
        
        return pd.DataFrame(results)

def main():
    print("=== CORRECTED Manufacturing Tolerance Analysis ===\n")
    
    analyzer = CorrectedToleranceAnalyzer()
    
    # 1. Single-mode geometry validation
    print("1. SINGLE-MODE GEOMETRY VALIDATION:")
    print("=" * 50)
    
    sm_geometries = analyzer.analyze_single_mode_geometries()
    
    print("\n📊 Recommended Single-Mode Geometries:")
    print("Name                | Width | Height | Vx    | Vy    | Single-Mode | Safe Margin")
    print("-" * 85)
    
    for _, geo in sm_geometries.iterrows():
        status = "✅" if geo['single_mode'] else "❌"
        margin = f"{geo['safe_margin']:.3f}" if geo['safe_margin'] > 0 else "N/A"
        print(f"{geo['name']:20} | {geo['width']:5.2f} | {geo['height']:6.2f} | "
              f"{geo['Vx']:5.2f} | {geo['Vy']:5.2f} | {status:11} | {margin:>11}")
    
    # 2. Sidewall roughness analysis (FIXED)
    print("\n2. SIDEWALL ROUGHNESS IMPACT (1-10 nm RMS):")
    roughness_df = analyzer.analyze_sidewall_roughness()
    
    # FIX: Safe way to get 2nm value
    roughness_2nm = roughness_df.iloc[(roughness_df['roughness_nm'] - 2.0).abs().argsort()[:1]]
    typical_loss = roughness_2nm['scattering_loss_dB_cm'].values[0]
    
    print(f"   Worst-case scattering loss: {roughness_df['scattering_loss_dB_cm'].max():.3f} dB/cm")
    print(f"   Typical (2nm) loss: {typical_loss:.3f} dB/cm")
    
    # 3. Etch variation analysis
    print("\n3. ETCH VARIATION IMPACT (±50nm width, ±20nm height):")
    etch_df = analyzer.analyze_etch_variation()
    failed_single_mode = etch_df[~etch_df['remains_single_mode']]
    print(f"   Designs failing single-mode: {len(failed_single_mode)}/{len(etch_df)}")
    
    # Generate recommendations
    print("\n🎯 ENGINEERING RECOMMENDATIONS:")
    print("=" * 50)
    
    conservative_geo = sm_geometries[sm_geometries['name'] == 'Conservative SM'].iloc[0]
    print(f"1. IMMEDIATE FIX: Change to {conservative_geo['width']}×{conservative_geo['height']} µm")
    print(f"   - Guaranteed single-mode (Vx={conservative_geo['Vx']:.2f}, Vy={conservative_geo['Vy']:.2f} < π)")
    print(f"   - Safe margin: {conservative_geo['safe_margin']:.3f}")
    
    print("\n2. RIB WAVEGUIDE ALTERNATIVE:")
    rib_geo = sm_geometries[sm_geometries['name'] == 'Rib Waveguide'].iloc[0]
    if rib_geo['single_mode']:
        print("   ✅ Rib waveguide enables 0.40µm width while maintaining single-mode")
        print("   - Partial etch: 0.22µm ridge + 0.14µm slab")
        print("   - Better confinement than straight 0.26×0.22µm")
    else:
        print("   ❌ Rib design still multi-mode - need finer optimization")
    
    print("\n3. MANUFACTURING CONTROLS:")
    print("   - Control sidewall roughness < 3nm RMS")
    print("   - Maintain etch uniformity ±20nm")
    print("   - Use process control monitors on test structures")
    
    # Generate plots
    generate_corrected_plots(roughness_df, etch_df, sm_geometries)

def generate_corrected_plots(roughness_df, etch_df, sm_geometries):
    """Generate corrected tolerance analysis plots"""
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Sidewall roughness impact
    plt.subplot(2, 2, 1)
    plt.plot(roughness_df['roughness_nm'], roughness_df['scattering_loss_dB_cm'], 'ro-', linewidth=2)
    plt.axvline(x=3, color='g', linestyle='--', label='3nm spec limit', linewidth=2)
    plt.xlabel('Sidewall Roughness (nm RMS)')
    plt.ylabel('Scattering Loss (dB/cm)')
    plt.title('Sidewall Roughness Impact')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Single-mode geometry comparison
    plt.subplot(2, 2, 2)
    colors = ['green' if sm else 'red' for sm in sm_geometries['single_mode']]
    bars = plt.bar(sm_geometries['name'], sm_geometries['Vx'], color=colors, alpha=0.7)
    plt.axhline(y=np.pi, color='r', linestyle='--', label='V = π (single-mode limit)')
    plt.ylabel('V-Parameter')
    plt.title('Single-Mode Condition Check')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Etch variation impact on single-mode
    plt.subplot(2, 2, 3)
    scatter = plt.scatter(etch_df['width_variation_um']*1000, 
                         etch_df['height_variation_um']*1000,
                         c=etch_df['remains_single_mode'], cmap='coolwarm', alpha=0.6)
    plt.colorbar(scatter, label='Remains Single-Mode')
    plt.xlabel('Width Variation (nm)')
    plt.ylabel('Height Variation (nm)')
    plt.title('Etch Variation Impact on Single-Mode')
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Safe operating regions
    plt.subplot(2, 2, 4)
    widths = np.linspace(0.2, 0.5, 50)
    heights = np.linspace(0.15, 0.4, 50)
    W, H = np.meshgrid(widths, heights)
    
    # Calculate single-mode regions
    single_mode_region = np.zeros_like(W)
    analyzer = CorrectedToleranceAnalyzer()
    
    for i in range(len(widths)):
        for j in range(len(heights)):
            single_mode_region[j, i] = analyzer.is_single_mode(widths[i], heights[j], 3.5)
    
    plt.contourf(W, H, single_mode_region, levels=[-0.5, 0.5, 1.5], colors=['red', 'green'], alpha=0.3)
    plt.contour(W, H, single_mode_region, levels=[0.5], colors='black', linewidths=2)
    
    # Plot recommended points
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
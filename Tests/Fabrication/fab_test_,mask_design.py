#!/usr/bin/env python3
"""
FAB TEST MASK DESIGN: Single-Mode Waveguide Characterization
Mathematical layout for fabrication test structures
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import math

class FabTestMaskDesign:
    def __init__(self, chip_size=5000, waveguide_width=0.22, waveguide_height=0.18):
        self.chip_size = chip_size  # µm
        self.wg_width = waveguide_width
        self.wg_height = waveguide_height
        self.layer_spacing = 100  # µm between test structures
    
    def straight_waveguide_array(self, lengths=[1000, 5000, 10000]):
        """Design straight waveguides for cut-back loss measurement"""
        structures = []
        y_position = 100
        
        for i, length in enumerate(lengths):
            # Waveguide
            structures.append({
                'type': 'waveguide',
                'x': 100, 'y': y_position,
                'width': self.wg_width, 'length': length,
                'label': f'Straight_{length}um'
            })
            
            # Grating couplers (simplified)
            structures.extend([
                {
                    'type': 'grating_coupler',
                    'x': 50, 'y': y_position,
                    'width': 20, 'length': 50,
                    'label': f'GC_in_{length}um'
                },
                {
                    'type': 'grating_coupler', 
                    'x': 100 + length, 'y': y_position,
                    'width': 20, 'length': 50,
                    'label': f'GC_out_{length}um'
                }
            ])
            
            y_position += self.layer_spacing
        
        return structures
    
    def taper_designs(self, taper_lengths=[5, 10, 20]):
        """Design adiabatic tapers from 0.40µm to 0.22µm"""
        structures = []
        y_position = 1500
        wide_width = 0.40
        narrow_width = 0.22
        
        for i, taper_len in enumerate(taper_lengths):
            # Input wide section
            structures.append({
                'type': 'waveguide',
                'x': 100, 'y': y_position,
                'width': wide_width, 'length': 50,
                'label': f'Wide_in_{taper_len}um'
            })
            
            # Taper section
            structures.append({
                'type': 'taper',
                'x': 150, 'y': y_position,
                'width_start': wide_width, 'width_end': narrow_width,
                'length': taper_len,
                'label': f'Taper_{taper_len}um'
            })
            
            # Output narrow section
            structures.append({
                'type': 'waveguide', 
                'x': 150 + taper_len, 'y': y_position,
                'width': narrow_width, 'length': 50,
                'label': f'Narrow_out_{taper_len}um'
            })
            
            # Grating couplers
            structures.extend([
                {
                    'type': 'grating_coupler',
                    'x': 50, 'y': y_position,
                    'width': 20, 'length': 50,
                    'label': f'GC_taper_in_{taper_len}um'
                },
                {
                    'type': 'grating_coupler',
                    'x': 200 + taper_len, 'y': y_position, 
                    'width': 20, 'length': 50,
                    'label': f'GC_taper_out_{taper_len}um'
                }
            ])
            
            y_position += self.layer_spacing
        
        return structures
    
    def rib_waveguide_variants(self, etch_depths=[0.70, 0.75, 0.80]):
        """Design rib waveguide variants with different etch depths"""
        structures = []
        y_position = 3000
        total_height = 0.36
        rib_width = 0.40
        
        for i, etch_ratio in enumerate(etch_depths):
            ridge_height = total_height * (1 - etch_ratio)
            slab_height = total_height - ridge_height
            
            # Rib waveguide (simplified representation)
            structures.append({
                'type': 'rib_waveguide',
                'x': 100, 'y': y_position,
                'width': rib_width, 'length': 200,
                'ridge_height': ridge_height,
                'slab_height': slab_height,
                'etch_ratio': etch_ratio,
                'label': f'Rib_etch{int(etch_ratio*100)}pc'
            })
            
            # Grating couplers
            structures.extend([
                {
                    'type': 'grating_coupler',
                    'x': 50, 'y': y_position,
                    'width': 20, 'length': 50,
                    'label': f'GC_rib_in_{etch_ratio}'
                },
                {
                    'type': 'grating_coupler',
                    'x': 300, 'y': y_position,
                    'width': 20, 'length': 50, 
                    'label': f'GC_rib_out_{etch_ratio}'
                }
            ])
            
            y_position += self.layer_spacing
        
        return structures
    
    def ring_resonator_design(self, radius=10, gap=0.2, coupling_length=5):
        """Design ring resonator for Q-factor and index measurement"""
        structures = []
        y_position = 4500
        
        # Bus waveguide
        structures.append({
            'type': 'waveguide',
            'x': 100, 'y': y_position,
            'width': self.wg_width, 'length': 100,
            'label': 'Ring_bus_waveguide'
        })
        
        # Ring resonator
        structures.append({
            'type': 'ring_resonator',
            'x': 150, 'y': y_position,
            'radius': radius,
            'width': self.wg_width,
            'gap': gap,
            'coupling_length': coupling_length,
            'label': f'Ring_R{radius}um_gap{gap}um'
        })
        
        # Grating couplers
        structures.extend([
            {
                'type': 'grating_coupler',
                'x': 50, 'y': y_position,
                'width': 20, 'length': 50,
                'label': 'GC_ring_in'
            },
            {
                'type': 'grating_coupler',
                'x': 250, 'y': y_position,
                'width': 20, 'length': 50,
                'label': 'GC_ring_out'
            },
            {
                'type': 'grating_coupler',
                'x': 150, 'y': y_position + radius + gap + 10,
                'width': 20, 'length': 50,
                'label': 'GC_ring_drop'
            }
        ])
        
        return structures
    
    def process_control_monitors(self):
        """Design process control monitors"""
        structures = []
        y_position = 500
        
        # Width variation test
        widths = [0.18, 0.20, 0.22, 0.24, 0.26]
        for i, width in enumerate(widths):
            structures.append({
                'type': 'waveguide',
                'x': 2000 + i * 50, 'y': y_position,
                'width': width, 'length': 100,
                'label': f'PCM_width_{width}um'
            })
        
        # Etch depth test (simplified)
        y_position += 200
        for i, depth in enumerate([0.65, 0.70, 0.75, 0.80, 0.85]):
            structures.append({
                'type': 'pcm_etch',
                'x': 2000 + i * 50, 'y': y_position,
                'width': 10, 'length': 20,
                'etch_depth': depth,
                'label': f'PCM_etch_{depth}'
            })
        
        return structures
    
    def generate_mask_layout(self):
        """Generate complete mask layout"""
        print("=== FAB TEST MASK DESIGN ===")
        print("Waveguide geometry: 0.22×0.18 µm (single-mode)")
        print(f"Chip size: {self.chip_size}×{self.chip_size} µm")
        print()
        
        all_structures = []
        
        # Add all test structures
        all_structures.extend(self.straight_waveguide_array())
        all_structures.extend(self.taper_designs())
        all_structures.extend(self.rib_waveguide_variants())
        all_structures.extend(self.ring_resonator_design())
        all_structures.extend(self.process_control_monitors())
        
        return all_structures
    
    def calculate_expected_performance(self):
        """Calculate expected performance metrics"""
        print("=== EXPECTED PERFORMANCE CALCULATIONS ===")
        
        # Updated loss values based on material optimization
        optimistic_loss = 0.132  # dB/cm (best-case from material sims)
        conservative_loss = 2.4   # dB/cm (conservative estimate)
        expected_loss = (optimistic_loss + conservative_loss) / 2  # Realistic
        
        print(f"Optimistic propagation loss: {optimistic_loss:.3f} dB/cm")
        print(f"Conservative propagation loss: {conservative_loss:.1f} dB/cm") 
        print(f"Expected propagation loss: {expected_loss:.3f} dB/cm")
        
        # Taper loss estimation (kept as is)
        print("\nTaper performance (0.40µm → 0.22µm):")
        taper_losses = {5: 0.40, 10: 0.25, 20: 0.10}
        for length in [5, 10, 20]:
            print(f"  {length}µm taper: {taper_losses[length]:.2f} dB estimated loss")
        
        # Ring resonator Q-factor estimation (optimistic)
        ring_radius = 10  # µm
        circumference = 2 * math.pi * ring_radius
        total_loss_optimistic = (optimistic_loss / 10000) * circumference
        if total_loss_optimistic > 0:
            Q_optimistic = (2 * math.pi * ring_radius * 3.48) / (1.55 * total_loss_optimistic / 4.343)
            print(f"\nRing resonator (R={ring_radius}µm) - Optimistic:")
            print(f"  Q-factor: {Q_optimistic:,.0f}")
            # FSR using group index
            self.calculate_ring_performance(n_eff=3.48, radius=ring_radius)
        
        return expected_loss

    def calculate_ring_performance(self, n_eff=3.48, radius=10):
        """Accurate FSR calculation using group index"""
        circumference = 2 * math.pi * radius  # µm
        FSR = (1.55**2) / (n_eff * circumference * 1e-3)  # nm
        n_g = n_eff - 1.55 * 0.01  # Approximate group index
        FSR_corrected = (1.55**2) / (n_g * circumference * 1e-3)
        print(f"Ring R={radius}µm, n_eff={n_eff}:")
        print(f"  FSR (n_eff): {FSR:.1f} nm")
        print(f"  FSR (n_g): {FSR_corrected:.1f} nm")
        return FSR_corrected

def visualize_mask_design(structures):
    """Create visualization of the mask layout"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))  # Increased from 12×12
    
    colors = {
        'waveguide': 'blue',
        'taper': 'green', 
        'rib_waveguide': 'red',
        'ring_resonator': 'purple',
        'grating_coupler': 'orange',
        'pcm_etch': 'gray',
        'alignment_cross': 'black',
        'scribe_line': 'brown'
    }
    
    for struct in structures:
        color = colors.get(struct['type'], 'black')
        
        if struct['type'] in ['waveguide', 'rib_waveguide']:
            rect = Rectangle((struct['x'], struct['y']), struct['length'], struct['width'],
                           facecolor=color, alpha=0.7, edgecolor='black')
            ax.add_patch(rect)
            
        elif struct['type'] == 'taper':
            # Draw trapezoid for taper
            x = struct['x']
            y = struct['y'] - struct['width_start']/2
            width_start = struct['width_start']
            width_end = struct['width_end']
            length = struct['length']
            
            points = [(x, y), (x + length, y - (width_start - width_end)/2),
                     (x + length, y - (width_start - width_end)/2 - width_end),
                     (x, y - width_start)]
            poly = Polygon(points, facecolor=color, alpha=0.7, edgecolor='black')
            ax.add_patch(poly)
            
        elif struct['type'] == 'ring_resonator':
            circle = Circle((struct['x'], struct['y']), struct['radius'],
                          facecolor='none', edgecolor=color, linewidth=2)
            ax.add_patch(circle)
            
        elif struct['type'] == 'grating_coupler':
            rect = Rectangle((struct['x'], struct['y']), struct['length'], struct['width'],
                           facecolor=color, alpha=0.5, edgecolor='black')
            ax.add_patch(rect)
        
        elif struct['type'] == 'alignment_cross':
            size = struct['size']
            x, y = struct['x'], struct['y']
            ax.plot([x - size/2, x + size/2], [y, y], color=color, linewidth=2)
            ax.plot([x, x], [y - size/2, y + size/2], color=color, linewidth=2)
        
        elif struct['type'] == 'scribe_line':
            rect = Rectangle((struct['x'], struct['y']), struct['width'], struct['height'],
                             facecolor=color, alpha=0.2, edgecolor='black')
            ax.add_patch(rect)
        
        # Add label (smaller font)
        ax.text(struct['x'], struct['y'] - 10, struct['label'] if 'label' in struct else struct['type'], 
               fontsize=6, ha='center', va='top')
    
    ax.set_xlim(0, 2500)
    ax.set_ylim(0, 5000)
    ax.set_aspect('equal')
    ax.set_xlabel('X position (µm)')
    ax.set_ylabel('Y position (µm)')
    ax.set_title('Fab Test Mask Layout: Single-Mode Waveguide Characterization')
    ax.grid(True, alpha=0.3)
    
    # Create legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, label=type_name)
                     for type_name, color in colors.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout(pad=3.0)  # Add padding
    plt.savefig('fab_test_mask_design.png', dpi=300, bbox_inches='tight')
    plt.show()

def add_fiducials_and_scribe():
    """Add alignment marks and dicing lines"""
    structures = []
    # Alignment crosses at corners
    cross_positions = [(100, 100), (4900, 100), (100, 4900), (4900, 4900)]
    for x, y in cross_positions:
        structures.append({'type': 'alignment_cross', 'x': x, 'y': y, 'size': 50})
    # Scribe lines (100 µm wide, 100 µm from chip edge)
    scribe_width = 100
    structures.extend([
        {'type': 'scribe_line', 'x': 0, 'y': 0, 'width': 5000, 'height': scribe_width},
        {'type': 'scribe_line', 'x': 0, 'y': 4900, 'width': 5000, 'height': scribe_width},
        {'type': 'scribe_line', 'x': 0, 'y': 0, 'width': scribe_width, 'height': 5000},
        {'type': 'scribe_line', 'x': 4900, 'y': 0, 'width': scribe_width, 'height': 5000},
    ])
    return structures

# Process notes and measurement protocol
LAYER_MAPPING = {
    'waveguide_core': (1, 0),      # Layer 1, Datatype 0
    'rib_etch': (2, 0),            # Layer 2, Datatype 0  
    'grating_couplers': (3, 0),     # Layer 3, Datatype 0
    'pcm_structures': (10, 0),      # Layer 10, Datatype 0
    'alignment_marks': (100, 0),    # Layer 100, Datatype 0
    'scribe_lines': (101, 0)        # Layer 101, Datatype 0
}

PROCESS_SPECIFICATIONS = """
FILM STACK:
- Silicon thickness: 360 nm (±10 nm)
- TE doping target: 5e19 atoms/cm³ (n ≈ 3.48)
- Etch depth (rib): 252 nm (70%), 270 nm (75%), 288 nm (80%)
- Oxide cladding: 2 µm PECVD SiO₂

MASK ALIGNMENT:
- 1st mask: Waveguide core + grating couplers
- 2nd mask: Rib etch definition  
- Overlay accuracy: < 100 nm
"""

MEASUREMENT_PROTOCOL = """
LIGHT SOURCE: Tunable laser 1500-1600 nm
POLARIZATION: TE (Transverse Electric)
COUPLING: Grating couplers (single polarization)
PCM CORRELATION:
- PCM_width_0.18um → Waveguide width control
- PCM_etch_0.70 → Rib etch depth verification  
- Ring resonators → n_eff and loss extraction
- Taper structures → Mode conversion efficiency

MEASUREMENT SEQUENCE:
1. Spectral sweep: 1500-1600 nm, find resonances
2. Cut-back: Measure 1, 5, 10 mm waveguides
3. Taper loss: Reference vs tapered paths
4. Ring Q: High-resolution scan around resonances
"""

def generate_gds_script(structures):
    """Generate pseudo-GDSII script (conceptual)"""
    print("\n=== GDSII SCRIPT OUTLINE ===")
    print("Layer mapping:")
    print("  Layer 1: Waveguide core (0.22×0.18 µm)")
    print("  Layer 2: Rib etch definition")
    print("  Layer 3: Grating couplers")
    print("  Layer 10: Process control monitors")
    print("  Layer 100: Alignment marks")
    
    print("\nMain structures:")
    for struct in structures:
        if struct['type'] in ['waveguide', 'taper']:
            print(f"  {struct.get('label', struct['type'])}: Layer 1")
        elif struct['type'] == 'rib_waveguide':
            print(f"  {struct.get('label', struct['type'])}: Layers 1+2")
        elif struct['type'] == 'grating_coupler':
            print(f"  {struct.get('label', struct['type'])}: Layer 3")
        elif struct['type'] == 'pcm_etch':
            print(f"  {struct.get('label', struct['type'])}: Layer 10")
        elif struct['type'] == 'alignment_cross':
            print(f"  Alignment cross at ({struct['x']},{struct['y']}): Layer 100")
        elif struct['type'] == 'scribe_line':
            print(f"  Scribe line at ({struct['x']},{struct['y']}): Layer 101")
    return structures

def integrate_pcms_into_mask(mask_structures, pcm_structures):
    """Integrate PCM structures into main mask design"""
    print("Integrating PCMs into mask design...")
    
    # Filter out existing PCMs to avoid duplicates
    existing_pcm_types = ['pcm_etch', 'pcm_width']
    filtered_structures = [s for s in mask_structures 
                          if s.get('type') not in existing_pcm_types]
    
    # Add PCM structures
    integrated_structures = filtered_structures + pcm_structures
    
    print(f"Added {len(pcm_structures)} PCM structures")
    print(f"Total structures in mask: {len(integrated_structures)}")
    
    return integrated_structures

def main():
    """Main mask design function"""
    # Create mask design
    mask_designer = FabTestMaskDesign()
    structures = mask_designer.generate_mask_layout()
    # Add fiducials and scribe lines
    structures.extend(add_fiducials_and_scribe())
    
    # Calculate expected performance
    expected_loss = mask_designer.calculate_expected_performance()
    
    # Generate visualization
    visualize_mask_design(structures)
    
    # Generate GDSII outline
    generate_gds_script(structures)
    
    # Summary
    print(f"\n=== MASK DESIGN SUMMARY ===")
    print(f"Total test structures: {len(structures)}")
    print(f"Target waveguide: {mask_designer.wg_width}×{mask_designer.wg_height} µm")
    print(f"Expected propagation loss: {expected_loss:.3f} dB/cm (avg of optimistic and conservative)")
    print(f"Optimistic loss: 0.132 dB/cm, Conservative loss: 2.4 dB/cm")
    chip_area = 2500 * 5000 / 1e6  # mm²
    print(f"Chip area utilized: ~{chip_area:.1f} mm²")
    print("\nProcess Specifications:")
    print(PROCESS_SPECIFICATIONS)
    print("Layer Mapping:", LAYER_MAPPING)
    print("\n🎯 MEASUREMENT PRIORITY:")
    print("1. Cut-back loss (1, 5, 10 mm waveguides)")
    print("2. Taper insertion loss (5, 10, 20 µm lengths)") 
    print("3. Ring resonator Q-factor and FSR")
    print("4. Rib waveguide confinement vs etch depth")
    print("5. Process control monitor correlation")
    print("\nMeasurement Protocol:")
    print(MEASUREMENT_PROTOCOL)

if __name__ == "__main__":
    main()
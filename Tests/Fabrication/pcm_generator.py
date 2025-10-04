#!/usr/bin/env python3
"""
PCM Generator: Multi-Concentration TE Doping Stripes
Automatically generates Process Control Monitors for doping gradient characterization
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import json

class PCMGenerator:
    def __init__(self, chip_size=5000, feature_size=0.22):
        self.chip_size = chip_size
        self.feature_size = feature_size
        self.structures = []
        
    def generate_te_doping_stripes(self, concentrations=[1e18, 5e18, 1e19, 5e19], 
                                 stripe_width=500, stripe_height=300):
        """Generate TE doping concentration test stripes"""
        print("Generating TE doping gradient PCMs...")
        
        x_start = 3500
        y_start = 2000
        
        for i, conc in enumerate(concentrations):
            # Main doping stripe (for SIMS measurement)
            stripe_id = f"Te_{self._format_concentration(conc)}"
            
            self.structures.append({
                'type': 'doping_stripe',
                'x': x_start,
                'y': y_start + i * stripe_height,
                'width': stripe_width,
                'height': stripe_height,
                'doping_concentration': conc,
                'label': stripe_id,
                'layer': 'doping_pcm'
            })
            
            # Add waveguide test structures on each doping stripe
            self._add_waveguide_test_structures(x_start, y_start + i * stripe_height, 
                                              stripe_width, stripe_height, conc)
            
            # Add alignment marks for each stripe
            self._add_doping_alignment_marks(x_start, y_start + i * stripe_height, 
                                           stripe_width, stripe_height, stripe_id)
        
        return self.structures
    
    def _format_concentration(self, conc):
        """Format concentration for labels (1e18 -> 1E18)"""
        if conc >= 1e19:
            return f"{int(conc/1e18)}E19"
        else:
            return f"{int(conc/1e18)}E18"
    
    def _add_waveguide_test_structures(self, x, y, width, height, concentration):
        """Add waveguide test structures to doping stripe"""
        # Straight waveguide for cut-back
        wg_length = 200
        self.structures.append({
            'type': 'waveguide',
            'x': x + 50,
            'y': y + 100,
            'width': 0.22,
            'length': wg_length,
            'doping_concentration': concentration,
            'label': f'WG_{self._format_concentration(concentration)}_straight',
            'layer': 'waveguide'
        })
        
        # Ring resonator for Q-factor measurement
        ring_radius = 5
        self.structures.append({
            'type': 'ring_resonator',
            'x': x + 300,
            'y': y + 150,
            'radius': ring_radius,
            'width': 0.22,
            'gap': 0.2,
            'doping_concentration': concentration,
            'label': f'Ring_{self._format_concentration(concentration)}_R{ring_radius}',
            'layer': 'ring_pcm'
        })
        
        # Grating couplers
        self.structures.extend([
            {
                'type': 'grating_coupler',
                'x': x + 20,
                'y': y + 100,
                'width': 20,
                'length': 50,
                'label': f'GC_{self._format_concentration(concentration)}_in',
                'layer': 'grating'
            },
            {
                'type': 'grating_coupler',
                'x': x + 250,
                'y': y + 100,
                'width': 20,
                'length': 50,
                'label': f'GC_{self._format_concentration(concentration)}_out',
                'layer': 'grating'
            }
        ])
    
    def _add_doping_alignment_marks(self, x, y, width, height, stripe_id):
        """Add alignment marks for doping stripe registration"""
        mark_size = 10
        
        # Cross alignment marks at corners
        marks = [
            (x + 10, y + 10),  # Top-left
            (x + width - 20, y + 10),  # Top-right
            (x + 10, y + height - 20),  # Bottom-left
            (x + width - 20, y + height - 20)  # Bottom-right
        ]
        
        for i, (mx, my) in enumerate(marks):
            self.structures.append({
                'type': 'alignment_cross',
                'x': mx,
                'y': my,
                'size': mark_size,
                'label': f'Align_{stripe_id}_{i}',
                'layer': 'alignment'
            })
    
    def generate_geometry_pcms(self, x_start=2000, y_start=500):
        """Generate geometry variation PCMs (width, etch depth)"""
        print("Generating geometry variation PCMs...")
        
        # Width variation PCMs
        widths = [0.18, 0.20, 0.22, 0.24, 0.26]
        for i, width in enumerate(widths):
            self.structures.append({
                'type': 'waveguide',
                'x': x_start + i * 60,
                'y': y_start,
                'width': width,
                'length': 200,
                'label': f'PCM_width_{width}um',
                'layer': 'width_pcm'
            })
        
        # Etch depth PCMs
        etch_depths = [0.65, 0.70, 0.75, 0.80, 0.85]
        for i, depth in enumerate(etch_depths):
            self.structures.append({
                'type': 'etch_test',
                'x': x_start + i * 60,
                'y': y_start + 100,
                'width': 10,
                'length': 50,
                'etch_depth': depth,
                'label': f'PCM_etch_{depth}',
                'layer': 'etch_pcm'
            })
        
        return self.structures
    
    def generate_roughness_pcms(self, x_start=2000, y_start=700):
        """Generate sidewall roughness test structures"""
        print("Generating roughness PCMs...")
        
        # Different grating periods for roughness characterization
        periods = [0.2, 0.3, 0.4, 0.5, 0.6]  # µm
        
        for i, period in enumerate(periods):
            self.structures.append({
                'type': 'roughness_test',
                'x': x_start + i * 80,
                'y': y_start,
                'width': 5,
                'length': 100,
                'grating_period': period,
                'label': f'PCM_roughness_{period}um',
                'layer': 'roughness_pcm'
            })
        
        return self.structures
    
    def generate_gds_layer_mapping(self):
        """Generate GDSII layer mapping for fabrication"""
        layer_mapping = {
            'waveguide': (1, 0),
            'doping_pcm': (10, 0),
            'ring_pcm': (11, 0),
            'grating': (20, 0),
            'alignment': (100, 0),
            'width_pcm': (12, 0),
            'etch_pcm': (13, 0),
            'roughness_pcm': (14, 0)
        }
        
        return layer_mapping
    
    def generate_fab_instructions(self):
        """Generate fabrication instructions for PCMs"""
        instructions = {
            'te_doping_gradient': {
                'description': 'Multi-concentration Tellurium doping stripes',
                'implantation_energy': '50-100 keV',
                'dose_calibration': 'SIMS verification required for each stripe',
                'annealing': '1000°C, 30s RTA',
                'metrology': ['SIMS', 'Ellipsometry', 'Four-point probe']
            },
            'geometry_pcms': {
                'description': 'Process variation monitors',
                'width_tolerance': '±10 nm',
                'etch_depth_tolerance': '±5%',
                'metrology': ['SEM cross-section', 'AFM', 'Optical profiler']
            },
            'roughness_pcms': {
                'description': 'Sidewall roughness characterization',
                'target_roughness': '< 3 nm RMS',
                'metrology': ['AFM', 'TEM', 'Light scattering']
            }
        }
        
        return instructions
    
    def visualize_pcms(self):
        """Create visualization of all PCM structures"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        colors = {
            'doping_stripe': 'lightblue',
            'waveguide': 'darkblue',
            'ring_resonator': 'purple',
            'grating_coupler': 'orange',
            'alignment_cross': 'red',
            'etch_test': 'green',
            'roughness_test': 'brown'
        }
        
        for struct in self.structures:
            color = colors.get(struct['type'], 'gray')
            
            if struct['type'] == 'doping_stripe':
                rect = Rectangle((struct['x'], struct['y']), struct['width'], struct['height'],
                               facecolor=color, alpha=0.3, edgecolor='black')
                ax.add_patch(rect)
                # Add concentration label
                ax.text(struct['x'] + struct['width']/2, struct['y'] + struct['height']/2,
                       f"Te {struct['doping_concentration']:.1e}", 
                       ha='center', va='center', fontsize=8, weight='bold')
                
            elif struct['type'] == 'waveguide':
                rect = Rectangle((struct['x'], struct['y']), struct['length'], struct['width'],
                               facecolor=color, alpha=0.7, edgecolor='black')
                ax.add_patch(rect)
                
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
            
            # Add label
            if 'label' in struct:
                ax.text(struct['x'], struct['y'] - 5, struct['label'], 
                       fontsize=6, ha='left', va='top', rotation=45)
        
        ax.set_xlim(0, self.chip_size)
        ax.set_ylim(0, self.chip_size)
        ax.set_aspect('equal')
        ax.set_xlabel('X Position (µm)')
        ax.set_ylabel('Y Position (µm)')
        ax.set_title('Process Control Monitors (PCMs) Layout')
        ax.grid(True, alpha=0.3)
        
        # Create legend
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, label=label)
                         for label, color in colors.items()]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig('pcm_layout.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_to_json(self, filename='pcm_design.json'):
        """Export PCM design to JSON file"""
        design_data = {
            'metadata': {
                'chip_size': self.chip_size,
                'feature_size': self.feature_size,
                'timestamp': np.datetime64('now').astype(str),
                'version': '1.0'
            },
            'layer_mapping': self.generate_gds_layer_mapping(),
            'fab_instructions': self.generate_fab_instructions(),
            'structures': self.structures
        }
        
        with open(filename, 'w') as f:
            json.dump(design_data, f, indent=2)
        
        print(f"PCM design exported to {filename}")
        return design_data
    
    def generate_fab_report(self):
        """Generate comprehensive fabrication report"""
        report = f"""
=== PCM FABRICATION REPORT ===
Generated: {np.datetime64('now').astype(str)}

DESIGN SUMMARY:
- Chip size: {self.chip_size} × {self.chip_size} µm
- Total PCM structures: {len(self.structures)}
- Feature size: {self.feature_size} µm

TE DOPING GRADIENT:
- Concentrations: 1×10¹⁸, 5×10¹⁸, 1×10¹⁹, 5×10¹⁹ atoms/cm³
- Each concentration has: waveguide, ring resonator, alignment marks
- SIMS verification required for each stripe

GEOMETRY PCMS:
- Width variations: 0.18, 0.20, 0.22, 0.24, 0.26 µm
- Etch depth variations: 65%, 70%, 75%, 80%, 85%

METROLOGY REQUIREMENTS:
1. SIMS: Te concentration per stripe
2. Ellipsometry: Refractive index vs doping
3. SEM: Cross-section for geometry verification
4. AFM: Sidewall roughness < 3 nm RMS
5. Optical: Cut-back loss measurement

CRITICAL PARAMETERS:
- Doping uniformity: ±10% within stripe
- Etch depth tolerance: ±5%
- Overlay accuracy: < 100 nm
- Sidewall roughness: < 3 nm RMS
        """
        
        print(report)
        return report

def main():
    """Main PCM generation function"""
    print("=== PROCESS CONTROL MONITOR GENERATOR ===")
    
    # Initialize PCM generator
    pcm_gen = PCMGenerator(chip_size=5000, feature_size=0.22)
    
    # Generate all PCM types
    pcm_gen.generate_te_doping_stripes()
    pcm_gen.generate_geometry_pcms()
    pcm_gen.generate_roughness_pcms()
    
    # Visualize and export
    pcm_gen.visualize_pcms()
    pcm_gen.export_to_json()
    
    # Generate reports
    pcm_gen.generate_fab_report()
    
    # Display summary
    print(f"\n=== GENERATION COMPLETE ===")
    print(f"Total PCM structures generated: {len(pcm_gen.structures)}")
    print(f"TE doping concentrations: 4 stripes (1E18 to 5E19 atoms/cm³)")
    print(f"Geometry variations: 5 widths + 5 etch depths")
    print(f"Roughness test structures: 5 different periods")
    
    return pcm_gen

if __name__ == "__main__":
    pcm_design = main()
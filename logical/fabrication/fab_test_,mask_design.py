
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import math

class FabTestMaskDesign:
    def __init__(self, chip_size=5000, waveguide_width=0.22, waveguide_height=0.18):
        self.wg_width = waveguide_width
        self.wg_height = waveguide_height
    
    def straight_waveguide_array(self, lengths=[1000, 5000, 10000]):
        structures = []
        y_position = 1500
        wide_width = 0.40
        narrow_width = 0.22
        
        for i, taper_len in enumerate(taper_lengths):
            structures.append({
                'type': 'waveguide',
                'x': 100, 'y': y_position,
                'width': wide_width, 'length': 50,
                'label': f'Wide_in_{taper_len}um'
            })
            
            structures.append({
                'type': 'taper',
                'x': 150, 'y': y_position,
                'width_start': wide_width, 'width_end': narrow_width,
                'length': taper_len,
                'label': f'Taper_{taper_len}um'
            })
            
            structures.append({
                'type': 'waveguide', 
                'x': 150 + taper_len, 'y': y_position,
                'width': narrow_width, 'length': 50,
                'label': f'Narrow_out_{taper_len}um'
            })
            
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
        structures = []
        y_position = 4500
        
        structures.append({
            'type': 'waveguide',
            'x': 100, 'y': y_position,
            'width': self.wg_width, 'length': 100,
            'label': 'Ring_bus_waveguide'
        })
        
        structures.append({
            'type': 'ring_resonator',
            'x': 150, 'y': y_position,
            'radius': radius,
            'width': self.wg_width,
            'gap': gap,
            'coupling_length': coupling_length,
            'label': f'Ring_R{radius}um_gap{gap}um'
        })
        
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
        print("=== FAB TEST MASK DESIGN ===")
        print("Waveguide geometry: 0.22×0.18 µm (single-mode)")
        print(f"Chip size: {self.chip_size}×{self.chip_size} µm")
        print()
        
        all_structures = []
        
        all_structures.extend(self.straight_waveguide_array())
        all_structures.extend(self.taper_designs())
        all_structures.extend(self.rib_waveguide_variants())
        all_structures.extend(self.ring_resonator_design())
        all_structures.extend(self.process_control_monitors())
        
        return all_structures
    
    def calculate_expected_performance(self):
        FSR_corrected = (1.55**2) / (n_g * circumference * 1e-3)
        print(f"Ring R={radius}µm, n_eff={n_eff}:")
        print(f"  FSR (n_eff): {FSR:.1f} nm")
        print(f"  FSR (n_g): {FSR_corrected:.1f} nm")
        return FSR_corrected

def visualize_mask_design(structures):
    structures = []
    cross_positions = [(100, 100), (4900, 100), (100, 4900), (4900, 4900)]
    for x, y in cross_positions:
        structures.append({'type': 'alignment_cross', 'x': x, 'y': y, 'size': 50})
    scribe_width = 100
    structures.extend([
        {'type': 'scribe_line', 'x': 0, 'y': 0, 'width': 5000, 'height': scribe_width},
        {'type': 'scribe_line', 'x': 0, 'y': 4900, 'width': 5000, 'height': scribe_width},
        {'type': 'scribe_line', 'x': 0, 'y': 0, 'width': scribe_width, 'height': 5000},
        {'type': 'scribe_line', 'x': 4900, 'y': 0, 'width': scribe_width, 'height': 5000},
    ])
    return structures

LAYER_MAPPING = {
}



def generate_gds_script(structures):
    print("Integrating PCMs into mask design...")
    
    existing_pcm_types = ['pcm_etch', 'pcm_width']
    filtered_structures = [s for s in mask_structures 
                          if s.get('type') not in existing_pcm_types]
    
    integrated_structures = filtered_structures + pcm_structures
    
    print(f"Added {len(pcm_structures)} PCM structures")
    print(f"Total structures in mask: {len(integrated_structures)}")
    
    return integrated_structures

def main():

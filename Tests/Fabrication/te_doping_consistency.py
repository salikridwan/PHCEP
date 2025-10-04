#!/usr/bin/env python3
"""
CRITICAL FIX: TE Doping Gradient Implementation
Adding multi-concentration test structures to resolve the 1e18 vs 5e19 discrepancy
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class DopingGradientDesign:
    def __init__(self):
        self.doping_concentrations = [
            1e18,   # Optimal from material sims (0.132 dB/cm target)
            5e18,   # Intermediate point  
            1e19,   # Moderate doping
            5e19    # High doping (original spec)
        ]
        
    def create_doping_test_structures(self):
        """Create test stripes for different TE doping concentrations"""
        structures = []
        x_start = 3500
        y_start = 2000
        stripe_width = 200
        stripe_length = 500
        
        for i, conc in enumerate(self.doping_concentrations):
            structures.append({
                'type': 'doping_test_stripe',
                'x': x_start,
                'y': y_start + i * 300,
                'width': stripe_width,
                'length': stripe_length,
                'doping_concentration': conc,
                'label': f'Te_doping_{conc:.0e}'
            })
            
            # Add waveguide test structure on each doping stripe
            structures.append({
                'type': 'waveguide',
                'x': x_start + 50,
                'y': y_start + i * 300 + 100,
                'width': 0.22,
                'length': 400,
                'label': f'WG_Te_{conc:.0e}'
            })
        
        return structures
    
    def update_process_specs(self):
        """Updated process specifications with doping gradient"""
        return """
FILM STACK:
- Silicon thickness: 360 nm (±10 nm)
- TE DOPING GRADIENT: Four concentrations across wafer
  * Region A: 1×10¹⁸ atoms/cm³ (optimal low-loss target)
  * Region B: 5×10¹⁸ atoms/cm³  
  * Region C: 1×10¹⁹ atoms/cm³
  * Region D: 5×10¹⁹ atoms/cm³ (original spec)
- Rib etch depths: 252 nm (70%), 270 nm (75%), 288 nm (80%)
- Oxide cladding: 2 µm PECVD SiO₂

DOPING IMPLANTATION:
- Use masked implantation for gradient
- Implant energy: 50-100 keV for 360 nm Si
- Anneal: 1000°C, 30s RTA
- SIMS verification required on each region
"""

# Add this to the main FabTestMaskDesign class
def add_doping_gradient_structures(self):
    """Add TE doping gradient test structures to mask"""
    doping_designer = DopingGradientDesign()
    return doping_designer.create_doping_test_structures()

# Update the main mask generation
def generate_mask_layout(self):
    """Generate complete mask layout with doping gradient"""
    print("=== FAB TEST MASK DESIGN ===")
    print("Waveguide geometry: 0.22×0.18 µm (single-mode)")
    print(f"Chip size: {self.chip_size}×{self.chip_size} µm")
    print("TE DOPING: Gradient across wafer (1e18 to 5e19 atoms/cm³)")
    print()
    
    all_structures = []
    
    # Add all test structures
    all_structures.extend(self.straight_waveguide_array())
    all_structures.extend(self.taper_designs())
    all_structures.extend(self.rib_waveguide_variants())
    all_structures.extend(self.ring_resonator_design())
    all_structures.extend(self.process_control_monitors())
    all_structures.extend(self.add_doping_gradient_structures())  # NEW
    all_structures.extend(add_fiducials_and_scribe())
    
    return all_structures
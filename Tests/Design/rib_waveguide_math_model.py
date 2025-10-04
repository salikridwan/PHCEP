#!/usr/bin/env python3
"""
MATH TEST: Rib Waveguide Single-Mode Condition
Mathematical model for partial-etch waveguides
"""

import numpy as np
import math

class RibWaveguideMath:
    def __init__(self, total_height=0.36, n_core=3.48, n_clad=1.44):
        self.total_height = total_height
        self.n_core = n_core
        self.n_clad = n_clad
        self.wavelength = 1.55
        
    def calculate_effective_index(self, etch_depth_ratio):
        """
        Mathematical approximation of rib waveguide effective index
        etch_depth_ratio: 0 (no etch) to 1 (full etch)
        """
        # Simplified model: effective index decreases with etch depth
        n_slab = self.n_core  # Unetched region
        n_ridge = self.n_core - (self.n_core - self.n_clad) * etch_depth_ratio
        
        # Weighted average based on etch ratio
        n_eff = etch_depth_ratio * n_ridge + (1 - etch_depth_ratio) * n_slab
        return n_eff
    
    def rib_v_parameter(self, width, etch_depth_ratio):
        """Calculate effective V-parameter for rib waveguide"""
        n_eff = self.calculate_effective_index(etch_depth_ratio)
        
        # Use effective index for V-parameter calculation
        delta_n_sq = n_eff**2 - self.n_clad**2
        V_eff = (2 * math.pi * width / self.wavelength) * math.sqrt(delta_n_sq)
        
        return V_eff, n_eff
    
    def find_single_mode_rib(self, target_width=0.40):
        """Mathematically find etch depth for single-mode operation"""
        print("=== MATHEMATICAL RIB WAVEGUIDE OPTIMIZATION ===")
        
        etch_ratios = np.linspace(0.3, 0.8, 20)  # 30% to 80% etch
        valid_designs = []
        
        for ratio in etch_ratios:
            V_eff, n_eff = self.rib_v_parameter(target_width, ratio)
            
            if V_eff < math.pi:  # Single-mode condition
                valid_designs.append({
                    'width': target_width,
                    'etch_ratio': ratio,
                    'etch_depth': ratio * self.total_height,
                    'V_effective': V_eff,
                    'n_effective': n_eff
                })
        
        # Display results
        if valid_designs:
            print(f"Valid single-mode rib designs for width={target_width}µm:")
            for design in valid_designs[:5]:  # Show first 5
                print(f"  Etch ratio: {design['etch_ratio']:.1%} "
                      f"(depth: {design['etch_depth']:.3f}µm) → "
                      f"V_eff={design['V_effective']:.3f}, n_eff={design['n_effective']:.3f}")
            
            # Recommend optimal
            optimal = min(valid_designs, key=lambda x: abs(x['etch_ratio'] - 0.5))
            print(f"\n🎯 OPTIMAL RIB DESIGN:")
            print(f"  Width: {optimal['width']}µm")
            print(f"  Etch ratio: {optimal['etch_ratio']:.1%}")
            print(f"  Etch depth: {optimal['etch_depth']:.3f}µm")
            print(f"  Effective V: {optimal['V_effective']:.3f} (< π)")
            
            return optimal
        else:
            print("❌ No single-mode rib design found for this width")
            return None

# Mathematical proof of rib waveguide advantage
def rib_waveguide_proof():
    """Mathematical demonstration of rib waveguide benefits"""
    print("\n=== MATHEMATICAL RIB WAVEGUIDE PROOF ===")
    
    # Compare straight vs rib waveguide
    width = 0.40
    rib_math = RibWaveguideMath()
    
    # Straight waveguide V-parameter
    V_straight = (2 * math.pi * width / 1.55) * math.sqrt(3.48**2 - 1.44**2)
    print(f"Straight waveguide {width}µm: V = {V_straight:.3f}")
    print(f"Single-mode? {V_straight < math.pi}")
    
    # Rib waveguide with 50% etch
    V_rib, n_eff = rib_math.rib_v_parameter(width, 0.5)
    print(f"Rib waveguide {width}µm (50% etch): V_eff = {V_rib:.3f}")
    print(f"Single-mode? {V_rib < math.pi}")
    print(f"Effective index reduction: {3.48 - n_eff:.3f}")
    
    # Confinement factor approximation
    confinement_straight = 1 - math.exp(-V_straight**2 / 10)
    confinement_rib = 1 - math.exp(-V_rib**2 / 10)
    
    print(f"\nConfinement factor comparison:")
    print(f"Straight: {confinement_straight:.3f}")
    print(f"Rib: {confinement_rib:.3f}")
    print(f"Confinement reduction: {confinement_straight - confinement_rib:.3f}")

if __name__ == "__main__":
    # Rib waveguide mathematical optimization
    rib_designer = RibWaveguideMath()
    optimal_rib = rib_designer.find_single_mode_rib(0.40)
    
    # Mathematical proof
    rib_waveguide_proof()
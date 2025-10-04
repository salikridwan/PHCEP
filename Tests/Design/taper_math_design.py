#!/usr/bin/env python3
"""
MATH TEST: Adiabatic Taper Design
Mathematical validation of mode-filtering tapers
"""

import numpy as np
import math

class TaperMathTest:
    def __init__(self):
        self.wide_width = 0.40    # µm (multi-mode section)
        self.narrow_width = 0.22  # µm (single-mode section)
        
    def calculate_adiabatic_length(self, delta_neff=0.5):
        """
        Mathematical adiabatic condition: L > λ / (2 * Δneff)
        where Δneff is the effective index difference between fundamental and first higher mode
        """
        wavelength = 1.55  # µm
        minimum_length = wavelength / (2 * delta_neff)
        
        # Practical safety factor
        safety_factor = 3.0
        recommended_length = minimum_length * safety_factor
        
        return minimum_length, recommended_length
    
    def test_taper_designs(self):
        """Mathematical test of various taper lengths"""
        print("=== MATHEMATICAL TAPER DESIGN VERIFICATION ===")
        
        # Test different mode index differences
        delta_neff_cases = [0.1, 0.3, 0.5, 0.7]
        
        for delta_neff in delta_neff_cases:
            min_len, rec_len = self.calculate_adiabatic_length(delta_neff)
            
            print(f"\nΔneff = {delta_neff}:")
            print(f"  Minimum length: {min_len:.1f} µm")
            print(f"  Recommended: {rec_len:.1f} µm")
            print(f"  Taper angle: {math.degrees(math.atan((0.40-0.22)/2/rec_len)):.2f}°")
        
        # Optimal design recommendation
        optimal_delta_neff = 0.5  # Typical for silicon waveguides
        min_len, rec_len = self.calculate_adiabatic_length(optimal_delta_neff)
        
        print(f"\n🎯 OPTIMAL TAPER DESIGN:")
        print(f"  Width: {self.wide_width}µm → {self.narrow_width}µm")
        print(f"  Length: {rec_len:.0f} µm")
        print(f"  Taper angle: {math.degrees(math.atan((0.40-0.22)/2/rec_len)):.2f}°")

# Mathematical taper validation
def validate_taper_math():
    """Pure mathematical taper validation"""
    print("\n=== MATHEMATICAL TAPER VALIDATION ===")
    
    # Adiabatic condition derivation
    λ = 1.55
    Δneff = 0.5
    L_min = λ / (2 * Δneff)
    
    print("Adiabatic condition derivation:")
    print(f"L > λ / (2 × Δneff)")
    print(f"L > {λ} / (2 × {Δneff})")
    print(f"L > {L_min:.2f} µm")
    
    # Power transfer calculation
    def power_transfer(L, Δβ, coupling=0.1):
        """Calculate power remaining in fundamental mode"""
        # Simplified model: P_fundamental = 1 - exp(-L/Δβ) * coupling
        return 1 - math.exp(-L/Δβ) * coupling
    
    # Test various lengths
    lengths = [5, 10, 20, 30]
    Δβ = 10  # Propagation constant difference
    
    print("\nPower transfer estimation:")
    for L in lengths:
        P_fund = power_transfer(L, Δβ)
        print(f"L = {L:2d} µm → Fundamental mode power: {P_fund:.1%}")
    
    return L_min

if __name__ == "__main__":
    # Taper mathematical design
    taper_test = TaperMathTest()
    taper_test.test_taper_designs()
    
    # Mathematical validation
    L_min = validate_taper_math()
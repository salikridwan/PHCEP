
import numpy as np
import math

class TaperMathTest:
    def __init__(self):
        
    def calculate_adiabatic_length(self, delta_neff=0.5):
        minimum_length = wavelength / (2 * delta_neff)
        
        safety_factor = 3.0
        recommended_length = minimum_length * safety_factor
        
        return minimum_length, recommended_length
    
    def test_taper_designs(self):
    print("\n=== MATHEMATICAL TAPER VALIDATION ===")
    
    λ = 1.55
    Δneff = 0.5
    L_min = λ / (2 * Δneff)
    
    print("Adiabatic condition derivation:")
    print(f"L > λ / (2 × Δneff)")
    print(f"L > {λ} / (2 × {Δneff})")
    print(f"L > {L_min:.2f} µm")
    
    def power_transfer(L, Δβ, coupling=0.1):

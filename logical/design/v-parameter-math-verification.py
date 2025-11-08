
import numpy as np
import math

class SingleModeMathTest:
    def __init__(self, n_core=3.48, n_clad=1.44, wavelength=1.55):
        self.n_core = n_core
        self.n_clad = n_clad
        self.wavelength = wavelength
        self.pi = math.pi
        
    def calculate_v_parameters(self, width, height):
        Vx, Vy = self.calculate_v_parameters(width, height)
        return Vx < self.pi and Vy < self.pi, Vx, Vy
    
    def calculate_safe_margin(self, Vx, Vy):
        test_cases = [
            (0.40, 0.36, "Original problematic"),
            (0.22, 0.18, "Recommended single-mode"),
            (0.26, 0.22, "Conservative alternative"),
            (0.30, 0.28, "Liberal single-mode"),
            (0.35, 0.25, "Intermediate case")
        ]
        
        print("=== MATHEMATICAL SINGLE-MODE VERIFICATION ===")
        print(f"Parameters: n_core={self.n_core}, n_clad={self.n_clad}, λ={self.wavelength}µm")
        print(f"Single-mode condition: Vx < π AND Vy < π (π ≈ {self.pi:.3f})")
        print()
        
        results = []
        for width, height, desc in test_cases:
            valid, Vx, Vy = self.is_single_mode(width, height)
            margin = self.calculate_safe_margin(Vx, Vy)
            
            status = "PASS" if valid else "FAIL"
            results.append({
                'width': width, 'height': height, 'description': desc,
                'Vx': Vx, 'Vy': Vy, 'valid': valid, 'margin': margin
            })
            
            print(f"{desc:>25}: {width}×{height}µm → Vx={Vx:.3f}, Vy={Vy:.3f} → {status}")
            if valid:
                print(f"{'':>25}  Safety margin: {margin:.3f}")
        
        return results

def mathematical_proof():

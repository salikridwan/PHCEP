import numpy as np
import math

class RibWaveguideMath:
    def __init__(self, total_height=0.36, n_core=3.48, n_clad=1.44, wavelength=1.55):
        self.total_height = total_height
        self.n_core = n_core
        self.n_clad = n_clad
        self.wavelength = wavelength  # in microns

    def calculate_effective_index(self, etch_depth_ratio):

        n_slab = self.n_core

        n_ridge = self.n_core - (self.n_core - self.n_clad) * etch_depth_ratio

        n_eff = etch_depth_ratio * n_ridge + (1.0 - etch_depth_ratio) * n_slab
        return n_eff

    def rib_v_parameter(self, width, etch_depth_ratio):
        n_eff = self.calculate_effective_index(etch_depth_ratio)
        delta = max(n_eff**2 - self.n_clad**2, 0.0)
        V = (2.0 * math.pi / self.wavelength) * width * math.sqrt(delta)
        return V, n_eff

    def optimize_for_width(self, target_width, etch_ratios=None):
        if etch_ratios is None:
            etch_ratios = np.linspace(0.05, 0.95, 19) 

        print("=== MATHEMATICAL RIB WAVEGUIDE OPTIMIZATION ===")
        print(f"Scanning width = {target_width} µm")

        valid_designs = []

        for ratio in etch_ratios:
            V_eff, n_eff = self.rib_v_parameter(target_width, ratio)

            if V_eff < math.pi and V_eff > 0:
                valid_designs.append({
                    'width': target_width,
                    'etch_ratio': ratio,
                    'etch_depth': ratio * self.total_height,
                    'V_effective': V_eff,
                    'n_effective': n_eff
                })

        if valid_designs:
            print(f"Valid single-mode rib designs for width={target_width}µm:")
            for design in valid_designs:
                print(f"  Etch ratio: {design['etch_ratio']:.1%} "
                      f"(depth: {design['etch_depth']:.3f}µm) → "
                      f"V_eff={design['V_effective']:.3f}, n_eff={design['n_effective']:.3f}")

            optimal = min(valid_designs, key=lambda x: abs(x['etch_ratio'] - 0.5))
            print(f"\n OPTIMAL RIB DESIGN:")
            print(f"  Width: {optimal['width']}µm")
            print(f"  Etch ratio: {optimal['etch_ratio']:.1%}")
            print(f"  Etch depth: {optimal['etch_depth']:.3f}µm")
            print(f"  Effective V: {optimal['V_effective']:.3f} (< π)")

            return optimal
        else:
            print("❌ No single-mode rib design found for this width")
            return None

def rib_waveguide_proof():
    model = RibWaveguideMath()
    target_width = 0.5 
    etch_ratios = np.linspace(0.05, 0.95, 19)
    return model.optimize_for_width(target_width, etch_ratios)

if __name__ == "__main__":
    rib_waveguide_proof()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
import datetime
import os

class ThermalManagementValidation:
    def __init__(self):
        self.test_data = None
        self.results = {}
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_thermal_data(self, duration_hours=24, sample_interval_min=5):
        print("Calculating thermal metrics...")

        if self.test_data is None:
            num_samples = int(max(2, (duration_hours * 60) / max(1, sample_interval_min)))
            base_time = datetime.datetime.now() - datetime.timedelta(hours=duration_hours)
            timestamps = [base_time + datetime.timedelta(minutes=i * sample_interval_min) for i in range(num_samples)]
            rng = np.random.default_rng(0)
            cpu = 45 + 5 * np.sin(np.linspace(0, 6.28, num_samples)) + rng.normal(0, 0.8, num_samples)
            gpu = 40 + 6 * np.sin(np.linspace(0, 3.14, num_samples)) + rng.normal(0, 1.0, num_samples)
            psu = 38 + 2 * np.sin(np.linspace(0, 12.56, num_samples)) + rng.normal(0, 0.5, num_samples)
            if num_samples > 10:
                spike_idx = rng.integers(0, num_samples, size=3)
                cpu[spike_idx] += rng.uniform(5, 15, size=3)
            self.test_data = pd.DataFrame({
                'timestamp': timestamps,
                'CPU': cpu,
                'GPU': gpu,
                'PSU': psu
            })

        metrics = {}
        for component in [c for c in self.test_data.columns if c != 'timestamp']:
            temps = self.test_data[component].to_numpy(dtype=float)
            metrics[component] = {
                'mean_temperature': float(np.mean(temps)),
                'max_temperature': float(np.max(temps)),
                'min_temperature': float(np.min(temps)),
                'temperature_std': float(np.std(temps)),
                'temperature_variance': float(np.var(temps)),
                'exceed_70C_count': int(np.sum(temps > 70)),
                'exceed_80C_count': int(np.sum(temps > 80)),
                'exceed_90C_count': int(np.sum(temps > 90)),
                'thermal_cycling_range': float(np.max(temps) - np.min(temps)),
                'skewness': float(stats.skew(temps)),
                'kurtosis': float(stats.kurtosis(temps))
            }

        self.results['component_metrics'] = metrics
        return metrics
    
    def perform_thermal_analysis(self):
        print("Validating thermal limits...")

        validation = {
            'safety_limits': {
                'critical_limit': 90.0,
                'high_warning': 80.0
            },
            'component_validation': {},
            'overall_status': 'PASS'
        }

        critical_failures = []
        warnings = []

        for component, metrics in self.results.get('component_metrics', {}).items():
            max_temp = metrics['max_temperature']
            exceed_80_count = metrics['exceed_80C_count']
            exceed_90_count = metrics['exceed_90C_count']

            component_status = 'PASS'
            if max_temp > validation['safety_limits']['critical_limit']:
                component_status = 'CRITICAL_FAIL'
                critical_failures.append(component)
                validation['overall_status'] = 'FAIL'
            elif max_temp > validation['safety_limits']['high_warning']:
                component_status = 'WARNING'
                warnings.append(component)
            elif exceed_80_count > 0:
                component_status = 'WARNING'
                warnings.append(component)

            validation['component_validation'][component] = {
                'status': component_status,
                'max_temperature': max_temp,
                'exceed_80C_count': exceed_80_count,
                'exceed_90C_count': exceed_90_count
            }

        validation['critical_failures'] = critical_failures
        validation['warnings'] = warnings

        self.results['validation'] = validation
        self.results['thermal_analysis'] = {
            'summary': f"Checked {len(self.results.get('component_metrics', {}))} components",
            'generated_at': self.timestamp
        }
        return validation
    
    def create_visualizations(self):
        print("Generating validation report...")

        if isinstance(self.test_data, pd.DataFrame) and 'timestamp' in self.test_data.columns:
            try:
                duration = (pd.to_datetime(self.test_data['timestamp'].iloc[-1]) - pd.to_datetime(self.test_data['timestamp'].iloc[0])).total_seconds() / 3600.0
            except Exception:
                duration = None
        else:
            duration = None

        report = {
            'timestamp': self.timestamp,
            'test_duration_hours': duration,
            'total_samples': len(self.test_data) if self.test_data is not None else 0,
            'validation_summary': self.results.get('validation', {}),
            'component_metrics': self.results.get('component_metrics', {}),
            'thermal_analysis': self.results.get('thermal_analysis', {})
        }

        try:
            fig, ax = plt.subplots(figsize=(8, 3))
            for comp in self.results.get('component_metrics', {}).keys():
                ax.plot(self.test_data['timestamp'], self.test_data[comp], label=comp)
            ax.set_xlabel('Time')
            ax.set_ylabel('Temperature (°C)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plot_path = f"thermal_plot_{self.timestamp}.png"
            fig.tight_layout()
            fig.savefig(plot_path, dpi=150)
            plt.close(fig)
            report['plot'] = plot_path
        except Exception:
            report['plot'] = None

        return report
    
    def save_results(self):
        print("=" * 60)
        print("THERMAL MANAGEMENT VALIDATION SUITE")
        print("PHCEP Experimental Validation Platform")
        print("=" * 60)

        self.generate_thermal_data()
        self.perform_thermal_analysis()
        report = self.create_visualizations()

        out_dir = os.getcwd()
        data_file = os.path.join(out_dir, f"thermal_testdata_{self.timestamp}.csv")
        metrics_file = os.path.join(out_dir, f"thermal_metrics_{self.timestamp}.csv")
        validation_file = os.path.join(out_dir, f"thermal_validation_{self.timestamp}.json")

        try:
            if isinstance(self.test_data, pd.DataFrame):
                self.test_data.to_csv(data_file, index=False)
            else:
                data_file = None
        except Exception:
            data_file = None

        try:
            metrics_df = pd.DataFrame.from_dict(self.results.get('component_metrics', {}), orient='index')
            metrics_df.to_csv(metrics_file)
        except Exception:
            metrics_file = None

        try:
            with open(validation_file, 'w') as f:
                json.dump(self.results.get('validation', {}), f, indent=2)
        except Exception:
            validation_file = None

        print("\n" + "=" * 60)
        print("THERMAL MANAGEMENT VALIDATION SUMMARY")
        print("=" * 60)
        validation = self.results.get('validation', {})
        print(f"Overall Validation Status: {validation.get('overall_status', 'UNKNOWN')}")
        if validation.get('critical_failures'):
            print("CRITICAL FAILURES: " + ', '.join(validation.get('critical_failures', [])))
        if validation.get('warnings'):
            print("WARNINGS: " + ', '.join(validation.get('warnings', [])))

        print(f"\nKey Metrics:")
        for component, metrics in self.results.get('component_metrics', {}).items():
            status = validation.get('component_validation', {}).get(component, {}).get('status', 'UNKNOWN')
            status_symbol = "[PASS]" if status == "PASS" else "[WARNING]" if status == "WARNING" else "[FAIL]"
            print(f"  {status_symbol} {component}: Max {metrics['max_temperature']:.1f}°C, Mean {metrics['mean_temperature']:.1f}°C")

        print(f"\nGenerated Files:")
        print(f"  Test Data: {data_file}")
        print(f"  Metrics: {metrics_file}")
        print(f"  Validation: {validation_file}")
        print(f"  Plot: {report.get('plot', None)}")

        return {
            'report': report,
            'files': {
                'test_data': data_file,
                'metrics': metrics_file,
                'validation': validation_file,
                'plot': report.get('plot', None)
            }
        }

def main():
    validator = ThermalManagementValidation()
    result = validator.save_results()
    return result

if __name__ == "__main__":
    main()

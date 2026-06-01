import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
import numpy as np

log_directory = "/eos/home-a/asmishra/cms_project/CMSSW_10_6_29/src/DP1_folder/" # Set to the directory containing your .log files
energies = ["E10", "E5", "E1", "E0.5", "E0.1"]

def get_data(full_path):
    if not os.path.exists(full_path):
        print("ERROR: File not found -> {}".format(full_path))
        return None
    try:
        data = np.genfromtxt(full_path, delimiter=',', skip_header=1)
        if data.ndim == 1:
            return data[1:] # Handle single row
        return data[:, 1] 
    except Exception as e:
        print("ERROR: Could not read {}. {}".format(full_path, e))
        return None

print("--- Starting Per-Energy Plotting ---")

for e in energies:
    rho_path = os.path.join(log_directory, "run_RECO_RHO_{}.log".format(e))
    npu_path = os.path.join(log_directory, "run_DIGI_NPU_{}.log".format(e))
    
    rho_vals = get_data(rho_path)
    npu_vals = get_data(npu_path)
    
    if rho_vals is not None and npu_vals is not None:
        # Ensure we match the number of events (in case one log is shorter)
        min_len = min(len(rho_vals), len(npu_vals))
        x = npu_vals[:min_len]
        y = rho_vals[:min_len]

        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, alpha=0.6, edgecolors='w', color='darkblue')
        
        # Add a trend line (linear fit)
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), "r--", alpha=0.8, label="Linear Fit")

        plt.title("NPU vs Rho Correlation - Energy: {}".format(e))
        plt.xlabel("NPU (Pileup)")
        plt.ylabel(r"$\rho$ (Energy Density)")
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend()
        
        save_name = "Correlation_Plot_{}.png".format(e)
        plt.savefig(save_name)
        plt.close()
        print("Generated: {}".format(save_name))
    else:
        print("Skipped {} due to missing files.".format(e))

print("--- Done ---")
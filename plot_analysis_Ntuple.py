import ROOT
import numpy as np
import matplotlib.pyplot as plt
import os

# Define the list of files to process
# If they are in a specific folder, include the path like "DP1_folder/..."
file_list = [
    "AToGG_GEN_E0.1_new_Ntuple.root",
    "AToGG_GEN_E10_new_Ntuple.root",
    "AToGG_GEN_E0.5_new_Ntuple.root",
    "AToGG_GEN_E1_new_Ntuple.root",
    "AToGG_GEN_E5_new_Ntuple.root"
]

# Helper function to save plots with unique names
def save_hist(data_list, title, xlabel, filename, color, bins=50, x_range=None):
    if not data_list: return # Skip if no data (e.g. no events passed nPho==2)
    plt.figure(figsize=(8, 6))
    plt.hist(data_list, bins=bins, range=x_range, color=color, alpha=0.7, edgecolor='black' if bins < 15 else None)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Events')
    plt.grid(True, alpha=0.3)
    plt.savefig(filename)
    plt.close()

# Main loop
for fname in file_list:
    # Check if file exists (adding DP1_folder prefix if needed)
    path = os.path.join("DP1_folder", fname)
    if not os.path.exists(path):
        print("Skipping: {} not found".format(path))
        continue

    print("Processing: {}...".format(fname))
    
    # Create a unique prefix for images (e.g., "E10" from "AToGG_GEN_E10_new_Ntuple.root")
    # This splits the filename to extract the energy part
    prefix = fname.split('_')[2] 

    f = ROOT.TFile.Open(path)
    tree = f.Get("ntupler/T")
    if not tree:
        print("Error: TTree not found in {}".format(path))
        continue

    data = {'nPho': [], 'l_pt': [], 's_pt': [], 'l_eta': [], 's_eta': [], 'l_phi': [], 's_phi': []}

    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        data['nPho'].append(int(tree.nPhoton))
        
        # In the new .cc, only events with 2 photons exist in the tree
        data['l_pt'].append(tree.leading_pt)
        data['l_eta'].append(tree.leading_eta)
        data['l_phi'].append(tree.leading_phi)
        data['s_pt'].append(tree.subleading_pt)
        data['s_eta'].append(tree.subleading_eta)
        data['s_phi'].append(tree.subleading_phi)

    # Calculate Median
    median_npho = np.median(data['nPho']) if data['nPho'] else 0

    # Log the result
    with open("all_samples_results.log", "a") as log:
        log.write("File: {}, Median Photons: {}, Events: {}\n".format(fname, median_npho, len(data['nPho'])))

    # Save unique plots for this energy point
    save_hist(data['nPho'], '{} - Photon Multiplicity'.format(prefix), 'nPhoton', '{}_nPhoton_dist.png'.format(prefix), 'forestgreen', bins=5, x_range=(0, 5))
    save_hist(data['l_pt'], '{} - Leading $p_{{T}}$'.format(prefix), '$p_{T}$ [GeV]', '{}_leading_pt.png'.format(prefix), 'royalblue', x_range=(0,50))
    save_hist(data['s_pt'], '{} - Subleading $p_{{T}}$'.format(prefix), '$p_{T}$ [GeV]', '{}_subleading_pt.png'.format(prefix), 'crimson', x_range=(0,50))
    save_hist(data['l_eta'], '{} - Leading $\eta$'.format(prefix), '$\eta$', '{}_leading_eta.png'.format(prefix), 'royalblue', x_range=(-3,3))
    save_hist(data['s_eta'], '{} - Subleading $\eta$'.format(prefix), '$\eta$', '{}_subleading_eta.png'.format(prefix), 'crimson', x_range=(-3,3))
    save_hist(data['l_phi'], '{} - Leading $\phi$'.format(prefix), '$\phi$', '{}_leading_phi.png'.format(prefix), 'royalblue', x_range=(-3.15, 3.15))
    save_hist(data['s_phi'], '{} - Subleading $\phi$'.format(prefix), '$\phi$', '{}_subleading_phi.png'.format(prefix), 'crimson', x_range=(-3.15, 3.15))

print("\nAll done! Check your folder for E10_..., E5_..., etc. plots.")
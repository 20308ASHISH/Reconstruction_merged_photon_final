import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    print("Error: Could not retrieve the tree.")
    exit(1)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

total_gen_photons = 0
failed_reco_photons = 0

num_events = tree.GetEntries()
print("Processing {} entries to calculate true detector inefficiency...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
        continue

    for g_idx in range(2):
        g_pt = float(tree.Pho_Gen_Pt[g_idx])
        g_eta = float(tree.Pho_Gen_Eta[g_idx])
        g_phi = float(tree.Pho_Gen_Phi[g_idx])
        
        if g_pt < 10.0 or abs(g_eta) > 2.5:
            continue
            
        total_gen_photons += 1
        
        min_dr = 999.0
        
        for r_idx in range(len(tree.eta)):
            if float(tree.pt[r_idx]) > 10.0:
                dr = calculate_dr(tree.eta[r_idx], tree.phi[r_idx], g_eta, g_phi)
                if dr < min_dr:
                    min_dr = dr
                    
        if min_dr >= 0.1:
            failed_reco_photons += 1

if total_gen_photons > 0:
    inefficiency = float(failed_reco_photons) / total_gen_photons
    error = math.sqrt((inefficiency * (1.0 - inefficiency)) / total_gen_photons)
    
    print("\n--- TRUE DETECTOR INEFFICIENCY RESULTS ---")
    print("Total Gen Photons Inspected: {}".format(total_gen_photons))
    print("True Unreconstructed Photons: {}".format(failed_reco_photons))
    print("Detector Inefficiency:       {:.4f} +/- {:.4f} ({:.2f}%)".format(inefficiency, error, inefficiency * 100))
else:
    print("No generator photons passed the initial acceptance requirements.")

infile.Close()
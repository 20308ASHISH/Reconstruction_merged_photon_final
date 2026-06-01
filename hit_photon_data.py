import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"

infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

merged_events = []
resolved_events = []

num_events = tree.GetEntries()

for entry in range(num_events):
    tree.GetEntry(entry)
    
    signal_gen_photons = []
    if hasattr(tree, 'Pho_Gen_Eta'):
        for g_idx in range(len(tree.Pho_Gen_Eta)):
            signal_gen_photons.append((tree.Pho_Gen_Eta[g_idx], tree.Pho_Gen_Phi[g_idx]))
            
    reco_elements_engaged = set()
    for r_idx in range(len(tree.eta)):
        r_eta = tree.eta[r_idx]
        r_phi = tree.phi[r_idx]
        
        min_dr = 999.0
        for g_idx, (g_eta, g_phi) in enumerate(signal_gen_photons):
            dr = calculate_dr(r_eta, r_phi, g_eta, g_phi)
            if dr < min_dr:
                min_dr = dr
                
        if min_dr < 0.1:
            reco_elements_engaged.add(r_idx)
            
    r_run = getattr(tree, "run", 1)
    r_lumi = getattr(tree, "lumi", 1)
    r_evt = getattr(tree, "event", entry)
            
    if len(reco_elements_engaged) == 1:
        merged_events.append((int(r_run), int(r_lumi), int(r_evt)))
    elif len(reco_elements_engaged) >= 2:
        resolved_events.append((int(r_run), int(r_lumi), int(r_evt)))

infile.Close()

with open("merged_events.txt", "w") as f:
    for evt in merged_events:
        f.write("{}:{}:{}\n".format(evt[0], evt[1], evt[2]))

with open("resolved_events.txt", "w") as f:
    for evt in resolved_events:
        f.write("{}:{}:{}\n".format(evt[0], evt[1], evt[2]))

print("Stored {} merged and {} resolved events.".format(len(merged_events), len(resolved_events)))
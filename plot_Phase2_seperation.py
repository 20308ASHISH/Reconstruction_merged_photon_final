import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_CrystalAnalysis"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

mass_configs = {
    "0.1-1.0":   {"label": "m_{A} = 0.1-1.0 GeV",  "min_m": 0.1, "max_m": 1.0,  "max_h": 150, "bnd": 25, "view": 10},
    "1.0-3.0":   {"label": "m_{A} = 1.0-3.0 GeV",  "min_m": 1.0, "max_m": 3.0,  "max_h": 200, "bnd": 25, "view": 15},
    "3.0-5.0":   {"label": "m_{A} = 3.0-5.0 GeV",  "min_m": 3.0, "max_m": 5.0,  "max_h": 250, "bnd": 25, "view": 20},
    "5.0-7.0":   {"label": "m_{A} = 5.0-7.0 GeV",  "min_m": 5.0, "max_m": 7.0,  "max_h": 300, "bnd": 25, "view": 25},
    "7.0-10.0":  {"label": "m_{A} = 7.0-10.0 GeV", "min_m": 7.0, "max_m": 10.0, "max_h": 350, "bnd": 25, "view": 30}
}

h_left_dict = {}
h_right_dict = {}
best_event_filled = {}

for key, cfg in mass_configs.items():
    bnd = cfg["bnd"]
    view = cfg["view"]
    suffix = key.replace('.', 'p')
    
    h_left_dict[key] = ROOT.TH2F(
        "h_left_{}".format(suffix),
        "RECO LEVEL;#Delta#phi(y_{{1}},y_{{2}}) [crystal units];#Delta#eta(y_{{1}},y_{{2}}) [crystal units]",
        bnd, -0.5, bnd - 0.5, bnd, -0.5, bnd - 0.5
    )
    
    h_right_dict[key] = ROOT.TH2F(
        "h_right_{}".format(suffix),
        "RECO LEVEL ({}, Raw Hits + Pileup);Relative Crystal #phi;Relative Crystal #eta".format(cfg["label"]),
        view * 2 + 1, -view - 0.5, view + 0.5, view * 2 + 1, -view - 0.5, view + 0.5
    )
    h_right_dict[key].GetZaxis().SetTitle("Energy [GeV]")
    best_event_filled[key] = False

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if len(tree.A_Gen_mass) == 0 or not hasattr(tree, 'iEtaPho1') or len(tree.iEtaPho1) == 0:
        continue
        
    event_mass = tree.A_Gen_mass[0]
    current_key = None
    for key, cfg in mass_configs.items():
        if cfg["min_m"] <= event_mass < cfg["max_m"]:
            current_key = key
            break
            
    if not current_key:
        continue

    p1_max = max(range(len(tree.RecHitEnPho1)), key=lambda i: tree.RecHitEnPho1[i])
    p1_eta = tree.iEtaPho1[p1_max]
    p1_phi = tree.iPhiPho1[p1_max]

    if hasattr(tree, 'iEtaPho2') and len(tree.iEtaPho2) > 0:
        p2_max = max(range(len(tree.RecHitEnPho2)), key=lambda i: tree.RecHitEnPho2[i])
        p2_eta = tree.iEtaPho2[p2_max]
        p2_phi = tree.iPhiPho2[p2_max]
        
        delta_eta = abs(p1_eta - p2_eta)
        delta_phi = abs(p1_phi - p2_phi)
        if delta_phi > 180:
            delta_phi = 360 - delta_phi
            
        h_left_dict[current_key].Fill(delta_phi, delta_eta)

    if not best_event_filled[current_key]:
        for i in range(len(tree.iEtaPho1)):
            h_right_dict[current_key].Fill(tree.iPhiPho1[i] - p1_phi, tree.iEtaPho1[i] - p1_eta, tree.RecHitEnPho1[i])
            
        if hasattr(tree, 'iEtaPho2') and len(tree.iEtaPho2) > 0:
            for i in range(len(tree.iEtaPho2)):
                h_right_dict[current_key].Fill(tree.iPhiPho2[i] - p1_phi, tree.iEtaPho2[i] - p1_eta, tree.RecHitEnPho2[i])
                
        best_event_filled[current_key] = True

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    c_combined = ROOT.TCanvas("c_comb_{}".format(suffix), "", 1400, 600)
    c_combined.Divide(2, 1)
    
    c_combined.cd(1)
    ROOT.gPad.SetMargin(0.15, 0.15, 0.12, 0.10)
    if h_left_dict[key].GetEntries() > 0:
        h_left_dict[key].Scale(1.0 / h_left_dict[key].GetEntries())
    h_left_dict[key].Draw("COLZ")
    
    c_combined.cd(2)
    ROOT.gPad.SetMargin(0.15, 0.15, 0.12, 0.10)
    ROOT.gPad.SetLogz(True)
    h_right_dict[key].Draw("COLZ")
    
    c_combined.SaveAs(os.path.join(output_dir, "combined_analysis_mass_{}.png".format(suffix)))
    
    h_left_dict[key].Delete()
    h_right_dict[key].Delete()
    c_combined.Delete()

infile.Close()
print("Plots generated successfully with clean layouts.")
import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kBird)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_phase1_analysis.root"
output_dir = "plot_GenSimAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("demo/T")

if not tree:
    print("Error: Could not open tree 'demo/T'")
    exit(1)

CRYSTAL_SIZE = 0.0174

mass_configs = {
    "0.1-1.0":   {"label": "m_{A} = 0.1-1.0 GeV",  "min_m": 0.1, "max_m": 1.0,  "zoom": 30, "bnd": 6},
    "1.0-3.0":   {"label": "m_{A} = 1.0-3.0 GeV",  "min_m": 1.0, "max_m": 3.0,  "zoom": 30, "bnd": 15},
    "3.0-5.0":   {"label": "m_{A} = 3.0-5.0 GeV",  "min_m": 3.0, "max_m": 5.0,  "zoom": 30, "bnd": 25},
    "5.0-7.0":   {"label": "m_{A} = 5.0-7.0 GeV",  "min_m": 5.0, "max_m": 7.0,  "zoom": 30, "bnd": 35},
    "7.0-10.0":  {"label": "m_{A} = 7.0-10.0 GeV", "min_m": 7.0, "max_m": 10.0, "zoom": 30, "bnd": 55}
}

h_left_dict = {}
h_right_dict = {}
best_event_filled = {}

for key, cfg in mass_configs.items():
    bnd = cfg["bnd"]
    z_lim = cfg["zoom"]
    suffix = key.replace('.', 'p')
    
    h_left_dict[key] = ROOT.TH2F(
        "h_left_{}".format(suffix),
        "GEN LEVEL;#Delta#phi(y_{{1}},y_{{2}})^{{gen}} [crystal units];#Delta#eta(y_{{1}},y_{{2}})^{{gen}} [crystal units]",
        bnd, -0.5, bnd - 0.5, bnd, -0.5, bnd - 0.5
    )
    
    h_right_dict[key] = ROOT.TH2F(
        "h_right_{}".format(suffix),
        "GEN LEVEL ({});Relative Crystal #phi;Relative Crystal #eta".format(cfg["label"]),
        z_lim * 2 + 1, -z_lim - 0.5, z_lim + 0.5, z_lim * 2 + 1, -z_lim - 0.5, z_lim + 0.5
    )
    h_right_dict[key].GetZaxis().SetTitle("Energy Fraction")
    best_event_filled[key] = False

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    photons = []
    for i in range(len(tree.GenPart_pdgId)):
        if tree.GenPart_pdgId[i] == 22:
            photons.append(i)
            
    if len(photons) < 2:
        continue
        
    photons.sort(key=lambda idx: tree.GenPart_pt[idx], reverse=True)
    idx1, idx2 = photons[0], photons[1]
    
    p1 = ROOT.TLorentzVector()
    p2 = ROOT.TLorentzVector()
    p1.SetPtEtaPhiE(tree.GenPart_pt[idx1], tree.GenPart_eta[idx1], tree.GenPart_phi[idx1], tree.GenPart_energy[idx1])
    p2.SetPtEtaPhiE(tree.GenPart_pt[idx2], tree.GenPart_eta[idx2], tree.GenPart_phi[idx2], tree.GenPart_energy[idx2])
    
    event_mass = (p1 + p2).M()
    
    current_key = None
    for key, cfg in mass_configs.items():
        if cfg["min_m"] <= event_mass < cfg["max_m"]:
            current_key = key
            break
            
    if not current_key:
        continue

    deta_rad = abs(tree.GenPart_eta[idx1] - tree.GenPart_eta[idx2])
    dphi_rad = abs(tree.GenPart_phi[idx1] - tree.GenPart_phi[idx2])
    if dphi_rad > math.pi:
        dphi_rad = 2 * math.pi - dphi_rad
        
    delta_eta_cryst = round(deta_rad / CRYSTAL_SIZE)
    delta_phi_cryst = round(dphi_rad / CRYSTAL_SIZE)
    h_left_dict[current_key].Fill(delta_phi_cryst, delta_eta_cryst)

    if not best_event_filled[current_key]:
        z_lim = mass_configs[current_key]["zoom"]
        
        for ph_idx in [idx1, idx2]:
            dphi = tree.GenPart_phi[ph_idx] - tree.GenPart_phi[idx1]
            if dphi > math.pi: dphi -= 2 * math.pi
            if dphi < -math.pi: dphi += 2 * math.pi
                
            mean_phi = round(dphi / CRYSTAL_SIZE)
            mean_eta = round((tree.GenPart_eta[ph_idx] - tree.GenPart_eta[idx1]) / CRYSTAL_SIZE)
            energy = tree.GenPart_energy[ph_idx]
            
            for x in range(-z_lim, z_lim + 1):
                for y in range(-z_lim, z_lim + 1):
                    dist_sq = (x - mean_phi)**2 + (y - mean_eta)**2
                    weight = math.exp(-dist_sq / 1.5)
                    h_right_dict[current_key].Fill(x, y, energy * weight)
                    
        best_event_filled[current_key] = True

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    c_combined = ROOT.TCanvas("c_comb_{}".format(suffix), "", 1400, 600)
    c_combined.Divide(2, 1)
    
    c_combined.cd(1)
    ROOT.gPad.SetMargin(0.15, 0.15, 0.12, 0.10)
    if h_left_dict[key].GetEntries() > 0:
        h_left_dict[key].Scale(1.0 / h_left_dict[key].GetEntries())
    h_left_dict[key].Draw("COLZ")  # Removed TEXT format constraint to keep blocks clean
    
    c_combined.cd(2)
    ROOT.gPad.SetMargin(0.15, 0.15, 0.12, 0.10)
    ROOT.gPad.SetLogz(True)
    h_right_dict[key].Draw("COLZ")
    
    c_combined.SaveAs(os.path.join(output_dir, "combined_analysis_mass_{}.png".format(suffix)))
    
    h_left_dict[key].Delete()
    h_right_dict[key].Delete()
    c_combined.Delete()

infile.Close()
print("Cleaned layout plots generated successfully.")
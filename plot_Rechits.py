import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_RecHitAnalysis"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

mass_configs = {
    "0.1-1.0":   {"label": "m_{A} = 0.1-1.0 GeV",  "min_m": 0.1, "max_m": 1.0,  "max_h": 150},
    "1.0-3.0":   {"label": "m_{A} = 1.0-3.0 GeV",  "min_m": 1.0, "max_m": 3.0,  "max_h": 200},
    "3.0-5.0":   {"label": "m_{A} = 3.0-5.0 GeV",  "min_m": 3.0, "max_m": 5.0,  "max_h": 250},
    "5.0-7.0":   {"label": "m_{A} = 5.0-7.0 GeV",  "min_m": 5.0, "max_m": 7.0,  "max_h": 300},
    "7.0-10.0":  {"label": "m_{A} = 7.0-10.0 GeV",  "min_m": 7.0, "max_m": 10.0, "max_h": 350}
}

h_hits_orig = {}
h_hits_cut = {}

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    h_hits_orig[key] = ROOT.TH1F(
        "h_hits_orig_{}".format(suffix),
        "RECO LEVEL (No Cut) - {};Total Number of RecHits;Fraction of Events".format(cfg["label"]),
        100, 0, cfg["max_h"]
    )
    # Doubled the curly braces around T here to prevent the Python KeyError
    h_hits_cut[key] = ROOT.TH1F(
        "h_hits_cut_{}".format(suffix),
        "RECO LEVEL (p_{{T}} > 10 GeV Cut) - {};Total Number of RecHits;Fraction of Events".format(cfg["label"]),
        100, 0, cfg["max_h"]
    )

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'RecHitEnPho1') or not hasattr(tree, 'pt') or not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
        continue

    v1 = ROOT.TLorentzVector()
    v2 = ROOT.TLorentzVector()
    v1.SetPtEtaPhiE(tree.Pho_Gen_Pt[0], tree.Pho_Gen_Eta[0], tree.Pho_Gen_Phi[0], tree.Pho_Gen_E[0])
    v2.SetPtEtaPhiE(tree.Pho_Gen_Pt[1], tree.Pho_Gen_Eta[1], tree.Pho_Gen_Phi[1], tree.Pho_Gen_E[1])
    event_mass = (v1 + v2).M()
    
    current_key = None
    for key, cfg in mass_configs.items():
        if cfg["min_m"] <= event_mass < cfg["max_m"]:
            current_key = key
            break
            
    if not current_key:
        continue

    n_hits = len(tree.RecHitEnPho1)
    if hasattr(tree, 'RecHitEnPho2'):
        n_hits += len(tree.RecHitEnPho2)

    h_hits_orig[current_key].Fill(n_hits)
    
    pass_pt = False
    for p in tree.pt:
        if p > 10.0:
            pass_pt = True
            break
            
    if pass_pt:
        h_hits_cut[current_key].Fill(n_hits)

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    c_combined = ROOT.TCanvas("c_hits_comb_{}".format(suffix), "", 1400, 600)
    c_combined.Divide(2, 1)
    
    orig_entries = h_hits_orig[key].GetEntries()
    cut_entries = h_hits_cut[key].GetEntries()
    
    if orig_entries > 0:
        h_hits_orig[key].Scale(1.0 / orig_entries)
    if cut_entries > 0:
        h_hits_cut[key].Scale(1.0 / cut_entries)
        
    h_hits_orig_ref = h_hits_orig[key].Clone("h_hits_orig_ref_{}".format(suffix))
    h_hits_orig_ref.SetTitle("") 
    
    h_hits_orig[key].SetLineColor(ROOT.kBlue)
    h_hits_orig[key].SetLineWidth(2)
    
    h_hits_orig_ref.SetLineColor(ROOT.kBlue)
    h_hits_orig_ref.SetLineWidth(2)
    h_hits_orig_ref.SetLineStyle(7) 
    
    h_hits_cut[key].SetLineColor(ROOT.kRed)
    h_hits_cut[key].SetLineWidth(2)
    h_hits_cut[key].SetLineStyle(1)
    
    c_combined.cd(1)
    ROOT.gPad.SetMargin(0.12, 0.05, 0.12, 0.10)
    h_hits_orig[key].Draw("HIST")
    
    leg_left = ROOT.TLegend(0.60, 0.78, 0.92, 0.88)
    leg_left.SetBorderSize(0)
    leg_left.SetFillStyle(0)
    leg_left.AddEntry(h_hits_orig[key], "Original Hits", "l")
    leg_left.Draw()
    
    c_combined.cd(2)
    ROOT.gPad.SetMargin(0.12, 0.05, 0.12, 0.10)
    
    max_orig = h_hits_orig_ref.GetMaximum()
    max_cut = h_hits_cut[key].GetMaximum()
    h_hits_cut[key].SetMaximum(max(max_orig, max_cut) * 1.15)
    
    h_hits_cut[key].Draw("HIST")
    h_hits_orig_ref.Draw("HIST SAME")
    
    leg_right = ROOT.TLegend(0.50, 0.75, 0.92, 0.88)
    leg_right.SetBorderSize(0)
    leg_right.SetFillStyle(0)
    leg_right.AddEntry(h_hits_cut[key], "p_{T} > 10 GeV Cut", "l")
    leg_right.AddEntry(h_hits_orig_ref, "Original Hits Reference", "l")
    leg_right.Draw()
    
    c_combined.SaveAs(os.path.join(output_dir, "rechit_side_by_side_mass_{}.png".format(suffix)))
    
    h_hits_orig[key].Delete()
    h_hits_orig_ref.Delete()
    h_hits_cut[key].Delete()
    c_combined.Delete()

infile.Close()
print("Normalized side-by-side RecHit comparative distributions generated successfully.")
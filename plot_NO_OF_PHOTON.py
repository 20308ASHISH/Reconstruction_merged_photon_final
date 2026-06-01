import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat("g")
ROOT.gStyle.SetTextSize(0.035)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_PhotonMultiplicity"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

mass_configs = {
    "0.1-1.0":   {"label": "m_{A} = 0.7 GeV",  "min_m": 0.1, "max_m": 1.0},
    "1.0-3.0":   {"label": "m_{A} = 2.5 GeV",  "min_m": 1.0, "max_m": 3.0},
    "3.0-5.0":   {"label": "m_{A} = 3.5 GeV",  "min_m": 3.0, "max_m": 5.0},
    "5.0-7.0":   {"label": "m_{A} = 5.5 GeV",  "min_m": 5.0, "max_m": 7.0},
    "7.0-10.0":  {"label": "m_{A} = 9.0 GeV",  "min_m": 7.0, "max_m": 10.0}
}

h_npho_orig = {}
h_npho_cut = {}
h_npho_all = {}

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    h_npho_orig[key] = ROOT.TH1F(
        "h_npho_orig_{}".format(suffix),
        "CMS Simulation ({});Number of Photons (nPho);Events".format(cfg["label"]),
        10, 0, 10
    )
    h_npho_cut[key] = ROOT.TH1F(
        "h_npho_cut_{}".format(suffix),
        "",
        10, 0, 10
    )
    h_npho_all[key] = ROOT.TH1F(
        "h_npho_all_{}".format(suffix),
        "",
        10, 0, 10
    )

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

all_events_npho = []
for entry in range(num_events):
    tree.GetEntry(entry)
    if hasattr(tree, 'nPho'):
        all_events_npho.append(tree.nPho)

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if len(tree.A_Gen_mass) == 0 or not hasattr(tree, 'nPho'):
        continue
        
    event_mass = tree.A_Gen_mass[0]
    current_key = None
    for key, cfg in mass_configs.items():
        if cfg["min_m"] <= event_mass < cfg["max_m"]:
            current_key = key
            break
            
    if not current_key:
        continue

    h_npho_orig[current_key].Fill(tree.nPho)
    
    n_cut = 0
    if hasattr(tree, 'pt'):
        for p in tree.pt:
            if p > 10.0:
                n_cut += 1
                
    h_npho_cut[current_key].Fill(n_cut)

for key in mass_configs.keys():
    for n_val in all_events_npho:
        h_npho_all[key].Fill(n_val)

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    c = ROOT.TCanvas("c_npho_comp_{}".format(suffix), "", 800, 600)
    c.SetMargin(0.12, 0.05, 0.12, 0.10)
    
    h_npho_orig[key].SetLineColor(ROOT.kBlue)
    h_npho_orig[key].SetLineWidth(2)
    h_npho_orig[key].SetLineStyle(2)
    h_npho_orig[key].SetMarkerColor(ROOT.kBlue)
    
    h_npho_cut[key].SetLineColor(ROOT.kRed)
    h_npho_cut[key].SetLineWidth(2)
    h_npho_cut[key].SetLineStyle(1)
    h_npho_cut[key].SetMarkerColor(ROOT.kRed)
    
    h_npho_all[key].SetLineColor(ROOT.kBlack)
    h_npho_all[key].SetLineWidth(2)
    h_npho_all[key].SetLineStyle(1)
    h_npho_all[key].SetMarkerColor(ROOT.kBlack)
    
    max_orig = h_npho_orig[key].GetMaximum()
    max_cut = h_npho_cut[key].GetMaximum()
    max_all = h_npho_all[key].GetMaximum()
    h_npho_orig[key].SetMaximum(max(max_orig, max_cut, max_all) * 1.25)
    
    h_npho_orig[key].Draw("HIST TEXT0")
    h_npho_cut[key].Draw("HIST TEXT0 SAME")
    h_npho_all[key].Draw("HIST TEXT0 SAME")
    
    leg = ROOT.TLegend(0.52, 0.72, 0.92, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(h_npho_orig[key], "Original (Binned)", "l")
    leg.AddEntry(h_npho_cut[key], "p_{T} > 10 GeV (Binned)", "l")
    leg.AddEntry(h_npho_all[key], "All Mass Ranges Combined", "l")
    leg.Draw()
    
    c.SaveAs(os.path.join(output_dir, "photon_multiplicity_mass_{}.png".format(suffix)))
    
    h_npho_orig[key].Delete()
    h_npho_cut[key].Delete()
    h_npho_all[key].Delete()
    c.Delete()

infile.Close()
print("Plots generated successfully with numeric labels.")
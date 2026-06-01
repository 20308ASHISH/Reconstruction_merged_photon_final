import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_RhoAnalysis"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

mass_configs = {
    "0.1-1.0":   {"label": "m_{A} = 0.1-1.0 GeV",  "min_m": 0.1, "max_m": 1.0},
    "1.0-3.0":   {"label": "m_{A} = 1.0-3.0 GeV",  "min_m": 1.0, "max_m": 3.0},
    "3.0-5.0":   {"label": "m_{A} = 3.0-5.0 GeV",  "min_m": 3.0, "max_m": 5.0},
    "5.0-7.0":   {"label": "m_{A} = 5.0-7.0 GeV",  "min_m": 5.0, "max_m": 7.0},
    "7.0-10.0":  {"label": "m_{A} = 7.0-10.0 GeV",  "min_m": 7.0, "max_m": 10.0}
}

h_rho_orig = {}
h_rho_cut = {}

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    h_rho_orig[key] = ROOT.TH1F(
        "h_rho_orig_{}".format(suffix),
        "CMS Simulation ({});#rho [GeV/unit area];Fraction of Events".format(cfg["label"]),
        100, 0, 50
    )
    h_rho_cut[key] = ROOT.TH1F(
        "h_rho_cut_{}".format(suffix),
        "",
        100, 0, 50
    )

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if len(tree.A_Gen_mass) == 0 or not hasattr(tree, 'rho') or not hasattr(tree, 'pt'):
        continue
        
    event_mass = tree.A_Gen_mass[0]
    current_key = None
    for key, cfg in mass_configs.items():
        if cfg["min_m"] <= event_mass < cfg["max_m"]:
            current_key = key
            break
            
    if not current_key:
        continue

    h_rho_orig[current_key].Fill(tree.rho)
    
    pass_pt = False
    for p in tree.pt:
        if p > 10.0:
            pass_pt = True
            break
            
    if pass_pt:
        h_rho_cut[current_key].Fill(tree.rho)

for key, cfg in mass_configs.items():
    suffix = key.replace('.', 'p')
    
    c = ROOT.TCanvas("c_rho_comp_{}".format(suffix), "", 800, 600)
    c.SetMargin(0.12, 0.05, 0.12, 0.10)
    
    h_rho_orig[key].SetLineColor(ROOT.kBlue)
    h_rho_orig[key].SetLineWidth(2)
    h_rho_orig[key].SetLineStyle(2)
    
    h_rho_cut[key].SetLineColor(ROOT.kRed)
    h_rho_cut[key].SetLineWidth(2)
    h_rho_cut[key].SetLineStyle(1)
    
    if h_rho_orig[key].GetEntries() > 0:
        h_rho_orig[key].Scale(1.0 / h_rho_orig[key].GetEntries())
        
    if h_rho_cut[key].GetEntries() > 0:
        h_rho_cut[key].Scale(1.0 / h_rho_cut[key].GetEntries())
        
    max_orig = h_rho_orig[key].GetMaximum()
    max_cut = h_rho_cut[key].GetMaximum()
    h_rho_orig[key].SetMaximum(max(max_orig, max_cut) * 1.15)
    
    h_rho_orig[key].Draw("HIST")
    h_rho_cut[key].Draw("HIST SAME")
    
    leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(h_rho_orig[key], "Original", "l")
    leg.AddEntry(h_rho_cut[key], "p_{T} > 10 GeV", "l")
    leg.Draw()
    
    c.SaveAs(os.path.join(output_dir, "rho_comparison_mass_{}.png".format(suffix)))
    
    h_rho_orig[key].Delete()
    h_rho_cut[key].Delete()
    c.Delete()

infile.Close()
print("Comparison plots generated successfully.")
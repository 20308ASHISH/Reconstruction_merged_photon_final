import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_Phase2"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if not os.path.exists(input_filename):
    raise FileNotFoundError("Input file not found: {}".format(input_filename))

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    raise ValueError("Could not find TTree 'ntupler/T' in the root file.")

plots_config = {
    "nRecHits": {
        "title": "Number of RecHits;Number of RecHits;Events",
        "bins": 100, "min": 0, "max": 2000, "color": ROOT.kBlue + 1
    },
    "rho": {
        "title": "Rho Energy;#rho [GeV];Events",
        "bins": 100, "min": 0, "max": 50, "color": ROOT.kRed + 1
    },
    "nPhotons": {
        "title": "Number of Photons;Number of Photons;Events",
        "bins": 10, "min": 0, "max": 10, "color": ROOT.kGreen + 2
    },
    "min_dR_twoPhotons": {
        "title": "Minimum dR Between Photons;min #DeltaR(#gamma, #gamma);Events",
        "bins": 100, "min": 0, "max": 5.0, "color": ROOT.kOrange + 7
    }
}

canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)

for branch_name, cfg in plots_config.items():
    canvas.Clear()
    
    hist = ROOT.TH1F("h_" + branch_name, cfg["title"], cfg["bins"], cfg["min"], cfg["max"])
    hist.SetLineColor(cfg["color"])
    hist.SetLineWidth(2)
    hist.SetFillColorAlpha(cfg["color"], 0.15)
    
    tree.Draw("{} >> h_{}".format(branch_name, branch_name), "", "goff")
    
    hist.Draw("HIST")
    
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.12, 0.92, "#bf{CMS} #it{Simulation}")
    latex.DrawLatex(0.70, 0.92, "Phase-2 (14 TeV)")
    
    output_path = os.path.join(output_dir, "{}.png".format(branch_name))
    canvas.SaveAs(output_path)
    
    hist.Delete()

infile.Close()
print("Plots successfully saved in directory: {}".format(output_dir))
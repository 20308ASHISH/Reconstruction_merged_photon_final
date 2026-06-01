import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")
ROOT.gStyle.SetPalette(ROOT.kBird)

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_NoisePileupAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_pileup = ROOT.TH2F("h_pileup", "Pileup Hit Pattern (Noise-Free Hits);iEta;iPhi;Entries", 170, -85, 85, 360, 1, 361)
h_noise  = ROOT.TH2F("h_noise", "Electronic Noise Pattern (Noise-Tagged Hits);iEta;iPhi;Entries", 170, -85, 85, 360, 1, 361)

num_events = tree.GetEntries()
print("Processing {} entries for hardware-level noise analysis...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    try:
        if tree.iEtaPho1 and tree.iPhiPho1 and tree.HitNoisePho1:
            for ieta, iphi, noise_flag in zip(tree.iEtaPho1, tree.iPhiPho1, tree.HitNoisePho1):
                if noise_flag == 0:
                    h_pileup.Fill(ieta, iphi)
                else:
                    h_noise.Fill(ieta, iphi)
    except AttributeError:
        pass

    try:
        if tree.iEtaPho2 and tree.iPhiPho2 and tree.HitNoisePho2:
            for ieta, iphi, noise_flag in zip(tree.iEtaPho2, tree.iPhiPho2, tree.HitNoisePho2):
                if noise_flag == 0:
                    h_pileup.Fill(ieta, iphi)
                else:
                    h_noise.Fill(ieta, iphi)
    except AttributeError:
        pass

c = ROOT.TCanvas("c_noise_vs_pileup", "Noise vs Pileup Structural Analysis", 1600, 600)
c.Divide(2, 1)

c.cd(1)
ROOT.gPad.SetMargin(0.12, 0.15, 0.12, 0.10)
h_pileup.Draw("COLZ")

c.cd(2)
ROOT.gPad.SetMargin(0.12, 0.15, 0.12, 0.10)
h_noise.Draw("COLZ")

c.SaveAs(os.path.join(output_dir, "pileup_vs_noise_hardware_heatmap.png"))
infile.Close()
print("Hardware heatmaps successfully generated inside: {}".format(output_dir))
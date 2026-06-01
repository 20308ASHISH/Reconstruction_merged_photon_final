import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_RecHitAnalysis"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

# Set range to 0-1500 to account for raw unsuppressed noise and pileup contributions
h_raw_hits = ROOT.TH1F("h_raw_hits", "RawHit_Phi_Pho RecHit Multiplicity;Number of RecHits;Events", 100, 0, 1500)

num_events = tree.GetEntries()
print("Processing {} entries for raw unsuppressed hit analysis...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    unique_raw_hits = set()
    
    # Extract raw unsuppressed hits (Signal + PileUp + Noise) around Photon 1
    try:
        if tree.RawHit_Eta_Pho1 and tree.RawHit_Phi_Pho1:
            for eta, phi in zip(tree.RawHit_Eta_Pho1, tree.RawHit_Phi_Pho1):
                unique_raw_hits.add((round(eta, 4), round(phi, 4)))
    except AttributeError:
        pass

    # Extract raw unsuppressed hits (Signal + PileUp + Noise) around Photon 2
    try:
        if tree.RawHit_Eta_Pho2 and tree.RawHit_Phi_Pho2:
            for eta, phi in zip(tree.RawHit_Eta_Pho2, tree.RawHit_Phi_Pho2):
                unique_raw_hits.add((round(eta, 4), round(phi, 4)))
    except AttributeError:
        pass

    if len(unique_raw_hits) == 0:
        continue

    h_raw_hits.Fill(len(unique_raw_hits))

c = ROOT.TCanvas("c_raw_hits", "", 800, 600)
c.SetMargin(0.12, 0.05, 0.12, 0.10)

h_raw_hits.SetLineColor(ROOT.kGreen+2)
h_raw_hits.SetLineWidth(2)
h_raw_hits.Draw("HIST")

leg = ROOT.TLegend(0.50, 0.75, 0.92, 0.88)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.Draw()

c.SaveAs(os.path.join(output_dir, "rechit_multiplicity_inclusive_all_RawHit_Phi_Pho.png"))
infile.Close()
print("Plots generated inside: {}".format(output_dir))
import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_dRAnalysis"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_matching_dr = ROOT.TH1F("h_matching_dr", "Geometric Distance; #DeltaR(reco, gen); Entries", 100, 0, 0.2)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_bins = 50
min_mass = 0.1
max_mass = 10.0
bin_width = (max_mass - min_mass) / num_bins
bin_drs = [[] for _ in range(num_bins)]

num_events = tree.GetEntries()
print("Processing {} events by computing True Mother Mass via 4-vectors...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'eta') or not hasattr(tree, 'Pho_Gen_Eta') or not hasattr(tree, 'Pho_Gen_Pt'):
        continue

    if len(tree.Pho_Gen_Eta) < 2:
        continue

    v1 = ROOT.TLorentzVector()
    v2 = ROOT.TLorentzVector()
    
    v1.SetPtEtaPhiE(tree.Pho_Gen_Pt[0], tree.Pho_Gen_Eta[0], tree.Pho_Gen_Phi[0], tree.Pho_Gen_E[0])
    v2.SetPtEtaPhiE(tree.Pho_Gen_Pt[1], tree.Pho_Gen_Eta[1], tree.Pho_Gen_Phi[1], tree.Pho_Gen_E[1])
    
    mother_v = v1 + v2
    event_mass = mother_v.M()

    if event_mass < min_mass or event_mass > max_mass:
        continue

    bin_idx = int((event_mass - min_mass) / bin_width)
    if bin_idx >= num_bins: bin_idx = num_bins - 1

    for g_idx in range(len(tree.Pho_Gen_Eta)):
        g_eta = tree.Pho_Gen_Eta[g_idx]
        g_phi = tree.Pho_Gen_Phi[g_idx]
        
        min_dr = 999.0
        for r_idx in range(len(tree.eta)):
            dr = calculate_dr(tree.eta[r_idx], tree.phi[r_idx], g_eta, g_phi)
            if dr < min_dr:
                min_dr = dr
                
        if min_dr < 999.0:
            h_matching_dr.Fill(min_dr)
            bin_drs[bin_idx].append(min_dr)

c1 = ROOT.TCanvas("c_dr_match", "", 800, 600)
c1.SetMargin(0.12, 0.05, 0.12, 0.10)
h_matching_dr.SetLineColor(ROOT.kBlue+2)
h_matching_dr.SetLineWidth(2)
h_matching_dr.Draw("HIST")
c1.SaveAs(os.path.join(output_dir, "matching_dr_distribution.png"))

c2 = ROOT.TCanvas("c_median_dr_vs_mass", "", 800, 600)
c2.SetMargin(0.12, 0.05, 0.12, 0.10)

graph = ROOT.TGraph()
graph.SetTitle("Median #DeltaR vs Calculated Mother A Mass;Mother A Mass [GeV];Median #DeltaR(reco, gen)")

point_idx = 0
for b in range(num_bins):
    drs_in_bin = sorted(bin_drs[b])
    if drs_in_bin:
        median_value = drs_in_bin[len(drs_in_bin) // 2]
        bin_center = min_mass + (b + 0.5) * bin_width
        graph.SetPoint(point_idx, bin_center, median_value)
        point_idx += 1

if point_idx > 0:
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.2)
    graph.SetMarkerColor(ROOT.kRed+1)
    graph.SetLineColor(ROOT.kRed+1)
    graph.SetLineWidth(2)
    graph.Draw("APL")
    c2.SaveAs(os.path.join(output_dir, "median_dr_vs_mass.png"))
else:
    print("Error: Invariant mass calculation yielded no points inside [0.1, 10] GeV.")

infile.Close()
print("Plots generated successfully with clean 4-vector kinematics.")
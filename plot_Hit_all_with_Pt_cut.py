import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_RecHitAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_total_hits = ROOT.TH1F("h_total_hits", "Total Independent RecHits (pt > 10 GeV);Number of RecHits;Events", 100, 1, 800)
h_pho1_hits = ROOT.TH1F("h_pho1_hits", "RecHits for Matched Photon 1 (pt > 10 GeV);Number of RecHits;Events", 100, 1, 500)
h_pho2_hits = ROOT.TH1F("h_pho2_hits", "RecHits for Matched Photon 2 (pt > 10 GeV);Number of RecHits;Events", 100, 1, 500)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} entries...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)

    if len(tree.Pho_Gen_Pt) < 2:
        continue

    gen_photons = []
    for idx in range(len(tree.Pho_Gen_Pt)):
        gen_photons.append({
            'pt': float(tree.Pho_Gen_Pt[idx]),
            'eta': float(tree.Pho_Gen_Eta[idx]),
            'phi': float(tree.Pho_Gen_Phi[idx])
        })
    
    gen_photons.sort(key=lambda x: x['pt'], reverse=True)

    g1_eta = gen_photons[0]['eta']
    g1_phi = gen_photons[0]['phi']
    g2_eta = gen_photons[1]['eta']
    g2_phi = gen_photons[1]['phi']

    pt_vals = [float(x) for x in tree.pt]
    pt_pho1 = pt_vals[0] if len(pt_vals) > 0 else 0.0
    pt_pho2 = pt_vals[1] if len(pt_vals) > 1 else 0.0

    pho1_reco_matched = False
    try:
        if tree.Hit_Eta_Pho1 and tree.Hit_Phi_Pho1:
            for r_eta, r_phi in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1):
                if calculate_dr(r_eta, r_phi, g1_eta, g1_phi) < 0.1:
                    pho1_reco_matched = True
                    break
    except AttributeError:
        pass

    pho2_reco_matched = False
    try:
        if tree.Hit_Eta_Pho2 and tree.Hit_Phi_Pho2:
            for r_eta, r_phi in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2):
                if calculate_dr(r_eta, r_phi, g2_eta, g2_phi) < 0.1:
                    pho2_reco_matched = True
                    break
    except AttributeError:
        pass

    unique_pho1 = set()
    unique_pho2 = set()

    if pho1_reco_matched and pt_pho1 > 10.0:
        try:
            for eta, phi in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1):
                unique_pho1.add((round(eta, 4), round(phi, 4)))
        except AttributeError:
            pass

    if pho2_reco_matched and pt_pho2 > 10.0:
        try:
            for eta, phi in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2):
                unique_pho2.add((round(eta, 4), round(phi, 4)))
        except AttributeError:
            pass

    unique_total = unique_pho1 | unique_pho2

    if len(unique_pho1) > 0:
        h_pho1_hits.Fill(len(unique_pho1))
    if len(unique_pho2) > 0:
        h_pho2_hits.Fill(len(unique_pho2))
    if len(unique_total) > 0:
        h_total_hits.Fill(len(unique_total))

c_combined = ROOT.TCanvas("c_combined", "RecHit Multiplicity Analysis pt > 10GeV", 1500, 500)
c_combined.Divide(3, 1)

c_combined.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_total_hits.SetLineColor(ROOT.kBlack)
h_total_hits.SetLineWidth(2)
h_total_hits.Draw("HIST")

c_combined.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho1_hits.SetLineColor(ROOT.kBlue+1)
h_pho1_hits.SetLineWidth(2)
h_pho1_hits.Draw("HIST")

c_combined.cd(3)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho2_hits.SetLineColor(ROOT.kRed+1)
h_pho2_hits.SetLineWidth(2)
h_pho2_hits.Draw("HIST")

c_combined.SaveAs(os.path.join(output_dir, "rechit_multiplicity_matched_pt10_side_by_side.png"))
infile.Close()
print("Plots generated successfully without 0 bins.")
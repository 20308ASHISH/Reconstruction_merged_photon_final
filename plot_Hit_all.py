import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
gensim_filename = "file:DP1_folder/AToGG_GEN_E_new_all_10k.root"
output_dir = "plots_RecHitAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gensim_file = ROOT.TFile.Open(gensim_filename, "READ")
gensim_tree = gensim_file.Get("T")

gen_truth_map = {}

if gensim_tree:
    for entry in range(gensim_tree.GetEntries()):
        gensim_tree.GetEntry(entry)
        evt_key = (int(gensim_tree.run), int(gensim_tree.lumi), int(gensim_tree.event))
        true_photons = []
        for g_idx in range(len(gensim_tree.GenPart_pdgId)):
            if abs(gensim_tree.GenPart_pdgId[g_idx]) == 22 and abs(gensim_tree.GenPart_motherPdgId[g_idx]) == 36:
                true_photons.append((gensim_tree.GenPart_eta[g_idx], gensim_tree.GenPart_phi[g_idx]))
        gen_truth_map[evt_key] = true_photons
    gensim_file.Close()

infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_total_hits = ROOT.TH1F("h_total_hits", "Total Independent RecHits (Union);Number of RecHits;Events", 100, 0, 800)
h_pho1_hits = ROOT.TH1F("h_pho1_hits", "Dependent RecHits (Photon 1 Matched);Number of RecHits;Events", 100, 0, 500)
h_pho2_hits = ROOT.TH1F("h_pho2_hits", "Dependent RecHits (Photon 2 Matched);Number of RecHits;Events", 100, 0, 500)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()

for entry in range(num_events):
    tree.GetEntry(entry)
    reco_evt_key = (int(tree.run), int(tree.lumi), int(tree.event))
    
    if reco_evt_key in gen_truth_map:
        signal_gen_photons = gen_truth_map[reco_evt_key]
    else:
        continue

    if len(signal_gen_photons) < 2:
        continue

    g1_eta, g1_phi = signal_gen_photons[0]
    g2_eta, g2_phi = signal_gen_photons[1]

    pho1_reco_matched = False
    pho2_reco_matched = False

    try:
        if tree.Hit_Eta_Pho1 and tree.Hit_Phi_Pho1:
            for r_eta, r_phi in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1):
                if calculate_dr(r_eta, r_phi, g1_eta, g1_phi) < 0.1:
                    pho1_reco_matched = True
                    break
    except AttributeError:
        pass

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

    if pho1_reco_matched:
        try:
            for eta, phi in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1):
                unique_pho1.add((round(eta, 4), round(phi, 4)))
        except AttributeError:
            pass

    if pho2_reco_matched:
        try:
            for eta, phi in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2):
                unique_pho2.add((round(eta, 4), round(phi, 4)))
        except AttributeError:
            pass

    unique_total = unique_pho1 | unique_pho2

    h_pho1_hits.Fill(len(unique_pho1))
    h_pho2_hits.Fill(len(unique_pho2))
    h_total_hits.Fill(len(unique_total))

c_combined = ROOT.TCanvas("c_combined", "RecHit Multiplicity", 1500, 500)
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

c_combined.SaveAs(os.path.join(output_dir, "rechit_multiplicity_matched_side_by_side.png"))
infile.Close()
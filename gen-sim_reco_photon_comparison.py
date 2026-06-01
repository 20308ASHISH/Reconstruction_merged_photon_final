import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat("5.0f")

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
gensim_filename = "file:DP1_folder/AToGG_GEN_E_new_all_10k.root"
output_dir = "plots_AdvancedAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gensim_file = ROOT.TFile.Open(gensim_filename, "READ")
gensim_tree = gensim_file.Get("T") 

gen_truth_map = {}

if gensim_tree:
    print("Building generator truth map from gen-sim file...")
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

h_npho_decay = ROOT.TH1F("h_npho_decay", "Photon Multiplicity Summary (p_{T} > 10 GeV);Number of Photons;Events", 6, 0, 6)
h_npho_pileup = ROOT.TH1F("h_npho_pileup", "", 6, 0, 6)
h_hit_classification = ROOT.TH1F("h_hit_classification", "Decay Photon Hit Category (p_{T} > 10 GeV);;Events", 2, 0, 2)

h_min_dr_lead = ROOT.TH1F("h_min_dr_lead", "Minimum DeltaR Mapping (p_{T} > 10 GeV);Minimum #DeltaR(reco, gen);Entries", 50, 0, 0.5)
h_min_dr_sublead = ROOT.TH1F("h_min_dr_sublead", "", 50, 0, 0.5)

h_hit_classification.GetXaxis().SetBinLabel(1, "Single Hit (Merged)")
h_hit_classification.GetXaxis().SetBinLabel(2, "Double Hit (Resolved)")

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} reconstruction events...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    reco_evt_key = (int(tree.run), int(tree.lumi), int(tree.event))
    
    if reco_evt_key in gen_truth_map:
        signal_gen_photons = gen_truth_map[reco_evt_key]
    else:
        signal_gen_photons = []
        if hasattr(tree, 'Pho_Gen_Eta'):
            for g_idx in range(len(tree.Pho_Gen_Eta)):
                signal_gen_photons.append((tree.Pho_Gen_Eta[g_idx], tree.Pho_Gen_Phi[g_idx]))

    if len(signal_gen_photons) >= 2:
        g1_eta, g1_phi = signal_gen_photons[0]
        min_dr1 = 999.0
        for r_idx in range(len(tree.eta)):
            if float(tree.pt[r_idx]) > 10.0:
                dr = calculate_dr(tree.eta[r_idx], tree.phi[r_idx], g1_eta, g1_phi)
                if dr < min_dr1:
                    min_dr1 = dr
        if min_dr1 < 999.0:
            h_min_dr_lead.Fill(min_dr1)

        g2_eta, g2_phi = signal_gen_photons[1]
        min_dr2 = 999.0
        for r_idx in range(len(tree.eta)):
            if float(tree.pt[r_idx]) > 10.0:
                dr = calculate_dr(tree.eta[r_idx], tree.phi[r_idx], g2_eta, g2_phi)
                if dr < min_dr2:
                    min_dr2 = dr
        if min_dr2 < 999.0:
            h_min_dr_sublead.Fill(min_dr2)

    decay_indices_matched = set()
    pileup_count = 0
    gen_to_reco_matches = {i: [] for i in range(len(signal_gen_photons))}

    for r_idx in range(len(tree.eta)):
        if float(tree.pt[r_idx]) <= 10.0:
            continue
            
        r_eta = tree.eta[r_idx]
        r_phi = tree.phi[r_idx]
        
        min_dr_for_this_reco = 999.0
        best_g_idx = -1
        
        for g_idx, (g_eta, g_phi) in enumerate(signal_gen_photons):
            dr = calculate_dr(r_eta, r_phi, g_eta, g_phi)
            if dr < min_dr_for_this_reco:
                min_dr_for_this_reco = dr
                best_g_idx = g_idx
                
        if min_dr_for_this_reco < 0.1:
            decay_indices_matched.add(r_idx)
            gen_to_reco_matches[best_g_idx].append(r_idx)
        else:
            pileup_count += 1

    h_npho_decay.Fill(len(decay_indices_matched))
    h_npho_pileup.Fill(pileup_count)

    reco_elements_engaged = set()
    for g_idx in gen_to_reco_matches:
        for r_idx in gen_to_reco_matches[g_idx]:
            reco_elements_engaged.add(r_idx)
            
    if len(reco_elements_engaged) == 1:
        h_hit_classification.Fill(0)
    elif len(reco_elements_engaged) >= 2:
        h_hit_classification.Fill(1)

c1 = ROOT.TCanvas("c_multiplicity", "", 800, 600)
c1.SetMargin(0.12, 0.05, 0.12, 0.10)
h_npho_decay.SetLineColor(ROOT.kBlue)
h_npho_decay.SetLineWidth(2)
h_npho_decay.SetMarkerColor(ROOT.kBlue)
h_npho_decay.SetMarkerSize(1.2)

h_npho_pileup.SetLineColor(ROOT.kRed)
h_npho_pileup.SetLineWidth(2)
h_npho_pileup.SetLineStyle(2)
h_npho_pileup.SetMarkerColor(ROOT.kRed)
h_npho_pileup.SetMarkerSize(1.2)

h_npho_decay.SetMaximum(max(h_npho_decay.GetMaximum(), h_npho_pileup.GetMaximum()) * 1.3)
h_npho_decay.Draw("HIST TEXT0")
h_npho_pileup.Draw("HIST TEXT0 SAME")

leg1 = ROOT.TLegend(0.55, 0.75, 0.92, 0.88)
leg1.SetBorderSize(0)
leg1.SetFillStyle(0)
leg1.AddEntry(h_npho_decay, "Decay Photons", "l")
leg1.AddEntry(h_npho_pileup, "Pileup Photons", "l")
leg1.Draw()
c1.SaveAs(os.path.join(output_dir, "photon_multiplicity_comparison.png"))

c2 = ROOT.TCanvas("c_hits", "", 800, 600)
c2.SetMargin(0.12, 0.05, 0.12, 0.10)
h_hit_classification.SetFillColor(ROOT.kAzure+1)
h_hit_classification.SetLineColor(ROOT.kBlack)
h_hit_classification.SetMarkerSize(1.5)
h_hit_classification.SetMinimum(0)
h_hit_classification.SetMaximum(h_hit_classification.GetMaximum() * 1.3)
h_hit_classification.Draw("BAR TEXT0")
c2.SaveAs(os.path.join(output_dir, "decay_photon_hit_splitting.png"))

c3 = ROOT.TCanvas("c_dr", "", 800, 600)
c3.SetMargin(0.12, 0.05, 0.12, 0.10)

h_min_dr_lead.SetLineColor(ROOT.kBlue)
h_min_dr_lead.SetLineWidth(2)

h_min_dr_sublead.SetLineColor(ROOT.kRed)
h_min_dr_sublead.SetLineWidth(2)
h_min_dr_sublead.SetLineStyle(7)

max_val = max(h_min_dr_lead.GetMaximum(), h_min_dr_sublead.GetMaximum())
h_min_dr_lead.SetMaximum(max_val * 1.2)

h_min_dr_lead.Draw("HIST")
h_min_dr_sublead.Draw("HIST SAME")

leg2 = ROOT.TLegend(0.55, 0.75, 0.92, 0.88)
leg2.SetBorderSize(0)
leg2.SetFillStyle(0)
leg2.AddEntry(h_min_dr_lead, "Gen Photon 1", "l")
leg2.AddEntry(h_min_dr_sublead, "Gen Photon 2", "l")
leg2.Draw()

c3.SaveAs(os.path.join(output_dir, "photon_minimum_dr_distribution.png"))

infile.Close()
print("Plots generated successfully with pT > 10 GeV cut applied to both signal and pileup.")
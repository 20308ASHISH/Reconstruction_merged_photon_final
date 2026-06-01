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
    print("Building generator truth map...")
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

h_npho_decay  = ROOT.TH1F("h_npho_decay", "Photon Origin Multiplicity (p_{T} > 10 GeV);Number of Photons;Events", 6, 0, 6)
h_npho_pileup = ROOT.TH1F("h_npho_pileup", "", 6, 0, 6)
h_npho_noise  = ROOT.TH1F("h_npho_noise", "", 6, 0, 6)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} events...".format(num_events))

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

    decay_count = 0
    pileup_count = 0
    noise_count = 0

    for r_idx in range(len(tree.eta)):
        if float(tree.pt[r_idx]) <= 10.0:
            continue
            
        r_eta = tree.eta[r_idx]
        r_phi = tree.phi[r_idx]
        
        min_dr = 999.0
        for g_eta, g_phi in signal_gen_photons:
            dr = calculate_dr(r_eta, r_phi, g_eta, g_phi)
            if dr < min_dr:
                min_dr = dr
                
        if min_dr < 0.1:
            decay_count += 1
        else:
            reco_energy = float(tree.pt[r_idx]) * math.cosh(r_eta) 
            if reco_energy > 2.0:
                pileup_count += 1
            else:
                noise_count += 1

    h_npho_decay.Fill(decay_count)
    h_npho_pileup.Fill(pileup_count)
    h_npho_noise.Fill(noise_count)

c1 = ROOT.TCanvas("c_noise_vs_pu", "", 800, 600)
c1.SetMargin(0.12, 0.05, 0.12, 0.10)

h_npho_decay.SetLineColor(ROOT.kBlue)
h_npho_decay.SetLineWidth(2)
h_npho_decay.SetMarkerColor(ROOT.kBlue)

h_npho_pileup.SetLineColor(ROOT.kRed)
h_npho_pileup.SetLineWidth(2)
h_npho_pileup.SetLineStyle(2)
h_npho_pileup.SetMarkerColor(ROOT.kRed)

h_npho_noise.SetLineColor(ROOT.kGreen+2)
h_npho_noise.SetLineWidth(2)
h_npho_noise.SetLineStyle(3)
h_npho_noise.SetMarkerColor(ROOT.kGreen+2)

max_val = max(h_npho_decay.GetMaximum(), h_npho_pileup.GetMaximum(), h_npho_noise.GetMaximum())
h_npho_decay.SetMaximum(max_val * 1.3)

h_npho_decay.Draw("HIST TEXT0")
h_npho_pileup.Draw("HIST TEXT0 SAME")
h_npho_noise.Draw("HIST TEXT0 SAME")

leg1 = ROOT.TLegend(0.55, 0.70, 0.92, 0.88)
leg1.SetBorderSize(0)
leg1.SetFillStyle(0)
leg1.AddEntry(h_npho_decay, "Decay Photons", "l")
leg1.AddEntry(h_npho_pileup, "Pure Pileup (> 2 GeV)", "l")
leg1.AddEntry(h_npho_noise, "Detector Noise (#le 2 GeV)", "l")
leg1.Draw()

c1.SaveAs(os.path.join(output_dir, "photon_multiplicity_noise_separation.png"))
infile.Close()
print("New analysis plots splitting pileup and noise generated cleanly.")
import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_RhoAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_total_orig = ROOT.TH1F("h_total_orig", "Total Event Rho (No Cut); #rho [GeV]; Fraction", 100, 0, 50)
h_total_cut  = ROOT.TH1F("h_total_cut", "Total Event Rho (p_{T} > 10 GeV Cut); #rho [GeV]; Fraction", 100, 0, 50)

h_pho1_orig  = ROOT.TH1F("h_pho1_orig", "Photon 1 Rho (No Cut); #rho [GeV]; Fraction", 100, 0, 50)
h_pho1_cut   = ROOT.TH1F("h_pho1_cut", "Photon 1 Rho (p_{T} > 10 GeV Cut); #rho [GeV]; Fraction", 100, 0, 50)

h_pho2_orig  = ROOT.TH1F("h_pho2_orig", "Photon 2 Rho (No Cut); #rho [GeV]; Fraction", 100, 0, 50)
h_pho2_cut   = ROOT.TH1F("h_pho2_cut", "Photon 2 Rho (p_{T} > 10 GeV Cut); #rho [GeV]; Fraction", 100, 0, 50)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} entries for 6 separate Rho plots...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'rho') or not hasattr(tree, 'pt'):
        continue
    if not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
        continue

    v1 = ROOT.TLorentzVector()
    v2 = ROOT.TLorentzVector()
    v1.SetPtEtaPhiE(tree.Pho_Gen_Pt[0], tree.Pho_Gen_Eta[0], tree.Pho_Gen_Phi[0], tree.Pho_Gen_E[0])
    v2.SetPtEtaPhiE(tree.Pho_Gen_Pt[1], tree.Pho_Gen_Eta[1], tree.Pho_Gen_Phi[1], tree.Pho_Gen_E[1])
    event_mass = (v1 + v2).M()

    if event_mass < 0.1 or event_mass > 10.0:
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

    h_total_orig.Fill(tree.rho)
    
    pass_total_pt = False
    for p in pt_vals:
        if p > 10.0:
            pass_total_pt = True
            break
    if pass_total_pt:
        h_total_cut.Fill(tree.rho)

    if pho1_reco_matched:
        h_pho1_orig.Fill(tree.rho)
        if pt_pho1 > 10.0:
            h_pho1_cut.Fill(tree.rho)

    if pho2_reco_matched:
        h_pho2_orig.Fill(tree.rho)
        if pt_pho2 > 10.0:
            h_pho2_cut.Fill(tree.rho)

for h in [h_total_orig, h_total_cut, h_pho1_orig, h_pho1_cut, h_pho2_orig, h_pho2_cut]:
    if h.GetEntries() > 0:
        h.Scale(1.0 / h.GetEntries())

c_matrix = ROOT.TCanvas("c_matrix", "Rho Distribution Analysis Matrix", 1500, 1000)
c_matrix.Divide(3, 2)

c_matrix.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_total_orig.SetLineColor(ROOT.kBlue)
h_total_orig.SetLineWidth(2)
h_total_orig.Draw("HIST")

c_matrix.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho1_orig.SetLineColor(ROOT.kBlue)
h_pho1_orig.SetLineWidth(2)
h_pho1_orig.Draw("HIST")

c_matrix.cd(3)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho2_orig.SetLineColor(ROOT.kBlue)
h_pho2_orig.SetLineWidth(2)
h_pho2_orig.Draw("HIST")

c_matrix.cd(4)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_total_cut.SetLineColor(ROOT.kRed)
h_total_cut.SetLineWidth(2)
h_total_cut.Draw("HIST")

c_matrix.cd(5)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho1_cut.SetLineColor(ROOT.kRed)
h_pho1_cut.SetLineWidth(2)
h_pho1_cut.Draw("HIST")

c_matrix.cd(6)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_pho2_cut.SetLineColor(ROOT.kRed)
h_pho2_cut.SetLineWidth(2)
h_pho2_cut.Draw("HIST")

c_matrix.SaveAs(os.path.join(output_dir, "rho_6_plots_matrix.png"))
infile.Close()
print("Saved 6 separate matrix plots into: {}".format(output_dir))
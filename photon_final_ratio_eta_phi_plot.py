import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_MatchedPhotonAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_merged_eta = ROOT.TH1F("h_merged_eta", "Merged Matched Photons ([0.4, 0.6]); Reco #eta; Events", 50, -3.0, 3.0)
h_merged_phi = ROOT.TH1F("h_merged_phi", "Merged Matched Photons ([0.4, 0.6]); Reco #phi; Events", 50, -math.pi, math.pi)

h_res_eta    = ROOT.TH1F("h_res_eta", "Resolved Matched Photons ([0.4, 0.6]); Reco #eta; Events", 50, -3.0, 3.0)
h_res_phi    = ROOT.TH1F("h_res_phi", "Resolved Matched Photons ([0.4, 0.6]); Reco #phi; Events", 50, -math.pi, math.pi)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Analyzing matched photon kinematics in energy ratio region [0.4, 0.6]...")

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
        continue
    if not hasattr(tree, 'A_Gen_pt') or len(tree.A_Gen_pt) == 0:
        continue

    vA = ROOT.TLorentzVector()
    vA.SetPtEtaPhiM(float(tree.A_Gen_pt[0]), float(tree.A_Gen_eta[0]), float(tree.A_Gen_phi[0]), float(tree.A_Gen_mass[0]))
    E_A_gen = vA.E()

    if E_A_gen <= 0:
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

    reco_elements_engaged = []
    pt_vals = [float(x) for x in tree.pt]
    eta_vals = [float(x) for x in tree.eta]
    phi_vals = [float(x) for x in tree.phi]
    
    for r_idx in range(len(tree.eta)):
        r_eta = tree.eta[r_idx]
        r_phi = tree.phi[r_idx]
        
        dr1 = calculate_dr(r_eta, r_phi, g1_eta, g1_phi)
        dr2 = calculate_dr(r_eta, r_phi, g2_eta, g2_phi)
        min_dr = min(dr1, dr2)
                
        if min_dr < 0.1:
            reco_elements_engaged.append(r_idx)

    pt_pho1 = pt_vals[0] if len(pt_vals) > 0 else 0.0
    pt_pho2 = pt_vals[1] if len(pt_vals) > 1 else 0.0

    pho1_reco_matched = False
    try:
        if hasattr(tree, 'Hit_Eta_Pho1') and tree.Hit_Eta_Pho1:
            for r_eta, r_phi in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1):
                if calculate_dr(r_eta, r_phi, g1_eta, g1_phi) < 0.1:
                    pho1_reco_matched = True
                    break
    except AttributeError:
        pass

    pho2_reco_matched = False
    try:
        if hasattr(tree, 'Hit_Eta_Pho2') and tree.Hit_Phi_Pho2:
            for r_eta, r_phi in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2):
                if calculate_dr(r_eta, r_phi, g2_eta, g2_phi) < 0.1:
                    pho2_reco_matched = True
                    break
    except AttributeError:
        pass

    if len(reco_elements_engaged) == 1:
        sum_e_merged = 0.0
        if pho1_reco_matched and pt_pho1 > 10.0 and hasattr(tree, 'RecHitEnPho1'):
            for en in tree.RecHitEnPho1:
                sum_e_merged += en
        if pho2_reco_matched and pt_pho2 > 10.0 and hasattr(tree, 'RecHitEnPho2'):
            for en in tree.RecHitEnPho2:
                sum_e_merged += en
                
        if sum_e_merged > 0:
            ratio = sum_e_merged / E_A_gen
            if 0.4 <= ratio <= 0.6:
                if pho1_reco_matched and len(eta_vals) > 0:
                    h_merged_eta.Fill(eta_vals[0])
                    h_merged_phi.Fill(phi_vals[0])
                if pho2_reco_matched and len(eta_vals) > 1:
                    h_merged_eta.Fill(eta_vals[1])
                    h_merged_phi.Fill(phi_vals[1])

    elif len(reco_elements_engaged) >= 2:
        sum_e_res = 0.0
        if pho1_reco_matched and pt_pho1 > 10.0 and hasattr(tree, 'RecHitEnPho1'):
            for en in tree.RecHitEnPho1:
                sum_e_res += en
        if pho2_reco_matched and pt_pho2 > 10.0 and hasattr(tree, 'RecHitEnPho2'):
            for en in tree.RecHitEnPho2:
                sum_e_res += en
                
        if sum_e_res > 0:
            ratio = sum_e_res / E_A_gen
            if 0.4 <= ratio <= 0.6:
                if pho1_reco_matched and len(eta_vals) > 0:
                    h_res_eta.Fill(eta_vals[0])
                    h_res_phi.Fill(phi_vals[0])
                if pho2_reco_matched and len(eta_vals) > 1:
                    h_res_eta.Fill(eta_vals[1])
                    h_res_phi.Fill(phi_vals[1])

c_kinematics = ROOT.TCanvas("c_kinematics", "Kinematics Analysis [0.4, 0.6]", 1200, 1000)
c_kinematics.Divide(2, 2)

c_kinematics.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_merged_eta.SetLineColor(ROOT.kBlack)
h_merged_eta.SetLineWidth(2)
h_merged_eta.Draw("HIST")

c_kinematics.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_merged_phi.SetLineColor(ROOT.kBlack)
h_merged_phi.SetLineWidth(2)
h_merged_phi.Draw("HIST")

c_kinematics.cd(3)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_res_eta.SetLineColor(ROOT.kBlue+1)
h_res_eta.SetLineWidth(2)
h_res_eta.Draw("HIST")

c_kinematics.cd(4)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_res_phi.SetLineColor(ROOT.kBlue+1)
h_res_phi.SetLineWidth(2)
h_res_phi.Draw("HIST")

c_kinematics.SaveAs(os.path.join(output_dir, "matched_photons_kinematics_0p4_0p6.png"))
infile.Close()
print("Kinematic distributions for the [0.4, 0.6] match region generated successfully.")
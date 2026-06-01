import os
import math
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("emruo")

reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_CategoryAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(reco_filename, "READ")
tree = infile.Get("ntupler/T")

if not tree:
    exit(1)

h_merged_ratio = ROOT.TH1F("h_merged_ratio", "Merged Category Energy Ratio; #sum E_{crystal} / E_{A, Gen}; Events", 100, 0.0, 1.5)
h_res_ratio    = ROOT.TH1F("h_res_ratio", "Resolved Category Energy Ratio; #sum E_{crystal} / E_{A, Gen}; Events", 100, 0.0, 1.5)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} entries for energy ratio analysis...".format(num_events))

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
            h_merged_ratio.Fill(sum_e_merged / E_A_gen)

    elif len(reco_elements_engaged) >= 2:
        sum_e_res = 0.0
        if pho1_reco_matched and pt_pho1 > 10.0 and hasattr(tree, 'RecHitEnPho1'):
            for en in tree.RecHitEnPho1:
                sum_e_res += en
        if pho2_reco_matched and pt_pho2 > 10.0 and hasattr(tree, 'RecHitEnPho2'):
            for en in tree.RecHitEnPho2:
                sum_e_res += en
        if sum_e_res > 0:
            h_res_ratio.Fill(sum_e_res / E_A_gen)

c_ratio = ROOT.TCanvas("c_ratio", "Energy Ratio Analysis", 1100, 500)
c_ratio.Divide(2, 1)

c_ratio.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_merged_ratio.SetLineColor(ROOT.kBlack)
h_merged_ratio.SetLineWidth(2)
h_merged_ratio.Draw("HIST")

c_ratio.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_res_ratio.SetLineColor(ROOT.kBlue+1)
h_res_ratio.SetLineWidth(2)
h_res_ratio.Draw("HIST")

c_ratio.SaveAs(os.path.join(output_dir, "energy_ratio_side_by_side.png"))
infile.Close()
print("Fixed energy ratio distributions generated successfully.")
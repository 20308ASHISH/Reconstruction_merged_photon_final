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

h_merged_num   = ROOT.TH1F("h_merged_num", "Merged Photon (Barrel + Endcap);Number of RecHits;Events", 100, 0, 500)
h_merged_energy = ROOT.TH1F("h_merged_energy", "Merged Photon (Barrel + Endcap);RecHit Energy [GeV];Entries", 100, 0, 150)

h_res_pho1_num    = ROOT.TH1F("h_res_pho1_num", "Resolved Photon 1 (Barrel + Endcap);Number of RecHits;Events", 100, 0, 500)
h_res_pho1_energy = ROOT.TH1F("h_res_pho1_energy", "Resolved Photon 1 (Barrel + Endcap);RecHit Energy [GeV];Entries", 100, 0, 150)

h_res_pho2_num    = ROOT.TH1F("h_res_pho2_num", "Resolved Photon 2 (Barrel + Endcap);Number of RecHits;Events", 100, 0, 500)
h_res_pho2_energy = ROOT.TH1F("h_res_pho2_energy", "Resolved Photon 2 (Barrel + Endcap);RecHit Energy [GeV];Entries", 100, 0, 150)

def calculate_dr(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    while dphi > math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return math.sqrt(deta**2 + dphi**2)

num_events = tree.GetEntries()
print("Processing {} entries for categorized analysis...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    if not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
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

    if len(reco_elements_engaged) == 1:
        unique_hits = set()
        if pho1_reco_matched and pt_pho1 > 10.0:
            try:
                for eta, phi, en in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1, tree.RecHitEnPho1):
                    unique_hits.add((round(eta, 4), round(phi, 4)))
                    h_merged_energy.Fill(en)
            except AttributeError:
                pass
        if pho2_reco_matched and pt_pho2 > 10.0:
            try:
                for eta, phi, en in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2, tree.RecHitEnPho2):
                    unique_hits.add((round(eta, 4), round(phi, 4)))
                    h_merged_energy.Fill(en)
            except AttributeError:
                pass
        if len(unique_hits) > 0 or (pt_pho1 > 10.0 or pt_pho2 > 10.0):
            h_merged_num.Fill(len(unique_hits))

    elif len(reco_elements_engaged) >= 2:
        if pho1_reco_matched and pt_pho1 > 10.0:
            count1 = 0
            try:
                for eta, phi, en in zip(tree.Hit_Eta_Pho1, tree.Hit_Phi_Pho1, tree.RecHitEnPho1):
                    count1 += 1
                    h_res_pho1_energy.Fill(en)
                h_res_pho1_num.Fill(count1)
            except AttributeError:
                pass
        else:
            h_res_pho1_num.Fill(0)

        if pho2_reco_matched and pt_pho2 > 10.0:
            count2 = 0
            try:
                for eta, phi, en in zip(tree.Hit_Eta_Pho2, tree.Hit_Phi_Pho2, tree.RecHitEnPho2):
                    count2 += 1
                    h_res_pho2_energy.Fill(en)
                h_res_pho2_num.Fill(count2)
            except AttributeError:
                pass
        else:
            h_res_pho2_num.Fill(0)

c_num = ROOT.TCanvas("c_num", "RecHit Multiplicity Analysis", 1500, 500)
c_num.Divide(3, 1)

c_num.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_merged_num.SetLineColor(ROOT.kBlack)
h_merged_num.SetLineWidth(2)
h_merged_num.Draw("HIST")

c_num.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_res_pho1_num.SetLineColor(ROOT.kBlue+1)
h_res_pho1_num.SetLineWidth(2)
h_res_pho1_num.Draw("HIST")

c_num.cd(3)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
h_res_pho2_num.SetLineColor(ROOT.kRed+1)
h_res_pho2_num.SetLineWidth(2)
h_res_pho2_num.Draw("HIST")

c_num.SaveAs(os.path.join(output_dir, "category_rechit_multiplicity_side_by_side.png"))

c_en = ROOT.TCanvas("c_en", "RecHit Energy Spectrum Analysis", 1500, 500)
c_en.Divide(3, 1)

c_en.cd(1)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
ROOT.gPad.SetLogy(True)
h_merged_energy.SetLineColor(ROOT.kBlack)
h_merged_energy.SetLineWidth(2)
h_merged_energy.Draw("HIST")

c_en.cd(2)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
ROOT.gPad.SetLogy(True)
h_res_pho1_energy.SetLineColor(ROOT.kBlue+1)
h_res_pho1_energy.SetLineWidth(2)
h_res_pho1_energy.Draw("HIST")

c_en.cd(3)
ROOT.gPad.SetMargin(0.15, 0.05, 0.12, 0.10)
ROOT.gPad.SetLogy(True)
h_res_pho2_energy.SetLineColor(ROOT.kRed+1)
h_res_pho2_energy.SetLineWidth(2)
h_res_pho2_energy.Draw("HIST")

c_en.SaveAs(os.path.join(output_dir, "category_rechit_energy_side_by_side.png"))

infile.Close()
print("Plots generated successfully inside: {}".format(output_dir))
import os
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

# Combined inclusive histograms for all valid events
h_rho_orig = ROOT.TH1F("h_rho_orig", "Normalized Rho Energy Density Comparison;#rho [GeV/unit area];Fraction of Events", 100, 0, 50)
h_rho_cut = ROOT.TH1F("h_rho_cut", "", 100, 0, 50)

num_events = tree.GetEntries()
print("Processing {} entries for normalized Rho analysis...".format(num_events))

for entry in range(num_events):
    tree.GetEntry(entry)
    
    # Safety checks
    if not hasattr(tree, 'rho') or not hasattr(tree, 'pt'):
        continue
    if not hasattr(tree, 'Pho_Gen_Eta') or len(tree.Pho_Gen_Eta) < 2:
        continue

    # 4-Vector mass check to handle physical acceptance limits [0.1, 10.0] GeV
    v1 = ROOT.TLorentzVector()
    v2 = ROOT.TLorentzVector()
    v1.SetPtEtaPhiE(tree.Pho_Gen_Pt[0], tree.Pho_Gen_Eta[0], tree.Pho_Gen_Phi[0], tree.Pho_Gen_E[0])
    v2.SetPtEtaPhiE(tree.Pho_Gen_Pt[1], tree.Pho_Gen_Eta[1], tree.Pho_Gen_Phi[1], tree.Pho_Gen_E[1])
    event_mass = (v1 + v2).M()

    if event_mass < 0.1 or event_mass > 10.0:
        continue

    h_rho_orig.Fill(tree.rho)
    
    pass_pt = False
    for p in tree.pt:
        if p > 10.0:
            pass_pt = True
            break
            
    if pass_pt:
        h_rho_cut.Fill(tree.rho)

c = ROOT.TCanvas("c_rho_inclusive", "", 800, 600)
c.SetMargin(0.12, 0.05, 0.12, 0.10)

# Apply Event Normalization Scale Factor: 1.0 / Entries
if h_rho_orig.GetEntries() > 0:
    h_rho_orig.Scale(1.0 / h_rho_orig.GetEntries())
if h_rho_cut.GetEntries() > 0:
    h_rho_cut.Scale(1.0 / h_rho_cut.GetEntries())

h_rho_orig.SetLineColor(ROOT.kBlue)
h_rho_orig.SetLineWidth(2)
h_rho_orig.SetLineStyle(2)

h_rho_cut.SetLineColor(ROOT.kRed)
h_rho_cut.SetLineWidth(2)
h_rho_cut.SetLineStyle(1)

# Dynamically find the maximum height scale limit
max_orig = h_rho_orig.GetMaximum()
max_cut = h_rho_cut.GetMaximum()
h_rho_orig.SetMaximum(max(max_orig, max_cut) * 1.2)

h_rho_orig.Draw("HIST")
h_rho_cut.Draw("HIST SAME")

leg = ROOT.TLegend(0.60, 0.75, 0.92, 0.88)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.AddEntry(h_rho_orig, "Original (Normalized)", "l")
leg.AddEntry(h_rho_cut, "p_{T} > 10 GeV (Normalized)", "l")
leg.Draw()

c.SaveAs(os.path.join(output_dir, "rho_multiplicity_inclusive_normalized.png"))

infile.Close()
print("Normalized Rho distribution generated inside: {}".format(output_dir))
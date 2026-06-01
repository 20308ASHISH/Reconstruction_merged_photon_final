import os
import ROOT
from DataFormats.FWLite import Events, Handle

digi_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_DIGI.root"
reco_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root"
output_dir = "plots_PileupAnalysis"
log_filename = "plots_PileupAnalysis/npu_rho_metrics.log"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Opening flat Reco Ntuple tree...")
reco_file = ROOT.TFile.Open(reco_filename, "READ")
reco_tree = reco_file.Get("ntupler/T")
if not reco_tree:
    raise ValueError("Could not find TTree 'ntupler/T' in Reco file.")

print("Initializing FWLite for DIGI file...")
digi_events = Events(digi_filename)
pu_handle = Handle("std::vector<PileupSummaryInfo>")
pu_label = ("addPileupInfo")

h_npu_vs_rho = ROOT.TH2F("h_npu_vs_rho", "Pileup vs Rho;#rho [GeV];True N_{PU}", 50, 0, 50, 60, 0, 60)
h_npu_vs_rho.SetDirectory(0)

npu_list = []
rho_list = []

print("Extracting matched event data...")
for i, event in enumerate(digi_events):
    if i >= reco_tree.GetEntries():
        break
        
    event.getByLabel(pu_label, pu_handle)
    pu_infos = pu_handle.product()
    
    npu_val = -999.0
    for pu_info in pu_infos:
        if pu_info.getBunchCrossing() == 0:
            npu_val = pu_info.getTrueNumInteractions()
            break
            
    reco_tree.GetEntry(i)
    rho_val = getattr(reco_tree, "rho", -999.0)
    
    if npu_val != -999.0 and rho_val != -999.0:
        h_npu_vs_rho.Fill(rho_val, npu_val)
        npu_list.append(npu_val)
        rho_list.append(rho_val)

reco_file.Close()

avg_npu = sum(npu_list) / len(npu_list) if npu_list else 0
avg_rho = sum(rho_list) / len(rho_list) if rho_list else 0

print("Writing metrics log file...")
with open(log_filename, "w") as log_file:
    log_file.write("=========================================\n")
    log_file.write(" Phase-2 Analysis: Pileup vs Rho Metrics \n")
    log_file.write("=========================================\n")
    log_file.write("Total Matched Events : {}\n".format(len(npu_list)))
    log_file.write("Average True N_PU    : {:.3f}\n".format(avg_npu))
    log_file.write("Average Rho Energy   : {:.3f} GeV\n".format(avg_rho))
    log_file.write("=========================================\n")

print("Generating 2D Canvas Profile...")
canvas = ROOT.TCanvas("canvas", "canvas", 900, 700)
canvas.SetRightMargin(0.15)
canvas.SetBottomMargin(0.12)
canvas.SetLeftMargin(0.12)

h_npu_vs_rho.GetXaxis().SetTitleSize(0.045)
h_npu_vs_rho.GetYaxis().SetTitleSize(0.045)
h_npu_vs_rho.Draw("COLZ")

latex = ROOT.TLatex()
latex.SetNDC()
latex.SetTextSize(0.038)
latex.DrawLatex(0.12, 0.93, "#bf{CMS} #it{Simulation}")
latex.DrawLatex(0.65, 0.93, "Phase-2 Premix (14 TeV)")

output_path = os.path.join(output_dir, "npu_vs_rho_2d.png")
canvas.SaveAs(output_path)

h_npu_vs_rho.Delete()
canvas.Delete()

print("Process finished successfully!")
print("Log written to: {}".format(log_filename))
print("Plot saved to: {}".format(output_path))
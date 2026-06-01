import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

input_filename = "pu_distribution.root"
output_dir = "plots_PileupAnalysis"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

infile = ROOT.TFile.Open(input_filename, "READ")
h_npu = infile.Get("h_npu")

canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)
canvas.SetLeftMargin(0.13)
canvas.SetBottomMargin(0.12)

h_npu.SetLineColor(ROOT.kViolet + 1)
h_npu.SetLineWidth(2)
h_npu.SetFillColorAlpha(ROOT.kViolet + 1, 0.15)
h_npu.GetXaxis().SetTitleSize(0.045)
h_npu.GetYaxis().SetTitleSize(0.045)

h_npu.Draw("HIST")

latex = ROOT.TLatex()
latex.SetNDC()
latex.SetTextSize(0.04)
latex.DrawLatex(0.13, 0.92, "#bf{CMS} #it{Simulation}")
latex.DrawLatex(0.68, 0.92, "2018 Premix (13 TeV)")

output_path = os.path.join(output_dir, "pileup_distribution.png")
canvas.SaveAs(output_path)

infile.Close()
print("Pileup graph generated successfully at: {}".format(output_path))
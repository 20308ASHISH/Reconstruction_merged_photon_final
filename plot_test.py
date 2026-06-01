import ROOT
infile = ROOT.TFile.Open("DP1_folder/AToGG_GEN_E_new_all_10k_phase1_analysis.root", "READ")
tree = infile.Get("demo/T")
tree.Print()
infile.Close()
import ROOT
from DataFormats.FWLite import Events, Handle

input_file = "DP1_folder/AToGG_GEN_E_new_all_10k_DIGI.root"
output_file = "pu_distribution.root"

print("Analyzing pileup from: {}".format(input_file))

events = Events(input_file)
pu_handle = Handle("std::vector<PileupSummaryInfo>")
pu_label = ("addPileupInfo")

h_npu = ROOT.TH1F("h_npu", "True Number of Pileup Interactions;N_{PU};Events", 100, 0, 100)

for i, event in enumerate(events):
    if i % 1000 == 0:
        print("Processing Event {}".format(i))
        
    event.getByLabel(pu_label, pu_handle)
    pu_infos = pu_handle.product()
    
    for pu_info in pu_infos:
        if pu_info.getBunchCrossing() == 0:
            npu = pu_info.getTrueNumInteractions()
            h_npu.Fill(npu)
            break

outfile = ROOT.TFile(output_file, "RECREATE")
h_npu.Write()
outfile.Close()

print("Analysis finished! Histogram saved in: {}".format(output_file))
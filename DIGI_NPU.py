import ROOT
import sys
from DataFormats.FWLite import Events, Handle

def main():
    input_file = 'file:DP1_folder/AToGG_GEN_E0.1_new_DIGI.root'
    output_name = 'run_DIGI_NPU_E0.1.png'
    log_name = 'DP1_folder/run_DIGI_NPU_E0.1.log'
    
    print('--------------------------------------------------')
    print('Analysis Tool: DIGI_NPU.py')
    print('Processing File: {}'.format(input_file))
    print('--------------------------------------------------')

    events = Events(input_file)
    pu_handle = Handle('std::vector<PileupSummaryInfo>')
    pu_label = ('addPileupInfo')

    hist_pu = ROOT.TH1F("hist_pu", "Pileup Validation;Observed NPU;Number of Events", 100, 0, 100)

    count = 0
    # Open the log file for writing
    with open(log_name, 'w') as log_file:
        log_file.write("Event_Index,Observed_NPU\n") # Header

        for i, event in enumerate(events):
            try:
                event.getByLabel(pu_label, pu_handle)
                pu_infos = pu_handle.product()
                
                for pu in pu_infos:
                    if pu.getBunchCrossing() == 0:
                        true_npu = pu.getPU_NumInteractions() # Integer value
                        hist_pu.Fill(true_npu)
                        
                        # Log the value to the file
                        log_file.write("{},{}\n".format(i, true_npu))
                
                count += 1
                if count % 100 == 0:
                    print('Processed {} events...'.format(count))
                    
            except Exception as e:
                print('Event {}: Error accessing Pileup Info -> {}'.format(i, e))

    # Plotting
    canvas = ROOT.TCanvas("canvas", "Validation Canvas", 800, 600)
    ROOT.gStyle.SetOptStat(1111)
    hist_pu.SetLineColor(ROOT.kAzure+2)
    hist_pu.SetFillColor(ROOT.kAzure+1)
    hist_pu.SetFillStyle(3003)
    hist_pu.Draw()
    
    canvas.SaveAs(output_name)
    
    print('--------------------------------------------------')
    print('Analysis Complete.')
    print('Validation plot saved to: {}'.format(output_name))
    print('Data values logged to: {}'.format(log_name))
    print('Total events successfully read: {}'.format(count))
    print('--------------------------------------------------')

if __name__ == '__main__':
    main()
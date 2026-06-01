void plot_normal_hist(const char* fileName) {
    TFile *f = TFile::Open(fileName);
    if (!f || f->IsZombie()) {
        printf("Error: Could not open file %s\n", fileName);
        return;
    }

    TCanvas *c1 = new TCanvas("c1", "Replication_Results", 1200, 600);
    c1->Divide(2,1);
    gStyle->SetOptStat(0);
    gStyle->SetPalette(kBird);

    c1->cd(1);
    TH2F *h_gen = (TH2F*)f->Get("demo/h_GenSep_Crystals");
    if(h_gen && h_gen->GetEntries() > 0) {
        h_gen->SetTitle("Normalized GEN Separation; |#Delta i#eta|; |#Delta i#phi|");
        
        h_gen->Scale(1.0 / h_gen->GetEntries());
        
        h_gen->GetXaxis()->SetRangeUser(0, 5);
        h_gen->GetYaxis()->SetRangeUser(0, 5);
        
        // Fix 1: Force the Z-axis to show the probability density clearly
        h_gen->GetZaxis()->SetRangeUser(0.001, h_gen->GetMaximum()); 
        
        h_gen->Draw("COLZ");
        h_gen->GetZaxis()->SetTitle("Fraction of Events");
        h_gen->GetZaxis()->SetTitleOffset(1.4);
    }

    c1->cd(2);
    TH2F *h_eb_center = (TH2F*)f->Get("demo/Hits_EB_Centered");
    if(h_eb_center && h_eb_center->GetEntries() > 0) {
        h_eb_center->SetTitle("Normalized ECAL Energy Pattern; i#eta pixel; i#phi pixel");
        
        h_eb_center->Scale(1.0 / h_eb_center->GetEntries());
        
        h_eb_center->GetXaxis()->SetRangeUser(0, 31);
        h_eb_center->GetYaxis()->SetRangeUser(0, 31);
        
        // Fix 2: Adjusting Log scale range so the "shower" tail is visible
        // Set minimum to a very small value so the blue/purple shows the edges
        h_eb_center->GetZaxis()->SetRangeUser(1e-6, h_eb_center->GetMaximum()); 
        
        h_eb_center->Draw("COLZ");
        gPad->SetLogz();
        gPad->SetRightMargin(0.18);
        h_eb_center->GetZaxis()->SetTitle("Avg Energy per Event (GeV)");
        h_eb_center->GetZaxis()->SetTitleOffset(1.5);
    }
    
    c1->SaveAs("Normalized_10_1_events.png");
}
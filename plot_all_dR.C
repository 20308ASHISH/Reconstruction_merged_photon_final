void plot_all_dR() {
    // 1. Setup Canvas
    TCanvas *c1 = new TCanvas("c1", "dR Comparison", 900, 700);
    gStyle->SetOptStat(0); // Remove statistics boxes for cleaner look
    
    // 2. Create a Stack to handle auto-scaling
    THStack *hs = new THStack("hs", "Photon Separation #DeltaR; #DeltaR; Events");

    // 3. Define file names and legend labels
    // Update these paths to your actual file locations
    std::vector<TString> files = {
        "DP1_folder/genparticle_histE10_ECal.root",
        "DP1_folder/genparticle_histE5_ECal.root",
        "DP1_folder/genparticle_histE1_ECal.root",
        "DP1_folder/genparticle_histE0.5_ECal.root",
        "DP1_folder/genparticle_histE0.1_ECal.root"
    };
    std::vector<TString> labels = {"E10 GeV", "E5 GeV", "E1 GeV", "E0.5 GeV", "E0.1 GeV"};
    std::vector<int> colors = {kBlack, kRed, kBlue, kGreen+2, kMagenta};

    // 4. Loop through files and add histograms to stack
    TLegend *leg = new TLegend(0.6, 0.65, 0.88, 0.88);
    leg->SetBorderSize(0);

    for (int i = 0; i < files.size(); ++i) {
        TFile *f = TFile::Open(files[i]);
        if (!f || f->IsZombie()) continue;

        TH1F *h = (TH1F*)f->Get("demo/Hits_dR");
        if (!h) continue;

        // Clone to keep it in memory after file closes
        TH1F *h_clone = (TH1F*)h->Clone(Form("h_%d", i));
        h_clone->SetDirectory(0); 
        h_clone->SetLineColor(colors[i]);
        h_clone->SetLineWidth(2);
        
        // Normalize if you want to compare shapes instead of raw counts
        h_clone->Scale(1.0 / h_clone->Integral()); 

        hs->Add(h_clone);
        leg->AddEntry(h_clone, labels[i], "l");
        f->Close();
    }

    
    hs->Draw("nostack hist"); 
    leg->Draw();

    
    c1->SetLogy(); 
    c1->SaveAs("All_Energies_dR_Comparison.png");
}
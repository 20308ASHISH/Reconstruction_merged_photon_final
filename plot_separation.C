
void plot_separation(const char* fileName) {
    TFile *f = TFile::Open(fileName);
    if (!f || f->IsZombie()) {
        printf("Error: Could not open file %s\n", fileName);
        return;
    }

    TCanvas *c1 = new TCanvas("c1", "Photon Separation Analysis", 1200, 400);
    c1->Divide(3,1);
    gStyle->SetOptStat(1111);

    c1->cd(1);
    TH1F *h_dr = (TH1F*)f->Get("demo/Hits_dR");
    if(h_dr) { h_dr->SetLineColor(kBlue); h_dr->Draw(); }

    c1->cd(2);
    TH1F *h_eta = (TH1F*)f->Get("demo/Hits_delta_eta");
    if(h_eta) { h_eta->SetLineColor(kRed); h_eta->Draw(); }

    c1->cd(3);
    TH1F *h_phi = (TH1F*)f->Get("demo/Hits_delta_phi");
    if(h_phi) { h_phi->SetLineColor(kGreen+2); h_phi->Draw(); }
    c1->SaveAs("Separation_Analysis.png");

    TCanvas *c2 = new TCanvas("c2", "Detector Hit Map", 800, 600);
    gStyle->SetOptStat(0);
    gStyle->SetPalette(kBird);

    TH2F *h_eb = (TH2F*)f->Get("demo/Hits_EB");
    if(h_eb) {
        h_eb->SetTitle("ECAL Barrel Hit Map; i#eta; i#phi");
        h_eb->GetXaxis()->SetRangeUser(-90, 90);
        h_eb->Draw("COLZ");
        gPad->SetLogz();
    }
    c2->SaveAs("Detector_Hit_Map.png");
} 

void plot_dR_all() {

  TCanvas *c = new TCanvas();

  TFile *f1 = TFile::Open("AToGG_GEN_E0.1_new.root");      // E10
  TFile *f2 = TFile::Open("AToGG_GEN_E0.5_new.root");
  TFile *f3 = TFile::Open("AToGG_GEN_E1_new.root");
  TFile *f4 = TFile::Open("AToGG_GEN_E5_new.root");
  TFile *f5 = TFile::Open("AToGG_GEN_E10_new.root");

  TTree *t1 = (TTree*)f1->Get("Events");
  TTree *t2 = (TTree*)f2->Get("Events");
  TTree *t3 = (TTree*)f3->Get("Events");
  TTree *t4 = (TTree*)f4->Get("Events");
  TTree *t5 = (TTree*)f5->Get("Events");

  t1->Draw("dR>>h1(50,0,5)");
  t2->Draw("dR>>h2(50,0,5)", "", "same");
  t3->Draw("dR>>h3(50,0,5)", "", "same");
  t4->Draw("dR>>h4(50,0,5)", "", "same");
  t5->Draw("dR>>h5(50,0,5)", "", "same");

  h1->SetLineColor(1);
  h2->SetLineColor(2);
  h3->SetLineColor(3);
  h4->SetLineColor(4);
  h5->SetLineColor(6);

  TLegend *leg = new TLegend(0.7,0.7,0.9,0.9);
  leg->AddEntry(h1,"E10","l");
  leg->AddEntry(h2,"E5","l");
  leg->AddEntry(h3,"E1","l");
  leg->AddEntry(h4,"E0.5","l");
  leg->AddEntry(h5,"E0.1","l");
  leg->Draw();
}
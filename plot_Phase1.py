import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPaintTextFormat(".2f")

f = ROOT.TFile.Open("DP1_folder/AToGG_GEN_E_new_all_10k_phase1_analysis.root", "READ")
tree = f.Get("demo/photonTree")

# Dynamic configuration adjusting ranges based on mass expectations
mass_ranges = [
    {"min": 0.1, "max": 1.0, "bins": 5,  "max_val": 5.0,  "lim": 5.0},
    {"min": 1.0, "max": 3.0, "bins": 5,  "max_val": 15.0, "lim": 15.0},
    {"min": 3.0, "max": 5.0, "bins": 5,  "max_val": 30.0, "lim": 30.0},
    {"min": 5.0, "max": 7.0, "bins": 5,  "max_val": 50.0, "lim": 50.0},
    {"min": 7.0, "max": 10.0, "bins": 5, "max_val": 80.0, "lim": 80.0}
]

for cfg in mass_ranges:
    m_min, m_max = cfg["min"], cfg["max"]
    
    h_left = ROOT.TH2F(
        "h_left_{}_{}".format(m_min, m_max), 
        "CMS Simulation (m_{A} = " + str(m_min) + "-" + str(m_max) + " GeV)", 
        cfg["bins"], 0, cfg["max_val"], cfg["bins"], 0, cfg["max_val"]
    )
    
    h_right = ROOT.TH2F(
        "h_right_{}_{}".format(m_min, m_max), 
        "CMS Simulation (m_{A} = " + str(m_min) + "-" + str(m_max) + " GeV, Single Event)", 
        60, -cfg["lim"], cfg["lim"], 60, -cfg["lim"], cfg["lim"]
    )
    
    found_event = False

    for entry in tree:
        m = entry.mass
        if not (m_min <= m < m_max):
            continue
        
        eta1, phi1, e1 = entry.pho1_eta, entry.pho1_phi, entry.pho1_energy
        eta2, phi2, e2 = entry.pho2_eta, entry.pho2_phi, entry.pho2_energy
        
        deta = abs(eta1 - eta2)
        dphi = abs(ROOT.TVector2.Phi_mpi_pi(phi1 - phi2))
        
        deta_c = deta / 0.0174
        dphi_c = dphi / 0.0174
        h_left.Fill(dphi_c, deta_c)
        
        if not found_event:
            # Anchor everything relative to the leading photon (pho1)
            rel_eta1 = 0.0
            rel_phi1 = 0.0
            
            # The subleading photon shows the true relative distance in crystal units
            rel_eta2 = (eta2 - eta1) / 0.0174
            rel_phi2 = ROOT.TVector2.Phi_mpi_pi(phi2 - phi1) / 0.0174
            
            h_right.Fill(rel_phi1, rel_eta1, e1)
            h_right.Fill(rel_phi2, rel_eta2, e2)
            found_event = True
        
    c = ROOT.TCanvas("c_{}_{}".format(m_min, m_max), "", 1600, 700)
    c.Divide(2, 1)
    
    # Left Panel: Accumulated Grid Matrix
    c.cd(1)
    ROOT.gPad.SetRightMargin(0.15)
    if h_left.Integral() > 0:
        h_left.Scale(1.0 / h_left.Integral())
    h_left.GetXaxis().SetTitle("#Delta#phi(y_{1},y_{2})^{gen} [crystal units]")
    h_left.GetYaxis().SetTitle("#Delta#eta(y_{1},y_{2})^{gen} [crystal units]")
    h_left.Draw("COLZ TEXT")
    
    # Right Panel: Centered Energy Scatter Display
    c.cd(2)
    ROOT.gPad.SetRightMargin(0.15)
    ROOT.gPad.SetLogz(True)
    h_right.GetXaxis().SetTitle("Relative Crystal #phi (centered on leading photon)")
    h_right.GetYaxis().SetTitle("Relative Crystal #eta (centered on leading photon)")
    h_right.GetZaxis().SetTitle("Energy [GeV]")
    h_right.Draw("COLZ")
    
    c.SaveAs("cms_plots_mass_{}_{}.png".format(m_min, m_max))
    
    h_left.Delete()
    h_right.Delete()
    c.Delete()

f.Close()
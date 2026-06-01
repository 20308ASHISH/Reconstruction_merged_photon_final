#include <memory>
#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include <algorithm>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "TH1F.h"
#include "TH2F.h"
#include "TTree.h"

class GenParticleAnalyzer_RECO : public edm::one::EDAnalyzer<edm::one::SharedResources> {

   public:
      explicit GenParticleAnalyzer_RECO(const edm::ParameterSet&);
      ~GenParticleAnalyzer_RECO() override = default;

   private:
      void analyze(const edm::Event&, const edm::EventSetup&) override;

      edm::EDGetTokenT<reco::GenParticleCollection> genParticlesToken_;

      TH1F* h_massA;
      TH1F* h_ptA;
      TH1F* h_ptPhotonLead;
      TH1F* h_ptPhotonSubLead;
      TH1F* h_deltaRPhotons;
      TH2F* h_deltaRVsMass;

      TTree* outTree_;

      float tree_mass_;
      int tree_nPhotons_;

      float A_pt_;
      float A_eta_;
      float A_phi_;
      float A_energy_;

      float pho1_pt_;
      float pho1_eta_;
      float pho1_phi_;
      float pho1_energy_;

      float pho2_pt_;
      float pho2_eta_;
      float pho2_phi_;
      float pho2_energy_;
};

GenParticleAnalyzer_RECO::GenParticleAnalyzer_RECO(const edm::ParameterSet& iConfig) :
   genParticlesToken_(
      consumes<reco::GenParticleCollection>(
         iConfig.getParameter<edm::InputTag>("genParticles")
      )
   )
{
   usesResource("TFileService");

   edm::Service<TFileService> fs;

   h_massA = fs->make<TH1F>("h_massA", "Mass of Particle A;Mass [GeV];Events", 120, 0.0, 12.0);
   h_ptA = fs->make<TH1F>("h_ptA", "p_{T} of Particle A;p_{T} [GeV];Events", 100, 0.0, 110.0);
   h_ptPhotonLead = fs->make<TH1F>("h_ptPhotonLead", "Leading Photon p_{T};p_{T} [GeV];Events", 100, 0.0, 110.0);
   h_ptPhotonSubLead = fs->make<TH1F>("h_ptPhotonSubLead", "Sub-Leading Photon p_{T};p_{T} [GeV];Events", 100, 0.0, 110.0);
   h_deltaRPhotons = fs->make<TH1F>("h_deltaRPhotons", "#DeltaR between Photons;#DeltaR;Events", 100, 0.0, 5.0);
   h_deltaRVsMass = fs->make<TH2F>("h_deltaRVsMass", "#DeltaR vs Mass of A;Mass [GeV];#DeltaR", 120, 0.0, 12.0, 100, 0.0, 5.0);

   outTree_ = fs->make<TTree>("photonTree", "Event Multiplicity Tree");
   outTree_->Branch("mass", &tree_mass_, "mass/F");
   outTree_->Branch("nPhotons", &tree_nPhotons_, "nPhotons/I");

   outTree_->Branch("A_pt",     &A_pt_,     "A_pt/F");
   outTree_->Branch("A_eta",    &A_eta_,    "A_eta/F");
   outTree_->Branch("A_phi",    &A_phi_,    "A_phi/F");
   outTree_->Branch("A_energy", &A_energy_, "A_energy/F");

   outTree_->Branch("pho1_pt",     &pho1_pt_,     "pho1_pt/F");
   outTree_->Branch("pho1_eta",    &pho1_eta_,    "pho1_eta/F");
   outTree_->Branch("pho1_phi",    &pho1_phi_,    "pho1_phi/F");
   outTree_->Branch("pho1_energy", &pho1_energy_, "pho1_energy/F");

   outTree_->Branch("pho2_pt",     &pho2_pt_,     "pho2_pt/F");
   outTree_->Branch("pho2_eta",    &pho2_eta_,    "pho2_eta/F");
   outTree_->Branch("pho2_phi",    &pho2_phi_,    "pho2_phi/F");
   outTree_->Branch("pho2_energy", &pho2_energy_, "pho2_energy/F");
}

void GenParticleAnalyzer_RECO::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

   edm::Handle<reco::GenParticleCollection> genParticles;
   iEvent.getByToken(genParticlesToken_, genParticles);

   std::vector<const reco::GenParticle*> photons;

   for (const auto& particle : *genParticles) {

      if (std::abs(particle.pdgId()) == 36) {
         photons.clear();

         for (unsigned int i = 0; i < particle.numberOfDaughters(); ++i) {
            const reco::Candidate* dau = particle.daughter(i);
            if (std::abs(dau->pdgId()) == 22) {
               const reco::GenParticle* genPho = dynamic_cast<const reco::GenParticle*>(dau);
               if (genPho) photons.push_back(genPho);
            }
         }

         if (!photons.empty()) {
            std::sort(photons.begin(), photons.end(), [](const reco::GenParticle* a, const reco::GenParticle* b) {
               return a->pt() > b->pt();
            });
         }

         double SimMass = particle.mass();
         double SimPt   = particle.pt();

         A_pt_     = particle.pt();
         A_eta_    = particle.eta();
         A_phi_    = particle.phi();
         A_energy_ = particle.energy();

         h_massA->Fill(SimMass);
         h_ptA->Fill(SimPt);

         pho1_pt_ = pho1_eta_ = pho1_phi_ = pho1_energy_ = -999.0;
         pho2_pt_ = pho2_eta_ = pho2_phi_ = pho2_energy_ = -999.0;

         if (photons.size() >= 1) {
            h_ptPhotonLead->Fill(photons[0]->pt());
            pho1_pt_     = photons[0]->pt();
            pho1_eta_    = photons[0]->eta();
            pho1_phi_    = photons[0]->phi();
            pho1_energy_ = photons[0]->energy();
         }

         if (photons.size() >= 2) {
            h_ptPhotonSubLead->Fill(photons[1]->pt());
            pho2_pt_     = photons[1]->pt();
            pho2_eta_    = photons[1]->eta();
            pho2_phi_    = photons[1]->phi();
            pho2_energy_ = photons[1]->energy();

            double dR = reco::deltaR(photons[0]->eta(), photons[0]->phi(), photons[1]->eta(), photons[1]->phi());
            h_deltaRPhotons->Fill(dR);
            h_deltaRVsMass->Fill(SimMass, dR);
         }

         tree_mass_ = SimMass;
         tree_nPhotons_ = photons.size();

         outTree_->Fill();
      }
   }
}

DEFINE_FWK_MODULE(GenParticleAnalyzer_RECO);
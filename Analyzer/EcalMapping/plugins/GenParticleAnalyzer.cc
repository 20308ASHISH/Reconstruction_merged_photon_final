#include <memory>
#include <iostream>
#include <cmath>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "DataFormats/Math/interface/deltaPhi.h"

#include "TTree.h"

class GenParticleAnalyzer : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit GenParticleAnalyzer(const edm::ParameterSet&);
  ~GenParticleAnalyzer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override {}

  edm::EDGetTokenT<edm::View<reco::GenParticle>> particleToken_;

  TTree* photonTree;
  float mass;
  float pho1_eta;
  float pho1_phi;
  float pho1_energy;
  float pho2_eta;
  float pho2_phi;
  float pho2_energy;
};

GenParticleAnalyzer::GenParticleAnalyzer(const edm::ParameterSet& iConfig) {
  usesResource("TFileService");
  particleToken_ = consumes<edm::View<reco::GenParticle>>(iConfig.getParameter<edm::InputTag>("genParticles"));
}

void GenParticleAnalyzer::beginJob() {
  edm::Service<TFileService> fs;
  photonTree = fs->make<TTree>("photonTree", "Generator Level Photon Kinematics");
  
  photonTree->Branch("mass", &mass, "mass/F");
  photonTree->Branch("pho1_eta", &pho1_eta, "pho1_eta/F");
  photonTree->Branch("pho1_phi", &pho1_phi, "pho1_phi/F");
  photonTree->Branch("pho1_energy", &pho1_energy, "pho1_energy/F");
  photonTree->Branch("pho2_eta", &pho2_eta, "pho2_eta/F");
  photonTree->Branch("pho2_phi", &pho2_phi, "pho2_phi/F");
  photonTree->Branch("pho2_energy", &pho2_energy, "pho2_energy/F");
}

void GenParticleAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace reco;

  Handle<View<GenParticle>> particles;
  iEvent.getByToken(particleToken_, particles);

  const GenParticle* pho1 = nullptr;
  const GenParticle* pho2 = nullptr;

  for (const auto& p : *particles) {
    if (p.pdgId() == 22 && p.status() == 1) { 
      if (!pho1) {
        pho1 = &p;
      } else if (!pho2) {
        pho2 = &p;
        break; 
      }
    }
  }

  if (pho1 && pho2) {
    if (pho2->pt() > pho1->pt()) {
      std::swap(pho1, pho2);
    }

    math::XYZTLorentzVector totalP4 = pho1->p4() + pho2->p4();
    mass = totalP4.M();

    pho1_eta = pho1->eta();
    pho1_phi = pho1->phi();
    pho1_energy = pho1->energy();

    pho2_eta = pho2->eta();
    pho2_phi = pho2->phi();
    pho2_energy = pho2->energy();

    photonTree->Fill();
  }
}

void GenParticleAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("genParticles", edm::InputTag("genParticles"));
  descriptions.addDefault(desc);
}

DEFINE_FWK_MODULE(GenParticleAnalyzer);


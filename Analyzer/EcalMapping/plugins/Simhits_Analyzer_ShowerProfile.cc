// -*- C++ -*-
//
// Package:    Simhits_Analyzer_ShowerProfile/Simhits_Analyzer_ShowerProfile
// Class:      Simhits_Analyzer_ShowerProfile
//
/**\class Simhits_Analyzer_ShowerProfile Simhits_Analyzer_ShowerProfile.cc Simhits_Analyzer_ShowerProfile/Simhits_Analyzer_ShowerProfile/plugins/Simhits_Analyzer_ShowerProfile.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Rajdeep Mohan Chatterjee
//         Created:  Fri, 16 Oct 2020 14:03:21 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"


#include "DataFormats/HepMCCandidate/interface/GenParticle.h"


#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/CaloGeometry/interface/TruncatedPyramid.h"
#include "Geometry/EcalAlgo/interface/EcalPreshowerGeometry.h"
#include "Geometry/CaloTopology/interface/EcalPreshowerTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/CaloEventSetup/interface/CaloTopologyRecord.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"


#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"

#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/ESDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"


#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TTree.h"
#include "TH1.h"
#include "TH2F.h"
#include "TCanvas.h"
#include <iostream>
#include <fstream>


//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<>
// This will improve performance in multithreaded jobs.


class Simhits_Analyzer_ShowerProfile : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit Simhits_Analyzer_ShowerProfile(const edm::ParameterSet&);
  ~Simhits_Analyzer_ShowerProfile();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  static const int offset = 0x3;

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // ----------member data ---------------------------
  TH1F* Profile_EB;
  TH1F* Profile_EB_Coarse;
  TH1F* NHits_EB;
  TH2F* Hits_EB;
  TH2F* Hits_EB_cartesian;
  TH1F* NHits_ES_Plus;
  TH2F* Hits_ES_Plus;
  TH1F* NHits_ES_Minus;
  TH2F* Hits_ES_Minus;
  TH1F* Profile_EE_Plus;
  TH1F* Profile_EE_Coarse_Plus;
  TH1F* NHits_EE_Plus;
  TH2F* Hits_EE_Plus;
  TH2F* Hits_EE_Plus_Depth0;
  TH1F* Profile_EE_Minus;
  TH1F* Profile_EE_Coarse_Minus;
  TH1F* NHits_EE_Minus;
  TH2F* Hits_EE_Minus;   
  Long64_t run, event, lumi;

  edm::Handle<edm::View<reco::GenParticle> > particle;
  edm::EDGetTokenT<edm::View< reco::GenParticle > > particleToken;

  edm::Handle<edm::PCaloHitContainer> pCaloHits_EB_Handle;
  edm::EDGetTokenT<edm::PCaloHitContainer> pCaloHits_EB_Token;

  edm::Handle<edm::PCaloHitContainer> pCaloHits_ES_Handle;
  edm::EDGetTokenT<edm::PCaloHitContainer> pCaloHits_ES_Token;
  
  edm::Handle<edm::PCaloHitContainer> pCaloHits_EE_Handle;
  edm::EDGetTokenT<edm::PCaloHitContainer> pCaloHits_EE_Token;  
  

#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  edm::ESGetToken<SetupData, SetupRecord> setupToken_;
#endif
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
Simhits_Analyzer_ShowerProfile::Simhits_Analyzer_ShowerProfile(const edm::ParameterSet& iConfig){

	usesResource("TFileService");
	particleToken = consumes< edm::View < reco::GenParticle> >(edm::InputTag("genParticles"));
        pCaloHits_EB_Token = consumes<edm::PCaloHitContainer>(edm::InputTag("g4SimHits", "EcalHitsEB", "SIM"));
        pCaloHits_ES_Token = consumes<edm::PCaloHitContainer>(edm::InputTag("g4SimHits","EcalHitsES","SIM"));
        pCaloHits_EE_Token = consumes<edm::PCaloHitContainer>(edm::InputTag("g4SimHits", "EcalHitsEE", "SIM"));
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  setupDataToken_ = esConsumes<SetupData, SetupRecord>();
#endif
  //now do what ever initialization is needed
}

Simhits_Analyzer_ShowerProfile::~Simhits_Analyzer_ShowerProfile() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called for each event  ------------
void Simhits_Analyzer_ShowerProfile::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using namespace reco;


  run = iEvent.id().run();
  event = iEvent.id().event();
  lumi = iEvent.id().luminosityBlock();
  

  iEvent.getByToken(particleToken, particle);         //GenParticles
  iEvent.getByToken(pCaloHits_EB_Token, pCaloHits_EB_Handle); //PCaloHits EB
  iEvent.getByToken(pCaloHits_ES_Token, pCaloHits_ES_Handle); //PCaloHits ES
  iEvent.getByToken(pCaloHits_EE_Token, pCaloHits_EE_Handle); //PCaloHits EE

  ESHandle<CaloGeometry> pG;
  iSetup.get<CaloGeometryRecord>().get(pG);
  const CaloGeometry* geo = pG.product();

  EBDetId* DidEB;
  ESDetId* DidES;
  EEDetId* DidEE;
 

  int NHits, NHits_Plus, NHits_Minus = 0;
  float Energy = 0.;

  edm::PCaloHitContainer::const_iterator caloHitsItr;

  const CaloSubdetectorGeometry* ecalEBGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalBarrel));

  
  for(caloHitsItr = pCaloHits_EB_Handle->begin(); caloHitsItr != pCaloHits_EB_Handle->end(); caloHitsItr++){
          int temp = caloHitsItr->depth();
          DidEB = new EBDetId(caloHitsItr->id());
//          temp &= 0x0003;
//          double depth = (1/8191.)*(caloHitsItr->depth()>>offset);
	  if ((temp == 1) || (temp == 2))
                continue;
//          double depth = (caloHitsItr->depth()>>3);
          double depth = (1./8191.)*(caloHitsItr->depth()>>3);
	  NHits++;
          Energy += caloHitsItr->energy();
          Hits_EB->Fill(DidEB->ieta(), DidEB->iphi());
	  Profile_EB->Fill(depth, caloHitsItr->energy());
          Profile_EB_Coarse->Fill(depth, caloHitsItr->energy());
  }

  NHits_EB->Fill(NHits);


  const CaloSubdetectorGeometry* ecalESGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalPreshower));
  NHits_Plus = 0;
  NHits_Minus = 0;
  Energy = 0.;

  for(caloHitsItr = pCaloHits_ES_Handle->begin(); caloHitsItr != pCaloHits_ES_Handle->end(); caloHitsItr++){
          DidES = new ESDetId(caloHitsItr->id());
          NHits++;
          Energy += caloHitsItr->energy();
	  std::shared_ptr<const CaloCellGeometry> geom = ecalESGeom->getGeometry(*DidES);

	  if (DidES->zside() == 1){
          	Hits_ES_Plus->Fill(geom->getPosition().x(), geom->getPosition().y());
		NHits_Plus++;
	  }
	  if (DidES->zside() == -1){
                Hits_ES_Minus->Fill(geom->getPosition().x(), geom->getPosition().y());
		NHits_Minus++;
	  }

  }

  NHits_ES_Plus->Fill(NHits_Plus);
  NHits_ES_Minus->Fill(NHits_Minus);
  NHits_Plus = 0;
  NHits_Minus = 0;
  Energy = 0.;


  const CaloSubdetectorGeometry* ecalEEGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalEndcap));

  for(caloHitsItr = pCaloHits_EE_Handle->begin(); caloHitsItr != pCaloHits_EE_Handle->end(); caloHitsItr++){
          uint16_t temp = caloHitsItr->depth();
          DidEE = new EEDetId(caloHitsItr->id());
//          temp &= 0x0003;
	  NHits++;
	  Energy += caloHitsItr->energy();
//          double depth = (1/8191.)*(caloHitsItr->depth()>>offset);
	  if ((temp == 1) || (temp == 2))
		continue;
//	  double depth = (caloHitsItr->depth()>>3);	
	  double depth = (1./8191.)*(caloHitsItr->depth()>>3);
	  std::shared_ptr<const CaloCellGeometry> geom = ecalEEGeom->getGeometry(*DidEE);
	  if (DidEE->zside() == 1){
		if(depth == 0){
			Hits_EE_Plus_Depth0->Fill(geom->getPosition().x(), geom->getPosition().y());
		}
		Profile_EE_Plus->Fill(depth,caloHitsItr->energy());
		Profile_EE_Coarse_Plus->Fill(depth, caloHitsItr->energy());
		Hits_EE_Plus->Fill(geom->getPosition().x(), geom->getPosition().y());
		NHits_Plus++;
	  }
	  if (DidEE->zside() == -1){
		Profile_EE_Minus->Fill(depth,caloHitsItr->energy());
		Profile_EE_Coarse_Minus->Fill(depth, caloHitsItr->energy());
                Hits_EE_Minus->Fill(geom->getPosition().x(), geom->getPosition().y());
		NHits_Minus++;
	  }
  }

  NHits_EE_Plus->Fill(NHits_Plus);
  NHits_EE_Minus->Fill(NHits_Minus);

//Gen Stuff
  for (auto &p : *particle){
//	cout<<endl<<" PDG Id = "<<p.pdgId()<<" Energy  = "<<p.energy()<<" Eta = "<<p.eta()<<endl;
  }


#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  // if the SetupData is always needed
  auto setup = iSetup.getData(setupToken_);
  // if need the ESHandle to check if the SetupData was there or not
  auto pSetup = iSetup.getHandle(setupToken_);
#endif
}

// ------------ method called once each job just before starting event loop  ------------
void Simhits_Analyzer_ShowerProfile::beginJob() {
  // please remove this method if not needed
  edm::Service<TFileService> fs;
  NHits_EB = fs->make<TH1F>("NHits_EB","NHits_EB",500,0, 500);
  Hits_EB = fs->make<TH2F>("Hits_EB","Hits_EB",400,-200, 200, 360,0, 360);
  Hits_EB_cartesian = fs->make<TH2F>("Hits_EB_cartesian", "Hits_EB_cartesian", 400,-200, 200, 400,-200, 200);
//  Profile_EB = fs->make<TH1F>("Profile_EB","Profile_EB",230,0., 23.);
  Profile_EB = fs->make<TH1F>("Profile_EB","Profile_EB",200,0., 1.);
  Profile_EB_Coarse = fs->make<TH1F>("Profile_EB_Coarse","Profile_EB_Coarse",23,0., 1.);

  NHits_ES_Plus = fs->make<TH1F>("NHits_ES_Plus","NHits_ES_Plus",500,0, 500);
  Hits_ES_Plus = fs->make<TH2F>("Hits_ES_Plus","Hits_ES_Plus",400,-200, 200, 400,-200, 200);
  NHits_ES_Minus = fs->make<TH1F>("NHits_ES_Minus","NHits_ES_Minus",500,0, 500);
  Hits_ES_Minus = fs->make<TH2F>("Hits_ES_Minus","Hits_ES_Minus",400,-200, 200, 400,-200, 200);

  Profile_EE_Plus = fs->make<TH1F>("Profile_EE_Plus","Profile_EE_Plus",200,0., 1.);
  Profile_EE_Coarse_Plus = fs->make<TH1F>("Profile_EE_Coarse_Plus","Profile_EE_Coarse_Plus",23,0., 1.);
  NHits_EE_Plus = fs->make<TH1F>("NHits_EE_Plus","NHits_EE_Plus",500,0, 500);
  Hits_EE_Plus = fs->make<TH2F>("Hits_EE_Plus","Hits_EE_Plus",400,-200, 200, 400, -200, 200);
  Hits_EE_Plus_Depth0 = fs->make<TH2F>("Hits_EE_Plus_Depth0","Hits_EE_Plus_Depth0",400,-200, 200, 400, -200, 200);
  
//  Profile_EE_Minus = fs->make<TH1F>("Profile_EE_Minus","Profile_EE_Minus",230,0., 23.);
  Profile_EE_Minus = fs->make<TH1F>("Profile_EE_Minus","Profile_EE_Minus",200,0., 1.);
  Profile_EE_Coarse_Minus = fs->make<TH1F>("Profile_EE_Coarse_Minus","Profile_EE_Coarse_Minus",23,0., 1.);
  NHits_EE_Minus = fs->make<TH1F>("NHits_EE_Minus","NHits_EE_Minus",500,0, 500);
  Hits_EE_Minus = fs->make<TH2F>("Hits_EE_Minus","Hits_EE_Minus", 400,-200, 200, 400, -200, 200);
}

// ------------ method called once each job just after ending the event loop  ------------
void Simhits_Analyzer_ShowerProfile::endJob() {
  // please remove this method if not needed
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void Simhits_Analyzer_ShowerProfile::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

  //Specify that only 'tracks' is allowed
  //To use, remove the default given above and uncomment below
  //ParameterSetDescription desc;
  //desc.addUntracked<edm::InputTag>("tracks","ctfWithMaterialTracks");
  //descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(Simhits_Analyzer_ShowerProfile);

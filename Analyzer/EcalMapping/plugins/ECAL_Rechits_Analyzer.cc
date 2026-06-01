// -*- C++ -*-
//
// Package:    ECAL_Rechits_Analyzer/ECAL_Rechits_Analyzer
// Class:      ECAL_Rechits_Analyzer
//
/**\class ECAL_Rechits_Analyzer ECAL_Rechits_Analyzer.cc ECAL_Rechits_Analyzer/ECAL_Rechits_Analyzer/plugins/ECAL_Rechits_Analyzer.cc

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

#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"


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


class ECAL_Rechits_Analyzer : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit ECAL_Rechits_Analyzer(const edm::ParameterSet&);
  ~ECAL_Rechits_Analyzer();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // ----------member data ---------------------------
  TH1F* NHits_EB;
  TH2F* Hits_EB;
  TH2F* Hits_EB_XZ;
  TH2F* Hits_EB_YZ;
  TH1F* NHits_ES_Plus;
  TH2F* Hits_ES_Plus;
  TH1F* NHits_ES_Minus;
  TH2F* Hits_ES_Minus;
  TH1F* NHits_EE_Plus;
  TH2F* Hits_EE_Plus;
  TH2F* Hits_EE_Local_Plus;
  TH1F* NHits_EE_Minus;
  TH2F* Hits_EE_Minus;  
  TH2F* Hits_EE_Local_Minus; 
  Long64_t run, event, lumi;

  edm::Handle<edm::View<reco::GenParticle> > particle;
  edm::EDGetTokenT<edm::View< reco::GenParticle > > particleToken;

  edm::Handle<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > EBRechitsHandle;
  edm::Handle<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > EERechitsHandle;
  edm::Handle<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > ESRechitsHandle;
        
  edm::EDGetTokenT<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > recHitCollectionEBToken_;
  edm::EDGetTokenT<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > recHitCollectionEEToken_;
  edm::EDGetTokenT<edm::SortedCollection<EcalRecHit, edm::StrictWeakOrdering<EcalRecHit> > > recHitCollectionESToken_;

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
ECAL_Rechits_Analyzer::ECAL_Rechits_Analyzer(const edm::ParameterSet& iConfig){

	usesResource("TFileService");
	particleToken = consumes< edm::View < reco::GenParticle> >(edm::InputTag("genParticles"));
        recHitCollectionEBToken_ = consumes<EcalRecHitCollection>(edm::InputTag("reducedEcalRecHitsEB"));
        recHitCollectionEEToken_ = consumes<EcalRecHitCollection>(edm::InputTag("reducedEcalRecHitsEE"));
        recHitCollectionESToken_ = consumes<EcalRecHitCollection>(edm::InputTag("reducedEcalRecHitsES"));

#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  setupDataToken_ = esConsumes<SetupData, SetupRecord>();
#endif
  //now do what ever initialization is needed
}

ECAL_Rechits_Analyzer::~ECAL_Rechits_Analyzer() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called for each event  ------------
void ECAL_Rechits_Analyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using namespace reco;


  run = iEvent.id().run();
  event = iEvent.id().event();
  lumi = iEvent.id().luminosityBlock();
  

  iEvent.getByToken(particleToken, particle);         //GenParticles
  iEvent.getByToken(recHitCollectionEBToken_, EBRechitsHandle);
  iEvent.getByToken(recHitCollectionEEToken_, EERechitsHandle);
  iEvent.getByToken(recHitCollectionESToken_, ESRechitsHandle);


  ESHandle<CaloGeometry> pG;
  iSetup.get<CaloGeometryRecord>().get(pG);
  const CaloGeometry* geo = pG.product();

  EBDetId* DidEB;
  ESDetId* DidES;
  EEDetId* DidEE;
 

  int NHits, NHits_Plus, NHits_Minus = 0;
  float Energy = 0.;

  EcalRecHitCollection::const_iterator oneHit;
  const CaloSubdetectorGeometry* ecalEBGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalBarrel));

  
  for(oneHit = EBRechitsHandle->begin(); oneHit != EBRechitsHandle->end(); oneHit++){
          DidEB = new EBDetId(oneHit->id());
	  NHits++;
          Energy += oneHit->energy();
	  std::shared_ptr<const CaloCellGeometry> geomEB = ecalEBGeom->getGeometry(*DidEB);

          Hits_EB->Fill(DidEB->ieta(), DidEB->iphi());
	  Hits_EB_XZ->Fill(geomEB->getPosition().x(), geomEB->getPosition().z());
	  Hits_EB_YZ->Fill(geomEB->getPosition().y(), geomEB->getPosition().z());
//	  cout<<endl<<" X = "<< geomEB->getPosition().x()<<" Y = "<<geomEB->getPosition().y()<<" Z = "<<geomEB->getPosition().z()<<endl;
  }

  NHits_EB->Fill(NHits);


  const CaloSubdetectorGeometry* ecalESGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalPreshower));
  NHits_Plus = 0;
  NHits_Minus = 0;
  Energy = 0.;

  for(oneHit = ESRechitsHandle->begin(); oneHit != ESRechitsHandle->end(); oneHit++){
          DidES = new ESDetId(oneHit->id());
          NHits++;
          Energy += oneHit->energy();
	  std::shared_ptr<const CaloCellGeometry> geomES = ecalESGeom->getGeometry(*DidES);

	  if (DidES->zside() == 1){
          	Hits_ES_Plus->Fill(geomES->getPosition().x(), geomES->getPosition().y());
		NHits_Plus++;
	  }
	  if (DidES->zside() == -1){
                Hits_ES_Minus->Fill(geomES->getPosition().x(), geomES->getPosition().y());
		NHits_Minus++;
	  }

  }

  NHits_ES_Plus->Fill(NHits_Plus);
  NHits_ES_Minus->Fill(NHits_Minus);
  NHits_Plus = 0;
  NHits_Minus = 0;
  Energy = 0.;


  const CaloSubdetectorGeometry* ecalEEGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalEndcap));

  for(oneHit = EERechitsHandle->begin(); oneHit != EERechitsHandle->end(); oneHit++){
          DidEE = new EEDetId(oneHit->id());
	  NHits++;
	  Energy += oneHit->energy();
	  std::shared_ptr<const CaloCellGeometry> geomEE = ecalEEGeom->getGeometry(*DidEE);
	  if (DidEE->zside() == 1){
		Hits_EE_Plus->Fill(geomEE->getPosition().x(), geomEE->getPosition().y());
		Hits_EE_Local_Plus->Fill(DidEE->ix(), DidEE->iy());
		NHits_Plus++;
	  }
	  if (DidEE->zside() == -1){
                Hits_EE_Minus->Fill(geomEE->getPosition().x(), geomEE->getPosition().y());
		Hits_EE_Local_Minus->Fill(DidEE->ix(), DidEE->iy());
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
void ECAL_Rechits_Analyzer::beginJob() {
  // please remove this method if not needed
  edm::Service<TFileService> fs;
  NHits_EB = fs->make<TH1F>("NHits_EB","NHits_EB",500,0, 500);
  Hits_EB = fs->make<TH2F>("Hits_EB","Hits_EB",400,-200, 200, 360,0, 360);
  Hits_EB_XZ = fs->make<TH2F>("Hits_EB_XZ", "Hits_EB_XZ", 800,-200., 200., 1600,-800, 800);
  Hits_EB_YZ = fs->make<TH2F>("Hits_EB_YZ", "Hits_EB_YZ", 800,-200., 200., 1600,-800, 800);


  NHits_ES_Plus = fs->make<TH1F>("NHits_ES_Plus","NHits_ES_Plus",500,0, 500);
  Hits_ES_Plus = fs->make<TH2F>("Hits_ES_Plus","Hits_ES_Plus",800,-200, 200, 400,-200, 200);
  NHits_ES_Minus = fs->make<TH1F>("NHits_ES_Minus","NHits_ES_Minus",500,0, 500);
  Hits_ES_Minus = fs->make<TH2F>("Hits_ES_Minus","Hits_ES_Minus",400,-200, 200, 400,-200, 200);

  NHits_EE_Plus = fs->make<TH1F>("NHits_EE_Plus","NHits_EE_Plus",500,0, 500);
  Hits_EE_Plus = fs->make<TH2F>("Hits_EE_Plus","Hits_EE_Plus",800,-200., 200., 800, -200., 200.);
  Hits_EE_Local_Plus = fs->make<TH2F>("Hits_EE_Local_Plus","Hits_EE_Local_Plus",110,0, 110, 110, 0, 110);  

  NHits_EE_Minus = fs->make<TH1F>("NHits_EE_Minus","NHits_EE_Minus",500,0, 500);
  Hits_EE_Minus = fs->make<TH2F>("Hits_EE_Minus","Hits_EE_Minus", 800,-200., 200., 800, -200., 200.);
  Hits_EE_Local_Minus = fs->make<TH2F>("Hits_EE_Local_Minus","Hits_EE_Local_Minus",110,0, 110, 110, 0, 110);
}

// ------------ method called once each job just after ending the event loop  ------------
void ECAL_Rechits_Analyzer::endJob() {
  // please remove this method if not needed
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void ECAL_Rechits_Analyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
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
DEFINE_FWK_MODULE(ECAL_Rechits_Analyzer);

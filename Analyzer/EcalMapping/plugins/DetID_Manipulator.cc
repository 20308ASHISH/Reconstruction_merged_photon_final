// -*- C++ -*-
//
// Package:    DetID_Manipulator/DetID_Manipulator
// Class:      DetID_Manipulator
//
/**\class DetID_Manipulator DetID_Manipulator.cc DetID_Manipulator/DetID_Manipulator/plugins/DetID_Manipulator.cc

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
#include <sstream>

using namespace std;

//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<>
// This will improve performance in multithreaded jobs.


class DetID_Manipulator : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit DetID_Manipulator(const edm::ParameterSet&);
  ~DetID_Manipulator();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


private:
  void beginJob(const edm::EventSetup&);
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // ----------member data ---------------------------
  Long64_t run, event, lumi;


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
DetID_Manipulator::DetID_Manipulator(const edm::ParameterSet& iConfig){

	usesResource("TFileService");
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  setupDataToken_ = esConsumes<SetupData, SetupRecord>();
#endif
  //now do what ever initialization is needed
}

DetID_Manipulator::~DetID_Manipulator() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called for each event  ------------
void DetID_Manipulator::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using namespace reco;


  run = iEvent.id().run();
  event = iEvent.id().event();
  lumi = iEvent.id().luminosityBlock();
  
ESHandle<CaloGeometry> pG;
   iSetup.get<CaloGeometryRecord>().get(pG);
   const CaloGeometry* geo = pG.product();
   const CaloSubdetectorGeometry* ecalEBGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalBarrel));
   const CaloSubdetectorGeometry* ecalEEGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalEndcap));


   std::vector<int> *XRecHitSCEle1=new std::vector<int>();
   std::vector<int> *XRecHitSCEle2=new std::vector<int>();
   std::vector<int> *YRecHitSCEle1=new std::vector<int>();
   std::vector<int> *YRecHitSCEle2=new std::vector<int>();

   std::vector<unsigned int> *rawIdRecHitSCEle1=new std::vector<unsigned int>();
   std::vector<unsigned int> *rawIdRecHitSCEle2=new std::vector<unsigned int>();

   std::vector<float> *energyRecHitSCEle1=new std::vector<float>();
   std::vector<float> *energyRecHitSCEle2=new std::vector<float>();
   std::vector<float> *fracRecHitSCEle1=new std::vector<float>();
   std::vector<float> *fracRecHitSCEle2=new std::vector<float>();

   TTree *Tread1;
   TFile *file_in1 = TFile::Open("/eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/13TeV/ALCARERECO//106X_dataRun2_UL18/EGamma-Run2018D-ZSkim-19Nov2018-v2/320500-325175/noJSON/pedNoise/extraCalibTree-EGamma-Run2018D-ZSkim-19Nov2018-v2-320500-325175.root");

   cout<<endl<<"  Reached Here "<<endl;
 
   file_in1->cd();

   Tread1 = (TTree*)gDirectory->Get("extraCalibTree");
   Tread1->SetBranchAddress("XRecHitSCEle1", &XRecHitSCEle1);
   Tread1->SetBranchAddress("XRecHitSCEle2", &XRecHitSCEle2);
   Tread1->SetBranchAddress("YRecHitSCEle1", &YRecHitSCEle1);
   Tread1->SetBranchAddress("YRecHitSCEle2", &YRecHitSCEle2);
   Tread1->SetBranchAddress("energyRecHitSCEle1", &energyRecHitSCEle1);
   Tread1->SetBranchAddress("energyRecHitSCEle2", &energyRecHitSCEle2);
   Tread1->SetBranchAddress("rawIdRecHitSCEle1", &rawIdRecHitSCEle1);
   Tread1->SetBranchAddress("rawIdRecHitSCEle2", &rawIdRecHitSCEle2);
   Tread1->SetBranchAddress("fracRecHitSCEle1", &fracRecHitSCEle1);
   Tread1->SetBranchAddress("fracRecHitSCEle2", &fracRecHitSCEle2);

   int nentries1 = Tread1->GetEntries();

   EBDetId* DidEB;

   for(int i=0; i  < nentries1; i++){
        
        if(i%100000==0) cout << i << endl;
        Tread1->GetEntry(i);
 

        if (rawIdRecHitSCEle1->size() < 1)
                continue;      

        for(unsigned int RecSize1 = 0; RecSize1 < rawIdRecHitSCEle1->size(); RecSize1++){
                DetId Did = (*rawIdRecHitSCEle1)[RecSize1];
                shared_ptr<const CaloCellGeometry> geom = ecalEBGeom->getGeometry(Did);
                cout<<endl<<" x = "<< geom->getPosition().x() << " y = " << geom->getPosition().y() << endl; 
                }
  
 
   }



#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
  // if the SetupData is always needed
  auto setup = iSetup.getData(setupToken_);
  // if need the ESHandle to check if the SetupData was there or not
  auto pSetup = iSetup.getHandle(setupToken_);
#endif
}

// ------------ method called once each job just before starting event loop  ------------
void DetID_Manipulator::beginJob(const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using namespace reco;

  // please remove this method if not needed
  edm::Service<TFileService> fs;
/*
   ESHandle<CaloGeometry> pG;
   iSetup.get<CaloGeometryRecord>().get(pG);
   const CaloGeometry* geo = pG.product();
   const CaloSubdetectorGeometry* ecalEBGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalBarrel));
   const CaloSubdetectorGeometry* ecalEEGeom = static_cast<const CaloSubdetectorGeometry*>(geo->getSubdetectorGeometry(DetId::Ecal, EcalEndcap));


   std::vector<int> *XRecHitSCEle1=new std::vector<int>();
   std::vector<int> *XRecHitSCEle2=new std::vector<int>();
   std::vector<int> *YRecHitSCEle1=new std::vector<int>();
   std::vector<int> *YRecHitSCEle2=new std::vector<int>();

   std::vector<unsigned int> *rawIdRecHitSCEle1=new std::vector<unsigned int>();
   std::vector<unsigned int> *rawIdRecHitSCEle2=new std::vector<unsigned int>();

   std::vector<float> *energyRecHitSCEle1=new std::vector<float>();
   std::vector<float> *energyRecHitSCEle2=new std::vector<float>();
   std::vector<float> *fracRecHitSCEle1=new std::vector<float>();
   std::vector<float> *fracRecHitSCEle2=new std::vector<float>();
*/

/*
   TTree *Tread1;
   TFile *file_in1 = TFile::Open("/eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/13TeV/ALCARERECO//106X_dataRun2_UL18/EGamma-Run2018D-ZSkim-19Nov2018-v2/320500-325175/noJSON/pedNoise/extraCalibTree-EGamma-Run2018D-ZSkim-19Nov2018-v2-320500-325175.root");

   cout<<endl<<"  Reached Here "<<endl;
 
   file_in1->cd();

   Tread1 = (TTree*)gDirectory->Get("extraCalibTree");
   Tread1->SetBranchAddress("XRecHitSCEle1", &XRecHitSCEle1);
   Tread1->SetBranchAddress("XRecHitSCEle2", &XRecHitSCEle2);
   Tread1->SetBranchAddress("YRecHitSCEle1", &YRecHitSCEle1);
   Tread1->SetBranchAddress("YRecHitSCEle2", &YRecHitSCEle2);
   Tread1->SetBranchAddress("energyRecHitSCEle1", &energyRecHitSCEle1);
   Tread1->SetBranchAddress("energyRecHitSCEle2", &energyRecHitSCEle2);
   Tread1->SetBranchAddress("rawIdRecHitSCEle1", &rawIdRecHitSCEle1);
   Tread1->SetBranchAddress("rawIdRecHitSCEle2", &rawIdRecHitSCEle2);
   Tread1->SetBranchAddress("fracRecHitSCEle1", &fracRecHitSCEle1);
   Tread1->SetBranchAddress("fracRecHitSCEle2", &fracRecHitSCEle2);
   
   int nentries1 = Tread1->GetEntries();

   EBDetId* DidEB;
*/
/*
   for(int i=0; i  < nentries1; i++){
	
	if(i%100000==0) cout << i << endl;
        Tread1->GetEntry(i);
 

        if (rawIdRecHitSCEle1->size() < 1)
		continue;      

	for(unsigned int RecSize1 = 0; RecSize1 < rawIdRecHitSCEle1->size(); RecSize1++){
		DetId Did = (*rawIdRecHitSCEle1)[RecSize1];
		shared_ptr<const CaloCellGeometry> geom = ecalEBGeom->getGeometry(Did);
		cout<<endl<<" x = "<< geom->getPosition().x() << " y = " << geom->getPosition().y() << endl; 
                }
  
 
   }
*/
}

// ------------ method called once each job just after ending the event loop  ------------
void DetID_Manipulator::endJob() {
  // please remove this method if not needed
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void DetID_Manipulator::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
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
DEFINE_FWK_MODULE(DetID_Manipulator);

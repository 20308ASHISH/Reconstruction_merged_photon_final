#ifndef Photon_RefinedRecHit_NTuplizer_h
#define Photon_RefinedRecHit_NTuplizer_h

// -*- C++ -*-
// //
// // Package:    EM_GNN_ID/EM_Skimmer/
// // Class:      Photon_RefinedRecHit_NTuplizer
// //
// /**\class Photon_RefinedRecHit_NTuplizer Photon_RefinedRecHit_NTuplizer.cc
//
// Description: Class to produce refined photon rechit Id
//
// Implementation:
// */
// //
// // Original Author:  Rajdeep Mohan Chatterjee
// //         Created:  Fri, 21 Feb 2020 11:38:58 GMT
// //
// //

// system include files
#include <memory>
#include <iostream>
#include <TTree.h>
#include <TXMLEngine.h>


// utilities
#include "Math/VectorUtil.h"
#include "TFile.h"
// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/CaloGeometry/interface/TruncatedPyramid.h"
#include "Geometry/EcalAlgo/interface/EcalPreshowerGeometry.h"
#include "Geometry/CaloTopology/interface/EcalPreshowerTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/CaloEventSetup/interface/CaloTopologyRecord.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"

#include "CondFormats/EcalObjects/interface/EcalPedestals.h"
#include "CondFormats/DataRecord/interface/EcalPedestalsRcd.h"

#include "DataFormats/EgammaCandidates/interface/Photon.h"
#include "DataFormats/PatCandidates/interface/Photon.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/PatCandidates/interface/VIDCutFlowResult.h"

#include "DataFormats/EgammaReco/interface/SuperCluster.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"

#include "RecoEcal/EgammaCoreTools/interface/EcalClusterTools.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterLazyTools.h"
#include "RecoEcal/EgammaCoreTools/interface/PositionCalc.h"

#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalDetId/interface/ESDetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHit.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"

//
//
// class declaration
//
using namespace std;
using namespace edm;
using namespace pat;
using namespace reco;

class Photon_RefinedRecHit_NTuplizer : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit Photon_RefinedRecHit_NTuplizer(const edm::ParameterSet&);
      ~Photon_RefinedRecHit_NTuplizer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

      void readROOTLUTables();
      void readXMLLUTables();
      std::vector<int> getDiffArray(std::vector<int>&, std::vector<int>&);


      // methods to produce XML files with mapping
      //void getEBMapXML(const edm::ParameterSet&, const edm::EventSetup&);
      //void getEEMapXML(const edm::ParameterSet&, const edm::EventSetup&);


      std::vector<float> Hit_ES_Eta[2];
      std::vector<float> Hit_ES_Phi[2];
      std::vector<float> Hit_ES_X[2];
      std::vector<float> Hit_ES_Y[2];
      std::vector<float> Hit_ES_Z[2];
      std::vector<float> ES_RecHitEn[2];


   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;


      bool DEBUG = false;


      //   cluster tools
      EcalClusterLazyTools *clustertools;
      noZS::EcalClusterLazyTools *clustertools_NoZS;
      edm::ESHandle<EcalPedestals> _ped;

      //   Identify if the SC lies in EB OR EE based on its seed
      bool isEB = 0;
      bool isEE = 0; // !isEB not sufficient since later will try to include the preshower as well


      //     bool GetGenMatchType(const reco::Photon& Photon, const reco::GenParticle& GenColl, int pdgId, double dRThresh);
      // Get the hits from the ES
      //     std::vector<GlobalPoint> GetESPlaneRecHits(const reco::SuperCluster& sc, unsigned int planeIndex) const;
      void GetESPlaneRecHits(const reco::SuperCluster& sc, const CaloGeometry* &geo, unsigned int phonum, unsigned int planeIndex);

      //   clear the vectors 
      void ClearTreeVectors();

      // ----------member data ---------------------------
      bool isMC_, miniAODRun_, useOuterHits_;
      edm::FileInPath ebNeighbourXtalMap_;
      edm::FileInPath eeNeighbourXtalMap_;
      
      TTree* T;
   
      // Create engine
      TXMLEngine xml;

      // Define xtal maps
      std::map<int, vector<int>> ebnxtals;
      std::map<int, vector<int>> eenxtals;

      // Variables for Run info.
      int run;
      int event;
      int lumi;

      // Electron variables
      int nPhotons_;
      Float_t rho;
      std::vector<float> iEta[2];
      std::vector<float> iPhi[2];
      std::vector<float> Hit_Eta[2];
      std::vector<float> Hit_Phi[2];
      std::vector<float> Hit_X[2];
      std::vector<float> Hit_Y[2];
      std::vector<float> Hit_Z[2];
      std::vector<float> dRHit_Eta[2];
      std::vector<float> dRHit_Phi[2];
      std::vector<float> dRHit_X[2];
      std::vector<float> dRHit_Y[2];
      std::vector<float> dRHit_Z[2];

      //std::vector<float> RawHit_Eta[1];
      //std::vector<float> RawHit_Phi[1];
      //std::vector<float> RawRecHitEn[1];

      std::vector<float> RecHitFrac[2];
      std::vector<float> RecHitEn[2];
      std::vector<float> dRRecHitFrac[2];
      std::vector<float> dRRecHitEn[2];
      std::vector<int>   RecHitGain[2];
      std::vector<bool>  RecHitQuality[2];
      std::vector<float> HitNoise[2];
//==================================================================
      std::vector<float> RawHit_Eta[2];
      std::vector<float> RawHit_Phi[2];
      std::vector<float> RawRecHitEn[2];
      std::vector<float> RawRecHitX[2];
      std::vector<float> RawRecHitY[2];
      std::vector<float> RawRecHitZ[2];
//==================================================================
      // individual flags
      std::vector<bool> RecHitFlag_kGood[2];                   // channel ok, the energy and time measurement are reliable
      std::vector<bool> RecHitFlag_kPoorReco[2];                 // the energy is available from the UncalibRecHit, but approximate (bad shape, large chi2)
      std::vector<bool> RecHitFlag_kOutOfTime[2];                // the energy is available from the UncalibRecHit (sync reco), but the event is out of time
      std::vector<bool> RecHitFlag_kFaultyHardware[2];           // The energy is available from the UncalibRecHit, channel is faulty at some hardware level (e.g. noisy)
      std::vector<bool> RecHitFlag_kNoisy[2];                    // the channel is very noisy
      std::vector<bool> RecHitFlag_kPoorCalib[2];                // the energy is available from the UncalibRecHit, but the calibration of the channel is poor
      std::vector<bool> RecHitFlag_kSaturated[2];                // saturated channel (recovery not tried)
      std::vector<bool> RecHitFlag_kLeadingEdgeRecovered[2];     // saturated channel: energy estimated from the leading edge before saturation
      std::vector<bool> RecHitFlag_kNeighboursRecovered[2];      // saturated/isolated dead: energy estimated from neighbours
      std::vector<bool> RecHitFlag_kTowerRecovered[2];           // channel in TT with no data link, info retrieved from Trigger Primitive
      std::vector<bool> RecHitFlag_kDead[2];                     // channel is dead and any recovery fails
      std::vector<bool> RecHitFlag_kKilled[2];                   // MC only flag: the channel is killed in the real detector
      std::vector<bool> RecHitFlag_kTPSaturated[2];              // the channel is in a region with saturated TP
      std::vector<bool> RecHitFlag_kL1SpikeFlag[2];              // the channel is in a region with TP with sFGVB = 0
      std::vector<bool> RecHitFlag_kWeird[2];                    // the signal is believed to originate from an anomalous deposit (spike) 
      std::vector<bool> RecHitFlag_kDiWeird[2];                  // the signal is anomalous, and neighbors another anomalous signal  
      std::vector<bool> RecHitFlag_kHasSwitchToGain6[2];         // at least one data frame is in G6
      std::vector<bool> RecHitFlag_kHasSwitchToGain1[2];         // at least one data frame is in G1

      // individual ES flags
      std::vector<bool> RecHitFlag_kESGood[2];
      std::vector<bool> RecHitFlag_kESDead[2];
      std::vector<bool> RecHitFlag_kESHot[2];
      std::vector<bool> RecHitFlag_kESPassBX[2];
      std::vector<bool> RecHitFlag_kESTwoGoodRatios[2];
      std::vector<bool> RecHitFlag_kESBadRatioFor12[2];
      std::vector<bool> RecHitFlag_kESBadRatioFor23Upper[2];
      std::vector<bool> RecHitFlag_kESBadRatioFor23Lower[2];
      std::vector<bool> RecHitFlag_kESTS1Largest[2];
      std::vector<bool> RecHitFlag_kESTS3Largest[2];
      std::vector<bool> RecHitFlag_kESTS3Negative[2];
      std::vector<bool> RecHitFlag_kESSaturated[2];
      std::vector<bool> RecHitFlag_kESTS2Saturated[2];
      std::vector<bool> RecHitFlag_kESTS3Saturated[2];
      std::vector<bool> RecHitFlag_kESTS13Sigmas[2];
      std::vector<bool> RecHitFlag_kESTS15Sigmas[2];

      std::vector<bool>* RecHitFlag_container[18] = {
         RecHitFlag_kGood,
         RecHitFlag_kPoorReco,
         RecHitFlag_kOutOfTime,
         RecHitFlag_kFaultyHardware,
         RecHitFlag_kNoisy,
         RecHitFlag_kPoorCalib,
         RecHitFlag_kSaturated,
         RecHitFlag_kLeadingEdgeRecovered,
         RecHitFlag_kNeighboursRecovered,
         RecHitFlag_kTowerRecovered,
         RecHitFlag_kDead,
         RecHitFlag_kKilled,
         RecHitFlag_kTPSaturated,
         RecHitFlag_kL1SpikeFlag,
         RecHitFlag_kWeird,
         RecHitFlag_kDiWeird,
         RecHitFlag_kHasSwitchToGain6,
         RecHitFlag_kHasSwitchToGain1
      };

      std::vector<bool>* RecHitESFlag_container[16] = {
         RecHitFlag_kESGood,
         RecHitFlag_kESDead,
         RecHitFlag_kESHot,
         RecHitFlag_kESPassBX,
         RecHitFlag_kESTwoGoodRatios,
         RecHitFlag_kESBadRatioFor12,
         RecHitFlag_kESBadRatioFor23Upper,
         RecHitFlag_kESBadRatioFor23Lower,
         RecHitFlag_kESTS1Largest,
         RecHitFlag_kESTS3Largest,
         RecHitFlag_kESTS3Negative,
         RecHitFlag_kESSaturated,
         RecHitFlag_kESTS2Saturated,
         RecHitFlag_kESTS3Saturated,
         RecHitFlag_kESTS13Sigmas,
         RecHitFlag_kESTS15Sigmas
      };


      std::vector<float> Pho_pt_;
      std::vector<float> Pho_eta_;
      std::vector<float> Pho_phi_;

      std::vector<float> Pho_cluster_seed_x;
      std::vector<float> Pho_cluster_seed_y;
      std::vector<float> Pho_cluster_seed_z;

      std::vector<float> Pho_cluster_seed_eta;
      std::vector<float> Pho_cluster_seed_phi;

      std::vector<float> Pho_energy_;
      std::vector<float> Pho_ecal_mustache_energy_;

      std::vector<float> Pho_R9;
      std::vector<float> Pho_S4;
      std::vector<float> Pho_SigIEIE;
      std::vector<float> Pho_SigIPhiIPhi;
      std::vector<float> Pho_SCEtaW;
      std::vector<float> Pho_SCPhiW;
      std::vector<float> Pho_CovIEtaIEta;
      std::vector<float> Pho_CovIEtaIPhi;
      std::vector<float> Pho_ESSigRR;
      std::vector<float> Pho_SCRawE;
      std::vector<float> Pho_SC_ESEnByRawE;
      std::vector<float> Pho_HadOverEm;

      // Photon Isolation Variables

      vector<float>  Pho_PFChIso;
      vector<float>  Pho_PFChPVIso;
      vector<float>  Pho_PFPhoIso;
      vector<float>  Pho_PFNeuIso;
      vector<float>  Pho_PFChWorstVetoIso;
      vector<float>  Pho_PFChWorstIso;
      vector<float>  Pho_EcalPFClusterIso;
      vector<float>  Pho_HcalPFClusterIso;

      vector<float> Pho_CorrectedEnergy;
      vector<float> Pho_CorrectedEnergyError;

      std::vector<float> Pho_Gen_Pt;

      std::vector<float> A_Gen_mass;
      std::vector<float> A_Gen_pt;
      std::vector<float> A_Gen_eta;
      std::vector<float> A_Gen_phi;

      std::vector<float> Pho_Gen_Eta;
      std::vector<float> Pho_Gen_Phi;
      std::vector<float> Pho_Gen_E;


      std::vector<int> passLooseId_;
      std::vector<int> passMediumId_;
      std::vector<int> passTightId_;
      std::vector<int> passMVAMediumId_;

      std::vector<int> isTrue_;

      // -----------------Handles--------------------------
      edm::Handle<double> rhoHandle;
      edm::Handle<EcalRecHitCollection> EBRechitsHandle;
      edm::Handle<EcalRecHitCollection> EERechitsHandle;
      edm::Handle<EcalRecHitCollection> ESRechitsHandle;
      edm::Handle<edm::View<reco::Photon> > photons;
      edm::Handle<edm::View<reco::GenParticle> > genParticles;
      edm::Handle<edm::ValueMap<bool> > medium_id_decisions;
      edm::Handle<edm::ValueMap<bool> > tight_id_decisions;

      //---------------- Input Tags-----------------------
      edm::EDGetTokenT<double> rhoToken_;
      edm::EDGetTokenT<EcalRecHitCollection> recHitCollectionEBToken_;
      edm::EDGetTokenT<EcalRecHitCollection> recHitCollectionEEToken_;
      edm::EDGetTokenT<EcalRecHitCollection> recHitCollectionESToken_;
      edm::EDGetToken photonsToken_;
      edm::EDGetTokenT<edm::View<reco::GenParticle> > genParticlesToken_;
      edm::EDGetTokenT<edm::ValueMap<bool> > eleMediumIdMapToken_;
      edm::EDGetTokenT<edm::ValueMap<bool> > eleTightIdMapToken_;

};

#endif 
import FWCore.ParameterSet.Config as cms

process = cms.Process("NTUPLE")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v11_L1v1', '')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/eos/user/a/asmishra/cms_project/CMSSW_10_6_29/src/DP1_folder/AToGG_GEN_E_new_all_10k_RECO.root'
    )
)

process.ntupler = cms.EDAnalyzer('Photon_RefinedRecHit_NTuplizer')
process.ntupler.rhoFastJet = cms.InputTag("fixedGridRhoAll")
process.ntupler.photons = cms.InputTag("photons")
process.ntupler.genParticles = cms.InputTag("genParticles")
process.ntupler.isMC = cms.bool(True)
process.ntupler.miniAODRun = cms.bool(False)
process.ntupler.useOuterHits = cms.bool(False)

# Add these lines if your EDAnalyzer supports global RecHit collections:
process.ntupler.ebRecHits = cms.InputTag("reducedEcalRecHitsEB")
process.ntupler.eeRecHits = cms.InputTag("reducedEcalRecHitsEE")

process.ntupler.eleMediumIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-noIso-V2-medium")
process.ntupler.eleTightIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-noIso-V2-tight")
process.ntupler.ebNeighbourXtalMap = cms.FileInPath("Analyzer/EcalMapping/plugins/getEcalMapXML.h")
process.ntupler.eeNeighbourXtalMap = cms.FileInPath("Analyzer/EcalMapping/plugins/getEcalMapXML.h")

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple_AllHits.root")
)

process.p = cms.Path(process.ntupler)
import FWCore.ParameterSet.Config as cms

process = cms.Process("NTUPLE")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:/eos/user/a/asmishra/cms_project/CMSSW_10_6_29/src/DP1_folder/AToGG_GEN_E_new_all_10k_RECO.root'
    )
)

process.ntupler = cms.EDAnalyzer('Photon_RefinedRecHit_NTuplizer',
    rhoFastJet = cms.InputTag("fixedGridRhoAll"),
    photons = cms.InputTag("photons")
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("DP1_folder/AToGG_GEN_E_new_all_10k_Ntuple.root")
)

process.p = cms.Path(process.ntupler)
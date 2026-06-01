import FWCore.ParameterSet.Config as cms

process = cms.Process("NTUPLE")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v11_L1v1', '')

process.source = cms.Source("PoolSource",
    # Pointing to the RECO file produced by your config
    fileNames = cms.untracked.vstring('file:DP1_folder/AToGG_GEN_E0.1_new_RECO.root')
)

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.ntupler = cms.EDAnalyzer("Photon_RefinedRecHit_NTuplizer",
    photons = cms.InputTag("photons"),
    rhoFastJet = cms.InputTag("fixedGridRhoFastjetAll")
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("DP1_folder/AToGG_GEN_E0.1_new_Ntuple.root")
)

process.p = cms.Path(process.ntupler)                
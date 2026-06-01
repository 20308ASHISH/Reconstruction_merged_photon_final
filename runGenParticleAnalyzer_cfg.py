import FWCore.ParameterSet.Config as cms

process = cms.Process("SHOWERANA")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v11_L1v1', '')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:Singularity> python genSim_test.py ')
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("DP1_folder/AToGG_GEN_E_new_all_10k_phase1_analysis.root")
)

process.demo = cms.EDAnalyzer('ECAL_Simhits_Analyzer',
    ecalHitsEB = cms.InputTag("g4SimHits","EcalHitsEB"),
    ecalHitsEE = cms.InputTag("g4SimHits","EcalHitsEE"),
    ecalHitsES = cms.InputTag("g4SimHits","EcalHitsES"),
    genParticles = cms.InputTag("genParticles") 
)

process.p = cms.Path(process.demo)
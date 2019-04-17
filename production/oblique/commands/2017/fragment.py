import FWCore.ParameterSet.Config as cms

#Link to datacards:
#https://github.com/jfernan2/genproductions/blob/935ee2b8f8fce279c60c0696fa9e03b7e556a91a/bin/MadGraph5_aMCatNLO/cards/production/2017/13TeV/TTZZ_5f_LO/

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.4.2/TTZZ_5f_LO/v1/TTZZ_5f_LO_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
generator = cms.EDFilter("Pythia8HadronizerFilter",
maxEventsToPrint = cms.untracked.int32(1),
pythiaPylistVerbosity = cms.untracked.int32(1),
filterEfficiency = cms.untracked.double(1.0),
pythiaHepMCVerbosity = cms.untracked.bool(False),
comEnergy = cms.double(13000.),
PythiaParameters = cms.PSet(
pythia8CommonSettingsBlock,
pythia8CP5SettingsBlock,
processParameters = cms.vstring(
        '6:m0 = 178.5',    # top mass'
        'ResonanceDecayFilter:filter = on',
        'ResonanceDecayFilter:exclusive = off', #off: require at least the specified number of daughters, on: require exactly the specified number of daughters
        'ResonanceDecayFilter:eMuAsEquivalent = off', #on: treat electrons and muons as equivalent
        'ResonanceDecayFilter:eMuTauAsEquivalent = on', #on: treat electrons, muons , and taus as equivalent
        'ResonanceDecayFilter:allNuAsEquivalent = on', #on: treat all three neutrino flavours as equivalent
        'ResonanceDecayFilter:daughters = 11,11',
        'Check:abortIfVeto = on',

),
parameterSets = cms.vstring('pythia8CommonSettings',
'pythia8CP5Settings',
'processParameters'
)
)
)
ProductionFilterSequence = cms.Sequence(generator)

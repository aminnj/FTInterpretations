import FWCore.ParameterSet.Config as cms

# link to cards:
# https://github.com/cms-sw/genproductions/tree/master/bin/MadGraph5_aMCatNLO/cards/production/13TeV/TTZZ_5f_LO

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/slc6_amd64_gcc481/13TeV/madgraph/V5_2.4.2/TTZZ_5f_LO/v2/TTZZ_5f_LO_tarball.tar.xz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *

generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        processParameters = cms.vstring(
        'TimeShower:mMaxGamma = 1.0',#cutting off lepton-pair production
        ##in the electromagnetic shower
        ##to not overlap with ttZ/gamma* samples
        'Tune:pp 14',
        'Tune:ee 7',
        'MultipartonInteractions:ecmPow=0.25208',
        'SpaceShower:alphaSvalue=0.1108',
        'PDF:pSet=LHAPDF6:NNPDF30_lo_as_0130',
        'MultipartonInteractions:pT0Ref=2.197139e+00',
        'MultipartonInteractions:expPow=1.608572e+00',
        'ColourReconnection:range=6.593269e+00',
        'ResonanceDecayFilter:filter = on',
        'ResonanceDecayFilter:exclusive = off', #off: require at least the specified number of daughters, on: require exactly the specified number of daughters
        'ResonanceDecayFilter:eMuAsEquivalent = off', #on: treat electrons and muons as equivalent
        'ResonanceDecayFilter:eMuTauAsEquivalent = on', #on: treat electrons, muons , and taus as equivalent
        'ResonanceDecayFilter:allNuAsEquivalent = on', #on: treat all three neutrino flavours as equivalent
        'ResonanceDecayFilter:daughters = 11,11',
        'Check:abortIfVeto = on',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'processParameters',
                                    )
    )
)

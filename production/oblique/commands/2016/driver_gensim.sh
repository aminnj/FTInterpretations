#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc481
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_7_1_32_patch1/src ] ; then 
 echo release CMSSW_7_1_32_patch1 already exists
else
scram p CMSSW CMSSW_7_1_32_patch1
fi
cd CMSSW_7_1_32_patch1/src
eval `scram runtime -sh`
# curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/SUS-RunIISummer15wmLHEGS-00256 --retry 2 --create-dirs -o Configuration/GenProduction/python/SUS-RunIISummer15wmLHEGS-00256-fragment.py 
# [ -s Configuration/GenProduction/python/SUS-RunIISummer15wmLHEGS-00256-fragment.py ] || exit $?;
cp ../../fragment.py Configuration/GenProduction/python/SUS-RunIISummer15wmLHEGS-00256-fragment.py
scram b
cd ../../
seed=$(date +%s)
cmsDriver.py Configuration/GenProduction/python/SUS-RunIISummer15wmLHEGS-00256-fragment.py --filein file:events.lhe --fileout file:output_gensim.root --mc --eventcontent RAWSIM,LHE --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --conditions MCRUN2_71_V1::All --beamspot Realistic50ns13TeVCollision --step LHE,GEN,SIM --magField 38T_PostLS1 --python_filename pset_gensim.py --no_exec --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed}%100)" -n 20 || exit $? ; 

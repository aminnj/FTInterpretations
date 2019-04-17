#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_3/src ] ; then 
 echo release CMSSW_10_2_3 already exists
else
scram p CMSSW CMSSW_10_2_3
fi
cd CMSSW_10_2_3/src
eval `scram runtime -sh`
# curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/TOP-RunIIFall18wmLHEGS-00125 --retry 2 --create-dirs -o Configuration/GenProduction/python/TOP-RunIIFall18wmLHEGS-00125-fragment.py 
# [ -s Configuration/GenProduction/python/TOP-RunIIFall18wmLHEGS-00125-fragment.py ] || exit $?;
cp ../../fragment.py Configuration/GenProduction/python/TOP-RunIIFall18wmLHEGS-00125-fragment.py
scram b
cd ../../
seed=$(date +%s)
cmsDriver.py Configuration/GenProduction/python/TOP-RunIIFall18wmLHEGS-00125-fragment.py --filein file:events.lhe --fileout file:output_gensim.root --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 102X_upgrade2018_realistic_v11 --beamspot Realistic25ns13TeVEarly2018Collision --step LHE,GEN,SIM --nThreads 1 --geometry DB:Extended --era Run2_2018 --python_filename pset_gensim.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed}%100)" -n 20 || exit $? ; 

#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_4/src ] ; then 
 echo release CMSSW_9_3_4 already exists
else
scram p CMSSW CMSSW_9_3_4
fi
cd CMSSW_9_3_4/src
eval `scram runtime -sh`
# curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/TOP-RunIIFall17wmLHEGS-00069 --retry 2 --create-dirs -o Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00069-fragment.py 
# [ -s Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00069-fragment.py ] || exit $?;
cp ../../fragment.py Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00069-fragment.py
scram b
cd ../../
seed=$(date +%s)
cmsDriver.py Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00069-fragment.py --filein file:events.lhe --fileout file:output_gensim.root --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE,GEN,SIM --nThreads 1 --geometry DB:Extended --era Run2_2017 --python_filename pset_gensim.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed}%100)" -n 20 || exit $? ; 

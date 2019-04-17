#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_5/src ] ; then 
 echo release CMSSW_10_2_5 already exists
else
scram p CMSSW CMSSW_10_2_5
fi
cd CMSSW_10_2_5/src
eval `scram runtime -sh`
scram b
cd ../../
cmsDriver.py step1 --filein file:output_aod.root --fileout file:output_miniaod.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 102X_upgrade2018_realistic_v15 --step PAT --nThreads 1 --geometry DB:Extended --era Run2_2018 --python_filename pset_miniaod.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 
# 2018

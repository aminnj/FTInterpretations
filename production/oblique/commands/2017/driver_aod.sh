#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_0_patch1/src ] ; then 
 echo release CMSSW_9_4_0_patch1 already exists
else
scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`
scram b
cd ../../
cmsDriver.py step2 --filein file:output_raw.root --fileout file:output_aod.root --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 1 --era Run2_2017 --python_filename pset_aod.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 


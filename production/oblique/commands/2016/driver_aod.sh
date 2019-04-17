#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc530
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_8_0_31/src ] ; then 
 echo release CMSSW_8_0_31 already exists
else
scram p CMSSW CMSSW_8_0_31
fi
cd CMSSW_8_0_31/src
eval `scram runtime -sh`
scram b
cd ../../
cmsDriver.py step2 --filein file:output_raw.root --fileout file:output_aod.root --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --step RAW2DIGI,RECO,EI --nThreads 1 --era Run2_2016 --python_filename pset_aod.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 

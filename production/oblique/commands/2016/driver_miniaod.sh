#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_9/src ] ; then 
 echo release CMSSW_9_4_9 already exists
else
scram p CMSSW CMSSW_9_4_9
fi
cd CMSSW_9_4_9/src
eval `scram runtime -sh`
scram b
cd ../../
cmsDriver.py step1 --filein file:output_aod.root --fileout file:output_miniaod.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 94X_mcRun2_asymptotic_v3 --step PAT --nThreads 1 --era Run2_2016,run2_miniAOD_80XLegacy --python_filename pset_miniaod.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 

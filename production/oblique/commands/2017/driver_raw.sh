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
cmsDriver.py step1 --filein file:output_gensim.root --fileout file:output_raw.root  --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 1 --datamix PreMix --era Run2_2017 --python_filename pset_raw.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 

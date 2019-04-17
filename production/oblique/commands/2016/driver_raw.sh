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
cmsDriver.py step1 --filein file:output_gensim.root --fileout file:output_raw.root  --pileup_input "dbs:/Neutrino_E-10_gun/RunIISpring15PrePremix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v2-v2/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:@frozen2016 --nThreads 1 --datamix PreMix --era Run2_2016 --python_filename pset_raw.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 20 || exit $? ; 

## CMSSW production

### Oblique higgs parameter

Collect GENSIM to MINIAODSIM PrepIDs and drivers from MCM for a LO
sample with no extra partons, for 2016,2017,2018:
```
/TTZZ_TuneCUETP8M2T4_13TeV-madgraph-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v1/MINIAODSIM
/TTZZ_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM
/TTZZ_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v2/MINIAODSIM
```
Modified driver commands and PSets are in `oblique/commands/`, split for the three years.
Input is an LHE file, not a gridpack, and the PU mixing list was trimmed to a few thousand files instead of 300000 files(!).

Assuming ProjectMetis is available in the environment, use `oblique/submission/makemc.py` to submit condor jobs.


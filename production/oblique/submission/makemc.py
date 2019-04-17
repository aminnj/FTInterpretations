from metis.CMSSWTask import CMSSWTask
from metis.Sample import DirectorySample
from metis.StatsParser import StatsParser
import time
import itertools

d_cmssw_version = {
        2016: { "gensim": "CMSSW_7_1_32_patch1", "raw": "CMSSW_8_0_31", "aod": "CMSSW_8_0_31", "miniaod": "CMSSW_9_4_9", },
        2017: { "gensim": "CMSSW_9_3_4", "raw": "CMSSW_9_4_0_patch1", "aod": "CMSSW_9_4_0_patch1", "miniaod": "CMSSW_9_4_7", },
        2018: { "gensim": "CMSSW_10_2_3", "raw": "CMSSW_10_2_5", "aod": "CMSSW_10_2_5", "miniaod": "CMSSW_10_2_5", },
        }

d_scram_arch = {
        2016: { "aod": "slc6_amd64_gcc530", "gensim": "slc6_amd64_gcc481", "miniaod": "slc6_amd64_gcc630", "raw": "slc6_amd64_gcc530", },
        2017: { "aod": "slc6_amd64_gcc630", "gensim": "slc6_amd64_gcc630", "miniaod": "slc6_amd64_gcc630", "raw": "slc6_amd64_gcc630", },
        2018: { "aod": "slc6_amd64_gcc700", "gensim": "slc6_amd64_gcc700", "miniaod": "slc6_amd64_gcc700", "raw": "slc6_amd64_gcc700", },
        }

d_pset_args = { 2016: "data=False year=2016", 2017: "data=False year=2017 metrecipe=True", 2018: "data=False year=2018", }
d_global_tag = { 2016: "94X_mcRun2_asymptotic_v3", 2017: "94X_mc2017_realistic_v17", 2018: "102X_upgrade2018_realistic_v12", }
d_special_dir = { 2016: "run2_mc2016_94x/", 2017: "run2_mc2017/", 2018: "run2_mc2018/", }


total_summary = {}
tag = "v2"

for _ in range(100):
    for year,hhat in itertools.product([
        2016,
        2017,
        2018,
        ],
        [
            0.0,
            0.04,
            0.08,
            0.12,
            0.16,
            ]):
        shortstr = str(hhat).replace(".","p")
        lhe = CMSSWTask(
                sample = DirectorySample(
                    location="/hadoop/cms/store/user/namin/oblique_lhe/year_{}/Events/".format(year),
                    globber="oblique_{}_50kevents.lhe".format(shortstr),
                    dataset="/tttt-LOoblique/year_{}_{}/LHE".format(year,shortstr),
                    ),
                events_per_output = 100,
                total_nevents = 50000,
                # events_per_output = 5,
                # total_nevents = 10,
                condor_submit_params = {"sites":"T2_US_UCSD"},
                pset = "../commands/{}/pset_gensim.py".format(year),
                cmssw_version = d_cmssw_version[year]["gensim"],
                scram_arch = d_scram_arch[year]["gensim"],
                split_within_files = True,
                report_every = 1,
                tag = tag,
                )

        raw = CMSSWTask(
                sample = DirectorySample(
                    location = lhe.get_outputdir(),
                    dataset = lhe.get_sample().get_datasetname().replace("LHE","RAW"),
                    ),
                open_dataset = True,
                files_per_output = 1,
                condor_submit_params = {"use_xrootd":True},
                pset = "../commands/{}/pset_raw.py".format(year),
                cmssw_version = d_cmssw_version[year]["raw"],
                scram_arch = d_scram_arch[year]["raw"],
                report_every = 1,
                tag = tag,
                )

        aod = CMSSWTask(
                sample = DirectorySample(
                    location = raw.get_outputdir(),
                    dataset = raw.get_sample().get_datasetname().replace("RAW","AOD"),
                    ),
                open_dataset = True,
                flush = True,
                files_per_output = 3,
                condor_submit_params = {"use_xrootd":True},
                pset = "../commands/{}/pset_aod.py".format(year),
                cmssw_version = d_cmssw_version[year]["aod"],
                scram_arch = d_scram_arch[year]["aod"],
                report_every = 10,
                tag = tag,
                )

        miniaod = CMSSWTask(
                sample = DirectorySample(
                    location = aod.get_outputdir(),
                    dataset = aod.get_sample().get_datasetname().replace("AOD","MINIAOD"),
                    ),
                open_dataset = True,
                flush = True,
                files_per_output = 4,
                condor_submit_params = {"use_xrootd":True},
                pset = "../commands/{}/pset_miniaod.py".format(year),
                cmssw_version = d_cmssw_version[year]["miniaod"],
                scram_arch = d_scram_arch[year]["miniaod"],
                report_every = 100,
                tag = tag,
                )

        cms4 = CMSSWTask(
                sample = DirectorySample(
                    location = miniaod.get_outputdir(),
                    dataset = miniaod.get_sample().get_datasetname(),
                    ),
                open_dataset = True,
                flush = True,
                # publish_to_dis = True,
                snt_dir = True,
                files_per_output = 5,
                output_name = "merged_ntuple.root",
                tag = "CMS4_V10-02-05",
                pset = "/home/users/namin/2017/ProjectMetis/pset_CMS4_V10-02-04.py",
                pset_args = d_pset_args[year],
                global_tag = d_global_tag[year],
                condor_submit_params = {"sites":"T2_US_UCSD"},
                cmssw_version = "CMSSW_10_2_5",
                scram_arch = "slc6_amd64_gcc700",
                tarfile = "/nfs-7/userdata/libCMS3/lib_CMS4_V10-02-05_1025.tar.xz",
                special_dir = d_special_dir[year],
                )

        tasks = [lhe,raw,aod,miniaod,cms4]
        for task in tasks:
            task.process()
            summary = task.get_task_summary()
            total_summary[task.get_sample().get_datasetname()] = summary

    StatsParser(data=total_summary, webdir="~/public_html/dump/metis_obliquescan/").do()
    time.sleep(2.0*3600)

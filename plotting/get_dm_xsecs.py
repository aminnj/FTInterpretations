from tqdm import tqdm
import json
import os
import numpy as np
import itertools
import re
import sys
sys.path.insert(0,'/home/users/{}/.local/lib/python2.7/site-packages/'.format(os.getenv("USER")))
from matplottery.plotter import plot_stack
from matplottery.utils import Hist1D, MET_LATEX, binomial_obs_z, register_root_palettes
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator
from scipy import interpolate

import utils

# grep "Integrated weight" runs/out_dm*v4/*/Events/run_01/run_01_tag_1_banner.txt > data_dm_v4.txt
def get_df():
    df = utils.load_data("data/data_dmhiggs_v1.txt")
    df = df[df.tag.str.contains("dmscalar") | df.tag.str.contains("dmpseudo")]
    df["which"] = df.tag.str.split("_").str[0]
    df["proc"] = df.tag.str.split("_").str[1]
    df["massmed"] = df.tag.str.split("_").str[2].astype(int)
    df["massdm"] = df.tag.str.split("_").str[3].astype(int)
    df = df.drop(["tag","folder"],axis=1)
    # separate 6 processes
    ttsm = df[df.proc=="ttsm"].rename(index=str,columns={"xsec":"xsec_ttsm"}).drop(["proc"],axis=1)
    stwsm = df[df.proc=="stwsm"].rename(index=str,columns={"xsec":"xsec_stwsm"}).drop(["proc"],axis=1)
    sttsm = df[df.proc=="sttsm"].rename(index=str,columns={"xsec":"xsec_sttsm"}).drop(["proc"],axis=1)
    # make dataframe where each row contains all 6 processes, and sum up xsecs
    dfc = ttsm
    for x in [stwsm,sttsm]:
        dfc = dfc.merge(x,suffixes=["",""],on=["which","massmed","massdm"],how="outer")
    dfc["xsec_totsm"] = dfc["xsec_ttsm"] + dfc["xsec_stwsm"] + dfc["xsec_sttsm"]
    return dfc

print get_df()
get_df().to_json("dump_dmhiggs.json")


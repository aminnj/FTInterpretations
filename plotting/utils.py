import json
import os
import numpy as np
import itertools
import re
import sys
from tqdm import tqdm
sys.path.insert(0,'/home/users/{}/.local/lib/python2.7/site-packages/'.format(os.getenv("USER")))
from matplottery.plotter import plot_stack
from matplottery.utils import Hist1D, MET_LATEX, binomial_obs_z, register_root_palettes
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from scipy import interpolate

pd.set_option('display.max_rows', 130)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 300)

def set_style_defaults():
    from matplotlib import rcParams
    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = ["Helvetica", "Arial", "Bitstream Vera Sans", "DejaVu Sans", "Liberation Sans"]
    rcParams['legend.fontsize'] = 13
    rcParams['legend.labelspacing'] = 0.2
    rcParams['axes.xmargin'] = 0.0 # rootlike, no extra padding within x axis
    rcParams['axes.labelsize'] = 'x-large'
    rcParams['axes.formatter.use_mathtext'] = True
    rcParams['legend.framealpha'] = 0.65
    rcParams['axes.labelsize'] = 'x-large'
    rcParams['axes.titlesize'] = 'x-large'
    rcParams['xtick.labelsize'] = 'x-large'
    rcParams['ytick.labelsize'] = 'x-large'
    rcParams['figure.subplot.hspace'] = 0.1
    rcParams['figure.subplot.wspace'] = 0.1
    rcParams['figure.subplot.right'] = 0.96
    rcParams['figure.max_open_warning'] = 0
    rcParams['figure.dpi'] = 125
    rcParams["axes.formatter.limits"] = [-5,4] # scientific notation if log(y) outside this
    # print rcParams
    # rcParams["pdf.fonttype"] = 42
    # rcParams["pdf.use14corefonts"] = True # this one uses helvetica for pdf saving
    # pdf.fonttype       : 3         ## Output Type 3 (Type3) or Type 42 (TrueType)
    # pdf.use14corefonts : False

def load_data(fname="data/data.txt"):
    data = []
    with open(fname,"r") as fh:
        for line in fh:
            parts = line.strip().split(":")
            if not parts: continue
            if "hadoop" in parts[0]:
                folder = ""
                proctag = parts[0].rsplit("/",1)[-1].rsplit(".",1)[0]
                xsec = float(parts[-1].strip())
            else:
                folder = parts[0].split("/Events",1)[0].rsplit("/",2)[-2]
                proctag = parts[0].split("/Events",1)[0].rsplit("/",1)[-1]
                xsec = float(parts[-1].strip())
            data.append(dict(folder=folder,tag=proctag,xsec=xsec))
    df = pd.DataFrame(data)
    return df

def add_cms_info(ax, typ="", lumi="137", xtype=0.12):
    ax.text(0.0, 1.01,"CMS", horizontalalignment='left', verticalalignment='bottom', transform = ax.transAxes, weight="bold", size="x-large")
    ax.text(xtype, 1.01,typ, horizontalalignment='left', verticalalignment='bottom', transform = ax.transAxes, style="italic", size="x-large")
    ax.text(0.99, 1.01,"%s fb${}^\mathregular{-1}$ (13 TeV)" % (lumi), horizontalalignment='right', verticalalignment='bottom', transform = ax.transAxes, size="x-large")

def get_fig_ax(wide=False):
    if wide:
        fig, ax = plt.subplots(gridspec_kw={"top":0.92,"bottom":0.14,"left":0.15,"right":0.95},figsize=(6.5,5.5))
    else:
        fig, ax = plt.subplots(gridspec_kw={"top":0.92,"bottom":0.14,"left":0.15,"right":0.95},figsize=(5.5,5.5))
    return fig, ax


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
from matplotlib.ticker import MultipleLocator

import utils
utils.set_style_defaults()

import ROOT as r
r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)
f = r.TFile("mh125_align_13.root")
m_H = f.Get("m_H")
br_A_tt = f.Get("br_A_tt")
br_H_tt = f.Get("br_H_tt")
# if True:
#     # m_H is a 2D histogram with x=mA, y=tanbeta, z=mH
#     # we want to make m_A which is a 2D histogram with x=mH, y=tanbeta, z=mA
#     xaxis = m_H.GetXaxis()
#     yaxis = m_H.GetYaxis()
#     m_A = r.TH2F("m_A","m_A",85,150,1000,38,0.99,20.1)
#     for ix in tqdm(range(1,m_H.GetNbinsX()+1)):
#         for iy in range(1,m_H.GetNbinsY()+1):
#             z = m_H.GetBinContent(ix,iy)
#             x = xaxis.GetBinCenter(ix)
#             y = yaxis.GetBinCenter(iy)
#             m_A.SetBinContent(m_A.FindBin(z,y),x)
def get_br(proc,mass,tanbeta=1.,convert_mh=False):
    if tanbeta < 1.: return 1.0
    if "a" in proc:
        return br_A_tt.GetBinContent(br_A_tt.FindBin(mass,tanbeta))
    elif "h" in proc:
        if convert_mh:
            # BR histograms have m_A on xaxis, so we have to convert mH to mA value first
            mass = m_A.GetBinContent(m_A.FindBin(mass,tanbeta))
        return br_H_tt.GetBinContent(br_H_tt.FindBin(mass,tanbeta))
    else:
        raise Exception("WTF are you doing?")


def get_df(already_decayed=False,apply_br=True):

    if already_decayed:
        df = utils.load_data("../data_Apr18.txt")
        df = df[df.folder.str.contains("2hdm_decay_scan_v2")]
        df  = df.drop(["folder"],axis=1)
        # print df.folder
        # sys.exit()
    else:
        df = utils.load_data()
        df = df[df.folder.str.contains("2hdm_scan")]
        df  = df.drop(["folder"],axis=1)

    df["proc"] = df.tag.str.split("_").str[1]
    df["mass"] = df.tag.str.split("_").str[2].astype(int)
    df["tanbeta"] = df.tag.str.split("_").str[3].str.replace("p",".").astype(float)
    df = df.drop(["tag"],axis=1)

    brs = []
    for i,(proc,mass,tanbeta) in df[["proc","mass","tanbeta"]].iterrows():
        if apply_br:
            br = get_br(proc,mass,tanbeta)
        else:
            br = 1.
        # print proc,mass,tanbeta,br
        brs.append(br)
    brs = np.array(brs)
    df["br"] = brs
    df["xsec"] *= df["br"]
    # sys.exit()

    # separate 6 processes
    tta = df[df.proc=="tta"].rename(index=str,columns={"xsec":"xsec_tta","br":"br_a"}).drop(["proc"],axis=1)
    taw = df[df.proc=="taw"].rename(index=str,columns={"xsec":"xsec_taw","br":"br_a"}).drop(["proc","br_a"],axis=1)
    taq = df[df.proc=="taq"].rename(index=str,columns={"xsec":"xsec_taq","br":"br_a"}).drop(["proc","br_a"],axis=1)
    tth = df[df.proc=="tth"].rename(index=str,columns={"xsec":"xsec_tth","br":"br_h"}).drop(["proc"],axis=1)
    thw = df[df.proc=="thw"].rename(index=str,columns={"xsec":"xsec_thw","br":"br_h"}).drop(["proc","br_h"],axis=1)
    thq = df[df.proc=="thq"].rename(index=str,columns={"xsec":"xsec_thq","br":"br_h"}).drop(["proc","br_h"],axis=1)

    # print df.query("mass==550 and tanbeta==1")

    # make dataframe where each row contains all 6 processes, and sum up xsecs
    dfc = tta
    for x in [taw,taq,tth,thw,thq]:
        dfc = dfc.merge(x,suffixes=["",""],on=["tanbeta","mass"],how="inner")
    dfc["xsec_a"] = (dfc["xsec_taw"]+dfc["xsec_taq"]+dfc["xsec_tta"])
    dfc["xsec_h"] = (dfc["xsec_thw"]+dfc["xsec_thq"]+dfc["xsec_tth"])
    dfc["xsec_b"] = (dfc["xsec_a"]+dfc["xsec_h"])

    dfc["stfrac_h"] = (dfc["xsec_thw"]+dfc["xsec_thq"])/dfc["xsec_h"]
    dfc["stfrac_a"] = (dfc["xsec_taw"]+dfc["xsec_taq"])/dfc["xsec_a"]

    return dfc

dfc = get_df()
# dfc_dec = get_df(already_decayed=True,apply_br=False)

# dfc["brmgratio_h"] = dfc_dec["xsec_h"]/dfc["xsec_h"]
# dfc["brmgratio_a"] = dfc_dec["xsec_a"]/dfc["xsec_a"]
# print dfc

print "Dumped json!"
dfc.to_json("xsecs_2hdm.json")

for key in [
        # "brmgratio_h",
        # "brmgratio_a",
        "xsec_h",
        "xsec_a",
        # "stfrac_h",
        # "stfrac_a",
        ]:
    fig,ax = plt.subplots()
    # key = "xsec_h"
    # ax.scatter(dfc["mass"],dfc["tanbeta"],c=dfc[key],norm=mpl.colors.LogNorm(vmin=dfc[key].min(), vmax=dfc[key].max()),
    # ax.scatter(dfc["mass"],dfc["tanbeta"],c=dfc[key],norm=mpl.colors.LogNorm(vmin=1.5*1e-3,vmax=500*1e-3),
    ax.scatter(dfc["mass"],dfc["tanbeta"],c=dfc[key],
            norm=mpl.colors.LogNorm(vmin=1.5*1e-3,vmax=500*1e-3),
                       cmap='cividis')
                       # cmap='PuBu')
                       # cmap='copper')
                       # cmap='kRainbow')

    if "frac" in key:
        for i,(m,tb,val) in dfc[["mass","tanbeta",key]].iterrows():
            s = "{:.2f}".format(val)
            ax.text(m,tb+0.04,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
            # print m,tb,xsec
        # plt.colorbar()
    elif "ratio" in key:
        for i,(m,tb,val) in dfc[["mass","tanbeta",key]].iterrows():
            s = "{:.3f}".format(val)
            ax.text(m,tb+0.04,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
            # print m,tb,xsec
        # plt.colorbar()
    else:
        for i,(m,tb,xsec) in dfc[["mass","tanbeta",key]].iterrows():
            xsec = xsec*1e3
            if xsec >= 100.:
                s = "{:.0f}".format(xsec)
            elif xsec >= 10.:
                s = "{:.1f}".format(xsec)
            elif xsec >= 1.:
                s = "{:.2f}".format(xsec)
            else:
                s = "{:.3f}".format(xsec)
            ax.text(m,tb+0.04,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
            # print m,tb,xsec
        # plt.colorbar()

    if "_h" in key:
        title = r"$\sigma$(pp$\rightarrow$ (t$\bar{\mathrm{t}}$,tW,tq)+H) $\times$ BR(H$\rightarrow$ t$\bar{\mathrm{t}}$) (fb)"
    else:
        title = r"$\sigma$(pp$\rightarrow$ (t$\bar{\mathrm{t}}$,tW,tq)+A) $\times$ BR(A$\rightarrow$ t$\bar{\mathrm{t}}$) (fb)"
    text = ax.set_title(title)
    ax.set_xlim([340.,660.])
    ax.set_ylabel(r"$\tan\beta$")
    ax.set_xlabel("mass (GeV)")

    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.xaxis.set_minor_locator(MultipleLocator(10.))


    fig.set_tight_layout(True)
    fname = "plots/plot_2d_2hdm_{}.png".format(key)
    fig.savefig(fname)
    fig.savefig(fname.replace(".png",".pdf"))
    os.system("ic "+fname)
    # for _ in range(10):
    #     print "Actually include BR(tt)!!!"

fig,ax = plt.subplots()
key = "xsec_h"
ax.plot(dfc[dfc.tanbeta==1.4]["mass"],1e3*dfc[dfc.tanbeta==1.4][key],label=r"$\tan\beta=1.4$ (H)",marker="o",linestyle="-",color="C0",markersize=5.0)
ax.plot(dfc[dfc.tanbeta==1.0]["mass"],1e3*dfc[dfc.tanbeta==1.0][key],label=r"$\tan\beta=1.0$ (H)",marker="o",linestyle="-",color="C3",markersize=5.0)
ax.plot(dfc[dfc.tanbeta==0.8]["mass"],1e3*dfc[dfc.tanbeta==0.8][key],label=r"$\tan\beta=0.8$ (H)",marker="o",linestyle="-",color="C2",markersize=5.0)
# ax.plot(dfc[dfc.tanbeta==0.5]["mass"],1e3*dfc[dfc.tanbeta==0.5][key],label=r"$\tan\beta=0.5$ (H)",marker="o",linestyle="-",color="C3",markersize=5.0)

key = "xsec_a"
ax.plot(dfc[dfc.tanbeta==1.4]["mass"],1e3*dfc[dfc.tanbeta==1.4][key],label=r"$\tan\beta=1.4$ (A)",marker="v",linestyle="--",color="C0",markersize=5.0)
ax.plot(dfc[dfc.tanbeta==1.0]["mass"],1e3*dfc[dfc.tanbeta==1.0][key],label=r"$\tan\beta=1.0$ (A)",marker="v",linestyle="--",color="C3",markersize=5.0)
ax.plot(dfc[dfc.tanbeta==0.8]["mass"],1e3*dfc[dfc.tanbeta==0.8][key],label=r"$\tan\beta=0.8$ (A)",marker="v",linestyle="--",color="C2",markersize=5.0)
# ax.plot(dfc[dfc.tanbeta==0.5]["mass"],1e3*dfc[dfc.tanbeta==0.5][key],label=r"$\tan\beta=0.5$ (A)",marker="v",linestyle="--",color="C3",markersize=5.0)
ax.legend(ncol=2,fontsize=10.)
ax.set_ylim([5.,150.])
ax.set_yscale("log")
title = r"$\sigma$(pp$\rightarrow$ (t$\bar{\mathrm{t}}$,tW,tq)+X) $\times$ BR(X$\rightarrow$ t$\bar{\mathrm{t}}$) (fb)"
text = ax.set_title(title)
ax.set_xlim([340.,660.])
ax.set_ylabel(r"$\sigma\times$BR (fb)")
ax.set_xlabel("mass (GeV)")

# ax.yaxis.set_minor_locator(MultipleLocator(0.1))
ax.xaxis.set_minor_locator(MultipleLocator(10.))
# ax.set_xlim([340.,660.])
# ax.set_ylabel(r"$\tan\beta$")
# ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# ax.xaxis.set_minor_locator(MultipleLocator(10.))

# fig.set_tight_layout(True)
# fig.savefig("plots/test.png")
# os.system("ic plots/test.png")

fig.set_tight_layout(True)
fname = "plots/plot_1d_2hdm_xsec.png".format(key)
fig.savefig(fname)
fig.savefig(fname.replace(".png",".pdf"))
os.system("ic "+fname)



# fig,ax = plt.subplots()
# tb = 2.0
# key = "br_h"
# ax.plot(dfc[dfc.tanbeta==tb]["mass"],dfc[dfc.tanbeta==tb][key],label=r"$\tan\beta=1.0$ (H)",marker="o",linestyle="-",color="C3",markersize=5.0)
# key = "br_a"
# ax.plot(dfc[dfc.tanbeta==tb]["mass"],dfc[dfc.tanbeta==tb][key],label=r"$\tan\beta=1.0$ (A)",marker="v",linestyle="--",color="C3",markersize=5.0)
# ax.legend(ncol=2,fontsize=10.)
# ax.set_ylim([0.,1.])
# # ax.set_yscale("log")
# title = r"BR(X$\rightarrow$ t$\bar{\mathrm{t}}$)"
# text = ax.set_title(title)
# ax.set_xlim([340.,660.])
# ax.set_ylabel(r"BR")
# ax.set_xlabel("mass (GeV)")
# # ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# ax.xaxis.set_minor_locator(MultipleLocator(10.))
# # ax.set_xlim([340.,660.])
# # ax.set_ylabel(r"$\tan\beta$")
# # ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# # ax.xaxis.set_minor_locator(MultipleLocator(10.))
# fig.set_tight_layout(True)
# fig.savefig("plots/test.png")
# os.system("ic plots/test.png")

# fig,ax = plt.subplots()
# # mass = 550
# from itertools import cycle
# colors = cycle(["C0","C1","C2","C3","C4"])
# for mass in [450,470,490,510,530]:
#     color = next(colors)
#     key = "br_h"
#     ax.plot(dfc[dfc.mass==mass]["tanbeta"],dfc[dfc.mass==mass][key],label=r"mass = {} (H)".format(mass),marker="o",linestyle="-",color=color,markersize=5.0)
#     key = "br_a"
#     ax.plot(dfc[dfc.mass==mass]["tanbeta"],dfc[dfc.mass==mass][key],label=r"mass = {} (A)".format(mass),marker="v",linestyle="--",color=color,markersize=5.0)
# ax.legend(ncol=2,fontsize=10.)
# # ax.set_ylim([0.,1.])
# # ax.set_yscale("log")
# title = r"BR(X$\rightarrow$ t$\bar{\mathrm{t}}$)"
# text = ax.set_title(title)
# # ax.set_xlim([340.,660.])
# ax.set_ylabel(r"BR")
# ax.set_xlabel(r"tan$\beta$")
# # ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# ax.xaxis.set_minor_locator(MultipleLocator(10.))
# # ax.set_xlim([340.,660.])
# # ax.set_ylabel(r"$\tan\beta$")
# # ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# # ax.xaxis.set_minor_locator(MultipleLocator(10.))
# fig.set_tight_layout(True)
# fig.savefig("plots/test.png")
# os.system("ic plots/test.png")

from tqdm import tqdm
import commands
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
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from scipy import interpolate

import utils
utils.set_style_defaults()

XSEC_TTTT = 11.97
def parse_yukawa_log(fname):
    d = {}
    tthscale = None
    for line in open(fname,"r").readlines():
        line = line.strip()
        if line.startswith("Set Default Value of"):
            tthscale = float(line.split()[-1])
            if tthscale not in d:
                d[tthscale] = {}
        if line.startswith("Observed Limit:"):
            limit = float(line.split("<")[-1].strip())
            d[tthscale]["limit"] = XSEC_TTTT*limit
        if line.startswith("Best fit r:"):
            parts = line.split(":")[-1].strip()
            central = float(parts.split()[0])
            down,up = map(float,parts.split()[1].split("/"))
            d[tthscale]["central"] = XSEC_TTTT*central
            d[tthscale]["up"] = XSEC_TTTT*up
            d[tthscale]["down"] = XSEC_TTTT*down
    keys = sorted(d.keys())
    ktvals = map(lambda x: x**.5, keys)
    ul = map(lambda x: d[x].get("limit",-1), keys)
    central = map(lambda x: d[x].get("central",-1), keys)
    ups = map(lambda x: d[x].get("up",-1), keys)
    downs = map(lambda x: d[x].get("down",-1), keys)
    return ktvals, ul, central, ups, downs


def get_df(s):
    # cmd = """grep -E "(# hhat|Integrated weight)" ../runs/out_oblique_scan_v1/out_test_hhatscan_part*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{print $3" "$11}'"""
    cmd = """grep -E "(# hhat|Integrated weight)" ../runs/out_oblique_scan_v1/{s}*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{{print $3" "$11}}'""".format(s=s)
    # for _ in range(10):
    #     print "FIXME" * 10 # delete next line and revert back to non ythhatscan
    # cmd = """grep -E "(# hhat|Integrated weight)" ../runs/out_oblique_scan_v1/out_test_ythhatscan_part*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{print $3" "$11}'"""
    data = map(lambda x:map(float,x.strip().split()),commands.getoutput(cmd).splitlines())
    df = pd.DataFrame(data,columns=["hhat","xsec"])
    df = df.sort_values(by=["hhat"])
    df["xsec"] *= 1e3
    return df

def get_df_tth(s):
    # cmd = """grep -E "(# hhat|Integrated weight)" ../runs/out_oblique_scan_v1/out_test_hhatscan_part*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{print $3" "$11}'"""
    cmd = """grep -E "(# hhat|Integrated weight)" ../runs/{s}/*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{{print $3" "$11}}'""".format(s=s)
    # for _ in range(10):
    #     print "FIXME" * 10 # delete next line and revert back to non ythhatscan
    # cmd = """grep -E "(# hhat|Integrated weight)" ../runs/out_oblique_scan_v1/out_test_ythhatscan_part*/Events/run_*/*_tag_1_banner.txt | xargs -L 2 echo | awk '{print $3" "$11}'"""
    data = map(lambda x:map(float,x.strip().split()),commands.getoutput(cmd).splitlines())
    df = pd.DataFrame(data,columns=["hhat","xsec"])
    df = df.sort_values(by=["hhat"])
    df["xsec"] *= 1e3
    return df

def get_df_custom():
    # from /home/users/namin/2018/fourtop/all/FTAnalysis/analysis/limits/test_ft_updated2018_run2_19Mar5/run_oblique_scan.sh
    lines = """
v3.28_ft_test_Apr20_oblique_v1///card_hhat0p04_srdisc_run2.log:Observed Limit: r < 1.6506
v3.28_ft_test_Apr20_oblique_v1///card_hhat0p08_srdisc_run2.log:Observed Limit: r < 1.3035
v3.28_ft_test_Apr20_oblique_v1///card_hhat0p0_srdisc_run2.log:Observed Limit: r < 1.8804
v3.28_ft_test_Apr20_oblique_v1///card_hhat0p12_srdisc_run2.log:Observed Limit: r < 1.0232
v3.28_ft_test_Apr20_oblique_v1///card_hhat0p16_srdisc_run2.log:Observed Limit: r < 0.8013
    """.strip().splitlines()
    def parse(line):
        hhat = float(line.split(":",1)[0].split("hhat",1)[1].split("_",1)[0].replace("p","."))
        rval = float(line.split()[-1])
        return hhat,rval
    data = map(parse,lines)
    df = pd.DataFrame(data,columns=["hhat","obsr"])
    df = df.sort_values(by=["hhat"])
    return df


def plot_main():
    df14 = get_df("out_test_fixhhatscan_part")
    df13 = get_df("out_test_13tevhhatscan_part")

    # df14 = df14[df14.hhat < 0.17]
    # df13 = df13[df13.hhat < 0.17]

    


    fig,ax = plt.subplots()

    # ax.plot
    def get_th_ratio(hhat):
        # dsig is (sigmahhat-sigmasm)/sigmasm = sigmahhat/sigmasm - 1
        # so ratio (wrt sm) is dsig + 1
        return 1+0.03*(hhat/0.04)+0.15*(hhat/0.04)**2

    hhats = np.linspace(0.,0.20,100)
    th_ratio = get_th_ratio(hhats)
    ax.plot(hhats,th_ratio,label=r"1903.07725 (14TeV): $1+0.03\left(\frac{\hat{H}}{0.04}\right)+0.15\left(\frac{\hat{H}}{0.04}\right)^{2}$",color="C3")
    ax.plot(df14.hhat,df14.xsec/df14.xsec.min(),marker="o",label="MadGraph (14TeV)",markersize=4.,alpha=0.75,color="C0")
    ax.plot(df13.hhat,df13.xsec/df13.xsec.min(),marker="o",label="MadGraph (13TeV)",markersize=4.,alpha=0.75,color="C2")


    # xs = np.linspace(0.,0.25,100)
    # def f(x):
    #     xp = x/0.2
    #     return 1.+0.5*xp+2*xp**2-xp**3
    # coef = np.polyfit(df13.hhat.values,df13.xsec/df13.xsec.min(),3)
    # print "my cubic",coef
    # fpoly = np.poly1d(coef)
    # # ys = f(xs)
    # ys = fpoly(xs)
    # ax.plot(xs,ys,label="fit",color="k")

    from scipy.optimize import curve_fit
    def f(x,a,b,c):
        return 1.+a*x+b*x**2+c*x**3
    subset = df13.hhat.values<0.25
    coef,cov = curve_fit(f,df13.hhat.values[subset],(df13.xsec/df13.xsec.min()).values[subset])
    coef = np.concatenate([np.array([1.]),coef])[::-1]
    xs = np.linspace(0.,0.25,1000)
    fpoly = np.poly1d(coef)
    ys = fpoly(xs)
    label = (
            r"Fit to 13TeV: "
            r"${:.0f}"
            r"{:+.2f}\hat{{H}}"
            r"{:+.2f}\hat{{H}}^2"
            r"{:+.2f}\hat{{H}}^3$"
            ).format(*coef[::-1])
    ax.plot(xs,ys,color="k",label=label)

    ul = 22.5/11.97
    # ax.plot([0.,ax.get_xlim()[1]],[ul,ul],label="obs UL (BDT)",color="k",linestyle="--")
    dfy, fyint = get_corrected_ul()
    ax.plot(hhats,np.ones(len(hhats))*ul,label="uncorrected obs UL (BDT)",color="0.6",linestyle="--")
    ax.plot(hhats,fyint(hhats)/11.97,label="ttH-corrected obs UL (BDT)",color="k",linestyle="--")
    # ax.plot([xcross,xcross],[0.,ul*1.5],linewidth=1.0,color="k",linestyle="--")

    gen_hhats = np.array([0.0,0.04,0.08,0.12,0.16])
    print np.c_[gen_hhats, 11.97*fpoly(gen_hhats)]

    # xy = np.c_[xs,ys]
    # xcross = xy[np.abs(xy[:,1]-ul).argmin()][0]
    # ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="k",linestyle="--")
    # ax.annotate(
    #         "$\hat{{H}}={:.3f}$".format(xcross), 
    #         xy=(xcross,1.0),
    #         xytext=(xcross*1.2,1+(ul-1)*0.5),
    #         arrowprops=dict(arrowstyle="->"),
    #         ha="left",
    #         fontsize=12
    #         )

    xs = np.linspace(0.,0.25,1000)
    xy = np.c_[xs,fpoly(xs),fyint(xs)/11.97]
    xcross = xy[np.abs(xy[:,1]-xy[:,2]).argmin()][0]
    ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="k",linestyle="--")
    ax.annotate(
            "$\hat{{H}}={:.3f}$".format(xcross), 
            xy=(xcross,1.0),
            xytext=(xcross*1.2,1+(ul-1)*0.5),
            arrowprops=dict(arrowstyle="->"),
            ha="left",
            fontsize=12
            )

    # print "my cubic",np.polyfit(df.hhat,df.xsec/df.xsec.min(),3)
    # print "my quadratic", np.polyfit(df.hhat,df.xsec/df.xsec.min(),2)
    # print "their quadratic", np.polyfit(hhats,th_ratio,2)

    ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylim([1.,5.])
    ax.set_ylabel(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$")
    ax.set_title(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$ vs $\hat{H}$")
    ax.set_xlabel(r"$\hat{H}$")

    # ax.xaxis.set_major_locator(MultipleLocator(0.02))
    # ax.xaxis.set_minor_locator(MultipleLocator(0.01))
    # ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    # ax.set_yscale("log")
    # ax.set_yscale("log")
    # ax.set_ylim([1.,1.3])
    # ax.set_xlim([0.,0.05])

    ax.legend()

    fig.set_tight_layout(True)
    fig.savefig("plots/plot_oblique.png")
    fig.savefig("plots/plot_oblique.pdf")
    os.system("ic plots/plot_oblique.png")

def get_corrected_ul(yukawa_log = "../../../analysis/limits/ft_updated2018_run2_19Mar5/v3.28_ft_mar18nominal_v1/log_yukawa_scan.txt"):
    # return tuple of 
    #   - dataframe with hhat and ul columns
    #   - interpolating function giving ul for a hhat value
    #
    kts, ul, central, ups, downs = parse_yukawa_log(yukawa_log)
    kts = np.array(kts)
    uls = np.array(ul)
    dfy = pd.DataFrame(np.c_[kts, uls], columns=["kt","ul"])
    dfy["hhat"] = 1.0-dfy["kt"]
    dfy = dfy[dfy["hhat"]>=0.]
    fyint = interpolate.interp1d(dfy["hhat"],dfy["ul"],kind="quadratic")
    return dfy, fyint


def plot_tth():
    df = get_df_tth("out_oblique_scan_tthyt_v1")
    # df1 = get_df_tth("out_oblique_scan_tthytprop_v1")
    # print prop0
    # print prop1
    # print prop0/prop1

    # yukawa_log = "../../../analysis/limits/ft_updated2018_run2_19Mar5/v3.28_ft_mar18nominal_v1/log_yukawa_scan.txt"
    # kts, ul, central, ups, downs = parse_yukawa_log(yukawa_log)
    # kts = np.array(kts)
    # uls = np.array(ul)
    # dfy = pd.DataFrame(np.c_[kts, uls], columns=["kt","ul"])
    # dfy["hhat"] = 1.0-dfy["kt"]
    # dfy = dfy[dfy["hhat"]>=0.]
    # print dfy
    # fyint = interpolate.interp1d(dfy["hhat"],dfy["ul"],kind="quadratic")

    # df = prop0.merge(prop1,on=["hhat"])
    # print df["xsec_y"]/df["xsec_x"]

    fig,ax = plt.subplots()

    # # ax.plot
    # def get_th_ratio(hhat):
    #     # dsig is (sigmahhat-sigmasm)/sigmasm = sigmahhat/sigmasm - 1
    #     # so ratio (wrt sm) is dsig + 1
    #     return 1+0.03*(hhat/0.04)+0.15*(hhat/0.04)**2

    hhats = np.linspace(0.,1.00,100)
    # th_ratio = get_th_ratio(hhats)
    # ax.plot(hhats,th_ratio,label=r"1903.07725 (14TeV): $1+0.03\left(\frac{\hat{H}}{0.04}\right)+0.15\left(\frac{\hat{H}}{0.04}\right)^{2}$",color="C3")
    # ax.plot(df0.hhat,df0.xsec/df0.xsec.min(),marker="o",label="No prop",markersize=4.,alpha=0.75,color="C0")
    # ax.plot(df13.hhat,df13.xsec/df13.xsec.min(),marker="o",label="MadGraph (13TeV)",markersize=4.,alpha=0.75,color="C2")
    # ax.plot(df.hhat,df.xsec/(df[df.hhat==0.].xsec.values[0]),marker="o",label="ttH",markersize=4.,alpha=0.75,color="C2")
    # ax.plot(df.hhat,(1-df.hhat)**2.,marker="o",label="(1-hhat)^2",markersize=4.,alpha=0.75,color="C1")
    # print df.hhat
    # print df.xsec/(df[df.hhat==0.].xsec.values[0])
    # print (1-df.hhat)**2.

    dfy,fyint = get_corrected_ul()
    ax.plot(dfy.hhat,dfy.ul,marker="o",label="obsUL",markersize=4.,alpha=0.75,color="k")
    ax.plot(hhats,fyint(hhats),marker="o",label="interpolation",markersize=4.,alpha=0.75,color="r")

    # ax.plot(df.hhat,df.xsec/(df[df.hhat==0.].xsec.values[0]),marker="o",label="ttH",markersize=4.,alpha=0.75,color="C2")

    # xs = np.linspace(0.,0.25,100)
    # def f(x):
    #     xp = x/0.2
    #     return 1.+0.5*xp+2*xp**2-xp**3
    # coef = np.polyfit(df13.hhat.values,df13.xsec/df13.xsec.min(),3)
    # print "my cubic",coef
    # fpoly = np.poly1d(coef)
    # # ys = f(xs)
    # ys = fpoly(xs)
    # ax.plot(xs,ys,label="fit",color="k")

    # from scipy.optimize import curve_fit
    # def f(x,a,b,c):
    #     return 1.+a*x+b*x**2+c*x**3
    # subset = df13.hhat.values<0.25
    # coef,cov = curve_fit(f,df13.hhat.values[subset],(df13.xsec/df13.xsec.min()).values[subset])
    # coef = np.concatenate([np.array([1.]),coef])[::-1]
    # xs = np.linspace(0.,0.25,1000)
    # fpoly = np.poly1d(coef)
    # ys = fpoly(xs)
    # label = (
    #         r"Fit to 13TeV: "
    #         r"${:.0f}"
    #         r"{:+.2f}\hat{{H}}"
    #         r"{:+.2f}\hat{{H}}^2"
    #         r"{:+.2f}\hat{{H}}^3$"
    #         ).format(*coef[::-1])
    # ax.plot(xs,ys,color="k",label=label)

    # ul = 22.5/11.97
    # ax.plot([0.,ax.get_xlim()[1]],[ul,ul],label="obs UL (BDT)",color="k",linestyle="--")
    # # ax.plot([xcross,xcross],[0.,ul*1.5],linewidth=1.0,color="k",linestyle="--")

    # xy = np.c_[xs,ys]
    # xcross = xy[np.abs(xy[:,1]-ul).argmin()][0]
    # ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="k",linestyle="--")
    # ax.annotate(
    #         "$\hat{{H}}={:.3f}$".format(xcross), 
    #         xy=(xcross,1.0),
    #         xytext=(xcross*1.2,1+(ul-1)*0.5),
    #         arrowprops=dict(arrowstyle="->"),
    #         ha="left",
    #         fontsize=12
    #         )

    # print "my cubic",np.polyfit(df.hhat,df.xsec/df.xsec.min(),3)
    # print "my quadratic", np.polyfit(df.hhat,df.xsec/df.xsec.min(),2)
    # print "their quadratic", np.polyfit(hhats,th_ratio,2)

    # # ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylabel(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$")
    # ax.set_title(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$ vs $\hat{H}$")
    # ax.set_xlabel(r"$\hat{H}$")

    # # ax.xaxis.set_major_locator(MultipleLocator(0.02))
    # # ax.xaxis.set_minor_locator(MultipleLocator(0.01))
    # # ax.yaxis.set_major_locator(MultipleLocator(0.5))
    # ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    # ax.set_yscale("log")
    # ax.set_yscale("log")
    # ax.set_ylim([1.,1.3])
    # ax.set_xlim([0.,0.05])

    ax.legend()

    fig.set_tight_layout(True)
    fig.savefig("plots/plot_tth_oblique.png")
    fig.savefig("plots/plot_tth_oblique.pdf")
    os.system("ic plots/plot_tth_oblique.png")

def plot_custom():
    # df14 = get_df("out_test_fixhhatscan_part")
    df13 = get_df("out_test_13tevhhatscan_part")
    dfcustom = get_df_custom()

    # df14 = df14[df14.hhat < 0.17]
    # df13 = df13[df13.hhat < 0.17]

    fig,ax = plt.subplots()

    # # ax.plot
    # def get_th_ratio(hhat):
    #     # dsig is (sigmahhat-sigmasm)/sigmasm = sigmahhat/sigmasm - 1
    #     # so ratio (wrt sm) is dsig + 1
    #     return 1+0.03*(hhat/0.04)+0.15*(hhat/0.04)**2

    hhats = np.linspace(0.,0.20,100)
    # th_ratio = get_th_ratio(hhats)
    # ax.plot(hhats,th_ratio,label=r"1903.07725 (14TeV): $1+0.03\left(\frac{\hat{H}}{0.04}\right)+0.15\left(\frac{\hat{H}}{0.04}\right)^{2}$",color="C3")
    # ax.plot(df14.hhat,df14.xsec/df14.xsec.min(),marker="o",label="MadGraph (14TeV)",markersize=4.,alpha=0.75,color="C0")
    ax.plot(df13.hhat,df13.xsec/df13.xsec.min(),marker="o",label="MadGraph",markersize=4.,alpha=0.75,color="C2")


    # xs = np.linspace(0.,0.25,100)
    # def f(x):
    #     xp = x/0.2
    #     return 1.+0.5*xp+2*xp**2-xp**3
    # coef = np.polyfit(df13.hhat.values,df13.xsec/df13.xsec.min(),3)
    # print "my cubic",coef
    # fpoly = np.poly1d(coef)
    # # ys = f(xs)
    # ys = fpoly(xs)
    # ax.plot(xs,ys,label="fit",color="k")

    from scipy.optimize import curve_fit
    def f(x,a,b,c):
        return 1.+a*x+b*x**2+c*x**3
    subset = df13.hhat.values<0.25
    coef,cov = curve_fit(f,df13.hhat.values[subset],(df13.xsec/df13.xsec.min()).values[subset])
    coef = np.concatenate([np.array([1.]),coef])[::-1]
    xs = np.linspace(0.,0.25,1000)
    fpoly = np.poly1d(coef)
    ys = fpoly(xs)
    label = (
            r"Fit to MadGraph: "
            r"${:.0f}"
            r"{:+.2f}\hat{{H}}"
            r"{:+.2f}\hat{{H}}^2"
            r"{:+.2f}\hat{{H}}^3$"
            ).format(*coef[::-1])
    ax.plot(xs,ys,color="k",label=label)

    ul = 22.5/11.97
    # ax.plot([0.,ax.get_xlim()[1]],[ul,ul],label="obs UL (BDT)",color="k",linestyle="--")
    dfy, fyint = get_corrected_ul()
    ax.plot(hhats,np.ones(len(hhats))*ul,label="uncorrected obs UL (BDT)",color="0.6",linestyle="--")
    ax.plot(hhats,fyint(hhats)/11.97,label="ttH-corrected obs UL (BDT)",color="k",linestyle="--")
    # ax.plot([xcross,xcross],[0.,ul*1.5],linewidth=1.0,color="k",linestyle="--")

    dfcustom["xsecratio"] = fpoly(dfcustom.hhat)*dfcustom.obsr
    print dfcustom

    ax.plot(dfcustom["hhat"],dfcustom["xsecratio"],label="Dedicated samples: obs UL (BDT)",color="r",marker="x")
    fcustomint = interpolate.interp1d(dfcustom["hhat"],dfcustom["xsecratio"],kind="linear")
    xs = np.linspace(dfcustom.hhat.min(),dfcustom.hhat.max(),100)
    # ax.plot(xs,fcustomint(xs),label="test interp",color="r",linestyle="--")

    # gen_hhats = np.array([0.0,0.04,0.08,0.12,0.16])
    # print np.c_[gen_hhats, 11.97*fpoly(gen_hhats)]

    # xy = np.c_[xs,ys]
    # xcross = xy[np.abs(xy[:,1]-ul).argmin()][0]
    # ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="k",linestyle="--")
    # ax.annotate(
    #         "$\hat{{H}}={:.3f}$".format(xcross), 
    #         xy=(xcross,1.0),
    #         xytext=(xcross*1.2,1+(ul-1)*0.5),
    #         arrowprops=dict(arrowstyle="->"),
    #         ha="left",
    #         fontsize=12
    #         )

    # xs = np.linspace(0.,0.25,1000)
    # xy = np.c_[xs,fpoly(xs),fyint(xs)/11.97]
    # xcross = xy[np.abs(xy[:,1]-xy[:,2]).argmin()][0]
    # ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="k",linestyle="--")
    # ax.annotate(
    #         "$\hat{{H}}={:.3f}$".format(xcross), 
    #         xy=(xcross,1.0),
    #         xytext=(xcross*1.2,1+(ul-1)*0.5),
    #         arrowprops=dict(arrowstyle="->"),
    #         ha="left",
    #         fontsize=12
    #         )

    xs = np.linspace(0.,dfcustom["hhat"].max(),1000)
    xy = np.c_[xs,fpoly(xs),fyint(xs)/11.97,fcustomint(xs)]
    # xcross = xy[np.abs(xy[:,1]-xy[:,2]).argmin()][0]
    xcross = xy[np.abs(xy[:,1]-xy[:,3]).argmin()][0]
    ax.plot([xcross,xcross],[1.,ul*1.5],linewidth=1.0,color="r",linestyle="--")
    ax.annotate(
            "$\hat{{H}}={:.3f}$".format(xcross),
            color="r",
            xy=(xcross,1.0),
            xytext=(xcross*1.2,1+(ul-1)*0.5),
            arrowprops=dict(arrowstyle="->",color="r"),
            ha="left",
            fontsize=12
            )

    # print "my cubic",np.polyfit(df.hhat,df.xsec/df.xsec.min(),3)
    # print "my quadratic", np.polyfit(df.hhat,df.xsec/df.xsec.min(),2)
    # print "their quadratic", np.polyfit(hhats,th_ratio,2)

    ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylim([1.,ax.get_ylim()[1]])
    # ax.set_ylim([1.,5.])
    ax.set_ylabel(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$")
    ax.set_title(r"$\sigma_{\hat{H}+\mathrm{SM}}/\sigma_\mathrm{SM}$ vs $\hat{H}$")
    ax.set_xlabel(r"$\hat{H}$")

    # ax.xaxis.set_major_locator(MultipleLocator(0.02))
    # ax.xaxis.set_minor_locator(MultipleLocator(0.01))
    # ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    # ax.set_yscale("log")
    # ax.set_yscale("log")
    # ax.set_ylim([1.,1.3])
    # ax.set_xlim([0.,0.05])

    ax.legend()

    fig.set_tight_layout(True)
    fig.savefig("plots/plot_oblique_custom.png")
    fig.savefig("plots/plot_oblique_custom.pdf")
    os.system("ic plots/plot_oblique_custom.png")

def get_corrected_ul(yukawa_log = "../../../analysis/limits/ft_updated2018_run2_19Mar5/v3.28_ft_mar18nominal_v1/log_yukawa_scan.txt"):
    # return tuple of 
    #   - dataframe with hhat and ul columns
    #   - interpolating function giving ul for a hhat value
    #
    kts, ul, central, ups, downs = parse_yukawa_log(yukawa_log)
    kts = np.array(kts)
    uls = np.array(ul)
    dfy = pd.DataFrame(np.c_[kts, uls], columns=["kt","ul"])
    dfy["hhat"] = 1.0-dfy["kt"]
    dfy = dfy[dfy["hhat"]>=0.]
    fyint = interpolate.interp1d(dfy["hhat"],dfy["ul"],kind="quadratic")
    return dfy, fyint


if __name__ == "__main__":

    # plot_main()
    plot_custom()

    # plot_tth()

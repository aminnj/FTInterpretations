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
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from scipy import interpolate

import utils
utils.set_style_defaults()

EXPCOLOR="C3"
class DoubleBandObject(object): pass
class DoubleBandObjectHandler(object):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch = mlines.Line2D(
                [x0+width*0.03,x0+width-width*0.03],[y0+height*0.5],
                linestyle=(-0.5,(2.6,1.6)), linewidth=1.5,marker="",color=EXPCOLOR,
                transform=handlebox.get_transform(),
                )
        handlebox.add_artist(patch)
        patch = mlines.Line2D(
                [x0+width*0.03,x0+width-width*0.03],[y0+height*1.0],
                linestyle=(2,(1.5,0.8)), linewidth=1.5,marker="",color=EXPCOLOR,
                transform=handlebox.get_transform(),
                )
        handlebox.add_artist(patch)
        patch = mlines.Line2D(
                [x0+width*0.03,x0+width-width*0.03],[y0+height*0.0],
                linestyle=(2,(1.5,0.8)), linewidth=1.5,marker="",color=EXPCOLOR,
                transform=handlebox.get_transform(),
                )
        handlebox.add_artist(patch)
        return patch

def grid(x, y, z, resX=100j, resY=100j):
    from scipy.interpolate import griddata
    xi, yi = np.mgrid[min(x):max(x):resX, min(y):max(y):resY]
    Z = griddata((x, y), z, (xi[None,:], yi[None,:]), method="linear")
    Z = Z[0]
    return xi, yi, Z

import ROOT as r
r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)
f = r.TFile("mh125_align_13.root")
br_H_tt = f.Get("br_H_tt")
def get_br(proc,mass,tanbeta=1.,convert_mh=False):
    if tanbeta < 1.: return 1.0
    return br_H_tt.GetBinContent(br_H_tt.FindBin(mass,tanbeta))

def get_df(already_decayed=False,apply_br=True):

    if already_decayed:
        df = utils.load_data("data/data_Apr18.txt")
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

if __name__ == "__main__":

    dfc = get_df()

    # dfc_dec = get_df(already_decayed=True,apply_br=False)
    # dfc["brmgratio_h"] = dfc_dec["xsec_h"]/dfc["xsec_h"]
    # dfc["brmgratio_a"] = dfc_dec["xsec_a"]/dfc["xsec_a"]
    # # print dfc

    print "Dumped json!"
    dfc.to_json("xsecs_2hdm.json")

    do_plot_xsecs_2d = True
    do_plot_xsecs_1d = False
    do_plot_tanbeta_exclusion = False

    if do_plot_xsecs_2d:
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

    if do_plot_xsecs_1d:

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
        # ax.set_yscale("log")
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

        fig.set_tight_layout(True)
        fname = "plots/plot_1d_2hdm_xsec.png".format(key)
        fig.savefig(fname)
        fig.savefig(fname.replace(".png",".pdf"))
        os.system("ic "+fname)


    if do_plot_tanbeta_exclusion:

        for particle in list("ahb"):

            # particle = "b"
            xseckey = "xsec_{}".format(particle.lower())

            dful = pd.read_json("../../../analysis/limits/dump_higgs_{}.json".format(particle.lower()))
            dful = dful.sort_values(["mass"])


            x = dfc["mass"].values
            y = dfc["tanbeta"].values
            z = dfc[xseckey].values

            for k in ["obsr","exprm2","exprm1","expr","exprp1","exprp2"]:
                dful["new_"+k.replace("r","")] = dful[k]*(dfc[dfc.tanbeta==1.][xseckey]).values

            for k in ["obs","expm2","expm1","exp","expp1","expp2"]:
                edges = []
                for mass in sorted(dful.mass.unique()):
                    ul = dful[np.abs(dful.mass-mass)<0.01]["new_"+k].values[0]
                    dftmp = dfc[np.abs(dfc.mass-mass)<0.01]
                    xs = dftmp["tanbeta"]
                    ys = dftmp[xseckey]
                    fint = interpolate.interp1d(xs,ys)
                    big_xy = np.c_[np.linspace(xs.min(),xs.max(),1000),fint(np.linspace(xs.min(),xs.max(),1000))]
                    tbcross = big_xy[np.abs(big_xy[:,1]-ul).argmin()][0]
                    edges.append([mass,tbcross])
                dful["tb_"+k] = np.array(edges)[:,1]

            X, Y, Z = grid(x,y,z)

            fig,ax = plt.subplots()

            masses = dful["mass"]
            pe1 = ax.fill_between(masses, dful["tb_obs"]*0., dful["tb_obs"], linewidth=0., facecolor="0.5", alpha=0.4)
            pe0 = ax.plot(masses,dful["tb_exp"], linestyle=(0,(5,3)), linewidth=2.,marker="",color=EXPCOLOR,solid_capstyle="butt")
            pep1 = ax.plot(masses,dful["tb_expm1"], linestyle=(0,(2,1)), linewidth=2.,marker="",color=EXPCOLOR,solid_capstyle="butt")
            pem1 = ax.plot(masses,dful["tb_expp1"], linestyle=(0,(2,1)), linewidth=2.,marker="",color=EXPCOLOR,solid_capstyle="butt")
            pobs = ax.plot(masses,dful["tb_obs"], linestyle="-", linewidth=2.,markersize=0.,marker="o",color="k",solid_capstyle="butt")
            obspatch = mpatches.Rectangle([0,0], 1, 1, facecolor="0.8", # alpha*(facecolor-1)+1 of regular fill_between, to emulate non-unity alpha
                                       edgecolor="k", lw=1.,)

            particletext = particle.upper().replace("B","H/A")
            ax.set_title(r"$\sigma(pp\rightarrow tX{particle}\rightarrow t\bar{{t}})\times BR({particle}\rightarrow t\bar{{t}})$".format(particle=particletext))
            ax.set_xlabel(r"$m_{{{particle}}}$ [GeV]".format(particle=particletext))
            ax.set_ylabel(r"$\tan\beta$")

            ax.set_ylim([0.,5.])
            ax.yaxis.set_minor_locator(MultipleLocator(0.2))
            ax.xaxis.set_minor_locator(MultipleLocator(10.))

            legend = ax.legend(
                    [
                        (obspatch),
                        DoubleBandObject(),
                        ],
                        [
                        "95% CL Observed exclusion",
                        r"95% CL Expected exclusion $\pm$1 $\sigma$",
                        ],
                    handler_map={DoubleBandObject: DoubleBandObjectHandler()},
                    # handlelength=2.0,
                    labelspacing=0.6,
                    )

            fig.tight_layout()
            fname = "plots/plot_2d_2hdm_tanbetaexclusion_{}.png".format(particle)
            fig.savefig(fname)
            fig.savefig(fname.replace(".png",".pdf"))
            os.system("ic "+fname)


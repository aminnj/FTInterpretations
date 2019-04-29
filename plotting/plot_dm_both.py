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

class OneSideHatchObject1(object): pass
class OneSideHatchObject2(object): pass
class OneSideHatchObject3(object): pass
class OneSideHatchObject4(object): pass
class OneSideHatchObjectHandler(object):
    def __init__(self, edgecolor=(0.4,0.4,0.4), facecolor="none", linewidth=1.5,dashed=False):
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.linewidth = linewidth
        self.dashed = dashed
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        edgecolor=self.edgecolor
        facecolor=self.facecolor
        linewidth=self.linewidth
        if self.dashed:
            x0, y0 = handlebox.xdescent, handlebox.ydescent
            width, height = handlebox.width, handlebox.height
            patch = mpatches.Rectangle([0.,0.], width, height, facecolor=(0,0,0,0),
                                       edgecolor=edgecolor, lw=linewidth, linestyle="--",
                                       transform=handlebox.get_transform())
            handlebox.add_artist(patch)
            return patch
        else:
            x0, y0 = handlebox.xdescent, handlebox.ydescent
            width, height = handlebox.width, handlebox.height
            # patch = mlines.Line2D(
            #         [x0+width*0.03,x0+width-width*0.03],[y0+height*0.2,y0+height*0.2],color=edgecolor,linewidth=linewidth,linestyle="-",
            #         transform=handlebox.get_transform(),
            #         )
            # handlebox.add_artist(patch)
            patch = mpatches.Rectangle([0.,0.], width, height, facecolor=facecolor,
                                       edgecolor=edgecolor, lw=linewidth,
                                       transform=handlebox.get_transform())
            handlebox.add_artist(patch)
            return patch

#         [
#             OneSideHatchObject(),
#             ],
#         [
#             "Observed upper limit",
#             # "Observed cross section",
#             # "Predicted cross section,\nPhys. Rev. D 95 (2017) 053004",
#             ],
#         handler_map={OneSideHatchObject: OneSideHatchObjectHandler()},
#         labelspacing=0.6,
#         )

import utils
utils.set_style_defaults()

# df = utils.load_data("../data_v3.txt")

# grep "Integrated weight" runs/out_dm*v4/*/Events/run_01/run_01_tag_1_banner.txt > data_dm_v4.txt
def get_df(g11=True):
    if g11:
        df = utils.load_data("../data_dm_v4.txt")
    else:
        df = utils.load_data("../data_dm_v5.txt")

    df = df[df.tag.str.contains("dmscalar") | df.tag.str.contains("dmpseudo")]
    print df.tag
    df["which"] = df.tag.str.split("_").str[0]
    df["proc"] = df.tag.str.split("_").str[1]
    df["massmed"] = df.tag.str.split("_").str[2].astype(int)
    df["massdm"] = df.tag.str.split("_").str[3].astype(int)
    df = df.drop(["tag","folder"],axis=1)

    # # drop phi->chichi points where mchi>0.5*mphi (these are unphysical)
    # df = df[~(df["proc"].str.contains("dm") & (df["massdm"]>0.5*df["massmed"]))]
    # sys.exit()

    # separate 6 processes
    ttdm = df[df.proc=="ttdm"].rename(index=str,columns={"xsec":"xsec_ttdm"}).drop(["proc"],axis=1)
    ttsm = df[df.proc=="ttsm"].rename(index=str,columns={"xsec":"xsec_ttsm"}).drop(["proc"],axis=1)
    stwdm = df[df.proc=="stwdm"].rename(index=str,columns={"xsec":"xsec_stwdm"}).drop(["proc"],axis=1)
    stwsm = df[df.proc=="stwsm"].rename(index=str,columns={"xsec":"xsec_stwsm"}).drop(["proc"],axis=1)
    sttdm = df[df.proc=="sttdm"].rename(index=str,columns={"xsec":"xsec_sttdm"}).drop(["proc"],axis=1)
    sttsm = df[df.proc=="sttsm"].rename(index=str,columns={"xsec":"xsec_sttsm"}).drop(["proc"],axis=1)

    # make dataframe where each row contains all 6 processes, and sum up xsecs
    # print ttdm
    dfc = ttdm
    for x in [ttsm,stwdm,stwsm,sttdm,sttsm]:
        dfc = dfc.merge(x,suffixes=["",""],on=["which","massmed","massdm"],how="outer")
    # dfc = dfc.fillna(0.) # FIXME
    # dfc = dfc.fillna(15.e-3) # FIXME
    dfc["xsec_totdm"] = dfc["xsec_ttdm"] + dfc["xsec_stwdm"] + dfc["xsec_sttdm"]
    dfc["xsec_totsm"] = dfc["xsec_ttsm"] + dfc["xsec_stwsm"] + dfc["xsec_sttsm"]

    dfc["stfrac_sm"] = (dfc["xsec_stwsm"] + dfc["xsec_sttsm"])/dfc["xsec_totsm"]
    dfc["stfrac_dm"] = (dfc["xsec_stwdm"] + dfc["xsec_sttdm"])/dfc["xsec_totdm"]

    return dfc

    # dfc["xsec_totdm"] *= 1000.
    # dfc["xsec_totsm"] *= 1000.

    # dfc = dfc.fillna(0.)
    # print dfc

fintuls_exp = {}
fintuls_obs = {}
for k in ["h","a"]:
    # dful = pd.read_json("../higgs/2019/data/dump_higgs_{}.json".format(k))
    dful = pd.read_json("../../../analysis/limits/dump_higgs_{}.json".format(k))
    dful = dful.sort_values(["mass"])
    dful["obs"] = dful["obsr"]*dful["xsec"]
    dful["exp"] = dful["expr"]*dful["xsec"]
    which = "dmscalar" if k == "h" else "dmpseudo"
    fintuls_exp[which] = interpolate.interp1d(dful["mass"],dful["exp"])
    fintuls_obs[which] = interpolate.interp1d(dful["mass"],dful["obs"])

def grid(x, y, z, resX=100j, resY=100j):
    from scipy.interpolate import griddata
    xi, yi = np.mgrid[min(x):max(x):resX, min(y):max(y):resY]
    # Z = griddata((x, y), z, (xi[None,:], yi[None,:]), method="linear") #, interp="linear")
    Z = griddata((x, y), z, (xi[None,:], yi[None,:]), method="linear") #, interp="linear")
    Z = Z[0]
    return xi, yi, Z


dfc1 = get_df(g11=True)
dfc2 = get_df(g11=False)

# # print dfc1
# compdf = dfc1.merge(dfc2,suffixes=["_1","_g"],on=["which","massmed","massdm"],how="inner")
# compdf = compdf[["which","massmed","massdm","xsec_ttsm_1","xsec_ttsm_g"]]
# # compdf = compdf[compdf["which"] == "dmpseudo"]
# compdf = compdf[compdf["which"] == "dmscalar"]
# # print compdf
# # print compdf.merge(compdf[compdf["massdm"] == 600.][["massmed","xsec_ttsm_1","xsec_ttsm_g"]],on=["massmed"],how="inner",suffixes=["","_high"])
# lut = dict(compdf[compdf["massdm"] == 600.][["massmed","xsec_ttsm_1"]].values)
# # compdf["xsec_ttsm_high"] = compdf["xsec_ttsm_g"]*0.
# compdf["xsec_ttsm_high"] = np.array(map(lut.__getitem__,compdf["massmed"].values))
# g = 0.5
# compdf["pred_g"] = compdf["xsec_ttsm_high"]/((1-g**2)+g**2*(compdf["xsec_ttsm_high"]/compdf["xsec_ttsm_1"]))
# compdf["err"] = (compdf["pred_g"]-compdf["xsec_ttsm_g"])/compdf["xsec_ttsm_g"]
# # print lut
# print compdf
# # print lut


# sys.exit()

do_scatter = False
for which in [
        "dmscalar",
        "dmpseudo",
        ]:
    for key in [
            "xsec_totsm",
            "stfrac_sm",
            # "xsec_totdm",
            # "stfrac_dm",
            ]:

        do_exclusion = "frac" not in key

        # fig,ax = plt.subplots()
        fig,ax = utils.get_fig_ax()
        # which = "dmscalar"
        # which = "dmpseudo"
        # key = "xsec_totdm"
        # key = "xsec_totsm"
        df1 = dfc1[dfc1["which"] == which]
        df2 = dfc2[dfc2["which"] == which]

        if do_scatter:
            ax.scatter(df1["massmed"],df1["massdm"],c=df1[key],
                    # norm=mpl.colors.LogNorm(vmin=1.5*1e-4,vmax=200*1e-3),
                    norm=mpl.colors.LogNorm(
                        vmin=max(df1[key].min(),0.001),
                        vmax=min(df1[key].max(),150.),
                        ),
                    cmap='cividis',
                    # cmap='Blues',
                               )

        data_rvals1 = []
        data_rvals2 = []
        if "frac" in key:
            for i,(massmed,massdm,val) in df1[["massmed","massdm",key]].iterrows():
                s = "{:.2f}".format(val)
                if do_scatter:
                    ax.text(massmed,massdm+8.,s,fontsize=7,horizontalalignment="center",verticalalignment="bottom")
        else:
            for i,(massmed,massdm,xsec) in df1[["massmed","massdm",key]].iterrows():
                xsec = xsec*1e3
                color = "k"
                exprval = fintuls_exp[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                obsrval = fintuls_obs[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                if not np.isfinite(xsec): continue
                if xsec >= 100.:
                    s = "{:.0f}".format(xsec)
                elif xsec >= 10.:
                    s = "{:.1f}".format(xsec)
                elif xsec >= 1.:
                    s = "{:.1f}".format(xsec)
                else:
                    s = "{:.2f}".format(xsec)
                # # FIXME
                # s = "{:.2f}".format(exprval)
                data_rvals1.append([massmed,massdm,exprval,obsrval])
                if do_scatter:
                    ax.text(massmed,massdm+8.,s,fontsize=6,horizontalalignment="center",verticalalignment="bottom",color=color)
            for i,(massmed,massdm,xsec) in df2[["massmed","massdm",key]].iterrows():
                xsec = xsec*1e3
                exprval = fintuls_exp[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                obsrval = fintuls_obs[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                data_rvals2.append([massmed,massdm,exprval,obsrval])

        if "dm" in key:
            title = r"DM+X, X=$\mathrm{{t\bar{{t}}}}$,tW,tq [{}]".format(which[2:])
        else:
            title = r"$\mathrm{{t\bar{{t}}}}$+X, X=$\mathrm{{t\bar{{t}}}}$,tW,tq [{}]".format(which[2:])

        # minx = 250.
        # miny = 0.
        # maxy = 800.
        # maxx = 800.

        minx = 300.
        miny = 0.
        maxy = 700.
        maxx = 700.

        ax.set_xlim([minx,maxx])
        ax.set_ylim([miny,maxy])

        line = ax.plot([250,800],[0.5*250,0.5*800],linestyle="-",color="k",alpha=0.3)
        p1 = ax.transData.transform_point((minx,0.5*minx))
        p2 = ax.transData.transform_point((maxx,0.5*maxy))
        angle =  np.degrees(np.arctan2(*(p2-p1)[::-1]))
        ax.text(maxx,0.5*maxy-40,r"$\mathrm{m}_\mathrm{med}<2 \mathrm{m}_\mathrm{DM}$   ",fontsize=10,horizontalalignment="right",verticalalignment="bottom",rotation=angle, color="0.3")

        if "pseudo" in which:
            ax.text((maxx-minx)*0.8+minx,maxy*0.8,"pseudoscalar\nmediator",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")
        else:
            ax.text((maxx-minx)*0.8+minx,maxy*0.8,"scalar\nmediator",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")

        if do_exclusion:

            data_rvals1 = np.array(data_rvals1)
            x = data_rvals1[:,0]
            y = data_rvals1[:,1]
            zexp1 = data_rvals1[:,2]
            zobs1 = data_rvals1[:,3]
            X1, Y1, Zexp1 = grid(x,y,zexp1)
            _, _, Zobs1 = grid(x,y,zobs1)

            data_rvals2 = np.array(data_rvals2)
            x = data_rvals2[:,0]
            y = data_rvals2[:,1]
            zexp2 = data_rvals2[:,2]
            zobs2 = data_rvals2[:,3]
            X2, Y2, Zexp2 = grid(x,y,zexp2)
            _, _, Zobs2 = grid(x,y,zobs2)

            levels = np.array([0.0,1.,50.])
            csexp1 = ax.contour(X1,Y1,Zexp1, levels=levels, alpha=0) #, colors="r") #, colors=None,alpha=0.0)
            csobs1 = ax.contour(X1,Y1,Zobs1, levels=levels, alpha=0) #, colors="r") #, colors=None,alpha=0.0)

            levels = np.array([0.0,1.,50.])
            csexp2 = ax.contour(X2,Y2,Zexp2, levels=levels, alpha=0) #, colors="r") #, colors=None,alpha=0.0)
            csobs2 = ax.contour(X2,Y2,Zobs2, levels=levels, alpha=0) #, colors="r") #, colors=None,alpha=0.0)

            ########################################
            ################ # 0.5 #################
            ########################################

            edges = csexp2.allsegs[0][0]
            # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
            if zexp2[np.argmin(np.hypot(x,y))] < 1.:
                edges = np.vstack([[350.,maxy],[350.,miny],edges])
            else:
                edges = np.vstack([[350.,edges[:,0].min()],[350.,edges[:,0].min()],edges])
            edges[:,1][edges[:,1] == 0] -= 50. # make y=0 line go below 0
            edges[0][1] = maxy
            edges[-1][1] = maxy
            edgecolor=tuple(np.array([30,139,228])/255.)
            # pfobs = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.15]))
            ppobs = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="--", marker="",color=tuple(list(edgecolor)+[1.0]))
            color_exp = edgecolor

            edges = csobs2.allsegs[0][0]
            # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
            if zobs2[np.argmin(np.hypot(x,y))] < 1.:
                edges = np.vstack([[350.,maxy],[350.,miny],edges])
            else:
                edges = np.vstack([[350.,edges[:,0].min()],[350.,edges[:,0].min()],edges])
            edges[:,1][edges[:,1] == 0] -= 50. # make y=0 line at zero go below 0
            edges[0][1] = maxy
            edges[-1][1] = maxy
            edgecolor=tuple(np.array([52,63,62])/255.)
            # pfexp = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.30]))
            ppexp = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="--", marker="",color=tuple(list(edgecolor)+[1.0]))
            color_obs = edgecolor


            ########################################
            ################ # 1.0 #################
            ########################################

            edges = csexp1.allsegs[0][0]
            # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
            if zexp1[np.argmin(np.hypot(x,y))] < 1.:
                edges = np.vstack([[350.,maxy],[350.,miny],edges])
            else:
                edges = np.vstack([[350.,edges[:,0].min()],[350.,edges[:,0].min()],edges])
            edges[0][1] = maxy
            edges[-1][1] = maxy
            edgecolor=tuple(np.array([30,139,228])/255.)
            pfobs = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.15]))
            ppobs = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="-", marker="",color=tuple(list(edgecolor)+[1.0]))
            color_exp = edgecolor

            edges = csobs1.allsegs[0][0]
            # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
            if zobs1[np.argmin(np.hypot(x,y))] < 1.:
                edges = np.vstack([[350.,maxy],[350.,miny],edges])
            else:
                edges = np.vstack([[350.,edges[:,0].min()],[350.,edges[:,0].min()],edges])
            edges[0][1] = maxy
            edges[-1][1] = maxy
            edgecolor=tuple(np.array([52,63,62])/255.)
            pfexp = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.30]))
            ppexp = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="-", marker="",color=tuple(list(edgecolor)+[1.0]))
            color_obs = edgecolor

            legend = ax.legend(
                    [
                    OneSideHatchObject1(),
                    OneSideHatchObject2(),
                    OneSideHatchObject3(),
                    OneSideHatchObject4(),
                    ],
                    [
                        r"Obs. ($g_\mathrm{q}$=1, $g_\mathrm{\chi}$=1)",
                        r"Exp. ($g_\mathrm{q}$=1, $g_\mathrm{\chi}$=1)",
                        r"Obs. ($g_\mathrm{q}$=1, $g_\mathrm{\chi}$=0.5)",
                        r"Exp. ($g_\mathrm{q}$=1, $g_\mathrm{\chi}$=0.5)",
                        ],
                    handler_map={
                        OneSideHatchObject1: OneSideHatchObjectHandler(edgecolor=color_obs,facecolor=tuple(list(color_obs)+[0.30])),
                        OneSideHatchObject2: OneSideHatchObjectHandler(edgecolor=color_exp,facecolor=tuple(list(color_exp)+[0.15])),
                        OneSideHatchObject3: OneSideHatchObjectHandler(edgecolor=color_obs,facecolor=tuple(list(color_obs)+[0.30]),dashed=True),
                        OneSideHatchObject4: OneSideHatchObjectHandler(edgecolor=color_exp,facecolor=tuple(list(color_exp)+[0.15]),dashed=True),
                        },
                    # labelspacing=0.6,
                    # ncol=2,
                    # loc="upper left",
                    loc="lower right",
                    # loc="upper right",
                    title="Exclusion at 95% CL",
                    fontsize=10,
                    )
            legend.get_title().set_fontsize(legend.get_texts()[0].get_fontsize())


        # text = ax.set_title(title)
        ax.set_ylabel(r"DM mass")
        ax.set_xlabel(r"mediator mass")

        ax.yaxis.set_minor_locator(MultipleLocator(25.))
        ax.xaxis.set_minor_locator(MultipleLocator(25.))

        utils.add_cms_info(ax, lumi="137")
        # ax.xaxis.set_minor_locator(MultipleLocator(10.))

        fig.set_tight_layout(True)
        if do_scatter:
            fname = "plots/plot_2d_{}_{}_bothcouplings_scatter.png".format(which,key)
        else:
            fname = "plots/plot_2d_{}_{}_bothcouplings.png".format(which,key)
        fig.savefig(fname)
        fig.savefig(fname.replace(".png",".pdf"))
        os.system("ic "+fname)



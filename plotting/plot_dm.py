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
class OneSideHatchObjectHandler(object):
    def __init__(self, edgecolor=(0.4,0.4,0.4), facecolor="none", linewidth=1.5):
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.linewidth = linewidth
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        edgecolor=self.edgecolor
        facecolor=self.facecolor
        linewidth=self.linewidth
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
df = utils.load_data("../data_dm_v4.txt")
# df = utils.load_data("../data_dm_v5.txt")

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

# def grid(x, y, z, resX=100j, resY=100j):
#     # stolen from stackoverflow
#     from numpy import linspace, meshgrid
#     from matplotlib.mlab import griddata
#     # from scipy.interpolate import griddata
#     # xi = linspace(min(x), max(x), resX)
#     # yi = linspace(min(y), max(y), resY)
#     xi, yi = np.mgrid[min(x):max(x):resX, min(y):max(y):resY]
#     # Z = griddata(x, y, z, xi, yi, interp="linear")
#     Z = griddata(x, y, z, xi, yi, interp="linear")
#     # print help(griddata)
#     # Z = griddata((x, y), z, (xi[None,:], yi[None,:]), method="cubic") #, interp="linear")
#     # Z = Z[0]
#     # print Z
#     print xi.shape
#     print yi.shape
#     # X, Y = meshgrid(xi, yi)
#     # return X, Y, Z
#     # print Z
#     # print Z.shape
#     return xi, yi, Z

do_scatter = False
for which in [
        "dmscalar",
        "dmpseudo",
        ]:
    for key in [
            "xsec_totsm",
            # "xsec_totdm",
            # "stfrac_sm",
            # "stfrac_dm",
            ]:
        # fig,ax = plt.subplots()
        fig,ax = utils.get_fig_ax()
        # which = "dmscalar"
        # which = "dmpseudo"
        # key = "xsec_totdm"
        # key = "xsec_totsm"
        df = dfc[dfc["which"] == which]


        if do_scatter:
            ax.scatter(df["massmed"],df["massdm"],c=df[key],
                    # norm=mpl.colors.LogNorm(vmin=1.5*1e-4,vmax=200*1e-3),
                    norm=mpl.colors.LogNorm(
                        vmin=max(df[key].min(),0.001),
                        vmax=min(df[key].max(),150.),
                        ),
                    cmap='cividis',
                    # cmap='Blues',
                               )

        data_rvals = []
        if "frac" in key:
            for i,(massmed,massdm,val) in df[["massmed","massdm",key]].iterrows():
                s = "{:.2f}".format(val)
                if do_scatter:
                    ax.text(massmed,massdm+8.,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
        else:
            for i,(massmed,massdm,xsec) in df[["massmed","massdm",key]].iterrows():
                xsec = xsec*1e3
                color = "k"
                exprval = fintuls_exp[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                obsrval = fintuls_obs[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max()))/xsec
                # print massmed,massdm,xsec,exprval
                # if xsec > fintuls_exp[which](np.clip(massmed,dful["mass"].min(),dful["mass"].max())):
                # if exprval < 1.:
                #     color = "r"
                if not np.isfinite(xsec): continue
                if xsec >= 100.:
                    # s = "{:.0f}fb".format(xsec)
                    s = "{:.0f}".format(xsec)
                elif xsec >= 10.:
                    # s = "{:.1f}fb".format(xsec)
                    s = "{:.1f}".format(xsec)
                elif xsec >= 1.:
                    # s = "{:.1f}fb".format(xsec)
                    s = "{:.1f}".format(xsec)
                else:
                    # s = "{:.2f}fb".format(xsec)
                    s = "{:.2f}".format(xsec)

                # # FIXME
                # s = "{:.2f}".format(exprval)
                data_rvals.append([massmed,massdm,exprval,obsrval])
                if do_scatter:
                    ax.text(massmed,massdm+8.,s,fontsize=6,horizontalalignment="center",verticalalignment="bottom",color=color)
                # print m,tb,xsec
            # plt.colorbar()

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

        g11 = False
        if g11:
            if "pseudo" in which:
                ax.text((maxx-minx)*0.8+minx,maxy*0.8,"pseudoscalar\nmediator\n$g_\\mathrm{DM}$ = 1\n$g_\\mathrm{SM}$ = 1",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")
            else:
                ax.text((maxx-minx)*0.8+minx,maxy*0.8,"scalar\nmediator\n$g_\\mathrm{DM}$ = 1\n$g_\\mathrm{SM}$ = 1",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")
        else:
            if "pseudo" in which:
                ax.text((maxx-minx)*0.8+minx,maxy*0.8,"pseudoscalar\nmediator\n$g_\\mathrm{DM}$ = 0.5\n$g_\\mathrm{SM}$ = 1",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")
            else:
                ax.text((maxx-minx)*0.8+minx,maxy*0.8,"scalar\nmediator\n$g_\\mathrm{DM}$ = 0.5\n$g_\\mathrm{SM}$ = 1",fontsize=14,horizontalalignment="center",verticalalignment="center",color="k")

        # data_rvals.append([349,1,5.,5.])
        # data_rvals.append([349,600,35.,35.])
        data_rvals = np.array(data_rvals)
        x = data_rvals[:,0]
        y = data_rvals[:,1]
        zexp = data_rvals[:,2]
        zobs = data_rvals[:,3]
        X, Y, Zexp = grid(x,y,zexp)
        X, Y, Zobs = grid(x,y,zobs)

        # fig,ax = plt.subplots()
        # levels = np.quantile(z,np.concatenate([[0.],np.linspace(0.1,0.95,35.),[1.0]]))
        # levels = np.quantile(z,np.array([0.,1.0,50.]))
        # levels = np.array([0.0,0.5,0.8,1.0,1.5,2.0,50.])
        levels = np.array([0.0,1.,50.])
        # levels = np.array([0.0,0.1,1.0,2.0])
        # CS = ax.contourf(X,Y,Z,levels=levels,cmap="PuBu_r",norm=mpl.colors.LogNorm(vmin=z.min(), vmax=z.max()))
        # CS2 = ax.contour(CS, levels=np.concatenate([CS.levels]), colors="k")
        # csexp = ax.contour(X,Y,Zexp, levels=levels, colors=None,alpha=0.0)
        # csobs = ax.contour(X,Y,Zobs, levels=levels, colors=None,alpha=0.0)
        csexp = ax.contour(X,Y,Zexp, levels=levels) #, colors="r") #, colors=None,alpha=0.0)
        csobs = ax.contour(X,Y,Zobs, levels=levels) #, colors="r") #, colors=None,alpha=0.0)

        # print csobs
        # print dir(csobs)
        # print csobs.allsegs[0][0]


        edges = csexp.allsegs[0][0]
        # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
        if zexp[np.argmin(np.hypot(x,y))] < 1.:
            edges = np.vstack([[350.,maxy],[350.,miny],edges])
        edges[0][1] = maxy
        edges[-1][1] = maxy
        # print edges
        # edges[0][0] = 350.
        # edgecolor=(0.0,0.06,0.64)
        # edgecolor=tuple(np.array([4,114,77])/255.)
        edgecolor=tuple(np.array([30,139,228])/255.)
        # edgecolor=tuple(np.array([148,176,218])/255.)
        # print edgecolor
        pfobs = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.15]))
        ppobs = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="-", marker="",color=tuple(list(edgecolor)+[1.0]))
        color_exp = edgecolor

        edges = csobs.allsegs[0][0]
        # if the bottom left most point is excluded, sometimes the contour doesn't extend there, so add points at 350 manually
        if zobs[np.argmin(np.hypot(x,y))] < 1.:
            edges = np.vstack([[350.,maxy],[350.,miny],edges])
        edges[0][1] = maxy
        edges[-1][1] = maxy
        # edgecolor=(0.,0.,0.)
        edgecolor=tuple(np.array([52,63,62])/255.)
        # print edgecolor
        pfexp = ax.fill_between(edges[:,0], edges[:,1], maxy*np.ones(len(edges)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=tuple(list(edgecolor)+[0.30]))
        ppexp = ax.plot(edges[:,0], edges[:,1], linewidth=1.5, linestyle="-", marker="",color=tuple(list(edgecolor)+[1.0]))
        color_obs = edgecolor

        legend = ax.legend(
                [
                # (ppobs[0],pfobs),
                # (ppexp[0],pfexp),
                OneSideHatchObject1(),
                OneSideHatchObject2(),
                ],
                [
                    "Observed exclusion",
                    "Expected exclusion",
                    ],
                handler_map={
                    OneSideHatchObject1: OneSideHatchObjectHandler(edgecolor=color_obs,facecolor=tuple(list(color_obs)+[0.30])),
                    OneSideHatchObject2: OneSideHatchObjectHandler(edgecolor=color_exp,facecolor=tuple(list(color_exp)+[0.15])),
                    },
                labelspacing=0.6,
                # ncol=2,
                # loc="upper right",
                # title=title,
                )
        # legend.get_title().set_fontsize(legend.get_texts()[0].get_fontsize())

        # Labels for contours
        # ax.clabel(csexp, csexp.levels, inline=True, fmt={l:"{:.1f}".format(l) for l in csexp.levels}, fontsize=10)
        # ax.clabel(csobs, csobs.levels, inline=True, fmt={l:"{:.1f}".format(l) for l in csobs.levels}, fontsize=10)
        # ax.set_title("H only -- theory xsec contours")
        # ax.set_xlabel(r"mass")
        # ax.set_ylabel(r"$\tan\beta$")
        # ax.set_ylabel(r"$\sigma$ [pb]")

        # text = ax.set_title(title)
        ax.set_ylabel(r"DM mass")
        ax.set_xlabel(r"mediator mass")

        ax.yaxis.set_minor_locator(MultipleLocator(25.))
        ax.xaxis.set_minor_locator(MultipleLocator(25.))

        utils.add_cms_info(ax, lumi="137")
        # ax.xaxis.set_minor_locator(MultipleLocator(10.))

        fig.set_tight_layout(True)
        fname = "plots/plot_2d_{}_{}.png".format(which,key)
        fig.savefig(fname)
        fig.savefig(fname.replace(".png",".pdf"))
        os.system("ic "+fname)



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

df = utils.load_data()

df = df[df.tag.str.contains("2hdm")]
df["proc"] = df.tag.str.split("_").str[1]
df["mass"] = df.tag.str.split("_").str[2].astype(int)
df["tanbeta"] = df.tag.str.split("_").str[3].str.replace("p",".").astype(float)
df = df.drop(["tag"],axis=1)

# separate 6 processes
tta = df[df.proc=="tta"].rename(index=str,columns={"xsec":"xsec_tta"}).drop(["proc"],axis=1)
taw = df[df.proc=="taw"].rename(index=str,columns={"xsec":"xsec_taw"}).drop(["proc"],axis=1)
taq = df[df.proc=="taq"].rename(index=str,columns={"xsec":"xsec_taq"}).drop(["proc"],axis=1)
tth = df[df.proc=="tth"].rename(index=str,columns={"xsec":"xsec_tth"}).drop(["proc"],axis=1)
thw = df[df.proc=="thw"].rename(index=str,columns={"xsec":"xsec_thw"}).drop(["proc"],axis=1)
thq = df[df.proc=="thq"].rename(index=str,columns={"xsec":"xsec_thq"}).drop(["proc"],axis=1)

print df.query("mass==550 and tanbeta==1")

# make dataframe where each row contains all 6 processes, and sum up xsecs
dfc = tta
for x in [taw,taq,tth,thw,thq]:
    dfc = dfc.merge(x,suffixes=["",""],on=["tanbeta","mass"],how="inner")
dfc["xsec_a"] = (dfc["xsec_taw"]+dfc["xsec_taq"]+dfc["xsec_tta"])
dfc["xsec_h"] = (dfc["xsec_thw"]+dfc["xsec_thq"]+dfc["xsec_tth"])
dfc["xsec_b"] = (dfc["xsec_a"]+dfc["xsec_h"])

dfc["stfrac_h"] = (dfc["xsec_thw"]+dfc["xsec_thq"])/dfc["xsec_h"]
dfc["stfrac_a"] = (dfc["xsec_taw"]+dfc["xsec_taq"])/dfc["xsec_a"]

print dfc

for key in [
        # "xsec_h",
        # "xsec_a",
        # "stfrac_h",
        "stfrac_a",
        ]:
    fig,ax = plt.subplots()
    # key = "xsec_h"
    # ax.scatter(dfc["mass"],dfc["tanbeta"],c=dfc[key],norm=mpl.colors.LogNorm(vmin=dfc[key].min(), vmax=dfc[key].max()),
    ax.scatter(dfc["mass"],dfc["tanbeta"],c=dfc[key],norm=mpl.colors.LogNorm(vmin=1.5*1e-3,vmax=500*1e-3),
                       cmap='cividis')
                       # cmap='kRainbow')

    for i,(m,tb,val) in dfc[["mass","tanbeta",key]].iterrows():
        s = "{:.2f}".format(val)
        ax.text(m,tb+0.04,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
        # print m,tb,xsec
    # plt.colorbar()

    # for i,(m,tb,xsec) in dfc[["mass","tanbeta",key]].iterrows():
    #     xsec = xsec*1e3
    #     if xsec >= 100.:
    #         s = "{:.0f}".format(xsec)
    #     elif xsec >= 10.:
    #         s = "{:.1f}".format(xsec)
    #     elif xsec >= 1.:
    #         s = "{:.2f}".format(xsec)
    #     else:
    #         s = "{:.3f}".format(xsec)
    #     ax.text(m,tb+0.04,s,fontsize=8,horizontalalignment="center",verticalalignment="bottom")
    #     # print m,tb,xsec
    # # plt.colorbar()

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
    for _ in range(10):
        print "Actually include BR(tt)!!!"

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
fig.set_tight_layout(True)
fig.savefig("plots/test.png")
os.system("ic plots/test.png")

# print mpl.rcParams['font.family']
# print mpl.rcParams['font.sans-serif']
# # for k in
# for k in ['get_font_properties', 'get_fontfamily', 'get_fontname', 'get_fontproperties', 'get_fontsize', 'get_fontstretch', 'get_fontstyle']:
#     print k, getattr(text,k)()
# # print dir(text)

# print (dfc<1.0e-6).any(axis=1).values.mean()


# # particle = "h"
# particle = "a"
# # particle = "b"
# xseckey = "xsec_{}".format(particle.lower())

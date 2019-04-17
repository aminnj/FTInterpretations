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

if __name__ == "__main__":

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
    ax.plot([0.,ax.get_xlim()[1]],[ul,ul],label="obs UL (BDT)",color="k",linestyle="--")
    # ax.plot([xcross,xcross],[0.,ul*1.5],linewidth=1.0,color="k",linestyle="--")

    xy = np.c_[xs,ys]
    xcross = xy[np.abs(xy[:,1]-ul).argmin()][0]
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

    # ax.set_ylim([1.,ax.get_ylim()[1]])
    ax.set_ylim([1.,ax.get_ylim()[1]])
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

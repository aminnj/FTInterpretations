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

BDTOBSULWEAKER = 23.0 # Note, this was calculated with an extra 10% normalization uncertainty for signal

class OneSideHatchObject1(object): pass
class OneSideHatchObject2(object): pass
class OneSideHatchObjectHandler(object):
    def __init__(self, edgecolor=(0.4,0.4,0.4), facecolor="none", linewidth=2.):
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.linewidth = linewidth
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        # print legend
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        width, height = handlebox.width, handlebox.height
        patch = mlines.Line2D(
                [x0+width*0.03,x0+width-width*0.03],[y0+height*0.2,y0+height*0.2],color=self.edgecolor,linewidth=self.linewidth,linestyle="-",
                transform=handlebox.get_transform(),
                )
        handlebox.add_artist(patch)
        patch = mpatches.Rectangle([x0, y0+height*0.2], width, height-height*0.2, facecolor=self.facecolor,
                                   edgecolor=self.edgecolor, hatch='///', lw=0.,
                                   transform=handlebox.get_transform())
        handlebox.add_artist(patch)
        return patch

def plot_crossings(df, ul=BDTOBSULWEAKER/11.97*12.32/12.32,which="phi"):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    edges = []
    for mass in sorted(df["mass"].unique()):
        sel = df["mass"]==mass
        xs = df["coupling"][sel]
        ys = df["ratio"][sel]
        # mask that returns unique elements (assuming xs is sorted, which it is)
        uniq = np.array([True]+(np.diff(xs)!=0).tolist())
        xs = xs[uniq]
        ys = ys[uniq]
        label = "{:.0f}GeV".format(mass)
        ax.plot(xs,ys,label=label,markersize=5.,marker="o")
        if len(xs) >= 3:
            fint = interpolate.interp1d(xs,ys,kind="quadratic")
            xnew = np.linspace(xs.min(),xs.max(),100.)
            ynew = fint(xnew)
            ax.plot(xnew,ynew,linewidth=1.0,color="k")
            if ynew.min() < ul < ynew.max():
                big_xy = np.c_[np.linspace(xs.min(),xs.max(),1000),fint(np.linspace(xs.min(),xs.max(),1000))]
                xcross = big_xy[np.abs(big_xy[:,1]-ul).argmin()][0]
                print xcross
                edges.append([mass,xcross])
                print "Can find coupling bound for {}".format(mass)
                ax.plot([xcross,xcross],[0.,ul*1.5],linewidth=1.0,color="k",linestyle="--")

    ax.plot([0.,1.4],[ul,ul],label="obs UL",color="k",linestyle="--")
    ax.set_ylim([1.,ax.get_ylim()[1]])
    ax.set_ylabel(r"$\sigma_\mathrm{NP+SM}/\sigma_\mathrm{SM}$")
    if which == "phi":
        ax.set_title(r"scalar $\phi$: $\sigma_\mathrm{NP+SM}/\sigma_\mathrm{SM}$ vs $y_\mathrm{t\phi}$")
        ax.set_xlabel(r"$y_\mathrm{t\phi}$")
    else:
        ax.set_title(r"vector $Z'$: $\sigma_\mathrm{NP+SM}/\sigma_\mathrm{SM}$ vs $g_\mathrm{tZ'}$")
        ax.set_xlabel(r"$g_\mathrm{tZ'}$")
    ax.legend()
    fig.tight_layout()
    fig.savefig("plots/plot_crossings_{}.pdf".format(which))
    fig.savefig("plots/plot_crossings_{}.png".format(which))
    os.system("ic plots/plot_crossings_{}.png".format(which))
    edges = np.array(edges)
    edges = np.concatenate([edges,[[340.,2.0],[25.,2.0]]])
    return edges


def plot_2d_single(df,edges,which="phi"):
    # edges = plot_crossings(df)

    fig,ax = utils.get_fig_ax()
    # close the polygon
    ax.set_xlim([25.,340.])
    ax.set_ylim([0.0,2.0])

    # edges.dump("edges_phi.npy")

    ax.xaxis.set_minor_locator(MultipleLocator(10.))
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    utils.add_cms_info(ax, lumi="137")
    if which == "phi":
        ax.set_ylabel(r"$g_\mathrm{t\phi}$")
        ax.set_xlabel(r"$m_\mathrm{\phi}$ (GeV)")
    else:
        ax.set_ylabel(r"$g_\mathrm{tZ'}$")
        ax.set_xlabel(r"$m_\mathrm{Z'}$ (GeV)")

    if which == "phi":
        facecolor=(0.0,0.06,0.64,0.5)
        edgecolor=(0.0,0.06,0.64,1.0)
    else:
        facecolor=(0.18,0.43,0.11,0.5)
        edgecolor=(0.18,0.43,0.11,1.0)
    ax.add_patch(mpl.patches.Polygon(edges, closed=True, fill=True, facecolor=facecolor,edgecolor=edgecolor,linewidth=1.5,label="Observed exclusion @ 95% CL"))

    ax.legend()

    fig.tight_layout()
    fig.savefig("plots/plot_2d_{}.png".format(which))
    fig.savefig("plots/plot_2d_{}.pdf".format(which))
    os.system("ic plots/plot_2d_{}.png".format(which))

def plot_2d_both(edges_zprime,edges_phi):
    # edges = plot_crossings(df)

    fig,ax = utils.get_fig_ax()
    ax.set_xlim([25.,339.])
    ax.set_ylim([0.0,1.8])

    ax.xaxis.set_minor_locator(MultipleLocator(10.))
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    utils.add_cms_info(ax, lumi="137")
    ax.set_ylabel(r"mediator-top coupling")
    ax.set_xlabel(r"mediator mass (GeV)")

    thickness = 0.075
    edgecolor_zprime=(0.18,0.43,0.11,1.0)
    ax.fill_between(edges_zprime[:,0], edges_zprime[:,1], 2.0*np.ones(len(edges_zprime)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=(0.18,0.43,0.11,0.15))
    p1 = ax.fill_between(edges_zprime[:,0], edges_zprime[:,1], edges_zprime[:,1]+thickness, linewidth=0., edgecolor=edgecolor_zprime, facecolor="none",hatch="////")
    p2 = ax.plot(edges_zprime[:,0], edges_zprime[:,1], linewidth=2.0, linestyle="-", marker="",color=edgecolor_zprime)

    edgecolor_phi=(0.0,0.06,0.64,1.0)
    ax.fill_between(edges_phi[:,0], edges_phi[:,1], 2.0*np.ones(len(edges_phi)), linewidth=0., edgecolor=(0.,0.,0.,0.), facecolor=(0.,0.06,0.64,0.15))
    p3 = ax.fill_between(edges_phi[:,0], edges_phi[:,1], edges_phi[:,1]+thickness, linewidth=0., edgecolor=edgecolor_phi, facecolor="none",hatch="///")
    p4 = ax.plot(edges_phi[:,0], edges_phi[:,1], linewidth=2.0, linestyle="-", marker="",color=edgecolor_phi)

    legend = ax.legend(
            [
                OneSideHatchObject1(),
                OneSideHatchObject2(),
                ],
            [
                "vector $\mathrm{Z'}$",
                "scalar $\phi$",
                ],
            handler_map={
                OneSideHatchObject1: OneSideHatchObjectHandler(edgecolor=edgecolor_zprime,linewidth=2.),
                OneSideHatchObject2: OneSideHatchObjectHandler(edgecolor=edgecolor_phi,linewidth=2.),
                },
            labelspacing=0.6,
            title="Observed exclusion",
            # ncol=2,
            )
    legend.get_title().set_fontsize(legend.get_texts()[0].get_fontsize())

    fig.tight_layout()
    fig.savefig("plots/plot_2d_{}.png".format("both"))
    fig.savefig("plots/plot_2d_{}.pdf".format("both"))
    os.system("ic plots/plot_2d_{}.png".format("both"))

if __name__ == "__main__":

    # FIXME is this right? it just gives the r value which has OUR xsec!!
    ul = (BDTOBSULWEAKER/11.97*12.32)/12.32
    # Scale our UL to their xsec
    # sigma_obs_prime = sigma_obs_ours / sigma_theory_ours * sigma_theory_theirs
    # Then compute sigma(np+sm)/sigma(sm) ratio
    # ratio = sigma_obs_prime / sigma_theory_theirs


    d_edges = {}
    for which in ["zprime","phi"]:
    # for which in ["zprime"]:
        df = utils.load_data()
        df = df[df.tag.str.contains(which)]
        df["mass"] = df.tag.str.split("_").str[2].astype(int)
        df["coupling"] = df.tag.str.split("_").str[3].str.replace("p",".").astype(float)
        df = df.drop(["tag"],axis=1)
        df = df.sort_values(["mass","coupling"])
        xsec_sm = df[df.coupling==0.]["xsec"].values.min()
        df["ratio"] = df["xsec"]/xsec_sm # ratio wrt SM (smallest xsec in the list)
        edges = plot_crossings(df,ul=ul,which=which)
        d_edges[which] = edges
        plot_2d_single(df,edges,which=which)
    d_edges["zprime"].dump("edges_zprime.npy")
    d_edges["phi"].dump("edges_phi.npy")

    edges_zprime = np.load("edges_zprime.npy")
    edges_phi = np.load("edges_phi.npy")
    plot_2d_both(edges_zprime,edges_phi)

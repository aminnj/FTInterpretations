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
utils.set_style_defaults()

def get_br(mdm,gsm,gdm,mmed,scalar=True,yt=1.0,mtop=173.):
    expo = 3./2 if scalar else 1./2
    wratio = 3.0/2. * yt**2. * (gsm/gdm)**2. * ((mmed**2.-4*mtop**2)/(mmed**2.-4*mdm**2))**expo
    return (1.+wratio**-1)**-1.

fig, ax = utils.get_fig_ax()
# text = ax.set_title(title)

xs = np.linspace(0.,225,100)
ax.plot(xs,25.7*get_br(xs,gsm=1.,gdm=1.,mmed=450,scalar=True),label=r"scalar, $g_\mathrm{DM}=$1",linewidth=2.,color="C0")
ax.plot(xs,26.1*get_br(xs,gsm=1.,gdm=1.,mmed=450,scalar=False),label=r"pseudo, $g_\mathrm{DM}=$1",linewidth=2.,color="C3")
ax.plot(xs,25.7*get_br(xs,gsm=1.,gdm=0.5,mmed=450,scalar=True),label=r"scalar, $g_\mathrm{DM}=$0.5",linewidth=2.,color="C0",linestyle="--")
ax.plot(xs,26.1*get_br(xs,gsm=1.,gdm=0.5,mmed=450,scalar=False),label=r"pseudo, $g_\mathrm{DM}=$0.5",linewidth=2.,color="C3",linestyle="--")

ax.set_title("$m_\mathrm{scalar/pseudo}=$450 GeV")
ax.set_xlabel(r"$m_\mathrm{DM}$ (GeV)")
ax.set_ylabel(r"$\sigma\times\mathrm{BR}(\phi / a \rightarrow t\bar{t})$ (fb)")

# ax.yaxis.set_minor_locator(MultipleLocator(25.))
ax.xaxis.set_minor_locator(MultipleLocator(10))
# utils.add_cms_info(ax, lumi="137")

ax.legend()

fig.set_tight_layout(True)
fname = "plots/plot_dm_formula.png"
fig.savefig(fname)
fig.savefig(fname.replace(".png",".pdf"))
os.system("ic "+fname)



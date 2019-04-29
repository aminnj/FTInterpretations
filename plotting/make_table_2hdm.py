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

# xsec cols already have br multiplied in
dfc = pd.read_json("xsecs_2hdm.json")

# x = (dfc[(dfc.tanbeta == 1.) & (dfc.mass==530.)]["xsec_thq"].values*1000.)[0]

def roundnum(x):
    if 100.0 <= x < 1e6:
        return "{:g}".format(float("{:.3g}".format(x)))
    if 10.0 <= x < 100.0:
        return "{:.1f}".format(x)
    if 1.0 <= x < 10.0:
        return "{:.2f}".format(x)
    else:
        return "{:.3f}".format(x)

# def roundnum(x):
#     # return "{:g}".format(float("{:.3g}".format(x)))
#     return "{:.3g}".format(x)

# sys.exit()

# print dfc

cnames = [
    "xsec_tth",
    "xsec_thw",
    "xsec_thq",
    "xsec_tta",
    "xsec_taw",
    "xsec_taq",
    # "xsec_h",
    # "xsec_a",
    ]

# def roundnum(x):
#     return "{:g}".format(float("{:.3g}".format(x)))

names = [
        "xsec_tth",
        "xsec_thw",
        "xsec_thq",
        "xsec_tta",
        "xsec_taw",
        "xsec_taq",
        # "xsec_h",
        # "xsec_a",
        ]



buff = ""
# buff += " & ".join(cnames)
buff += r"""
\begin{table}[h]
\footnotesize
\begin{center}
\caption{\label{tab:thdm_xsec} Cross sections for the case of scalar (H) and pseudoproduction (A), assuming a heavy higgs boson with SM-like top quark couplings.}
\resizebox{0.5\textwidth}{!}{
    % \begin{tabular}{|c|c|ccc|ccc|}
    \begin{tabular}{|c|c|ccc|ccc||c|c|ccc|ccc|}
    \hline
"""
# buff += r"$\tan\beta$ & m [\GeV] & $\sigma_{ttH}$ [fb] & $\sigma_{tWH}$ [fb] & $\sigma_{tqH}$ [fb] & $\sigma_{ttA}$ [fb] & $\sigma_{tWA}$ [fb] & $\sigma_{tqA}$ [fb] \\ \hline"
# buff += r"$\tan\beta$ & mass & $\sigma_{ttH}$  & $\sigma_{tWH}$  & $\sigma_{tqH}$  & $\sigma_{ttA}$  & $\sigma_{tWA}$  & $\sigma_{tqA}$  \\ \hline"
buff += r"$\tan\beta$ & mass & $\sigma_{ttH}$  & $\sigma_{tWH}$  & $\sigma_{tqH}$  & $\sigma_{ttA}$  & $\sigma_{tWA}$  & $\sigma_{tqA}$ & $\tan\beta$ & mass & $\sigma_{ttH}$  & $\sigma_{tWH}$  & $\sigma_{tqH}$  & $\sigma_{ttA}$  & $\sigma_{tWA}$  & $\sigma_{tqA}$  \\ \hline"
buff += "\n"

# drop 0.2
tbs = sorted(dfc.tanbeta.unique())[1:]

tbpairs = zip(tbs[:-1:2],tbs[1::2])

# sys.exit()


# for itb,tb in enumerate(sorted(dfc.tanbeta.unique())):
for itb,(tb1,tb2) in enumerate(tbpairs):

    df1 = dfc[dfc["tanbeta"] == tb1]
    df1 = df1.sort_values("mass")
    df1.loc[:,cnames] *= 1000.
    dftab1 = df1.loc[:,["mass"]+cnames].reset_index()

    df2 = dfc[dfc["tanbeta"] == tb2]
    df2 = df2.sort_values("mass")
    df2.loc[:,cnames] *= 1000.
    dftab2 = df2.loc[:,["mass"]+cnames].reset_index()


    for idx,stuff in enumerate(np.c_[dftab1.values,dftab2.values]):
        mass = stuff[1]
        xsecs1 = stuff[2:2+len(cnames)]
        xsecs2 = stuff[4+len(cnames):]
        xsecs1 = map(roundnum,xsecs1)
        xsecs2 = map(roundnum,xsecs2)

        if idx == 0:
            buff += r"\multirow{{15}}{{*}}{{{}}} & ".format(str(tb1))
        else:
            buff += " & "
        buff += "{:.0f}".format(mass)
        buff += (" & {}"*len(cnames)).format(*xsecs1)

        buff += " & "

        if idx == 0:
            buff += r"\multirow{{15}}{{*}}{{{}}} & ".format(str(tb2))
        else:
            buff += " & "
        buff += "{:.0f}".format(mass)
        buff += (" & {}"*len(cnames)).format(*xsecs2)

        buff += " \\\\ \n"

    if itb <= 3:
        buff += r"\hline \hline"

    # if itb >= 2:
    #     break

buff += r"""
        \hline
        \end{tabular}
}
\end{center}
\end{table}
"""

print buff
with open("blah.tex","w") as fh:
    fh.write(buff)

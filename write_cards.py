import os
import itertools
from textwrap import dedent

def get_card_dmscalar(
        proc="ttbar",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        massmed = 300,
        massdm = 1,
        ):
    d_procstr = {
            "sttdm": "generate p p > t~ b chi~ chi j $$ w+ w-\nadd process p p > t b~ chi~ chi j $$ w+ w-",
            "stwdm": "generate p p > t w- chi~ chi /h\nadd process p p > t~ w+ chi~ chi /h",
            # "ttdm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttdm": "generate p p > t~ t chi~ chi",
            "sttsm": "generate p p > t~ b t~ t j $$ w+ w-\nadd process p p > t b~ t~ t j $$ w+ w-",
            "stwsm": "generate p p > t w- t~ t /h\nadd process p p > t~ w+ t~ t /h",
            # "ttsm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttsm": "generate p p > t~ t t~ t",
            }

    template = dedent("""
    set run_mode 2
    set nb_core {ncores}

    import model DMScalar

    define p = p b b~
    define j = p
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False
    set run_card maxjetflavor 4
    set param_card mass 9100000 {massmed}
    set param_card mass 9100022 {massdm}
    """)
    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            massmed=massmed,
            massdm=massdm,
            mgoutputname=mgoutputname,
            )

def get_card_dmpseudo(
        proc="ttbar",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        massmed = 300,
        massdm = 1,
        ):
    d_procstr = {
            "sttdm": "generate p p > t~ b chi~ chi j $$ w+ w-\nadd process p p > t b~ chi~ chi j $$ w+ w-",
            "stwdm": "generate p p > t w- chi~ chi /h\nadd process p p > t~ w+ chi~ chi /h",
            # "ttdm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttdm": "generate p p > t~ t chi~ chi",
            "sttsm": "generate p p > t~ b t~ t j $$ w+ w-\nadd process p p > t b~ t~ t j $$ w+ w-",
            "stwsm": "generate p p > t w- t~ t /h\nadd process p p > t~ w+ t~ t /h",
            # "ttsm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttsm": "generate p p > t~ t t~ t",
            }

    template = dedent("""
    set run_mode 2
    set nb_core {ncores}

    import model DMPseudo

    define p = p b b~
    define j = p
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False
    set run_card maxjetflavor 4
    set param_card mass 9100000 {massmed}
    set param_card mass 9100022 {massdm}
    """)
    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            massmed=massmed,
            massdm=massdm,
            mgoutputname=mgoutputname,
            )

def get_card_2hdm(
        proc="tth",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        mass = 125,
        tanbeta = 1.0,
        sinbma = 1.0,
        decouplemass = 10000,
        ):

    d_procstr = {
            "tth": "generate p p > tpm tpm h2",
            "thq": "generate p p > tpm qpm h2",
            "thw": "generate p p > tpm wpm h2",
            "tta": "generate p p > tpm tpm h3",
            "taq": "generate p p > tpm qpm h3",
            "taw": "generate p p > tpm wpm h3",
            }

    template = dedent("""

    set run_mode 2
    set nb_core {ncores}

    import 2HDMtII_NLO

    define p = p b b~
    define j = p
    define tpm = t t~
    define wpm = w+ w-
    define qpm = u c d s u~ c~ d~ s~ b b~
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False

    set param_card mass 25 125 # h1
    set param_card frblock 1 {tanbeta} # tanbeta
    set param_card frblock 2 {sinbma} # sinbma
    set param_card mass 35 {mass} # H2 / H
    set param_card mass 36 {mass} # H3 / A
    set param_card mass 37 {decouplemass} # charged Hpm

    """)

    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            mass=mass,
            sinbma=sinbma,
            tanbeta=tanbeta,
            decouplemass=decouplemass,
            mgoutputname=mgoutputname,
            )


def get_card_zprime(
        proc="tttt",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        mass = 125,
        gt = 1.0
        ):
    d_procstr = {
            "tttt": "generate p p > t~ t t~ t QED=2",
            }
    template = dedent("""
    set run_mode 2
    set nb_core {ncores}

    import model Zprime_UFO

    define p = p b b~
    define j = p
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False
    set param_card mass 9000005 {mass}
    set param_card ZPRIME 1 {gt}
    """)

    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            gt = gt,
            mass=mass,
            mgoutputname=mgoutputname,
            )


def get_card_phi(
        proc="tttt",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        mass = 125,
        gt = 1.0
        ):
    d_procstr = {
            "tttt": "generate p p > t~ t t~ t QED=2",
            }
    template = dedent("""
    set run_mode 2
    set nb_core {ncores}

    import model Phi_UFO

    define p = p b b~
    define j = p
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False
    set param_card mass 9000005 {mass}
    set param_card PHI 1 {gt}
    """)

    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            gt = gt,
            mass=mass,
            mgoutputname=mgoutputname,
            )

def write_card(s,fname,dryrun=False):
    if dryrun:
        print("Would write {}".format(fname))
        return
    with open(fname,"w") as fh:
        fh.write(s)

def get_card(model,**kwargs):
    if model == "phi":
        return get_card_phi(**kwargs)
    elif model == "zprime":
        return get_card_zprime(**kwargs)
    elif model == "2hdm":
        return get_card_2hdm(**kwargs)
    elif model == "dmscalar":
        return get_card_dmscalar(**kwargs)
    elif model == "dmpseudo":
        return get_card_dmpseudo(**kwargs)
    else:
        raise Exception("{} isn't a valid model".format(model))

if __name__ == "__main__":

    os.system("mkdir -p runs")

    model = "phi"
    carddir = "./runs/out_phi_scan_v1/"
    os.system("mkdir -p {}".format(carddir))
    proc = "tttt"
    for mass in [25,75,125,200,280,300,310,340]:
        for gt in [0.5,0.7,0.8,0.9,1.0,1.1,1.2,1.3]:
            tag = "{model}_{proc}_{mass}_{gt}".format(model=model,proc=proc,mass=mass,gt=str(gt).replace(".","p"))
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,gt=gt)
            write_card(buff,cardname,dryrun=False)

    model = "zprime"
    carddir = "./runs/out_zprime_scan_v1/"
    os.system("mkdir -p {}".format(carddir))
    proc = "tttt"
    vals = sum([
        list(itertools.product([25], [0.0,0.025,0.05,0.10,0.15,0.20])),
        list(itertools.product([50], [0.1,0.15,0.20,0.25,0.30,0.35])),
        list(itertools.product([75], [0.1,0.2,0.25,0.30,0.35,0.4,0.5])),
        list(itertools.product([100], [0.1,0.2,0.25,0.30,0.35,0.4,0.45,0.5,0.6])),
        list(itertools.product([125], [0.1,0.2,0.3,0.4,0.45,0.50,0.55,0.60,0.65,0.7])),
        list(itertools.product([175], [0.5,0.6,0.7,0.8,0.9,1.0])),
        list(itertools.product([200,225,250,275,300,325], [0.6,0.7,0.8,0.9,1.0,1.1])),
        list(itertools.product([315], [0.8,0.9,1.0])),
        list(itertools.product([340], [0.6,0.7,0.8,0.9,1.0])),
        ],[])
    for mass,gt in vals:
        tag = "{model}_{proc}_{mass}_{gt}".format(model=model,proc=proc,mass=mass,gt=str(gt).replace(".","p"))
        mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
        cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
        buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,gt=gt)
        write_card(buff,cardname,dryrun=False)

    model = "2hdm"
    carddir = "./runs/out_2hdm_scan_v1/"
    os.system("mkdir -p {}".format(carddir))
    for proc in ["tth","tta","thw","taw","thq","taq"]:
        for mass in range(350,650+20,20):
            for tanbeta in [0.2,0.5,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.5,3.0]:
                tag = "{model}_{proc}_{mass}_{tanbeta}".format(model=model,proc=proc,mass=mass,tanbeta=str(tanbeta).replace(".","p"))
                mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
                cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
                buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,decouplemass=10000,tanbeta=tanbeta)
                write_card(buff,cardname,dryrun=False)

    model = "dmscalar"
    carddir = "./runs/out_dmscalar_scan_v1/"
    os.system("mkdir -p {}".format(carddir))
    for proc in ["ttdm", "sttdm", "stwdm", "ttsm", "sttsm", "stwsm"]:
        for massmed,massdm in list(itertools.product(range(300,750,50),range(0,750,50))):
            massdm = max(massdm,1)
            tag = "{model}_{proc}_{massmed}_{massdm}".format(model=model,proc=proc,massmed=massmed,massdm=massdm)
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, massmed=massmed,massdm=massdm)
            write_card(buff,cardname,dryrun=False)

    model = "dmpseudo"
    carddir = "./runs/out_dmpseudo_scan_v1/"
    os.system("mkdir -p {}".format(carddir))
    for proc in ["ttdm", "sttdm", "stwdm", "ttsm", "sttsm", "stwsm"]:
        for massmed,massdm in list(itertools.product(range(300,750,50),range(0,750,50))):
            massdm = max(massdm,1)
            tag = "{model}_{proc}_{massmed}_{massdm}".format(model=model,proc=proc,massmed=massmed,massdm=massdm)
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, massmed=massmed,massdm=massdm)
            write_card(buff,cardname,dryrun=False)

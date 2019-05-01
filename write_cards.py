import os
import itertools
from textwrap import dedent

iseed = 0

def get_card_oblique(
        proc="tttt",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        hhat = 0.1,
        unique_seeds=False,
        ):
    global iseed
    seedstr = ""
    if unique_seeds:
        iseed += 1
        seedstr = "set run_card iseed {}".format(iseed)
    d_procstr = {
            "tttt": "generate p p > t~ t t~ t QED=2",
            "tth": "generate p p > t t~ h, (h > w+ w-, w+ > wprod wprod, w- > wprod wprod)",
            }
    template = dedent("""
    set auto_update 0
    set run_mode 2
    set nb_core {ncores}

    import model Oblique_UFO

    define p = p b b~
    define j = p

    define wprod = u d u~ d~
    {procstr}
    output {mgoutputname} -nojpeg
    launch
    set run_card ebeam1 6500.0
    set run_card ebeam2 6500.0
    set run_card nevents {nevents}

    set run_card use_syst False
    set param_card PROP 1 {hhat}
    {seedstr}
    """)

    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            hhat = hhat,
            mgoutputname=mgoutputname,
            seedstr=seedstr,
            )


def get_card_dmscalar(
        proc="ttbar",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        massmed = 300,
        massdm = 1,
        gdm = 1,
        gsm = 1,
        ):
    d_procstr = {
            "sttdm": "generate p p > t~ b chi~ chi j $$ w+ w-\nadd process p p > t b~ chi~ chi j $$ w+ w-",
            "stwdm": "generate p p > t w- chi~ chi /h\nadd process p p > t~ w+ chi~ chi /h",
            # "ttdm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttdm": "generate p p > t~ t chi~ chi",
            "sttsm": "generate p p > t~ b t~ t j $$ w+ w- NP==2\nadd process p p > t b~ t~ t j $$ w+ w- NP==2",
            "stwsm": "generate p p > t w- t~ t /h NP==2\nadd process p p > t~ w+ t~ t /h NP==2",
            # "ttsm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttsm": "generate p p > t~ t t~ t NP==2",
            }

    extraparams = dedent("""
    set run_card maxjetflavor 4
    set run_card pdlabel 'lhapdf'
    set run_card lhaid 263000
    """)
    if proc in ["sttsm","sttdm"]:
        extraparams = dedent("""
        set run_card maxjetflavor 4
        set run_card pdlabel 'lhapdf'
        set run_card lhaid 263400
        """)
    if proc in ["stwsm","stwdm"]:
        extraparams = dedent("""
        set run_card maxjetflavor 5
        set run_card pdlabel 'lhapdf'
        set run_card lhaid 263000
        """)

    template = dedent("""
    set auto_update 0
    set run_mode 2
    set nb_core {ncores}
    set lhapdf /cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/lhapdf6/6.1.5-cms/bin/lhapdf-config

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
    {extraparams}
    set param_card mass 9100000 {massmed}
    set param_card mass 9100022 {massdm}
    set param_card MEDCOUPLINGS 4 {gdm} # gDM
    set param_card MEDCOUPLINGS 5 {gsm} # gqq
    """)
    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            massmed=massmed,
            massdm=massdm,
            mgoutputname=mgoutputname,
            extraparams=extraparams,
            gdm=gdm,
            gsm=gsm,
            )

def get_card_dmpseudo(
        proc="ttbar",
        ncores=4,
        nevents=3000,
        mgoutputname="./runs/out_test_v1/test_v1",
        carddir="./runs/out_test_v1/",
        massmed = 300,
        massdm = 1,
        gdm = 1,
        gsm = 1,
        ):
    d_procstr = {
            "sttdm": "generate p p > t~ b chi~ chi j $$ w+ w-\nadd process p p > t b~ chi~ chi j $$ w+ w-",
            "stwdm": "generate p p > t w- chi~ chi /h\nadd process p p > t~ w+ chi~ chi /h",
            # "ttdm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttdm": "generate p p > t~ t chi~ chi",
            "sttsm": "generate p p > t~ b t~ t j $$ w+ w- NP==2\nadd process p p > t b~ t~ t j $$ w+ w- NP==2",
            "stwsm": "generate p p > t w- t~ t /h NP==2\nadd process p p > t~ w+ t~ t /h NP==2",
            # "ttsm": "generate p p > t~ t chi~ chi\nadd process p p > t~ t chi~ chi j",
            "ttsm": "generate p p > t~ t t~ t NP==2",
            }

    extraparams = dedent("""
    set run_card maxjetflavor 4
    set run_card pdlabel 'lhapdf'
    set run_card lhaid 263000
    """)
    if proc in ["sttsm","sttdm"]:
        extraparams = dedent("""
        set run_card maxjetflavor 4
        set run_card pdlabel 'lhapdf'
        set run_card lhaid 263400
        """)
    if proc in ["stwsm","stwdm"]:
        extraparams = dedent("""
        set run_card maxjetflavor 5
        set run_card pdlabel 'lhapdf'
        set run_card lhaid 263000
        """)

    template = dedent("""
    set auto_update 0
    set run_mode 2
    set nb_core {ncores}
    set lhapdf /cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/lhapdf6/6.1.5-cms/bin/lhapdf-config

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
    {extraparams}
    set param_card mass 9100000 {massmed}
    set param_card mass 9100022 {massdm}
    set param_card MEDCOUPLINGS 4 {gdm} # gDM
    set param_card MEDCOUPLINGS 5 {gsm} # gqq
    """)
    return template.format(
            ncores=ncores,
            nevents=nevents,
            procstr=d_procstr[proc],
            massmed=massmed,
            massdm=massdm,
            mgoutputname=mgoutputname,
            extraparams=extraparams,
            gdm=gdm,
            gsm=gsm,
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
        decay=False,
        unique_seeds=False,
        ):
    global iseed
    seedstr = ""
    if unique_seeds:
        iseed += 1
        seedstr = "set run_card iseed {}".format(iseed)

    if decay:
        d_procstr = {
                "tth": "generate p p > tpm tpm h2, h2 > tpm tpm",
                "thq": "generate p p > tpm qpm h2, h2 > tpm tpm",
                "thw": "generate p p > tpm wpm h2, h2 > tpm tpm",
                "tta": "generate p p > tpm tpm h3, h3 > tpm tpm",
                "taq": "generate p p > tpm qpm h3, h3 > tpm tpm",
                "taw": "generate p p > tpm wpm h3, h3 > tpm tpm",
                }
    else:
        d_procstr = {
                "tth": "generate p p > tpm tpm h2",
                "thq": "generate p p > tpm qpm h2",
                "thw": "generate p p > tpm wpm h2",
                "tta": "generate p p > tpm tpm h3",
                "taq": "generate p p > tpm qpm h3",
                "taw": "generate p p > tpm wpm h3",
                }

    template = dedent("""

    set auto_update 0
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
    set param_card decay 35 Auto
    set param_card decay 36 Auto
    {seedstr}

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
            seedstr=seedstr,
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
    set auto_update 0
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
    set auto_update 0
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
    elif model == "oblique":
        return get_card_oblique(**kwargs)
    else:
        raise Exception("{} isn't a valid model".format(model))

if __name__ == "__main__":

    do_phi = False
    do_zprime = False
    do_2hdm = False
    do_dmscalar = False
    do_dmpseudo = False
    do_oblique = False

    # testing stuff
    do_dm_test = True
    do_2hdm_decay = False
    do_oblique_manyevents = False
    do_oblique_run2 = False
    do_oblique_tth_test = False
    do_2hdm_decaytest = False
    do_2hdm_bigtest = False

    os.system("mkdir -p runs")

    if do_phi:
        model = "phi"
        carddir = "./runs/out_phi_scan_v1/"
        os.system("mkdir -p {}".format(carddir))
        proc = "tttt"
        vals = sum([
            list(itertools.product([25,75,125,200,280,300,310,340], [0.5,0.7,0.8,0.9,1.0,1.1,1.2,1.3])),
            list(itertools.product([25], [0.0])),
            ],[])
        for mass,gt in vals:
            tag = "{model}_{proc}_{mass}_{gt}".format(model=model,proc=proc,mass=mass,gt=str(gt).replace(".","p"))
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,gt=gt)
            write_card(buff,cardname,dryrun=False)

    if do_zprime:
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

    if do_2hdm:
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

    if do_dmscalar:
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

    if do_dmpseudo:
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

    if do_oblique:
        model = "oblique"
        carddir = "./runs/out_oblique_scan_v1/"
        os.system("mkdir -p {}".format(carddir))
        proc = "tttt"
        hhats = [0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.1, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.22, 0.25]
        for hhat in hhats:
            tag = "{model}_{proc}_{hhat}".format(model=model,proc=proc,hhat=str(hhat).replace(".","p"))
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, hhat=hhat)
            write_card(buff,cardname,dryrun=False)

    if do_oblique_manyevents:
        model = "oblique"
        carddir = "./runs/out_obliquemanyevents_scan_v1/"
        os.system("mkdir -p {}".format(carddir))
        proc = "tttt"
        hhats = [0.0, 0.1, 0.15]
        for hhat in hhats:
            tag = "{model}_{proc}_{hhat}".format(model=model,proc=proc,hhat=str(hhat).replace(".","p"))
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=10,nevents=50000,proc=proc,mgoutputname=mgoutputname,carddir=carddir, hhat=hhat)
            write_card(buff,cardname,dryrun=False)

    if do_oblique_run2:
        model = "oblique"
        for year in [2016,2017,2018]:
            carddir = "./runs/out_obliqueyear{}_scan_v2/".format(year)
            os.system("mkdir -p {}".format(carddir))
            proc = "tttt"
            hhats = [0.0,0.04,0.08,0.12,0.16]
            for hhat in hhats:
                tag = "{model}_{proc}_{hhat}".format(model=model,proc=proc,hhat=str(hhat).replace(".","p"))
                mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
                cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
                buff = get_card(model=model,ncores=3,nevents=50000,proc=proc,mgoutputname=mgoutputname,carddir=carddir, hhat=hhat,unique_seeds=True)
                write_card(buff,cardname,dryrun=False)

    if do_oblique_tth_test:
        model = "oblique"
        # carddir = "./runs/out_oblique_scan_tthytprop_v1/" # NOTE this has one (1-hhat) term for a single yt, and also propagator modification
        carddir = "./runs/out_oblique_scan_tthyt_v1/" # NOTE this has one (1-hhat) term for a single yt, and NO other propagator modification
        os.system("mkdir -p {}".format(carddir))
        proc = "tth"
        hhats = [0.0, 0.02, 0.05, 0.08, 0.1, 0.13, 0.15, 0.18, 0.2, 0.25]
        for hhat in hhats:
            tag = "{model}_{proc}_{hhat}".format(model=model,proc=proc,hhat=str(hhat).replace(".","p"))
            mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
            cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
            buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, hhat=hhat)
            write_card(buff,cardname,dryrun=False)

    if do_dm_test:
        for model in ["dmpseudo","dmscalar"]:
            # model = "dmpseudo"
            # carddir = "./runs/out_{}_scan_v3/".format(model)
            # os.system("mkdir -p {}".format(carddir))
            # for proc in ["ttdm", "sttdm", "stwdm", "ttsm", "sttsm", "stwsm"]:
                # for massmed,massdm in list(itertools.product([300,350,400,450,500,600,700],[1,50,100,150,300,500,750])):
            # carddir = "./runs/out_{}_scan_v4/".format(model)
            # gdm = 1
            # gsm = 1
            carddir = "./runs/out_{}_scan_v5/".format(model)
            gdm = 0.5
            gsm = 1
            os.system("mkdir -p {}".format(carddir))
            for proc in ["ttsm", "sttsm", "stwsm"]:
                # for massmed,massdm in (
                #         list(itertools.product([350,370,390,410,430,450,470,490,530],[1,100,200,250,300,600])) +
                #         list(itertools.product([570,650],[1,200,300,600])) +
                #         list(itertools.product([350,370,390,410,430],[150])) +
                #         list(itertools.product([510],[250,300,600])) +
                #         list(itertools.product([550],[300,600]))
                #         ):
                for massmed,massdm in (
                        list(itertools.product([350,370,390,410,430,450,470,490,530],[1,100,200,600])) +
                        list(itertools.product([350,370,390,410,430,470,490,530],[50])) +
                        list(itertools.product([490,530,570,650],[1,200,300,600])) +
                        list(itertools.product([350,370,390,410,430,450,470,490,510],[150])) +
                        list(itertools.product([550,590],[300,600])) +
                        list(itertools.product([510],[250,300,600])) +
                        list(itertools.product([450,470,490,530],[250])) +
                        list(itertools.product([450,470],[300]))
                        ):
                    massdm = max(massdm,1)
                    tag = "{model}_{proc}_{massmed}_{massdm}".format(model=model,proc=proc,massmed=massmed,massdm=massdm)
                    mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
                    cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
                    buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, massmed=massmed,massdm=massdm,gdm=gdm,gsm=gsm)
                    write_card(buff,cardname,dryrun=False)

    if do_2hdm_decaytest:
        model = "2hdm"
        carddir = "./runs/out_2hdm_decay_scan_v2/"
        os.system("mkdir -p {}".format(carddir))
        for proc in ["tth","tta","thw","taw","thq","taq"]:
            for mass in range(350,650+20,20):
                for tanbeta in [0.2,0.5,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.5,3.0]:
                    tag = "{model}_{proc}_{mass}_{tanbeta}".format(model=model,proc=proc,mass=mass,tanbeta=str(tanbeta).replace(".","p"))
                    mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
                    cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
                    buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,decouplemass=10000,tanbeta=tanbeta,decay=True)
                    write_card(buff,cardname,dryrun=False)

    if do_2hdm_bigtest:
        model = "2hdm"
        carddir = "./runs/out_2hdm_bigdecay_scan_v2/"
        os.system("mkdir -p {}".format(carddir))
        mass = 450
        tanbeta = 1.0
        for run in range(1,15+1):
            for proc in ["tth","tta"]:
                tag = "{model}_{proc}_{mass}_{tanbeta}_{run}".format(model=model,proc=proc,mass=mass,tanbeta=str(tanbeta).replace(".","p"),run=run)
                mgoutputname = "{carddir}/{tag}".format(carddir=carddir,tag=tag)
                cardname = "{carddir}/proc_card_{tag}.dat".format(carddir=carddir,tag=tag)
                buff = get_card(model=model,ncores=3,proc=proc,mgoutputname=mgoutputname,carddir=carddir, mass=mass,decouplemass=10000,tanbeta=tanbeta,decay=True,nevents=100000,unique_seeds=True)
                write_card(buff,cardname,dryrun=False)

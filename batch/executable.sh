#!/bin/bash

OUTPUTDIR=$1
PROCTAG=$2
CARDNAME=$3

export SCRAM_ARCH=slc6_amd64_gcc630
export CMSSWVERSION=CMSSW_9_4_9

function getjobad {
    grep -i "^$1" "$_CONDOR_JOB_AD" | cut -d= -f2- | xargs echo
}

echo -e "\n--- begin header output ---\n" #                     <----- section division

echo "OUTPUTDIR: $OUTPUTDIR"
echo "PROCTAG: $PROCTAG"
echo "CARDNAME: $CARDNAME"

echo "GLIDEIN_CMSSite: $GLIDEIN_CMSSite"
echo "hostname: $(hostname)"
echo "uname -a: $(uname -a)"
echo "time: $(date +%s)"
echo "args: $@"

echo -e "\n--- end header output ---\n" #                       <----- section division

if [ -r "$OSGVO_CMSSW_Path"/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSGVO_CMSSW_Path/cmsset_default.sh"
    source "$OSGVO_CMSSW_Path"/cmsset_default.sh
elif [ -r "$OSG_APP"/cmssoft/cms/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSG_APP/cmssoft/cms/cmsset_default.sh"
    source "$OSG_APP"/cmssoft/cms/cmsset_default.sh
elif [ -r /cvmfs/cms.cern.ch/cmsset_default.sh ]; then
    echo "sourcing environment: source /cvmfs/cms.cern.ch/cmsset_default.sh"
    source /cvmfs/cms.cern.ch/cmsset_default.sh
else
    echo "ERROR! Couldn't find $OSGVO_CMSSW_Path/cmsset_default.sh or /cvmfs/cms.cern.ch/cmsset_default.sh or $OSG_APP/cmssoft/cms/cmsset_default.sh"
    exit 1
fi

ls -l

tarfile=package.tar.xz
eval `scramv1 project CMSSW $CMSSWVERSION`
cd $CMSSWVERSION
eval `scramv1 runtime -sh`
if [ -e ../${tarfile} ]; then
    mv ../${tarfile} ${tarfile};
    tar xf ${tarfile};
    mv ../$CARDNAME .
fi

ls -l

# 1. we end up with $CARDNAME in the current directory
# 2. copy it into the CMSSW folder after checking it out
# 3. sed the card to output into the `out` folder, and also use ONE core
# 4. Run MG
# 5. Copy back lhe and html (containing xsec) to $OUTPUTDIR/$PROCTAG.{txt,lhe.gz}

echo -e "\n--- begin running ---\n" #                           <----- section division


export MGEXE=$(ls -1 MG5*/bin/mg5_aMC | tail -n 1)

sed -i 's#output .*#output out -nojpeg#' $CARDNAME
sed -i 's#set nb_core.*#set nb_core 1#' $CARDNAME

# Run madgraph
$MGEXE $CARDNAME

textfile=out/Events/run_01/run_01_tag_1_banner.txt
lhegzfile=out/Events/run_01/unweighted_events.lhe.gz

echo -e "\n--- end running ---\n" #                             <----- section division

echo -e "\n--- begin copying output ---\n" #                    <----- section division

echo "time before copy: $(date +%s)"

COPY_SRC="file://`pwd`/$textfile"
COPY_DEST="gsiftp://gftp.t2.ucsd.edu${OUTPUTDIR}/${PROCTAG}.txt"
echo "Running: env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}"
env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST} 

COPY_SRC="file://`pwd`/$lhegzfile"
COPY_DEST="gsiftp://gftp.t2.ucsd.edu${OUTPUTDIR}/${PROCTAG}.lhe.gz"
echo "Running: env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}"
env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST} 

echo -e "\n--- end copying output ---\n" #                      <----- section division

echo "time at end: $(date +%s)"


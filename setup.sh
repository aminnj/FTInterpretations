#!/usr/bin/env sh

CMSSW_RELEASE=CMSSW_9_4_9
SCRAM_ARCH=slc6_amd64_gcc630
latest="https://launchpad.net/mg5amcnlo/2.0/2.6.x/+download/MG5_aMC_v2.6.5.tar.gz"

if [ -z "$CMSSW_BASE" ];  then
    if [ -e /cvmfs/ ]; then
        source /code/osgcode/cmssoft/cms/cmsset_default.sh
        cd /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/$CMSSW_RELEASE
        eval `scramv1 runtime -sh`
        cd -
        export LANG=en_US.UTF-8
    fi
fi

export FTINTBASE="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"

# Add some scripts to the path
export PATH=${FTINTBASE}/scripts:$PATH

tarball=$(basename $latest)
mgdir=$(echo $tarball | sed -s 's/\.tar\.gz//' | sed -s 's/\./\_/g')
if [ ! -d $mgdir ]; then
    # Install and untar MG
    curl -O -L $latest
    tar -xvf $tarball
    rm $tarball
    # Apply MG patches
    patch -N -r - -d ${mgdir}/Template/LO/SubProcesses/ < patches/LOmakefile.patch
    # Copy over models
    cp -r models/* $mgdir/models/
fi

export MGEXE=$(ls -1 MG5*/bin/mg5_aMC | tail -n 1)
alias run="./$MGEXE"

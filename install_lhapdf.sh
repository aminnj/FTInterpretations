#!/usr/bin/env sh

export SCRAM_ARCH=slc6_amd64_gcc481
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_7_1_15_patch1/src ] ; then
 echo release CMSSW_7_1_15_patch1 already exists
else
scram p CMSSW CMSSW_7_1_15_patch1
fi
cd CMSSW_7_1_15_patch1/src
eval `scram runtime -sh`
cd -

pwd
mgexe=$(ls -1 MG5*/bin/mg5_aMC | tail -n 1)
LHAPDF6TOOLFILE=$CMSSW_BASE/config/toolbox/$SCRAM_ARCH/tools/available/lhapdf6.xml
if [ -e $LHAPDF6TOOLFILE ]; then
    LHAPDFCONFIG=`cat $LHAPDF6TOOLFILE | grep "<environment name=\"LHAPDF6_BASE\"" | cut -d \" -f 4`/bin/lhapdf-config
else
    LHAPDFCONFIG=`echo "$LHAPDF_DATA_PATH/../../bin/lhapdf-config"`
fi
#make sure env variable for pdfsets points to the right place
export LHAPDF_DATA_PATH=`$LHAPDFCONFIG --datadir`
LHAPDFINCLUDES=`$LHAPDFCONFIG --incdir`
LHAPDFLIBS=`$LHAPDFCONFIG --libdir`

echo "set auto_update 0"                  >  mgconfigscript
echo "set automatic_html_opening False"   >> mgconfigscript
echo "set output_dependencies internal"   >> mgconfigscript
echo "set lhapdf $LHAPDFCONFIG"           >> mgconfigscript
echo "set run_mode 2" >> mgconfigscript
echo "save options" >> mgconfigscript
$mgexe mgconfigscript

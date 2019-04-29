#!/usr/bin/env sh


basedirs=$@
if [ -z "$basedirs" ] ; then
    echo "Need base directory/directories containing the cards"
    exit
fi
if ! ls -1d $basedirs >& /dev/null ; then
    echo "Need *valid* base directory/directories containing the cards"
    exit
fi
for basedir in $basedirs ; do
    logdir=$basedir/logs/
    exe=$(ls -1 MG5*/bin/mg5_aMC | tail -n 1)
    mkdir -p $logdir
    for card in `ls ${basedir}/proc*.dat`; do
        # logname=$(basename $card) # basename is slow
        logname=${card##*/}
        logname=${logname%.*}.log 
        if [ -e $logdir/$logname ] ; then
            if grep --quiet "INFO: Done" $logdir/$logname ; then
                continue
            fi
        fi
        echo "./${exe} $card >& $logdir/$logname"
    done
done

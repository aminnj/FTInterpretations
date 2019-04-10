#!/usr/bin/env sh

# XZ_OPT=-9 
XZ_OPT=-9 tar -Jch \
    --exclude='*/tests/*' \
    --exclude='*/MSSM_SLHA2/*' \
    --exclude='doc.tgz' \
    --exclude-vcs \
    -f package.tar.xz MG5_aMC_v2_6_5/

ls -lh package.tar.xz


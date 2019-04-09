#!/usr/bin/env sh

grep "./HTML/run_01/results.html" runs/*/*/crossx.html > data.txt
wc -l data.txt

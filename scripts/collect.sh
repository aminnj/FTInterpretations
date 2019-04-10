#!/usr/bin/env sh

# grep "./HTML/run_01/results.html" runs/*/*/crossx.html > data.txt
grep "Integrated weight" runs/*/*/Events/run_01/run_01_tag_1_banner.txt > data.txt
grep "Integrated weight" /hadoop/cms/store/user/namin/batch_madgraph//*_v1/*.txt >> data.txt
wc -l data.txt

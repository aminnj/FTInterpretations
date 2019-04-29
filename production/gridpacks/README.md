## CMSSW production

### Making gridpacks

We will make gridpacks with [this script](https://github.com/cms-sw/genproductions/blob/master/bin/MadGraph5_aMCatNLO/gridpack_generation.sh) 
from the master branch of cms-sw/genproductions, following the suggestions from [this Twiki](https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO).
Minimal instructions follow.

```bash
# Fork the cms-sw/genproductions repository and then clone your fork
git clone git@github.com:aminnj/genproductions.git
# Go to the relevant directory
cd genproductions/bin/MadGraph5_aMCatNLO/
```

Since I needed to use a custom MadGraph UFO model, I had to apply the following one-liner patch to `wget` it from a web area I control
instead of a central location (where I think the model will have to be uploaded in the end anyway).
```diff
diff --git a/bin/MadGraph5_aMCatNLO/gridpack_generation.sh b/bin/MadGraph5_aMCatNLO/gridpack_generation.sh
old mode 100644
new mode 100755
index 171e66f73..85541280b
--- a/bin/MadGraph5_aMCatNLO/gridpack_generation.sh
+++ b/bin/MadGraph5_aMCatNLO/gridpack_generation.sh
@@ -193,7 +193,7 @@ make_gridpack () {
           #get needed BSM model
           if [[ $model = *[!\ ]* ]]; then
             echo "Loading extra model $model"
-            wget --no-check-certificate https://cms-project-generators.web.cern.ch/cms-project-generators/$model
+            wget --no-check-certificate http://uaf-8.t2.ucsd.edu/~namin/dump/top_run2/production/oblique/$model
             cd models
             if [[ $model == *".zip"* ]]; then
               unzip ../$model
```

Next, you will need to set up a directory with cards following the structure in this commit of the cards 
to my private aminnj/genproductions repository [here](https://github.com/aminnj/genproductions/commit/fa7551a7cf7e75f039551ccba511eecae3da034c).
In order to minimize crashes, try to follow the structure exactly and make sure process names (in the example case,`TTTT_hhat_0p0` and others) 
are consistent in the folder name, the proc card name, and the `output <X> -nojpeg` line.

Finally, once all the delicate pieces are secured with duct tape, try running
```bash
pname=TTTT_hhat_0p08
./gridpack_generation.sh ${pname} cards/production/2017/13TeV/ObliqueHiggs/${pname}/
```
in a clean environment (no CMSSW, so you might have to re-ssh). If all goes well, you'll get a `.xz` gridpack that should be bigger than approximately 40MB (well,
in my case, when things failed, I got around 11MB). 


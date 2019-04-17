## Four top interpretations

Hosts MadGraph models and setup for various interpretations:
* two Higgs doublet models
* simplified dark matter models
* off-shell vector boson (zprime) and scalar boson (phi)
* EFT $\hat H$ modifications to the scalar higgs boson propagator

### Set up the environment

Need to `source setup.sh` every time to get an environment. The first time, it will
download and set up MadGraph

If you plan to use a pdf from lhapdf, you need to `./install_lhapdf.sh` once
and then before running cards, need to use a slightly different environment
with respect to what `source setup.sh` gives you, so do `source setup_lhapdf.sh`.
Sigh...CMSSW gymnastics.

### Write proc cards

Edit `write_cards.py` to your hearts content, then `python write_cards.py` will
put them into a `runs` directory.

### Get commands to run MG

Execute `make_commands.sh runs/*` (or any valid globber) to print out a list of
commands to run over the cards in the specified folders. Redirect it into a
file and potentially delete things you don't care about:
`make_commands.sh runs/* > commands.txt`.

### Use GNU parallel to actually run MG

When setting the `--jobs` parameter, be mindful that MG will spawn multiple
processes per card (3 by default in `write_cards.py`). `--shuf` mixes things
up. 
```bash
parallel --nice 10 --jobs 10 --bar --shuf --joblog joblog.txt < commands.txt
```

### Collect outputs

`collect.sh` will grep for cross-sections and write out `data.txt` with folder names and cross-sections.

### Clean up

If you're only interested in cross-sections, use `cleanup.sh` every now and
then to delete large files inside `runs/` (or else running on thousands of
cards adds up to hundreds of GB).

### Plotting

`cd plotting/` and see instructions there.

### Running cards with condor

Make a tarball of the MadGraph directory with `make_tar.sh`, then `cd batch/` and follow instructions there.

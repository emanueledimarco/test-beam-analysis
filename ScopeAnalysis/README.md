# Analysis of oscilloscope pulses
Tools to make a statistical analysis of pulse recorded at BTF in July 2017

Uses data from G. Mazzitelli's Mac disc, mounted on a Mac

## How to make plots of single pulses

To plot a single pulse, run the script on the single txt file of the scope:

   python txt2pulse.py /Volumes/Cygnus/Data/BTF_2017-2/Data_Scope/Run206/C3Run00072.txt --ngroup=100

The most relevant option is:
* the `--ngroup` option is used to average over ngroup samples registered by the oscilloscope


## How to run the reconstruction of multiple runs 

This is to run over multiple runs, where in each run N "events" (pulse shapes) are recorded. By default it analyzes 100 events for each run.
It looks for peaks of the three saved channels (PMT,BTF Calo,BTF trigger) saving:
* the time of the BTF trigger
* the time and amplitude of the BTF calorimeter
* the times and amplitudes of the PMT as an array
Run:

   python process_data.py /Volumes/Cygnus/Data/BTF_2017-2/Data_Scope/ --rmin=206 --rmax=214 --ngroup=100

where the parameters are:
* `--rmin`: the minimum run number to analyze
* `--rmax`: the maximim run number to analyze
* `--ngroup` is used to average over ngroup samples registered by the oscilloscope

Note that something is hardcoded: 
* the minimal amplitude used to define a peak of the PMT is 0.005V 
* the noise (computed as the RMS of the pedestal) is computed with the first 10 samples of the scope, and the cut is >3 sigma noise

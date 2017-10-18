#! /usr/bin/python

import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from reconstruction import *

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] DIR ")
    addTxt2PulseOptions(parser)
    parser.add_option("--rmin", dest="runMin", type="int", default=None, help="min run number to analyze");
    parser.add_option("--rmax", dest="runMax", type="int", default=None, help="max run number to analyze");
    parser.add_option("-o","--out", dest="outFile", type="string", default="reco.root", help="name of the output root file");

    (options, args) = parser.parse_args()
    if len(args)<1:
        parser.print_help()
        sys.exit(1)

    runs_dir = args[0]
    subdirs = [runs_dir+"/"+dir for dir in os.listdir(runs_dir) if 'Run' in dir]
    rmin = options.runMin if options.runMin else -1
    rmax = options.runMax if options.runMax else 99999

    selected_runs = []
    for s in subdirs:
        run = int((os.path.basename(s).split('Run')[-1]).lstrip('0'))
        if rmin<=run and run<=rmax:  selected_runs.append(s)
        
    print "Will run on the following runs: ", selected_runs
    
    p=PulseReconstruction(selected_runs,options=options,outputFileName=options.outFile)
    p.run()

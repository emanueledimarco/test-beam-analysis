#! /usr/bin/python

import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from output import OutputTree
from txt2pulse import PulseTxtFile

class PulseReconstruction:
    def __init__(self,dirs,nchunks=100,outputFileName="reco.root",options=None):
        self.runs=dirs
        self.nchunks=nchunks
        self.outputFileName=outputFileName
        self.options=options
    def beginJob(self,outTree):
        outTree.branch("run", "I")
        outTree.branch("event", "I")
        outTree.branch("amplitude_calo", "F")
        outTree.branch("time_calo", "F")
        outTree.branch("time_btf", "F")
        outTree.branch("amplitude_pmt", "F", lenVar="nPeaks")
        outTree.branch("time_pmt", "F", lenVar="nPeaks")
    def endJob(self,outTree,outFile):
        pass
    def run(self):
        # prepare output file
        outputFile = ROOT.TFile.Open(self.outputFileName, "RECREATE")
        # prepare output tree
        outputTree = ROOT.TTree("Events","Tree containing reconstructed pulses")
        
        outTree = OutputTree(outputFile,outputTree)
        self.beginJob(outTree)

        for run in self.runs:
            runi = int((os.path.basename(run).split('Run')[-1]).lstrip('0'))
            for chunk in xrange(self.nchunks):
                outTree.fillBranch("run",runi)
                outTree.fillBranch("event",chunk)
                for ic,channel in enumerate(['C1','C3','C4']):
                    inputf = "%s/%sRun%05d.txt"  % (run,channel,chunk)
                    print "Analyzing pulse from ",inputf
                    pulse = PulseTxtFile(inputf,self.options)
                    if channel=='C1': 
                        outTree.fillBranch("time_btf",pulse.time())
                    elif channel=='C4':
                        outTree.fillBranch("amplitude_calo",pulse.amplitude())
                        outTree.fillBranch("time_calo",pulse.time())
                    else:
                        outTree.fillBranch("amplitude_pmt",pulse.amplitudes())
                        outTree.fillBranch("time_pmt",pulse.times())
                outTree.fill()

        outTree.write()
        outputFile.Close()


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
        outTree.branch("run", "I", n=1)
        outTree.branch("event", "I", n=1)
        outTree.branch("amplitude", "F", n=3)
        outTree.branch("time", "F", n=3)
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
                amplitude=[]; time=[];
                for ic,channel in enumerate(['C1','C3','C4']):
                    inputf = "%s/%sRun%05d.txt"  % (run,channel,chunk)
                    print "Analyzing pulse from ",inputf
                    pulse = PulseTxtFile(inputf,self.options)
                    amplitude.append(pulse.amplitude())
                    time.append(pulse.time())
                outTree.fillBranch("run",runi)
                outTree.fillBranch("event",chunk)
                outTree.fillBranch("amplitude",amplitude)
                outTree.fillBranch("time",time)
                outTree.fill()

        outTree.write()
        outputFile.Close()


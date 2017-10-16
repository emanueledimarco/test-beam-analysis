#! /usr/bin/python

import sys
args = sys.argv[:]
sys.argv = ['-b']
import ROOT
sys.argv = args
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

class PulseReconstruction:
    def __init__(self,runMin,runMax,nchunks=100,outputFileName="reco.root",options=None):
        self.runMin=runMin
        self.runMax=runMax
        self.outputFileName=outputFileName

    def beginJob(self,outTree):
        outTree.branch("run", "I", n=1)

    def endJob(self,outTree,outFile):
        

    def run(self):
        # prepare output file
        outputFile = ROOT.TFile.Open(self.outputFileName, "RECREATE")
        # prepare output tree
        outputTree = ROOT.TTree(treeName,"Tree containing reconstructed pulses")
        
        outTree = OutputTree(outFile,outputTree)
        self.beginJob(outTree)

        for e in xrange(10):
            outTree.fillBranch("run",345)
            if True: # put here cuts
                outTree.fill()

        outTree.write()
        outputFile.Close()


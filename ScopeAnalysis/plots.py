#! /usr/bin/python

## safe batch mode                                                                                                                                                                                                                           
import sys
args = sys.argv[:]
sys.argv = ['-b']
import ROOT
sys.argv = args
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PlotUtils import customROOTstyle

_xpos = { 206:294.2, 207:314.2, 208:334.2, 209:354.2, 210:374.2, 211:394.2, 212:414.2, 213:434.2, 214:454.2 }

class PlotMaker:
    def __init__(self,infile,options=None):
        self.infile=infile
        self.options=options
    def beginJob(self):
        self.tfile = ROOT.TFile.Open(self.infile)
        self.tree = self.tfile.Get("Events")
        
    def endJob(self):
        self.tfile.Close()

    def secondaryArrivalTime(self):
        gr = ROOT.TGraphErrors(len(_xpos))
        point=0
        for run,xpos in _xpos.iteritems():
            cut = "nPeaks==2 && run==%d" % run
            print cut
            h_dt = ROOT.TH1D("h_dt","h_dt",200,10,100)
            self.tree.Draw("amplitude_pmt[1]-amplitude_pmt[0]>>h_dt",cut)
            mean,rms = h_dt.GetMean(),h_dt.GetRMS()
            print xpos,"  ",mean
            gr.SetPoint(point,xpos,mean)
            gr.SetPointError(point,0,rms)
        c1 = ROOT.TCanvas("dist_canvas","dist",600,600)
        gr.Draw("APE")
        c1.Print("distance.pdf")

if __name__ == "__main__":

    pm = PlotMaker("reco_all.root")
    pm.beginJob()
    pm.secondaryArrivalTime()
    pm.endJob()


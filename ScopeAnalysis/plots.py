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
        gr.SetTitle("")
        point=0
        for run,xpos in _xpos.iteritems():
            cut = "nPeaks==2 && run==%d" % run
            if ROOT.gROOT.FindObject("h_dt") != None: ROOT.gROOT.FindObject("h_dt").Delete()
            h_dt = ROOT.TH1D("h_dt","h_dt",200,10,100)
            self.tree.Draw("time_pmt[1]-time_pmt[0]>>h_dt",cut)
            mean,rms = h_dt.GetMean(),h_dt.GetRMS()
            gr.SetPoint(point,xpos,mean)
            gr.SetPointError(point,0,rms)
            point +=1
        c1 = ROOT.TCanvas("dist_canvas","dist",600,600)
        ROOT.gStyle.SetOptFit(11111)
        gr.SetMarkerStyle(21)
        gr.SetMarkerSize(0.4)
        gr.Draw("APE")
        gr.GetXaxis().SetNdivisions(510)
        gr.GetXaxis().SetTitleFont(42)
        gr.GetXaxis().SetTitleSize(0.05)
        gr.GetXaxis().SetTitleOffset(0.9)
        gr.GetXaxis().SetLabelFont(42)
        gr.GetXaxis().SetLabelSize(0.05)
        gr.GetXaxis().SetLabelOffset(0.007)
        gr.GetYaxis().SetTitleFont(42)
        gr.GetYaxis().SetTitleSize(0.05)
        gr.GetYaxis().SetTitleOffset(0.9)
        gr.GetYaxis().SetLabelFont(42)
        gr.GetYaxis().SetLabelSize(0.05)
        gr.GetYaxis().SetLabelOffset(0.007)
        gr.GetXaxis().SetTitle("x position [cm]")
        gr.GetYaxis().SetTitle("PMT #Deltat [ns]")
        gr.Fit("pol1")
        gr.Draw("APE")

        c1.Print("distance.pdf")

if __name__ == "__main__":

    pm = PlotMaker("reco.root")
    pm.beginJob()
    pm.secondaryArrivalTime()
    pm.endJob()


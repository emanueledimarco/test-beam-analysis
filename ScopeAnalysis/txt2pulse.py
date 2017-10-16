#! /usr/bin/python

from math import *
import re
import os, os.path
from array import array

from PlotUtils import customROOTstyle

## safe batch mode                                                                                                                                                                                                                           
import sys
args = sys.argv[:]
sys.argv = ['-b']
import ROOT
sys.argv = args
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

class PulseTxtFile:
    def __init__(self,txtFile,options=None):
        if "C3" in txtFile: self.channel = "PMT"
        elif "C4" in txtFile: self.channel = "calorimeter"
        else: self.channel = "Unknown"
        self.x = []
        self.y = []
        file = open(txtFile,"r")
        if not file: raise RuntimeError, "Cannot open "+txtFile+"\n"
        for line in file:
          try:
            line = line.strip()
            if len(line) == 0 or line[0] == '"': continue
            fields = line.split()
            self.x.append(10e6*float(fields[0]))
            self.y.append(float(fields[1]))
          except ValueError:
              print "Error parsing cut line [%s]" % line.strip()
              raise
        self.options = options

    def getPulse(self,averageNsamples=None):
        if averageNsamples:
            xav=[]; yav=[]
            i=0
            for i in xrange(0,len(self.x),averageNsamples):
                imin=i
                imax=min(i+averageNsamples,len(self.x)-1)
                xav.append(0.5*(self.x[imin]+self.x[imax]))
                yav.append(sum(self.y[imin:imax])/len(self.y[imin:imax]))
                #print "averaging imin=%d,imax=%d,xav=%f,yav=%f" % (imin,imax,xav[-1],yav[-1])
            pulse = ROOT.TGraph(len(xav),array('f',xav),array('f',yav))
        else:
            pulse = ROOT.TGraph(len(self.x),array('f',self.x),array('f',self.y))
        pulse.SetName(""); pulse.SetTitle("")
        return pulse

    def plot(self,saveName,doWide=False,extensions="pdf"):
        plotformat = (1200,600) if doWide else (600,600)
        sf = 20./plotformat[0]
        height=plotformat[1]
        ROOT.gStyle.SetPadLeftMargin(600.*0.18/plotformat[0])
        ROOT.gStyle.SetPaperSize(20.,sf*plotformat[1])
        customROOTstyle()
        c1 = ROOT.TCanvas(saveName+"_canvas",saveName,plotformat[0],height)
        g = self.getPulse(options.ngroup)
        colors = {"calorimeter":ROOT.kRed, "PMT":ROOT.kBlue} 
        g.SetLineColor(colors[self.channel])
        g.Draw("AL")
        g.GetXaxis().SetTitle("time (ns)")
        g.GetYaxis().SetTitle("Amplitude %s (V)" % self.channel)
        g.Draw("L")
        for ext in extensions.split(","):
            c1.Print("%s_%s.%s"%(saveName,self.channel,ext))

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file.txt")
    parser.add_option("--print", dest="printPlots", type="string", default="png,pdf,txt", help="print out plots in this format or formats (e.g. 'png,pdf,txt')");
    parser.add_option("--ngroup", dest="ngroup", type=int, default=1, help="average the pulse every ngroup samples");

    (options, args) = parser.parse_args()
    PulsePlot = PulseTxtFile(args[0],options)
    ext = options.printPlots 
    tokens = args[0].split("/")
    run = tokens[-2]
    chunk = tokens[-1].split("Run")[-1].split(".")[0]
    print "run=%s, chunk=%s" % (run,chunk)
    PulsePlot.plot("pulse_run%s_chunk%s" %(run,chunk),ext)

#! /usr/bin/python

from math import *
import re, os, os.path, operator
from array import array
import numpy as np

from PlotUtils import customROOTstyle

## safe batch mode                                                                                                                                                                                                                           
import sys
args = sys.argv[:]
sys.argv = ['-b']
import ROOT
sys.argv = args
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

class GraphVal:
    def __init__(self,x,y,w=0):
        self.x=x
        self.y=y
        self.width=w

class PulseTxtFile:
    def __init__(self,txtFile,options=None):
        if "C3" in txtFile: self.channel = "PMT"
        elif "C1" in txtFile: self.channel = "BTF"
        elif "C4" in txtFile: self.channel = "calorimeter"
        else: self.channel = "Unknown"
        self.x = []
        self.y = []
        file = open(txtFile,"r")
        if not file: 
            self.validpulse = False
            raise RuntimeError, "Cannot open "+txtFile+"\n"
        for line in file:
          try:
            line = line.strip()
            if len(line) == 0 or line[0] == '"': continue
            fields = line.split()
            self.x.append(10e6*float(fields[0]))
            self.y.append(float(fields[1]))
            self.validpulse=True
          except ValueError:
              print "Error parsing cut line [%s]" % line.strip()
              self.validpulse=False
              raise
        self.options = options

    def getPulse(self,averageNsamples=None):
        if not self.validpulse: return None
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
            pedestal = 0.5*(yav[0]+yav[-1])
            self.xy=[GraphVal(xav[i],yav[i]-pedestal) for i in xrange(len(xav))]
            yredge = np.array([point.y for point in self.xy[:3]]) # dangerous if the signal is not very centered! find a better way
            self.noise = np.sqrt(np.mean(yredge**2))
        else:
            pulse = ROOT.TGraph(len(self.x),array('f',self.x),array('f',self.y))
            pedestal = 0.5*(self.y[0]+self.y[-1])
            self.xy=[GraphVal(self.x[i],self.y[i]-pedestal) for i in xrange(len(self.x))]
            yredge = np.array(self.y[:3]) # dangerous if the signal is not very centered! find a better way
            self.noise = np.sqrt(np.mean(yredge**2))
        pulse.SetName(""); pulse.SetTitle("")
        self.pulse = pulse
        return pulse

    def amplitude(self):
        if not hasattr(self,'pulse'): self.getPulse(self.options.ngroup)
        sortedvals = sorted(self.xy, key = lambda point : point.y)
        return sortedvals[0].y

    def time(self):
        if not hasattr(self,'pulse'): self.getPulse(self.options.ngroup)
        sortedvals = sorted(self.xy, key = lambda point : point.y)
        return sortedvals[0].x

    def amplitudes(self):
        if not hasattr(self,'peaks'): self.getPeaks()
        return [peak.y for peak in self.peaks]

    def times(self):
        if not hasattr(self,'peaks'): self.getPeaks()
        return [peak.x for peak in self.peaks]

    def getPeaks(self):
        peaks=[]
        if not hasattr(self,'pulse'): self.getPulse(self.options.ngroup)
        localmin=GraphVal(-1000,1000)
        onPeak=False
        sampleWidth=self.xy[1].x-self.xy[0].x
        for i,point in enumerate(self.xy):
            if abs(point.y)>max(3.*self.noise,self.options.minampl) and point.y<localmin.y: 
                localmin.x=point.x; localmin.y=point.y;
                localmin.width = localmin.width+sampleWidth
                onPeak=True
            if abs(point.y)<min(self.options.minampl,3*self.noise) and onPeak==True:
                if len(peaks)==0 or abs(localmin.x-peaks[-1].x)>2.*peaks[-1].width: # remove afterpulses
                    peaks.append(GraphVal(localmin.x,localmin.y,localmin.width))
                    localmin.x=-1000; localmin.y=1000; localmin.width=0;
                    onPeak=False
        self.peaks = peaks
        return peaks
    
    def plot(self,saveName,doWide=False,extensions="pdf"):
        plotformat = (1200,600) if doWide else (600,600)
        sf = 20./plotformat[0]
        height=plotformat[1]
        ROOT.gStyle.SetPadLeftMargin(600.*0.18/plotformat[0])
        ROOT.gStyle.SetPaperSize(20.,sf*plotformat[1])
        customROOTstyle()
        c1 = ROOT.TCanvas(saveName+"_canvas",saveName,plotformat[0],height)
        g = self.getPulse(self.options.ngroup)
        colors = {"calorimeter":ROOT.kRed, "PMT":ROOT.kBlue} 
        g.SetLineColor(colors[self.channel])
        g.Draw("AL")
        g.GetXaxis().SetTitle("time (ns)")
        g.GetYaxis().SetTitle("Amplitude %s (V)" % self.channel)
        g.Draw("L")
        for ext in extensions.split(","):
            c1.Print("%s_%s.%s"%(saveName,self.channel,ext))
    
def addTxt2PulseOptions(parser):
    parser.add_option("--print", dest="printPlots", type="string", default="png,pdf", help="print out plots in this format or formats (e.g. 'png,pdf,txt')");
    parser.add_option("--ngroup", dest="ngroup", type="int", default=100, help="average the pulse every ngroup samples");
    parser.add_option("--minampl", dest="minampl", type="float", default=0.003, help="minimum amplitude required to define a peak (in Volts)");

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file.txt")
    addTxt2PulseOptions(parser)
    (options, args) = parser.parse_args()
    PulsePlot = PulseTxtFile(args[0],options)
    ext = options.printPlots 
    tokens = args[0].split("/")
    run = tokens[-2]
    chunk = tokens[-1].split("Run")[-1].split(".")[0]
    print "run=%s, chunk=%s" % (run,chunk)
    PulsePlot.plot("pulse_run%s_chunk%s" %(run,chunk),extensions=ext)

    peaks = PulsePlot.getPeaks()
    for i,p in enumerate(peaks):
        print "Peak # %d has amplitude = %f V and time = %f ns" %(i,p.y,p.x)

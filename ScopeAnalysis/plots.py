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

    def secondaryVarPlot(self,var,range):
        gr = ROOT.TGraphErrors(len(_xpos)-1 if "amplitude" in var else len(_xpos))
        gr.SetTitle("")
        point=0
        for run,xpos in _xpos.iteritems():
            if run==206 and "amplitude" in var: continue # saturation: too close to cathode
            cut = "nPeaks==2 && run==%d" % run
            if ROOT.gROOT.FindObject("h_dt") != None: ROOT.gROOT.FindObject("h_dt").Delete()
            self.tree.Draw('{var}>>h_dt(100,{min},{max})'.format(var=var,min=range[0],max=range[1]),cut)
            h_dt=ROOT.gROOT.FindObject("h_dt")
            mean,rms = h_dt.GetMean(),h_dt.GetMeanError()
            gr.SetPoint(point,xpos,mean)
            gr.SetPointError(point,0,rms)
            point +=1
        customROOTstyle()
        c1 = ROOT.TCanvas("dist_canvas","dist",600,600)
        ROOT.gStyle.SetOptFit(11111)
        gr.SetMarkerStyle(21)
        gr.SetMarkerSize(0.4)
        gr.Draw("APE")
        gr.GetXaxis().SetTitle("x position [cm]")
        gr.GetYaxis().SetTitle(range[2])
        gr.Fit("pol1")
        gr.Draw("APE")
        for ext in self.options.printPlots.split(','):
            plotname=var.replace("[",""); plotname=plotname.replace("]","")
            plotname=plotname.replace("(",""); plotname=plotname.replace(")","");
            plotname=plotname.replace("/","_over_")
            c1.Print('%s.%s'%(plotname,ext))

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file.txt")
    parser.add_option("--print", dest="printPlots", type="string", default="png,pdf", help="print out plots in this format or formats (e.g. 'png,pdf,txt')");
    (options, args) = parser.parse_args()

    pm = PlotMaker("reco_all.root",options)
    pm.beginJob()
    vars = {'time_pmt[1]-time_pmt[0]':(10,100,'PMT #Deltat [ns]'),
            'abs(amplitude_pmt[0])/abs(amplitude_pmt[1])/abs(amplitude_calo)':(0,1,'Primary/Secondary/Calo Ampl'),
            'abs(amplitude_pmt[0])/abs(amplitude_pmt[1])':(0,1,'Primary/Secondary Ampl'),
            'abs(amplitude_pmt[0])/abs(amplitude_calo)':(0,0.15,'Primary/Calo Ampl'),
            'abs(amplitude_pmt[1])':(0,0.1,'Secondary Ampl [V]'),
            'abs(amplitude_pmt[1])/abs(amplitude_calo)':(0,0.5,'Secondary/Calo Ampl') }
    for var,range in vars.iteritems():
        pm.secondaryVarPlot(var,range)

    pm.endJob()


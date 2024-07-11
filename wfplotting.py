import ROOT
import numpy as np
from array import array
import json


triggerMap={
    -1:'all',
    1:'event 61',
    2:'PMT',
    3:"PMT + event 61",
    4:'min bias',
    8:'high light',
    16:'low light',
    32:'SiPM',
    33:'SiPM + event 61',
    34:'PMT + SiPM',
    35:'PMT + SiPM + event 61'
}


randomTrigger=[2,32,34]



def wfPlotting(file='/raid13/rrapp/coherent_d2o/data/run7894_processed_v4.root', entryID=19415,counter=0,eventTypeDict={},timeDiff={},lastTime=0,lastTrigger=0,plot=False,startEntry=0,deltaTLs=[],mode='',numPMT=[],Threshold=0,targetTrigger=0,fireDistri={}): #file type should be tstring, i may need to solve it
    ROOT.gStyle.SetOptStat(0)
    # ROOT.gStyle.SetOptTitle(0)

    sipmMap={}
    sipmMap[19] = 1#; //panel 4
    sipmMap[20] = 2#; //panel 5
    sipmMap[16] = 3#; //panel 1
    sipmMap[23] = 4#; //panel 8
    sipmMap[24] = 5#; //panel 9
    sipmMap[25] = 5#; //panel 10
    sipmMap[21] = 6#; //panel 6
    sipmMap[18] = 7#; //panel 3
    sipmMap[22] = 8#; //panel 7
    sipmMap[17] = 9#; //panel 2
    # print(sipmMap)

    # eventTypeDict={
    #     1:[],
    #     2:[],
    #     3:[],
    #     4:[],
    #     8:[],
    #     16:[],
    #     32:[],
    #     33:[],
    #     34:[],
    #     35:[]
    # }
    # #this dict direct triggerBits to eventID's

    tree=ROOT.TChain('tree')
    tree.Add(file)

    #print(tree.GetEntries())

    adcVal=np.zeros((32,45),dtype=np.short) #The elements in this variable should be unitialized
    # adcVal=array('h',[0]*32*45)
    # baselineMean=array('d',[0.0]*32)
    baselineMean=np.zeros(32,dtype=np.double)
    # triggerBits=0
    triggerBits=array('i',[0])
    eventID=array('i',[0])
    nsTime=array('l',[0])
    peakPosition=array('i',[0]*32)
    pulseH=array('d',[0.0]*32)
    tree.SetBranchAddress('adcVal',adcVal)
    tree.SetBranchAddress('baselineMean',baselineMean)
    tree.SetBranchAddress('triggerBits',triggerBits)
    tree.SetBranchAddress('eventID',eventID)
    tree.SetBranchAddress('nsTime',nsTime)
    tree.SetBranchAddress('peakPosition',peakPosition)
    tree.SetBranchAddress('pulseH',pulseH)

    
    
    #eventID=36122
    tree.GetEntry(entryID)
    # tree.SetDirectory(0)
    # print(f'length of eventID:{len(eventID)} and the event is {eventID}')
    # print('adcVal:')
    # print(adcVal)
    # print('baselineMean:')
    # print(baselineMean)
    # print(f'triggerBits from entry {entryID}:')
    # print(triggerBits)
    # print(f'time is {nsTime}')
    # print('peakPsition:')
    # for i in range(len(peakPosition)):
    #     print(f'channel {i}')
    #     print(f'peak position: {peakPosition[i]}')
    #     print(f'pulse amplitude: {pulseH[i]}')

    #this part is for sortEvents(), uncomment this for sortEvents()
    if mode=='sort event':
        if triggerBits[0] in eventTypeDict:
            eventTypeDict[triggerBits[0]].append(entryID)
        return eventTypeDict

    #this part is for countType(), uncomment this for countType()
    elif mode=='count type':
        if triggerBits[0]==32:
            print(entryID)
            counter+=1
        return counter

    #this part is for deltaTAnalysis(). in this way the function return (a dictionary that contains time different between different triggerBits), time, and triggerBit
    elif mode=='delta t':
        presentTrigger=triggerBits[0]
        presentTime=nsTime[0]
        if lastTime==0 and lastTrigger==0 and entryID!=0:
            return timeDiff, presentTime, presentTrigger
        if presentTrigger!=lastTrigger:
            if frozenset({presentTrigger,lastTrigger}) in timeDiff:
                timeDiff[frozenset({presentTrigger,lastTrigger})].append(presentTime-lastTime)
            else:
                timeDiff[frozenset({presentTrigger,lastTrigger})]=[presentTime-lastTime]
            return timeDiff, presentTime, presentTrigger
        else: return timeDiff, presentTime, presentTrigger

    #this part is for deltaTForExent()
    elif mode=='delta t for entry':
        presentTrigger=triggerBits[0]
        presentTrigger=presentTrigger+0
        presentTime=nsTime[0]
        presentTime=presentTime+0
        #breaking aliase...
        tree.GetEntry(startEntry)
        startTrigger=triggerBits[0]
        startTime=nsTime[0]
        if presentTrigger!=startTrigger:
            deltaTLs.append(presentTime-startTime)
            return deltaTLs
        else:
            return deltaTLs

    elif mode=='#PMT fire':
        count=0
        if triggerBits[0]==targetTrigger:
            for i in range(0,12):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    # print(amplitude,Threshold)
                    count+=1
            numPMT.append(count)
            return numPMT
        else:
            return numPMT
        
    elif mode=='#siPM fire':
        count=0
        if triggerBits[0]==targetTrigger:
            for i in range(16,26):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    # print(amplitude,Threshold)
                    count+=1
            numPMT.append(count)
            return numPMT
        else:
            return numPMT

    elif mode=='PMT bar':
        if triggerBits[0]==targetTrigger:
            for i in range(0,12):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    if i not in fireDistri:
                        fireDistri[i]=1
                    else:
                        fireDistri[i]+=1
            return fireDistri
        else:
            return fireDistri

    elif mode=='siPM bar':
        if triggerBits[0]==targetTrigger:
            for i in range(16,26):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    if i not in fireDistri:
                        fireDistri[i]=1
                    else:
                        fireDistri[i]+=1
            return fireDistri
        else:
            return fireDistri

    elif mode=='delta t in event for PMT':
        temp=[]
        if targetTrigger==-1:
            for i in range(0,12):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    temp.append(peakPosition[i])
            if len(temp)>=2:
                #I count the condition that there is only one peak as delta t =0
                deltaTLs.append(max(temp)-min(temp))
                return deltaTLs
            else:
                return deltaTLs
        else:
            if triggerBits[0]==targetTrigger:
                # print('hi')
                for i in range(0,12):
                    amplitude=pulseH[i]
                    if amplitude>=Threshold:
                        temp.append(peakPosition[i])
                if len(temp)>=2:
                    #I count the condition that there is only one peak as delta t =0
                    deltaTLs.append(max(temp)-min(temp))
                    # print(9)
                    return deltaTLs
                else:
                    return deltaTLs
            else:
                return deltaTLs
            
    elif mode=='delta t in event for siPM':
        temp=[]
        if targetTrigger==-1:
            for i in range(16,26):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    temp.append(peakPosition[i])
            if len(temp)>=2:
                #I count the condition that there is only one peak as delta t =0
                deltaTLs.append(max(temp)-min(temp))
                return deltaTLs
            else:
                return deltaTLs
        else:
            if triggerBits[0]==targetTrigger:
                # print('hi')
                for i in range(16,26):
                    amplitude=pulseH[i]
                    if amplitude>=Threshold:
                        temp.append(peakPosition[i])
                if len(temp)>=2:
                    #I count the condition that there is only one peak as delta t =0
                    deltaTLs.append(max(temp)-min(temp))
                    # print(9)
                    return deltaTLs
                else:
                    return deltaTLs
            else:
                return deltaTLs



    c1=ROOT.TCanvas('c1','All PMTs and SiPms',2000,1000)
    c1.Divide(8,3)
    pltCtr=0

    c2=ROOT.TCanvas('c2','Muon Veto Panels (Top Down View)',1000,1000)
    c2.Divide(3,3)
    histList=[]

    # c3=ROOT.TCanvas('c3','Frequency of nsTime',1500,1000)
    # nsTime_hist=ROOT.TH1F('hist_nsTime',f';nsTime; count',100,0,5000E9)
    # for i in range(0,2220939):
    #     tree.GetEntry(i)
    #     nsTime_hist.Fill(nsTime[0],1)
    # c3.cd()
    # nsTime_hist.Draw()
    # c3.Update()
    # c3.SaveAs('c3.png')

    # for i in range(0,2220939):
    #     tree.GetEntry(i)
    #     if triggerBits[0]==35:
    #         print(i)

    if plot==True:
    
        for j in range(32):#create empty histogram and save them to the list first
            wf=ROOT.TH1D(f'wf_{j}',f';Sample (16 ns); Channel {j} (ADC)',45,0,44)#this line is histogram
            histList.append(wf)

        for j in range(32):
            wf=histList[j]
            for i in range(45):
                if j<12: #channel 0-11 -- PMTs
                    wf.SetLineColor(ROOT.kBlack)
                # print(baselineMean[j])
                wf.SetBinContent(i,adcVal[j][i]-baselineMean[j])
                # print(str(baselineMean[18])+'    '+str(adcVal[18][i]))

            if (not ((j>11 and j<16) or j>25)): #not 11<j<16 or j>25, that is j=0-11 and 16-25
                # print('c1 is running')
                pltCtr+=1
                if j==16: # leave some space for muon veto
                    pltCtr+=2
                
                c1.cd(pltCtr)
                # c1.Print('c1.pdf[')
                #if what condition i need to draw it
                # if triggerBits[0]==32:
                    # print(f'triggerBit:{triggerBits[0]}')
                wf.Draw()
                # c1.Print('c1.pdf')

            if j<26 and j>15: #sipm or muon veto
                # print(str(j)+'  '+str(sipmMap[j]))
                # print('c2 is running')
                
                c2.cd(sipmMap[j]) 
                if j==25:
                    wf.SetLineColor(ROOT.kRed)
                # c2.Print('c2.pdf[')
                #if what condition I need to draw it
                # if triggerBits[0]==32:
                wf.Draw('same')
                # c2.Print('c2.pdf')

        # print(adcVal)
        # print(baselineMean)
        
        # wf.SetDirectory(0)
        c1.Update()
        c2.Update()
        # c1.Print('c1.pdf]')
        # c2.Print('c2.pdf]')

        c1.SaveAs(f'c1_{triggerBits[0]}_{entryID}.png')
        c2.SaveAs(f'c2_{triggerBits[0]}_{entryID}.png')

    
    
def countType(start,end):
#take two entryID's and output and output the count of one type of trigger. note that the type of trigger need to be revised in wfPlotting()
    count=0
    for i in range(start,end):
        count=wfPlotting(entryID=i,counter=count,mode='count type')
    print(count)


# 0<=entryID<=2220939. there are over 4000000 total events, so the entries are selected from total events. 


def sortEvents(start,end):
#take two entryIDs and output a text file that contains the dictionary of diffeent trigger types.
    eventDict={
            1:[],
            2:[],
            3:[],
            4:[],
            8:[],
            16:[],
            32:[],
            33:[],
            34:[],
            35:[]
        }

    for i in range(start,end):
        eventDict=wfPlotting(entryID=i,eventTypeDict=eventDict,mode='sort event')
    print(eventDict)

    with open('event_type.txt','w') as output:
        json.dump(eventDict,output,indent=4)

def deltaTAnalysis(start,end):
    tDiff={}
    lastT=0
    lastTri=0
    for i in range(start,end):
        tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='delta t')
    # print(tDiff)
    c4=ROOT.TCanvas('c4','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between all adjacent entries with different triggers ({start}-{end});nsTime;count',50,0,70E5)
    
    for key in tDiff:
        for time in tDiff[key]:
            deltaT_hist.Fill(time,1)
    c4.cd()
    deltaT_hist.Draw()
    c4.Update()
    c4.SaveAs('c4.png')

def deltaTForTrigger(start,end,trigger):
    tDiff={}
    lastT=0
    lastTri=0
    if trigger not in [1,2,3,4,8,16,32,33,34,35]:
        print('invalid trigger')
        return
    for i in range(start,end):
        tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='delta t')
    c5=ROOT.TCanvas('c4','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between all adjacent entries with different triggers (one is [{triggerMap[trigger]}]) ({start}-{end});nsTime; count',50,0,70E5)
    for key in tDiff:
        if trigger in key:
            for time in tDiff[key]:
                deltaT_hist.Fill(time,1)
    c5.cd()
    deltaT_hist.Draw()
    c5.Update()
    c5.SaveAs(f'delta_t_for_trigger_{trigger}.png')

def deltaTForEntry(start,end):
    deltaT=[]
    for i in range(start+1,end):
        deltaT=wfPlotting(entryID=i,startEntry=start,deltaTLs=deltaT,mode='delta t for entry')
    c6=ROOT.TCanvas('c4','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between {start} and all subsequent entries up to {end} that has different triggers from {start};nsTime; count',100,0,2000E6) #number of bins need to be revised for different intervals
    for time in deltaT:
        deltaT_hist.Fill(time,1)
    c6.cd()
    deltaT_hist.Draw()
    c6.Update()
    c6.SaveAs(f'delta_t_{start}_{end}.png') 

def numFire(trigger,start,end,threshold,mode,graph):
    if mode=='PMT':
        if graph=='histo':
            num=[]
            for i in range(start,end):
                num=wfPlotting(entryID=i,mode='#PMT fire',numPMT=num,Threshold=threshold,targetTrigger=trigger)
            print(num)
            c7=ROOT.TCanvas('c7','number of PMT that fires',1500,1000)
            numPMT_hist=ROOT.TH1F('hist_numPMT',f'#PMTs that fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});number of PMT; count',15,-1,14)
            for PMT in num:
                numPMT_hist.Fill(PMT,1)
            c7.cd()
            numPMT_hist.Draw()
            c7.Update()
            c7.SaveAs(f'numPMT_{trigger}_{threshold}.png')
        elif graph=='bar':
            distribution={}
            for i in range(start,end):
                distribution=wfPlotting(entryID=i,mode='PMT bar',fireDistri=distribution, Threshold=threshold,targetTrigger=trigger)
            print(distribution)
            c9=ROOT.TCanvas('c9','distribution of PMT that fires',1500,1000)
            PMT_bar=ROOT.TH1F('bar_PMT',f'which PMTs fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});PMT ID(?) number;count',15,-1,14)
            for i in range(12):
                if i in distribution:
                    PMT_bar.Fill(i,distribution[i])
            c9.cd()
            PMT_bar.SetFillColor(ROOT.kGray)
            PMT_bar.SetLineColor(ROOT.kRed)
            PMT_bar.SetLineWidth(2)
            PMT_bar.Draw('bar hist')
            c9.Update()
            c9.SaveAs(f'PMTbar_{trigger}_{threshold}.png')
    elif mode=='siPM':
        if graph=='histo':
            num=[]
            for i in range(start,end):
                num=wfPlotting(entryID=i,mode='#siPM fire',numPMT=num,Threshold=threshold,targetTrigger=trigger)
            print(num)
            c8=ROOT.TCanvas('c7','number of siPM that fires',1500,1000)
            numsiPM_hist=ROOT.TH1F('hist_numsiPM',f'#SiPMs that fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});number of siPM; count',29,-1,28)
            for PMT in num:
                numsiPM_hist.Fill(PMT,1)
            c8.cd()
            numsiPM_hist.Draw()
            c8.Update()
            c8.SaveAs(f'numsiPM_{trigger}_{threshold}.png')
        elif graph=='bar':
            distribution={}
            for i in range(start,end):
                distribution=wfPlotting(entryID=i,mode='siPM bar',fireDistri=distribution, Threshold=threshold,targetTrigger=trigger)
            print(distribution)
            c10=ROOT.TCanvas('c10','distribution of siPM that fires',1500,1000)
            PMT_bar=ROOT.TH1F('bar_siPM',f'which SiPMs fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});distribution of siPM; count',29,-1,28)
            for i in range(16,26):
                if i in distribution:
                    PMT_bar.Fill(i,distribution[i])
            c10.cd()
            PMT_bar.SetFillColor(ROOT.kGray)
            PMT_bar.SetLineColor(ROOT.kBlack)
            PMT_bar.Draw('bar hist')
            c10.Update()
            c10.SaveAs(f'siPMbar_{trigger}_{threshold}.png')

def deltaTInEvent(start,end,threshold,trigger,mode):
    time=[]
    for i in range(start,end):
        if mode=='PMT':
            time=wfPlotting(entryID=i,mode='delta t in event for PMT',Threshold=threshold,targetTrigger=trigger,deltaTLs=time)
        elif mode=='siPM':
            time=wfPlotting(entryID=i,mode='delta t in event for siPM',Threshold=threshold,targetTrigger=trigger,deltaTLs=time)
    # print(time)
    c11=ROOT.TCanvas('c11','delta t in event',1500,1000)
    deltat_hist=ROOT.TH1F('hist_deltaT',f'max deltaT in event for {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});delta t in bins; count',16,-1,15)
    for bin in time:
        deltat_hist.Fill(bin,1)
    c11.cd()
    deltat_hist.Draw()
    c11.Update()
    c11.SaveAs(f'deltaT_inEvent_{trigger}_{threshold}.png')

def isRandomTrigger(key):
    #input:frozenSet
    #output: boolean
    for trigger in key:
        if trigger not in randomTrigger:
            return False
    return True

def poissonFit(start,end):
    tDiff={}
    lastT=0
    lastTri=0
    for i in range(start,end):
        tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='delta t')
    c12=ROOT.TCanvas('c12','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between all adjacent entries with different triggers that are random ({start}-{end});nsTime;count',50,0,50E5)
    for key in tDiff:
        if isRandomTrigger(key):
            for time in tDiff[key]:
                deltaT_hist.Fill(time,1)
    def poisson(x, par):
        # par[0]: normalization (amplitude)
        # par[1]: mean (lambda)
        return par[0] * ROOT.TMath.Poisson(x[0], par[1])
    poisson_func=ROOT.TF1('poisson function',poisson,0,50E5)
    poisson_func.SetParameters(150,1)
    '''
    #[0] is lamda,[1] is normalization factor
    poisson_a=[0]**x
    poisson_b=2.7182818**(-[0])
    poisson_c=x!
    poisson=f'[1]*{poisson_a}*{poisson_b}/{poisson_c}'
    poisson_func=ROOT.TF1('poissonfit',poisson,0,50E5)
    poisson_func.SetParameter(0,1)
    '''
    deltaT_hist.Fit(poisson_func,'R')
    c12.cd()
    deltaT_hist.Draw()
    poisson_func.Draw('same')
    c12.Update()
    c12.SaveAs(f'poissonFit_{start}_{end}.png')
    

poissonFit(19000,20000)
import ROOT
import numpy as np
from array import array
import json
from joblib import Parallel, delayed



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

tree=ROOT.TChain('tree')
tree.Add('/raid13/rrapp/coherent_d2o/data/run7894_processed_v4.root')

def wfPlotting(file='/raid13/rrapp/coherent_d2o/data/run7894_processed_v4.root', entryID=19415,counter=0,eventTypeDict={},timeDiff={},lastTime=0,lastTrigger=0,plot=False,startEntry=0,deltaTLs=[],mode='',numPMT=[],Threshold=0,targetTrigger=0,fireDistri={},tree=tree): #file type should be tstring, i may need to solve it
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

    

    #print(tree.GetEntries())

    adcVal=np.zeros((32,45),dtype=np.short) #The elements in this variable should be unitialized
    baselineMean=np.zeros(32,dtype=np.double)
    triggerBits=array('i',[0])
    eventID=array('i',[0])
    nsTime=array('l',[0])
    peakPosition=array('i',[0]*32)
    pulseH=array('d',[0.0]*32)
    # if mode!='PMT bar' and mode!='siPM bar':
    tree.SetBranchAddress('adcVal',adcVal)
    tree.SetBranchAddress('baselineMean',baselineMean)
    tree.SetBranchAddress('eventID',eventID)
    tree.SetBranchAddress('nsTime',nsTime)
    tree.SetBranchAddress('peakPosition',peakPosition)
    tree.SetBranchAddress('triggerBits',triggerBits)
    tree.SetBranchAddress('pulseH',pulseH)

    
    
    #eventID=36122
    tree.GetEntry(entryID)
    # tree.SetDirectory(0)
    # print(f'length of eventID:{len(eventID)} and the event is {eventID}')
    # print(eventID[0])
    # print('adcVal:')
    # print(adcVal)
    # print('baselineMean:')
    # print(baselineMean)
    # print(f'triggerBits from entry {entryID}:')
    # print(triggerBits)
    # print(f'time is {nsTime[0]}')
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

    elif mode=='delta t for poisson':
        presentTrigger=triggerBits[0]
        presentTime=nsTime[0]
        if (lastTime==0 and lastTrigger==0 and entryID!=0):
            return timeDiff, presentTime, presentTrigger
        if presentTrigger!=lastTrigger:
            if (presentTrigger not in randomTrigger or lastTrigger not in randomTrigger):
                return timeDiff, presentTime, presentTrigger
            else:
                if frozenset({presentTrigger,lastTrigger}) in timeDiff:
                    timeDiff[frozenset({presentTrigger,lastTrigger})].append(presentTime-lastTime)
                else:
                    timeDiff[frozenset({presentTrigger,lastTrigger})]=[presentTime-lastTime]
                return timeDiff, presentTime, presentTrigger
        else: return timeDiff, presentTime, presentTrigger

    elif mode=='fast poisson':
        presentTrigger=triggerBits[0]+0
        presentTime=nsTime[0]+0
        if entryID!=0:
            tree.GetEntry(entryID-1)
            lastTrigger=triggerBits[0]
            lastTime=nsTime[0]
        else:
            lastTime=0
            lastTrigger=0
        if (lastTime==0 and lastTrigger==0 and entryID!=0):
            # print(0)
            return None
        if presentTrigger!=lastTrigger:
            
            if (presentTrigger not in randomTrigger or lastTrigger not in randomTrigger):
                # print(presentTrigger,lastTrigger)
                return None
            else:
                return presentTime-lastTime
        else: return None
        
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
            # numPMT.append(count)
            # return numPMT
            return count
        else:
            # return numPMT
            return None
        
    elif mode=='#siPM fire':
        count=0
        if triggerBits[0]==targetTrigger:
            for i in range(16,26):
                amplitude=pulseH[i]
                if amplitude>=Threshold:
                    # print(amplitude,Threshold)
                    count+=1
            # numPMT.append(count)
            # return numPMT
            return count
        else:
            # return numPMT
            return None

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
            
    elif mode=='check time':
        presentTime=nsTime[0]
        presentTrigger=triggerBits[0]
        if lastTime==0 and lastTrigger==0 and entryID!=0:
            return timeDiff, presentTime, presentTrigger
        if presentTime-lastTime<45*16:
            timeDiff[entryID]=presentTime-lastTime
            return timeDiff, presentTime, presentTrigger
        else:
            return timeDiff, presentTime, presentTrigger




    c1=ROOT.TCanvas('c1','All PMTs and SiPms',2000,1000)
    c1.Divide(8,3)
    pltCtr=0

    c2=ROOT.TCanvas('c2','Muon Veto Panels (Top Down View)',1000,1000)
    c2.Divide(3,3)
    histList=[]

    c0=ROOT.TCanvas('c0','All PMTs and SiPMs with their layouts',2000,1000)

    PMTwidth=0.125
    PMTheight=0.25
    pad0=ROOT.TPad('0','0',0,0.5,0.125,0.75)
    pad1=ROOT.TPad('1','1',0.375-PMTwidth/2,0.25,0.375+PMTwidth/2,0.25+PMTheight)
    pad2=ROOT.TPad('2','2',0.25-PMTwidth/2,0.25,0.25+PMTwidth/2,0.25+PMTheight)
    pad3=ROOT.TPad('3','3',0.25-PMTwidth/2,0.75,0.25+PMTwidth/2,0.75+PMTheight)
    pad4=ROOT.TPad('4','4',0.125-PMTwidth/2,0.25,0.125+PMTwidth/2,0.25+PMTheight)
    pad5=ROOT.TPad('5','5',0.125,0,0.25,0.25)
    pad6=ROOT.TPad('6','6',0.25,0,0.375,0.25)
    pad7=ROOT.TPad('7','7',0.375,0.5,0.5,0.75)
    pad8=ROOT.TPad('8','8',0.375-PMTwidth/2,0.75,0.375+PMTwidth/2,0.75+PMTheight)
    pad9=ROOT.TPad('9','9',0.125-PMTwidth/2,0.75,0.125+PMTwidth/2,0.75+PMTheight)
    pad10=ROOT.TPad('10','10',0.25,0.5,0.375,0.75)
    pad11=ROOT.TPad('11','11',0.125,0.5,0.25,0.75)
    #done: 0,11,10,7,2,1,4,9,3,8,5
    PMTls=[pad0,pad1,pad2,pad3,pad4,pad5,pad6,pad7,pad8,pad9,pad10,pad11]

    SIPMwidth=0.5/3
    SIPMheight=1/3
    pad19=ROOT.TPad('19','19',0.5,2/3,0.5+SIPMwidth,1)
    pad20=ROOT.TPad('20','20',0.5+SIPMwidth,2/3,0.5+2*SIPMwidth,1)
    pad16=ROOT.TPad('16','16',0.5+2*SIPMwidth,2/3,1,1)
    pad23=ROOT.TPad('23','23',0.5,1/3,0.5+SIPMwidth,2/3)
    pad24=ROOT.TPad('24','24',0.5+SIPMwidth,1/3,0.5+2*SIPMwidth,2/3)
    pad21=ROOT.TPad('21','21',0.5+2*SIPMwidth,1/3,1,2/3)
    pad18=ROOT.TPad('18','18',0.5,0,0.5+SIPMwidth,1/3)
    pad22=ROOT.TPad('22','22',0.5+SIPMwidth,0,0.5+2*SIPMwidth,1/3)
    pad17=ROOT.TPad('17','17',0.5+2*SIPMwidth,0,1,1/3)
    SIPMls=[pad19,pad20,pad16,pad23,pad24,pad21,pad18,pad22,pad17]

    c0.cd()
    for pad in PMTls:
        pad.Draw()
    for pad in SIPMls:
        pad.Draw()


    # c3=ROOT.TCanvas('c3','Frequency of nsTime',1500,1000)
    # nsTime_hist=ROOT.TH1F('hist_nsTime',f';nsTime; count',100,0,5000E9)
    # for i in range(0,2220939):
    #     if i%1000==0:
    #         print(i)
    #     tree.GetEntry(i)
    #     nsTime_hist.Fill(nsTime[0],1)
    # c3.cd()
    # nsTime_hist.Draw()
    # c3.Update()
    # c3.SaveAs('c3.png')

    # for i in range(0,2220939):
    #     tree.GetEntry(i)
    #     if triggerBits[0]==35:
    #         print(i)sss

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
                if 0<=j<=11:
                    PMTls[j].cd()
                    wf.Draw()

            if j<26 and j>15: #sipm or muon veto
                # print(str(j)+'  '+str(sipmMap[j]))
                # print('c2 is running')
                SIPMindex=sipmMap[j]
                c2.cd(SIPMindex)
                if j==25:
                    wf.SetLineColor(ROOT.kRed)
                # c2.Print('c2.pdf[')
                #if what condition I need to draw it
                # if triggerBits[0]==32:
                wf.Draw('same')
                if j!=25:
                    SIPMls[SIPMindex-1].cd()
                    wf.Draw()
                else:
                    pad24.cd()
                    wf.Draw('same')
                # c2.Print('c2.pdf')

        # print(adcVal)
        # print(baselineMean)
        
        # wf.SetDirectory(0)
        c1.Update()
        c2.Update()
        c0.Update()
        # c1.Print('c1.pdf]')
        # c2.Print('c2.pdf]')

        c1.SaveAs(f'c1_{triggerBits[0]}_{entryID}.pdf')
        c2.SaveAs(f'c2_{triggerBits[0]}_{entryID}.png')
        c0.SaveAs(f'c0_{triggerBits[0]}_{entryID}.pdf')

    
    
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
            # for i in range(start,end):
            num=Parallel(n_jobs=8)(delayed(wfPlotting)(entryID=i,mode='#PMT fire',numPMT=num,Threshold=threshold,targetTrigger=trigger) for i in range(start,end))
            # print(num)
            c7=ROOT.TCanvas('c7','number of PMT that fires',1500,1000)
            numPMT_hist=ROOT.TH1F('hist_numPMT',f'#PMTs that fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});number of PMT; count',15,-1,14)
            for PMT in num:
                if PMT!=None:
                    numPMT_hist.Fill(PMT,1)
            c7.cd()
            numPMT_hist.Draw()
            c7.Update()
            c7.SaveAs(f'numPMT_{trigger}_{threshold}.png')
        elif graph=='bar':
            distribution={}
            for i in range(start,end):
                if i%1000==0:
                    print(i)
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
            # for i in range(start,end):
            num=Parallel(n_jobs=8)(delayed(wfPlotting)(entryID=i,mode='#siPM fire',numPMT=num,Threshold=threshold,targetTrigger=trigger) for i in range(start,end))
            # print(num)
            c8=ROOT.TCanvas('c7','number of siPM that fires',1500,1000)
            numsiPM_hist=ROOT.TH1F('hist_numsiPM',f'#SiPMs that fire with {triggerMap[trigger]} trigger ({start}-{end},threshold={threshold});number of siPM; count',29,-1,28)
            for PMT in num:
                if PMT!=None:
                    numsiPM_hist.Fill(PMT,1)
            c8.cd()
            numsiPM_hist.Draw()
            c8.Update()
            c8.SaveAs(f'numsiPM_{trigger}_{threshold}.png')
        elif graph=='bar':
            distribution={}
            for i in range(start,end):
                if i%1000==0:
                    print(i)
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
        if i%10000==0:
            print(i)
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
        if i%1000==0:
            print(i)
        tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='delta t for poisson')
    print('tDiff is filled.')
    c12=ROOT.TCanvas('c12','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between all adjacent entries with different triggers that are random ({start}-{end});nsTime*10E5;count',49,0.1,5)
    for key in tDiff:
        if isRandomTrigger(key):
            for time in tDiff[key]:
                deltaT_hist.Fill(time/10E5,1)
        else:
            print('not random trigger')
    # def poisson(x, par):
    #     # par[0]: normalization (amplitude)
    #     # par[1]: mean (lambda)
    #     return par[0] * ROOT.TMath.Poisson(x[0], par[1])
    # poisson_func=ROOT.TF1('poisson function',poisson,0,50E5)
    # poisson_func.SetParameters(150,1)
    # def poisson(x, par):
    #     k = x[0]
    #     lambd = par[0]
    #     return ROOT.TMath.Poisson(k, lambd)
    
    #[0] is lamda,[1] is normalization factor
    # poisson_a='[0]**x'
    # poisson_b='2.7182818**(-[0])'
    # poisson_c='x!'
    # poisson=f'[1]*{poisson_a}*{poisson_b}/{poisson_c}'
    poisson_func=ROOT.TF1('poissonfit','[1]*TMath::Poisson(x,[0])',0,50)

    poisson_func.SetParameter(0,0.5)
    # poisson_func.SetParameter(1,2000000000)
    latex=ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.03)
    deltaT_hist.Fit(poisson_func,'E')
    c12.cd()
    deltaT_hist.Draw()
    chi2=poisson_func.GetChisquare()
    ndof=poisson_func.GetNDF()
    lamda=poisson_func.GetParameter(0)
    latex.DrawText(0.5,0.80,f'chi2/ndof={round(chi2/ndof,3)}')
    latex.DrawText(0.5,0.75,f'lambda={round(lamda,3)}')
    # poisson_func.Draw('same')
    c12.Update()
    c12.SaveAs(f'poissonFit_{start}_{end}.png')
    #this function become much slower when entryID>23560 and I don't know why. 

def poisson():
    c13=ROOT.TCanvas('c13','poisson',1500,1000)
    poisson_func=ROOT.TF1('poissonfit','[1]*TMath::Poisson(x,[0])',0,5)
    poisson_func.SetParameter(0,0.5)
    poisson_func.SetParameter(1,10)
    c13.cd()
    poisson_func.Draw()
    c13.Update()
    c13.SaveAs('poissonTest.png')

def checkTime(start,end):
    tDiff={}
    lastT=0
    lastTri=0
    for i in range(start,end):
        # if i%100==0:
        #     print(i)
        tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='check time')
        if lastTri == 10 or lastTri==18:
            print(i)
    print('tDiff is filled.')
    print(tDiff)


def getPoissonT(i):
    if i%1000==0:
        print(i)
    tDiff,lastT,lastTri=wfPlotting(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='delta t for poisson')
    return tDiff, lastT, lastTri

def fastPoisson(start,end):
    tDiff={}
    lastT=0
    lastTri=0
    
    tList=Parallel(n_jobs=8)(delayed(wfPlotting)(entryID=i,timeDiff=tDiff, lastTime=lastT,lastTrigger=lastTri,mode='fast poisson') for i in range(start,end))
    print('tList is filled.')
    c13=ROOT.TCanvas('c12','delta t',1500,1000)
    deltaT_hist=ROOT.TH1F('hist_nsTime',f'deltaT between all adjacent entries with different triggers that are random ({start}-{end});nsTime*10E5;count',49,0.1,5)
    # for key in tDiff:
    #     if isRandomTrigger(key):
    #         for time in tDiff[key]:
    #             deltaT_hist.Fill(time/10E5,1)
    # print(tList)
    for time in tList:
        if time !=None:
            deltaT_hist.Fill(time/10E5,1)
    # def poisson(x, par):
    #     # par[0]: normalization (amplitude)
    #     # par[1]: mean (lambda)
    #     return par[0] * ROOT.TMath.Poisson(x[0], par[1])
    # poisson_func=ROOT.TF1('poisson function',poisson,0,50E5)
    # poisson_func.SetParameters(150,1)
    # def poisson(x, par):
    #     k = x[0]
    #     lambd = par[0]
    #     return ROOT.TMath.Poisson(k, lambd)

    #[0] is lamda,[1] is normalization factor
    # poisson_a='[0]**x'
    # poisson_b='2.7182818**(-[0])'
    # poisson_c='x!'
    # poisson=f'[1]*{poisson_a}*{poisson_b}/{poisson_c}'
    poisson_func=ROOT.TF1('poissonfit','[1]*TMath::Poisson(x,[0])',0,50)

    poisson_func.SetParameter(0,0.5)
    # poisson_func.SetParameter(1,2000000000)
    latex=ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.03)
    deltaT_hist.Fit(poisson_func,'E')
    c13.cd()
    deltaT_hist.Draw()
    chi2=poisson_func.GetChisquare()
    ndof=poisson_func.GetNDF()
    lamda=poisson_func.GetParameter(0)
    latex.DrawText(0.5,0.80,f'chi2/ndof={round(chi2/ndof,3)}')
    latex.DrawText(0.5,0.75,f'lambda={round(lamda,3)}')
    # poisson_func.Draw('same')
    c13.Update()
    c13.SaveAs(f'poissonFit_{start}_{end}.png')

#{0: 63003, 1: 70190, 2: 91207, 3: 66027, 4: 76381, 5: 60536, 6: 79865, 8: 71049, 9: 47683, 10: 88604, 11: 60451, 7: 77538} for 2
# {21: 101028, 20: 71710, 24: 233382, 25: 207289, 22: 131670, 23: 82782, 18: 162834, 19: 81980, 17: 74021, 16: 41532} for 32
def colorLayout(mode):
    c15=ROOT.TCanvas('c0','All PMTs and SiPMs with their layouts',2000,1000)
    dark_red = ROOT.TColor.GetColor(139, 0, 0)   # RGB for dark red
    light_red = ROOT.TColor.GetColor(255, 102, 102)
    pink=ROOT.TColor.GetColor(255, 204, 204)
    PMTwidth=0.125
    PMTheight=0.25
    pad0=ROOT.TPad('0','0',0,0.5,0.125,0.75)
    pad1=ROOT.TPad('1','1',0.375-PMTwidth/2,0.25,0.375+PMTwidth/2,0.25+PMTheight)
    pad2=ROOT.TPad('2','2',0.25-PMTwidth/2,0.25,0.25+PMTwidth/2,0.25+PMTheight)
    pad3=ROOT.TPad('3','3',0.25-PMTwidth/2,0.75,0.25+PMTwidth/2,0.75+PMTheight)
    pad4=ROOT.TPad('4','4',0.125-PMTwidth/2,0.25,0.125+PMTwidth/2,0.25+PMTheight)
    pad5=ROOT.TPad('5','5',0.125,0,0.25,0.25)
    pad6=ROOT.TPad('6','6',0.25,0,0.375,0.25)
    pad7=ROOT.TPad('7','7',0.375,0.5,0.5,0.75)
    pad8=ROOT.TPad('8','8',0.375-PMTwidth/2,0.75,0.375+PMTwidth/2,0.75+PMTheight)
    pad9=ROOT.TPad('9','9',0.125-PMTwidth/2,0.75,0.125+PMTwidth/2,0.75+PMTheight)
    pad10=ROOT.TPad('10','10',0.25,0.5,0.375,0.75)
    pad11=ROOT.TPad('11','11',0.125,0.5,0.25,0.75)
    #done: 0,11,10,7,2,1,4,9,3,8,5
    pad2.SetFillColor(dark_red)
    pad10.SetFillColor(dark_red)
    pad1.SetFillColor(ROOT.kRed)
    pad4.SetFillColor(ROOT.kRed)
    pad6.SetFillColor(ROOT.kRed)
    pad8.SetFillColor(ROOT.kRed)
    pad7.SetFillColor(ROOT.kRed)
    pad0.SetFillColor(light_red)
    pad3.SetFillColor(light_red)
    pad5.SetFillColor(light_red)
    pad11.SetFillColor(light_red)
    pad9.SetFillColor(pink)
    PMTls=[pad0,pad1,pad2,pad3,pad4,pad5,pad6,pad7,pad8,pad9,pad10,pad11]

    SIPMwidth=0.5/3
    SIPMheight=1/3
    pad19=ROOT.TPad('19','19',0.5,2/3,0.5+SIPMwidth,1)
    pad20=ROOT.TPad('20','20',0.5+SIPMwidth,2/3,0.5+2*SIPMwidth,1)
    pad16=ROOT.TPad('16','16',0.5+2*SIPMwidth,2/3,1,1)
    pad23=ROOT.TPad('23','23',0.5,1/3,0.5+SIPMwidth,2/3)
    pad24=ROOT.TPad('24','24',0.5+SIPMwidth,1/3,0.5+2*SIPMwidth,2/3)
    pad21=ROOT.TPad('21','21',0.5+2*SIPMwidth,1/3,1,2/3)
    pad18=ROOT.TPad('18','18',0.5,0,0.5+SIPMwidth,1/3)
    pad22=ROOT.TPad('22','22',0.5+SIPMwidth,0,0.5+2*SIPMwidth,1/3)
    pad17=ROOT.TPad('17','17',0.5+2*SIPMwidth,0,1,1/3)
    SIPMls=[pad19,pad20,pad16,pad23,pad24,pad21,pad18,pad22,pad17]
    

    c15.cd()
    for pad in PMTls:
        pad.Draw()
    # for pad in SIPMls:
    #     pad.Draw()
    textls=[]
    for i in range(len(PMTls)):
        textls.append(ROOT.TText(0.5, 0.5, f'{i}'))
    for i in range(len(PMTls)):
        pad=PMTls[i]
        pad.cd()
        text = textls[i]  # Place text at (0.5, 0.5) in normalized coordinates
        text.SetTextAlign(22)  # Center alignment
        text.SetTextSize(0.2)  # Adjust text size
        text.Draw()
        c15.Update()
    c15.cd()
    darkText=ROOT.TText(0.75,0.8,'>80000')
    darkText.SetTextColor(dark_red)
    darkText.SetTextAlign(22)  # Center alignment
    darkText.SetTextSize(0.1)  # Adjust text size
    darkText.Draw()

    redText=ROOT.TText(0.75,0.6,'70000-80000')
    redText.SetTextColor(ROOT.kRed)
    redText.SetTextAlign(22)  # Center alignment
    redText.SetTextSize(0.1)  # Adjust text size
    redText.Draw()
    
    lightText=ROOT.TText(0.75,0.4,'60000-70000')
    lightText.SetTextColor(light_red)
    lightText.SetTextAlign(22)  # Center alignment
    lightText.SetTextSize(0.1)  # Adjust text size
    lightText.Draw()

    pinkText=ROOT.TText(0.75,0.2,'<60000')
    pinkText.SetTextColor(pink)
    pinkText.SetTextAlign(22)  # Center alignment
    pinkText.SetTextSize(0.1)  # Adjust text size
    pinkText.Draw()
    c15.Update()
    c15.SaveAs('coloredLayout.png')



colorLayout('pmt')
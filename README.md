1. I will briefly explain what each function does and what their parameters mean in this file.
2. This script is used to plot waveforms of events and other meaningful histograms like the delta t between events and number of PMTs that fire given a entry interval. 
3. The first function is wfPlotting. Some parameters, including counter, eventTypeDict, timeDiff, lastTime, lastTrigger, deltaTLs, numPMT, targetTrigger, fireDistri, are used to carry specific values.
   They are created because of my horrible coding style, and I use them to record values when I need to run the function 'wfPlotting' several times in other functions later. The parameter 'file' is the
   

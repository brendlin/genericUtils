#!/bin/usr/env python

#
# asetup 20.1.5.12,gcc48,here
# asetup 20.1.7.1,gcc48,here
#
# Using svn+ssh://svn.cern.ch/reps/atlasoff/LumiBlock/LumiCalc/tags/LumiCalc-00-04-07

import os,string

def main(options) :

    my_triggers = []
    my_triggers = [
        "HLT_mu4",
        "HLT_mu6",
        "HLT_mu10",
        # # "HLT_mu11",
        "HLT_mu14",
        "HLT_mu18",
        # "HLT_mu20",
        # "HLT_mu22",
        # "HLT_mu24",
        # "HLT_mu26",
        # "HLT_mu40",
        "HLT_mu50",
    ]

    my_triggers += [
        "HLT_e24_lhmedium_iloose_L1EM18VH",
        "HLT_e60_lhmedium",
        # # "HLT_e5_lhloose",
        "HLT_e5_lhvloose",
        # # "HLT_e9_lhloose",
        "HLT_e10_lhvloose_L1EM7",
        # # "HLT_e12_lhloose",
        # "HLT_e12_lhvloose_L1EM10VH",
        # # "HLT_e15_lhloose_L1EM13VH",
        # "HLT_e15_lhvloose_L1EM13VH",
        # "HLT_e15_lhvloose_L1EM7",
        # "HLT_e17_lhloose",
        # "HLT_e17_lhvloose",
        # "HLT_e20_lhvloose",
        # "HLT_e20_lhvloose_L1EM12",
        "HLT_e24_lhvloose_L1EM18VH",
        # "HLT_e24_lhvloose_L1EM20VH",
        # "HLT_e25_lhvloose_L1EM15",
        # "HLT_e26_lhvloose_L1EM20VH",
        # "HLT_e30_lhvloose_L1EM15",
        # "HLT_e40_lhvloose",
        "HLT_e50_lhvloose_L1EM15",
        # # "HLT_e60_lhloose",
        # "HLT_e60_lhvloose",
        # # "HLT_e70_lhloose",
        "HLT_e70_lhvloose",
        # "HLT_e80_lhvloose",
        "HLT_e100_lhvloose",
        # "HLT_e120_lhloose",
        # "HLT_e120_lhvloose",
        # "HLT_e140_lhloose",
        ]

    text = 'Trigger'.ljust(40)+'Total IntL, LAr fraction'.ljust(30)+'Total IntL with prescale'.ljust(30)+'Prescale'.ljust(20)+'\n'

    for trig in my_triggers :
        cmd = "iLumiCalc.exe --lumitag=OflLumi-13TeV-001 --livetrigger=L1_EM12 --trigger=%s --xml=%s --lar --lartag=LARBadChannelsOflEventVeto-RUN2-UPD4-04"%(trig,options.grl)
        print cmd
        output = os.popen(cmd).readlines()
        total_int = 0
        recorded_int = 0
        #print output
        for i in output :
            i = i.replace('\n','')
            # if 'WARNING' in i :
            #     print i
            # if 'ERROR' in i :
            #     print i
            #if 'Total IntL after livefraction' in i :
            if 'Total IntL after LAr fraction' in i :
                # print trig
                thing = i.split()[-1].replace('e','E')
                #thing = ''.join(list(a if a in '.0123456789E+e' else '' for a in thing))
                thing = repr(thing).replace('\'','').replace('\\x1b[0m','')
                total_int = float(thing)
                # print i
            if 'Total IntL recorded' in i :
                thing = i.split()[-1].replace('e','E')
                thing = repr(thing).replace('\'','').replace('\\x1b[0m','')
                recorded_int = float(thing)
                # print i
        text += trig.ljust(40)+('%2.2f'%total_int).rjust(20)+' '*10+('%2.2f'%recorded_int).rjust(20)+' '*10

        if recorded_int :
            text += ('%2.2f'%(float(total_int/recorded_int))).rjust(10)+' '*10+'\n'
        else :
            text += '0'.rjust(20)+' '*10+'\n'

    print text
    print 'done.'

if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()

    p.add_option('--grl',type  ='string',default='',dest='grl',help='GRL xml file')
    options,args = p.parse_args()

    main(options)

#!/usr/bin/env python

# 2018: now using:
# asetup 20.7.8.6,here
# svn co svn+ssh://svn.cern.ch/reps/atlasoff/LumiBlock/LumiCalc/tags/LumiCalc-00-04-23
# If you see: "Invalid trigger: [HLT_j360] - will proceed with no trigger defined!"
# Then it is because you are not using this tag probably
#
# Older:
# asetup 20.1.5.12,gcc48,here
# asetup 20.1.7.1,gcc48,here
# Using svn+ssh://svn.cern.ch/reps/atlasoff/LumiBlock/LumiCalc/tags/LumiCalc-00-04-07

import os,string

def main(options) :

    my_triggers = []

    if options.trigger :
        my_triggers.append(options.trigger)
        lumitag = options.lumitag
        livetrigger = options.livetrigger
        lartag = options.lartag

    if options.file :
        my_trigger_file = open(options.file).readlines()
        for i in my_trigger_file :
            i = i.replace('\n','')
            if not i :
                continue
            if 'lumitag' in i :
                lumitag = i.split()[-1]
            if 'livetrigger' in i :
                livetrigger = i.split()[-1]
            if 'lartag' in i :
                lartag = i.split()[-1]
            if '#' not in i :
                my_triggers.append(i.rstrip())

    for i in my_triggers :
        print i

    # my_triggers += [
    #     "HLT_e24_lhmedium_iloose_L1EM18VH",
    #     "HLT_e24_lhmedium_iloose_L1EM20VH",
    #     "HLT_e60_lhmedium",
    #     # # "HLT_e5_lhloose",
    #     "HLT_e5_lhvloose",
    #     # # "HLT_e9_lhloose",
    #     "HLT_e10_lhvloose_L1EM7",
    #     # # "HLT_e12_lhloose",
    #     # "HLT_e12_lhvloose_L1EM10VH",
    #     # # "HLT_e15_lhloose_L1EM13VH",
    #     # "HLT_e15_lhvloose_L1EM13VH",
    #      "HLT_e15_lhvloose_L1EM7",
    #     # "HLT_e17_lhloose",
    #     # "HLT_e17_lhvloose",
    #     # "HLT_e20_lhvloose",
    #     # "HLT_e20_lhvloose_L1EM12",
    #     "HLT_e24_lhvloose_L1EM18VH",
    #     # "HLT_e24_lhvloose_L1EM20VH",
    #     # "HLT_e25_lhvloose_L1EM15",
    #     # "HLT_e26_lhvloose_L1EM20VH",
    #     # "HLT_e30_lhvloose_L1EM15",
    #     # "HLT_e40_lhvloose",
    #     "HLT_e50_lhvloose_L1EM15",
    #     # # "HLT_e60_lhloose",
    #     # "HLT_e60_lhvloose",
    #     # # "HLT_e70_lhloose",
    #     "HLT_e70_lhvloose",
    #     # "HLT_e80_lhvloose",
    #     "HLT_e100_lhvloose",
    #     # "HLT_e120_lhloose",
    #     # "HLT_e120_lhvloose",
    #     # "HLT_e140_lhloose",
    #     ]

    # my_triggers = [
    #     'HLT_e5_etcut',
    #     'HLT_e10_etcut_L1EM7',
    #     'HLT_e15_etcut_L1EM7',
    #     'HLT_e20_etcut_L1EM12',
    #     'HLT_e25_etcut_L1EM15',
    #     'HLT_e30_etcut_L1EM15',
    #     'HLT_e40_etcut_L1EM15',
    #     'HLT_e50_etcut_L1EM15',
    #     'HLT_e60_etcut',
    #     # 'HLT_e70_etcut', missing?
    #     'HLT_e80_etcut',
    #     'HLT_e100_etcut',
    #     'HLT_e120_etcut',
    #     ]

    # my_triggers = [
    #     'HLT_e5_lhvloose',
    #     'HLT_e10_lhvloose_L1EM7',
    #     'HLT_e15_lhvloose_L1EM7',
    #     'HLT_e20_lhvloose',
    #     'HLT_e25_lhvloose_L1EM15',
    #     'HLT_e30_lhvloose_L1EM15',
    #     'HLT_e40_lhvloose_L1EM15',
    #     'HLT_e50_lhvloose_L1EM15',
    #     'HLT_e70_lhvloose',
    #     'HLT_e80_lhvloose',
    #     'HLT_e100_lhvloose',
    #     'HLT_e120_lhvloose',
    #     ]

    text_header = 'Trigger'.ljust(40)+'Total IntL, LAr fraction'.ljust(30)+'Total IntL with prescale'.ljust(30)+'Prescale'.ljust(20)+'\n'
    print text_header

    text = text_header

    for trig in my_triggers :
        cmd = "iLumiCalc.exe --lumitag=%s --livetrigger=%s --trigger=%s --xml=%s --lar --lartag=%s"%(lumitag,livetrigger,trig,options.grl,lartag)
        print cmd
        # import sys
        # sys.exit()
        output = os.popen(cmd).readlines()
        if not output :
            import sys; sys.exit()
            continue
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
        text_trig = trig.ljust(40)+('%2.2f'%total_int).rjust(20)+' '*10+('%2.2f'%recorded_int).rjust(20)+' '*10

        if recorded_int :
            text_trig += ('%2.2f'%(float(total_int/recorded_int))).rjust(10)+' '*10+'\n'
        else :
            text_trig += '0'.rjust(20)+' '*10+'\n'

        a = open('results_%s_%s.txt'%(options.file.replace('.txt',''),trig),'w')
        a.write(text_header+'\n')
        a.write(text_trig+'\n')
        a.close()

        print text_trig
        text += text_trig

    print text
    print 'done.'

if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()

    p.add_option('--grl'    ,type='string',default='',dest='grl'    ,help='GRL xml file')
    p.add_option('--file'   ,type='string',default='',dest='file'   ,help='File containing the triggers')
    p.add_option('--trigger',type='string',default='',dest='trigger',help='trigger')
    p.add_option('--lumitag',type='string',default='',dest='lumitag',help='lumitag option')
    p.add_option('--livetrigger',type='string',default='',dest='livetrigger',help='livetrigger option')
    p.add_option('--lartag',type='string',default='',dest='lartag',help='lartag option')

    # In the file, you need these three lines (including "#")
    # # lumitag OflLumi-13TeV-001
    # # livetrigger L1_EM24VHI
    # # lartag LARBadChannelsOflEventVeto-RUN2-UPD4-04

    options,args = p.parse_args()

    main(options)

import os
import sys
import fnmatch
import time
import datetime
import socket
from itertools import product
from genericUtils.PyGenericUtils import getFile,getTree
from genericUtils.ProcessManager import GetInHMS,kBatchLocal,condorSubmit,BigHadd,AggregatePlots
###################
# Class PyParallelize - intended for handling multiple jobs, splitting into subjobs.
# - addMenu
# - addAlg
# - addDataset
###################
class PyParallelize :
    def __init__(self,script,p): # p = parser

        self.p = p

        from ROOT import gROOT
        gROOT.SetBatch(True)

        self.script = script
        self.debug = False

        self.copyWaitDir = '/disk/userdata00/atlas_data2/%s/veto'%os.getenv('USER')
        if not os.path.isdir(self.copyWaitDir) :
            os.mkdir(self.copyWaitDir)

        # for child processes
        p.add_option('--child' ,action='store_true',default=False     ,dest='child' ,help='Child process?')
        p.add_option('--nloop' ,type  ='int'       ,default=    0     ,dest='nloop' ,help='Loop number (from 0)')
        p.add_option('--out'   ,type  ='string'    ,default='out.root',dest='out'   ,help='Output file' )
        p.add_option('--first' ,type  ='int'       ,default=    0     ,dest='first' ,help='First Event')
        p.add_option('--last'  ,type  ='int'       ,default=   -1     ,dest='last'  ,help='Last Event')

        # for use in parent processes
        p.add_option('--n'        ,type='int'         ,default=-1             ,dest='n'       ,help='N events')
        p.add_option('--runmode'  ,type='string'      ,default='condor'       ,dest='runmode' ,help='Run mode (kbatch,condor)')
        p.add_option('--nosubmit' ,action='store_true',default=False          ,dest='nosubmit',help='Is a bkg file?')
        p.add_option('--steps'    ,type='string'      ,default='0,1,2,3,4,5,6',dest='steps'   ,help='Parent job steps')
        p.add_option('--hadd'     ,action='store_true',default=False          ,dest='hadd'    ,help='Force hadd 0')
        p.add_option('--hadd0'    ,action='store_true',default=False          ,dest='hadd0'   ,help='Force hadd 0')
        p.add_option('--hadd1'    ,action='store_true',default=False          ,dest='hadd1'   ,help='Force hadd 1')
        p.add_option('--hadd2'    ,action='store_true',default=False          ,dest='hadd2'   ,help='Force hadd 2')
        # to be deprecated
        p.add_option('--firstloop',type='int'   ,default=0       ,dest='firstloop',help='First loop to execute')
        p.add_option('--lastloop' ,type='int'   ,default=99      ,dest='lastloop' ,help='Last loop to execute')

        # general purpose
        p.add_option('--dir'           ,type='string',default='test'   ,dest='dir'           ,help='Output directory' )
        p.add_option('--config-default',type='string',default='default',dest='config_default',help='default menu/alg configs')
        p.add_option('--nevtsperproc'  ,type='int'   ,default=int(4e5) ,dest='nevtsperproc'  ,help='Number of events per subprocess')
        p.add_option('--treename'      ,type='string',default='photon'              ,dest='treename'      ,help='Tree name (e.g. egamma)')

        # message handler
        p.add_option('--verbose','-v',action='count'     ,default=0                  ,help='verbosity')
        p.add_option('--debug'       ,action='store_true',default=False,dest='DEBUG' ,help='Turn on debug')

        (self.options,self.args) = p.parse_args()
        self.submit = not self.options.nosubmit

        
        self.makeOutputDirectories(self.options)
        self.SetupBatch(self.options)
        
        return

    def parse_args(self,p) :

        (options,args) = p.parse_args()

        #
        # do some additional parsing
        #
        self.submit = not self.options.nosubmit
        options.parent = not options.child

        #
        # The standard nomenclature for job steering
        #
        options.submit_loop_0  = (options.parent and '0' in options.steps)
        options.run_loop_0     = (options.child and options.nloop == 0)
        options.run_hadd_0     = options.hadd0 or (options.parent and '0' in options.steps) or options.hadd
        options.run_analyze_0  = (options.parent and '1' in options.steps)
        options.submit_loop_1  = (options.parent and '2' in options.steps)
        options.run_loop_1     = (options.child and options.nloop == 1)
        options.run_hadd_1     = options.hadd1 or (options.parent and '2' in options.steps)
        options.run_analyze_1  = (options.parent and '3' in options.steps)
        options.submit_loop_2  = (options.parent and '4' in options.steps)
        options.run_loop_2     = (options.child and options.nloop == 2)
        options.run_hadd_2     = options.hadd2 or (options.parent and '4' in options.steps)
        options.run_analyze_2  = (options.parent and '5' in options.steps)

        self.makeOutputDirectories(options)

        self.options = options
        self.args = args
        return (self.options,self.args)

    def SetupBatch(self,options) :
        #
        # Set up batch system
        #
        if options.runmode == 'kbatch' :
            self.Batch = kBatchLocal()
        elif options.runmode == 'condor' :
            self.Batch = condorSubmit()
        
        return

    def deleteFilesFromLocal(self,args) :
        if not self.options.child :
            return
        if not (self.options.runmode == 'condor') :
            return

        #
        # Please! Do not delete the original file!
        #
        for arg in args :
            if '/' in arg : continue
            os.system('rm %s'%arg)

        return

    def copyFilesToLocal(self,args) :
        if not self.options.child :
            return args
        if not (self.options.runmode == 'condor') :
            return args
        if (socket.gethostname() == 'at3i00.hep.upenn.edu') :
            return args

        while len(os.listdir(self.copyWaitDir)) > 19 :
            print 'Waiting to copy files.'
            time.sleep(15)

        ctime = datetime.datetime.now()
        thetime = ctime.strftime('%Y-%m-%d_%H-%M-%S.%f')
        id = self.options.out.split('/')[-1].replace('.root','')
        self.copyWaitName = '%s/%s%s.log'%(self.copyWaitDir,thetime,id)
        file = open(self.copyWaitName,'w')
        file.write(self.copyWaitName+'\n')
        file.close()

        new_args = []
        for arg in args :
            new_arg = arg.replace('/','_')
            print 'cp %s %s'%(arg,new_arg)
            os.system('cp %s %s'%(arg,new_arg))
            print 'os.getcwd()',os.getcwd()
            print 'os.listdir(.)'
            print os.listdir('.')
            new_args.append(new_arg)

        print '########################################################'
        print 'OLD ARGS:'
        print args
        print 'NEW ARGS:'
        print new_args
        print '########################################################'

        if os.path.isfile(self.copyWaitName) :
            os.remove(self.copyWaitName)

        return new_args

    def Reset(self,options,args) :
        self.options = options
        self.args = args
        self.submit = not self.options.nosubmit
        if self.options.dir[0] != '/' : self.options.dir = os.getcwd()+'/'+self.options.dir
        if self.options.runmode == 'kbatch' :
            self.Batch = kBatchLocal()
        elif self.options.runmode == 'condor' :
            self.Batch = condorSubmit()
        self.makeOutputDirectories()
        return

    def makeOutputDirectories(self,options) :

        if options.dir[0] != '/' : options.dir = os.getcwd()+'/'+options.dir
        self.dirs = dict()
        self.dirs['outdir']     = options.dir
        self.dirs['tmvadir']    = options.dir+'/TMVA/'
        self.dirs['logdir']     = options.dir+'/logs/'
        self.dirs['scriptsdir'] = options.dir+'/scripts/'
        self.dirs['outputdir']  = options.dir+'/output/'
        self.dirs['plotdir']    = options.dir+'/plots/'
        self.dirs['inputdir']   = options.dir+'/input/'
        if not os.path.isdir(self.dirs['outdir']) :  os.mkdir(self.dirs['outdir'])
        for d in self.dirs : 
            if not os.path.isdir(self.dirs[d]) :
                os.mkdir(self.dirs[d])

        return

    def hadd(self,nloop) :
        hadd_id = self.getFileName(nloop)
        print 'Big hadd:',self.dirs['outputdir'],hadd_id,hadd_id+'.root'
        BigHadd(self.dirs['outputdir'],hadd_id,hadd_id+'.root')        

    def getJobResults(self,nloop) :
        return getFile(self.dirs['outputdir']+self.getFileName(nloop)+'.root')

    def aggregate(self,nloop) :
        agg_id = self.getFileName(nloop)
        print 'Aggregate:',self.dirs['outputdir'],agg_id,agg_id+'.root'
        AggregatePlots(self.dirs['outputdir'],agg_id,agg_id+'.root')
        return
        
    def getFileName(self,nloop,input_id=None,proc=None) :
        scr = self.script.replace('.py','')
        if input_id != None and proc != None :
            return scr + '_loop%02d_%s_%02d'%(nloop,input_id,proc)
        elif input_id != None :
            return scr + '_loop%02d_%s'%(nloop,input_id)
        else :
            return scr + '_loop%02d'%(nloop)

    def submitJobsSpecialBinning(self,nloop,optsdict,runmode='',script='',extraopts=[]) :
        #
        # Must specify root files in config.
        #
        if not runmode : runmode = self.options.runmode
        if not script : script = self.script
        optsnames = []
        optsvals = []
        for k in sorted(optsdict.keys()) :
            optsnames.append(k)
            optsvals.append(optsdict[k])

        for i in product(*optsvals) :
            runcmd = ['python',script]
            runcmd += ['--child']
            runcmd += ['--nloop',str(nloop)]
            runcmd += self.getBatchRunOpts(optsnames)
            input_id = ''
            for j in range(len(optsnames)) :
                input_id += optsnames[j].replace('-','')+str(i[j])
                runcmd += [optsnames[j],str(i[j])]
            outfile = self.dirs['outputdir']+self.getFileName(nloop,input_id)+'.root'
            runcmd += ['--out',outfile]
            outputlog = self.dirs['logdir']+self.getFileName(nloop,input_id)
            if self.debug or not self.submit : print ' '.join(runcmd)
            if self.submit : self.Batch.addJob(runcmd,outputlog)
        return

    def submitJobs(self,filestrlist,nloop,runmode='',script='',extraopts=[]) :
        if True in list('*' in filestr for filestr in filestrlist) :
            self.submitJobsWildcardFileList(filestrlist,nloop,runmode,script,extraopts)
        else :
            self.submitJobsRegular(filestrlist,nloop,runmode,script,extraopts)
        return

    def submitJobsRegular(self,filestrlist,nloop,runmode='',script='',extraopts=[]) :

        if not runmode : runmode = self.options.runmode
        if not script : script = self.script

        for fk in range(len(filestrlist)) :
            file = getFile(filestrlist[fk])
            tree = getTree(file,self.options.treename)
            if self.options.n <=0 : self.options.n = int(1e9)
            nevts = int(min(tree.GetEntries(),self.options.n))

            nsubprocs = int(nevts)/int(self.options.nevtsperproc)+1
            file.Close()

            for proc in range(nsubprocs) :

                input_id  = filestrlist[fk].replace('.root','').split('/')[-1]
                outputlog = self.dirs['logdir']+self.getFileName(nloop,input_id,proc)
                outfile   = self.dirs['outputdir']+self.getFileName(nloop,input_id,proc)+'.root'
                #
                firstevt = self.options.nevtsperproc*proc
                lastevt  = self.options.nevtsperproc*(proc+1)
                runcmd = ['python',script]
                runcmd += self.getBatchRunOpts()
                runcmd += ['--child']
                runcmd += ['--nloop'    ,str(nloop)]
                runcmd += ['--first'    ,str(firstevt)]
                runcmd += ['--last'     ,str(lastevt)]
                runcmd += ['--out'      ,outfile]
                if extraopts : runcmd += extraopts

                runcmd += [str(filestrlist[fk])]
                if self.debug or not self.submit : print ' '.join(runcmd)
                if self.submit : self.Batch.addJob(runcmd,outputlog)

        if not self.submit : sys.exit()
        return
    #
    # New Batch script
    #
    def submitJobsWildcardFileList(self,filestrlist,nloop,runmode='',script='',extraopts=[]) :

        if not runmode : runmode = self.options.runmode
        if not script : script = self.script

        for i,filestr in enumerate(filestrlist) :
            print 'filestr:',filestr
            filetup = self.getFiles(filestr)

            c,eventcounter,subfiles = -1,0,[]
            for file,nevents in filetup :
                c += 1
                eventcounter += nevents
                subfiles.append(file)
                if eventcounter < self.options.nevtsperproc and (file != filetup[-1][0]) :
                    continue
                else :
                    #
                    # submit
                    #
                    input_id = 'File%02d'%i
                    if 'ttbar' in subfiles[0]      : input_id = 'ttbar'
                    elif 'ztt' in subfiles[0]      : input_id = 'ztt'
                    #elif 'zee' in subfiles[0]      : input_id = 'zee'
                    #elif 'wminenu' in subfiles[0]  : input_id = 'wminenu'
                    #elif 'wplusenu' in subfiles[0] : input_id = 'wplusenu'
                    #elif 'mc12' in subfiles[0]     : input_id = 'mc12'
                    elif 'samesign' in subfiles[0] : input_id = 'samesign'
                    elif 'EWR' in subfiles[0]      : input_id = 'EWR'
                    elif 'signal' in subfiles[0]   : input_id = 'signal'
                    input_id += 'Group%05d'%c
                    outputlog = self.dirs['logdir']+self.getFileName(nloop,input_id)
                    outfile   = self.getFileName(nloop,input_id)+'.root'
                    runcmd = ['python',script]
                    runcmd += self.getBatchRunOpts()
                    runcmd += ['--child']
                    runcmd += ['--nloop'    ,str(nloop)]
                    runcmd += ['--out'      ,self.dirs['outputdir']+outfile]
                    if extraopts : runcmd += extraopts

                    runcmd += subfiles
                    if self.debug or not self.submit : print ' '.join(runcmd)
                    if self.submit :  self.Batch.addJob(runcmd,outputlog)
                    #
                    # reset
                    #
                    eventcounter,subfiles = 0,[]
        return
        
    #
    # Batch helpers
    #
    def getFiles(self,filestring) :
        #
        # Return a tuple of (files, # events per file)
        #
        filetup = []
        #
        # check for a summary list 
        #
        #self.debug = True
        basedir = filestring.replace('.root','').replace('*','')
        if self.debug : print basedir
        if 'filesummary.txt' in os.listdir(basedir) :
            tup_from_file = open(os.path.join(basedir,'filesummary.txt')).readlines()
            for tup in tup_from_file :
                tup.replace('\n','')
                if not tup : continue
                a = tup.split(',')
                filetup.append((a[0],int(a[1])))
        #
        elif '*' in filestring :
            ref_list_of_branches = []
            known_problems = []
            filesummary = open(os.path.join(basedir,'filesummary.txt'),'w')
            for tup in os.walk(basedir) :
                if self.debug : print tup
                for file in sorted(tup[2]) :
                    if self.debug : print file
                    if fnmatch.fnmatch(file, '*.root*'):
                        fileFullPath = os.path.join(tup[0],file)
                        f = getFile(fileFullPath)
                        tree = getTree(f,self.options.treename)
                        nentries = tree.GetEntries()
                        #
                        list_of_branches = list(a.GetName() for a in tree.GetListOfBranches())
                        if ref_list_of_branches :
                            for br in list_of_branches :
                                if br not in ref_list_of_branches and br not in known_problems :
                                    print br,'from this tree is not in reference list of branches'
                                    known_problems.append(br)
                            for br in ref_list_of_branches :
                                if br not in list_of_branches and br not in known_problems:
                                    print br,'is in reference, but not in current tree.'
                                    known_problems.append(br)
                        else :
                            ref_list_of_branches = list_of_branches
                        #
                        f.Close()
                        if self.debug : print 'file with %08d entries:'%nentries,'/'.join(fileFullPath.split('/')[-2:])
                        filetup.append((fileFullPath,nentries))
                        filesummary.write(fileFullPath+','+str(nentries)+'\n')
                        if not len(filetup)%50 : print 'Processed',len(filetup),'files...'
            filesummary.close()
        #
        else :
            f = getFile(filestring)
            tree = getTree(f,self.options.treename)
            nentries = tree.GetEntries()
            filetup.append((filestring,nentries))

        return filetup

    def getBatchRunOpts(self,notthese=[]) :
        notthese = list(a.replace('-','') for a in notthese)
        optionlist = []
        theoptions = vars(self.options)
        for k in theoptions.keys() :
            if type(theoptions[k]) == type(False) or type(theoptions[k] == type(None)):
                if not theoptions[k] : continue # no false flags
            if theoptions[k] == '' : continue
            if k in ['nloop','first','last','rootfiles','out'] : continue
            if k in ['firstloop','lastloop','nevtsperproc','nosubmit'] : continue
            if k in ['steps'] : continue
            if k in notthese : continue
            if k not in self.p.defaults.keys() : continue
            if theoptions[k] == self.p.defaults[k] : continue
            if self.debug : print 'Adding option',k
            if type(theoptions[k]) == type(True) :
                optionlist += ['--'+k.replace('_','-')]
            else :
                optionlist += ['--'+k.replace('_','-'),str(theoptions[k])]        

        return optionlist

    def wait(self) :
        self.Batch.wait()

    def checkCondor(self,runmode) :
        pass

        return
    

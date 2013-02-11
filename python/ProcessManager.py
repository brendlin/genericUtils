import os
from subprocess import PIPE,STDOUT
from sys import stdout
import time   # time accounting
import shlex, subprocess # subprocessing
from ROOT import TFile,TObject
from IsEMOptTools import MakeDirV2

#--------------------------------------------------------------------------------
class kBatchLocal :
    def __init__(self,maxnjobs=13) :
        self.outfiles = []
        self.errfiles = []
        self.subprocs = []
        self.maxnjobs = maxnjobs
        self.start_time = time.time()

    def addJob(self,cmd,logname,doprint=True) :
        # command in list form
        self.outfiles.append(open(logname+'.log','w'))
        self.errfiles.append(open(logname+'.err','w'))
        self.errfiles[-1].write('\n\n'+' '.join(cmd)+'\n\n')
        self.outfiles[-1].write('\n\n'+' '.join(cmd)+'\n\n')
        self.poll()
        #print logname
        if doprint : print ' '.join(cmd)
        time.sleep(5)
        self.subprocs.append(subprocess.Popen(cmd,stdout=self.outfiles[-1],stderr=self.errfiles[-1]))
        return

    def poll(self) :
        for i in range(1000000) :
            njobs = 0
            for subproc in self.subprocs :
                njobs += 1 if (subproc.poll() == None) else 0
            if njobs < self.maxnjobs :
                print 'njobs:',njobs,'. Adding.'
                break
            else :
                stdout.write("\rWaiting for jobs to clear: %d (%s)" % (njobs,GetInHMS(time.time() - self.start_time)))
                stdout.flush()
                time.sleep(5)
        return

    def wait(self) :
        for i in range(1000000) :
            nleft = 0
            for subproc in self.subprocs :
                nleft += 1 if (subproc.poll() == None) else 0
            if nleft == 0 :
                break
            else :
                stdout.write("\rJobs left: %d (%s)" % (nleft,GetInHMS(time.time() - self.start_time)))
                stdout.flush()
                time.sleep(5)
        print
        return

#--------------------------------------------------------------------------------
class condorSubmit :
    def __init__(self,maxnjobs=15) :
        #self.outfiles = []
        #self.errfiles = []
        self.subprocs = []
        self.jobfiles = []
        self.maxnjobs = maxnjobs
        self.start_time = time.time()
        self.jobids = []

    def addJob(self,cmd,logname) :
        # command in list form
        self.jobfiles.append(open(logname+'.job','w'))

        self.jobfiles[-1].write('universe   = vanilla'+'\n')
        self.jobfiles[-1].write('Executable = '+cmd[1]+'\n')
        self.jobfiles[-1].write('Initialdir = '+os.getcwd()+'\n')
        self.jobfiles[-1].write('getenv     = True'+'\n')
        self.jobfiles[-1].write('output     = '+logname+'.out\n')
        self.jobfiles[-1].write('error      = '+logname+'.err\n')
        self.jobfiles[-1].write('log        = '+logname+'.log\n')
        self.jobfiles[-1].write('arguments  = '+' '.join(cmd[2:])+'\n')
        self.jobfiles[-1].write('should_transfer_files = YES'+'\n')
        self.jobfiles[-1].write('when_to_transfer_output = ON_EXIT_OR_EVICT'+'\n\n')
        self.jobfiles[-1].write('queue'+'\n\n')

        self.jobfiles[-1].close()

        print 'condor_submit '+logname+'.job'
        #os.system('condor_submit '+logname+'.job')
        jobs = subprocess.Popen('condor_submit '+logname+'.job',shell=True,stdout=subprocess.PIPE)
        self.jobids.append(jobs.communicate()[0].split(' ')[-1].replace('.','').replace('\n',''))
        time.sleep(0.5)
        print 'job added.'
        return

    def wait(self) :
        for i in range(1000000) :
            jobs = subprocess.Popen('condor_q -submitter '+os.getenv('USER'),shell=True,stdout=subprocess.PIPE)
            # output = jobs.communicate()[0][35:]
            output = jobs.communicate()[0]
            #print output
            condor_error_msgs = ['contact the condor_collector','Failed to end classad message']
            if True in list(a in output for a in condor_error_msgs) :
                display = 'Condor Problem! Waiting...'
                stdout.write("\r%s: (%s) (%d jobs left in process)" % (display,GetInHMS(time.time() - self.start_time),len(self.jobids)))
                stdout.flush()
                time.sleep(5)
                continue
            c = -1
            for j in range(len(self.jobids)) :
                c += 1
                job = self.jobids[c]
                if job not in output :
                    self.jobids.remove(job)
                    c -= 1
            #if os.getenv('USER') not in output :
            #    break
            if not self.jobids : break
            else :
                display = output[35:].split('\n\n')[-1].rstrip('\n')
                stdout.write("\r%s: (%s) (%d jobs left in process)" % (display,GetInHMS(time.time() - self.start_time),len(self.jobids)))
                stdout.flush()
                time.sleep(5)
        print
        return

#--------------------------------------------------------------------------------
def BigHadd(dir,keyword,outname,nfilesperjob=5,tmpdir='/tmp/kurb/tmphadd/') :
    filelist = []
    filelist2 = []
    for i in os.listdir(dir) :
        if (keyword in i) and ('.root' in i) :
            if i == outname : continue
            if 'Iter' in i : continue
            filelist.append(dir+'/'+i)
    if not os.path.isdir(tmpdir) :
        os.mkdir(tmpdir)

    filelist.sort()
    Batch = kBatchLocal(13)

    # each iter
    for k in range(100) :
        hadd1 = ['hadd','-f']
        hadd2 = []
        nsubs = 0
        for file in filelist :
            i = filelist.index(file)
            hadd2.append(file)
            if (len(hadd2) == nfilesperjob) or (i == len(filelist)-1) :

                # output name
                if len(filelist) <= nfilesperjob :
                    tmpoutname = [tmpdir+'/'+outname]
                else :
                    #tmpoutname = [tmpdir+'/Iter%02d'+str(k)+'_'+str(nsubs)+'_'+outname % (k,nsubs)]
                    tmpoutname = [tmpdir+'/Iter%02d_%02d_%s' % (k,nsubs,outname)]
                    nsubs += 1

                filelist2 += tmpoutname
                Batch.addJob(hadd1+tmpoutname+hadd2,tmpoutname[0].replace('.root',''),doprint=False)
                hadd2 = []
                
        Batch.wait()
        if len(filelist2) == 1 : break

        filelist = []
        for file in filelist2 :
            filelist.append(file)
        filelist2 = []
        
    os.system('mv '+tmpdir+'/'+outname+' '+dir)
    print 'Hadd succeeded.'
    return

#--------------------------------------------------------------------------------
def AggregatePlots(dir,keyword,outname) : # outname does not include dir.
    filelist = []
    for i in os.listdir(dir) :
        if (keyword in i) and ('.root' in i) :
            if i == outname : continue
            filelist.append(dir+'/'+i)

    filelist.sort()
    
    def Copy(indir,outdir) :
        #print 'indir:',indir.GetName()
        #print 'outdir:',outdir.GetName()
        for i in indir.GetListOfKeys() :
            n = i.GetName()
            if not n : continue
            if i.GetClassName() == 'TDirectoryFile' :
                #print 'making dir',n
                MakeDirV2(outdir,n)
                Copy(indir.GetDirectory(n),outdir.GetDirectory(n))
            else :
                if n in list(a.GetName() for a in outdir.GetListOfKeys()) :
                    print 'Error! Hist already exists! Hadding it:',n
                    tmp = outdir.Get(n).Clone()
                    tmp.Add(i.ReadObj())
                    tmp.Write(tmp.GetName(),TObject.kOverwrite)
                    continue
                outdir.cd()
                i.ReadObj().Write()
        #print 'copy finsihed'
        return

    outfile = TFile(dir+'/'+outname,'recreate')
    for file in filelist :
        f = TFile(file,'read')
        Copy(f,outfile)

    outfile.Close()
    return

#--------------------------------------------------------------------------------
def lxBatch() :
    #
    # Not yet implemented.
    #
    return
    lsffilename = scriptsdir+'/NN_'+nn_scriptid+'.lsf'
    testlsf = open(lsffilename,'w')
    testlsf.write('source /afs/cern.ch/atlas/software/dist/AtlasSetup/scripts/asetup.sh '+AtlasVersion+',here\n')
    testlsf.write('mkdir '+basedir+'\n')
    testlsf.write('mkdir '+outdir+'\n')
    testlsf.write('mkdir '+tmvadir+'\n')
    testlsf.write('cd '+TESTAREA+'/egammaID/share\n')
    testlsf.write(' '.join(nncmd)+'\n')
    #testlsf.write(nn_eosmkdircmd+'\n')
    testlsf.write(rmcmd+'\n')
    #testlsf.write(copycmd+'\n')
    testlsf.close()
    nn_batchjob = 'bsub -J NN_'+nn_scriptid
    nn_batchjob += ' -o '+LOCALLOGDIR+'/NN_'+nn_scriptid+'.log'
    nn_batchjob += ' -q '+queue
    nn_batchjob += ' < '+lsffilename
    nn_batchjobs.append(nn_batchjob)
    if nn_outputname_bin in '__'.join(os.listdir('weights')) :
        print nn_outputname_bin,'exists; skipping training.'
        #continue
    print nn_batchjob
    os.system(nn_batchjob)

#--------------------------------------------------------------------------------
def eosManager() :
    return

#--------------------------------------------------------------------------------
def GetInHMS(seconds):
    seconds = int(seconds)
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

#--------------------------------------------------------------------------------
# Define waiting function
def wait(runMode,name,subprocs = 0) :
    if runMode == 'batch' :
        print 'Batch progress bar < =',
        while os.popen('bjobs -w').read().find(name) != -1 :
            print '=',
            time.sleep(15)
    elif runMode == 'local' :
        print 'waiting for local jobs to finish...'
        for subproc in subprocs :
            subproc.wait()
    print '>'
    return

#--------------------------------------------------------------------------------
def wait2(runMode,name,subprocs = 0,rmclass=False) :
    if runMode == 'batch' :
        print 'Batch progress bar < =',
        while os.popen('bjobs -w').read().find(name) != -1 :
            print '=',
            time.sleep(15)
    elif runMode == 'local' :
        jobsFinished = False
        #print 'waiting for local jobs to finish...'
        #while not jobsFinished :
        for i in range(1000000) :
            nleft = 0
            for subproc in subprocs :
                tmp = subproc.poll()
                nleft += 1 if (tmp == None) else 0
            if nleft == 0 :
                #jobsFinished = True
                break
            else :
                stdout.write("\rJobs left: %d (%s)" % (nleft,GetInHMS(i*15)))
                stdout.flush()
                if rmclass :
                    os.system('rm weights/*.class.C')
                time.sleep(15)
    print '>'
    return

#--------------------------------------------------------------------------------

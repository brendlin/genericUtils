import os
from subprocess import PIPE,STDOUT
from sys import stdout
import time   # time accounting
import shlex, subprocess # subprocessing
from ROOT import TFile,TObject
from genericUtils.PyGenericUtils import MakeDirV2
from genericUtils.PyConfigUtils import printConfigs

#--------------------------------------------------------------------------------
class kBatchLocal :
    def __init__(self,maxnjobs=15) :
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
        if doprint : print ' '.join(cmd)
        time.sleep(0.5)
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
        self.subprocs = []
        self.jobfiles = []
        self.maxnjobs = maxnjobs
        self.start_time = time.time()
        self.jobids = []

    def addJob(self,cmd,logname,Initialdir='') :
        # command in list form
        self.jobfiles.append(open(logname+'.job','w'))

        if not Initialdir : Initialdir = os.getcwd()

        self.jobfiles[-1].write('universe   = vanilla'+'\n')
        self.jobfiles[-1].write('Executable = '+cmd[1]+'\n')
        self.jobfiles[-1].write('Initialdir = '+Initialdir+'\n')
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
        jobs = subprocess.Popen('condor_submit '+logname+'.job',shell=True,stdout=subprocess.PIPE)
        self.jobids.append(jobs.communicate()[0].split(' ')[-1].replace('.','').replace('\n',''))
        time.sleep(0.5)
        print 'job added.'
        return

    def wait(self) :
        for i in range(1000000) :
            if not self.jobids : break
            jobs = subprocess.Popen('condor_q -submitter '+os.getenv('USER'),shell=True,stdout=subprocess.PIPE)
            output = jobs.communicate()[0]
            if not output.replace(' ','') :
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
            if not self.jobids : break
            else :
                display = output[35:].split('\n\n')[-1].rstrip('\n')
                stdout.write("\r%s: (%s) (%d jobs left in process)" % (display,GetInHMS(time.time() - self.start_time),len(self.jobids)))
                stdout.flush()
                time.sleep(5)
        print
        return

#--------------------------------------------------------------------------------
def chunkList(orig,nperchunk) :
    new = []
    for i in range(0,len(orig),nperchunk) :
        new.append(orig[i:i+nperchunk])
    return new

#--------------------------------------------------------------------------------
def BigHadd(dir,keyword,outname,nfilesperjob=5,tmpdir='') :
    #
    # if outname does not have a '/' in it, then it is put into the directory 'dir'.
    # Otherwise it is put in whatever directory you specified.
    #
    import os
    movetodir = not ('/' in outname)
    if (not movetodir) and (not (outname[0] == '/')) :
        outname = os.path.abspath(outname)
    if not os.path.exists(os.path.dirname(outname)) :
        print 'Error! %s does not exist.'%(os.path.dirname(outname))
        return

    USER = os.getenv('USER')
    if not tmpdir :
        tmpdir = '/tmp/%s/tmphadd/'%USER
    from time import strftime,localtime
    tmpdir = tmpdir+strftime("%d_%m_%Y_%H_%M_%S", localtime())+'/'
    os.system('mkdir -p %s'%(tmpdir))
    filelist = []
    filelist_nextiter = []
    for i in os.listdir(dir) :
        if (keyword in i) and ('.root' in i) :
            if i == outname : continue
            if 'Iter' in i : continue
            filelist.append(os.path.abspath(dir+'/'+i))

    filelist.sort()
    Batch = kBatchLocal(15)

    # each iter
    for k in range(10) :
        nsubs = 0
        file_chunks = chunkList(filelist,nfilesperjob)
        for i,file_chunk in enumerate(file_chunks) :
            
            if len(filelist) <= nfilesperjob :
                tmpoutname = os.path.abspath(tmpdir+'/'+outname)
                if not movetodir :
                    tmpoutname = outname
                logname = os.path.abspath(tmpdir+'/Iter%02d_%02d_%s'%(k,nsubs,outname.replace('/','_')))
                logname = logname.replace('.root','')
            else :
                tmpoutname = os.path.abspath(tmpdir+'/Iter%02d_%02d_%s'%(k,nsubs,outname.replace('/','_')))
                logname = tmpoutname.replace('.root','')
                nsubs += 1

            filelist_nextiter.append(tmpoutname)
            cmd = ['hadd','-f',tmpoutname]+file_chunk
            print ' '.join(cmd)
            Batch.addJob(cmd,logname,doprint=False)

        Batch.wait()
        if len(filelist_nextiter) == 1 : break

        filelist = filelist_nextiter
        filelist_nextiter = []
        
    result = outname
    if movetodir :
        os.system('mv '+tmpdir+'/'+outname+' '+dir)
        result = os.path.abspath(dir+'/'+outname)
    print 'Hadd succeeded. Result is',result
    os.system('rm '+tmpdir+'/*')
    os.system('rmdir '+tmpdir)
    return


#--------------------------------------------------------------------------------
def CopyDirectoryContents(indir,outdir,keyword_plot='') :
    #print 'indir:',indir.GetName()
    #print 'outdir:',outdir.GetName()
    from ROOT import gROOT
    for i in indir.GetListOfKeys() :
        n = i.GetName()
        if not n : continue
        if i.GetClassName() == 'TDirectoryFile' :
            #print 'making dir',n
            MakeDirV2(outdir,n)
            CopyDirectoryContents(indir.GetDirectory(n),outdir.GetDirectory(n),keyword_plot)
        else :
            if keyword_plot and keyword_plot not in n : continue
            if n in list(a.GetName() for a in outdir.GetListOfKeys()) :
                print 'Warning: Hist already exists! Hadding it:',n
                tmp = outdir.Get(n).Clone()
                tmp.Add(i.ReadObj())
                outdir.cd()
                tmp.Write(tmp.GetName(),TObject.kOverwrite)
                gROOT.ProcessLine('delete %s'%n)
                continue
            outdir.cd()
            i.ReadObj().Write()
    #print 'copy finsihed'
    return

#--------------------------------------------------------------------------------
def SecureTransferSlot(copyWaitDir,outputfilename,nConcurrentFileTransfers=10) :
    import os,datetime
    while len(os.listdir(copyWaitDir)) > nConcurrentFileTransfers :
        print 'Waiting to copy files.'
        time.sleep(15)

    ctime = datetime.datetime.now()
    thetime = ctime.strftime('%Y-%m-%d_%H-%M-%S.%f')
    id = outputfilename.split('/')[-1].replace('.root','')
    copyWaitName = '%s/%s%s.log'%(copyWaitDir,thetime,id)
    file = open(copyWaitName,'w')
    file.write(copyWaitName+'\n')
    file.close()
    return copyWaitName

def ReleaseTransferSlot(copyWaitName) :
    if os.path.isfile(copyWaitName) :
        os.remove(copyWaitName)
    return

#--------------------------------------------------------------------------------
def CopyFilesToNode(args) :
    import os,subprocess
    new_args = []
    os.system('mkdir -p tempdir') # So condor doesn't transfer these files if the job fails

    for arg in args :
        ##
        ## SRM file name
        ##
        if 'srm://srm.hep.upenn.edu/' in arg :
            srm_filename = arg.replace('srm://srm.hep.upenn.edu/disk/space00/','root://hn.at3f//')
            new_arg = srm_filename.replace('root://hn.at3f//','')
            new_arg = new_arg.replace('/','_')
            new_arg = 'tempdir/'+new_arg
            cmd = 'xrdcp %s %s'%(srm_filename,new_arg) # note xrdcp!
            os.system(cmd)
            new_args.append(new_arg)
            continue

        ##
        ## Local, or Joey's linking thing.
        ##
        p = subprocess.Popen(["file", arg], stdout=subprocess.PIPE) # Finds where the link/file points
        newfilename = p.communicate()[0] # Reads in the previous result

        if not 'xrootd' in newfilename : # i.e. local file
            new_arg = arg.replace('/','_')
            new_arg = 'tempdir/'+new_arg
            os.system('cp %s %s'%(arg,new_arg)) # note cp!

        else : # i.e. file on SRM
            newfilename = newfilename[newfilename.find("`")+1:newfilename.find("'")] # Parse the text
            newfilename = newfilename.replace('/xrootd//srm/', 'root://hn.at3f//srm/') # For SRM
            new_arg = newfilename.replace('/','_') # For condor copying
            new_arg = 'tempdir/'+new_arg
            os.system('xrdcp %s %s'%(newfilename,new_arg)) # note xrdcp!

        new_args.append(new_arg)

    print '########################################################'
    print 'OLD ARGS:'
    print args
    print 'NEW ARGS:'
    print new_args
    print '########################################################'

    return new_args

#--------------------------------------------------------------------------------
def AggregatePlots(dir,keyword,outname,keyword_plot='') : # outname does not include dir.
    filelist = []
    for i in os.listdir(dir) :
        if (keyword in i) and ('.root' in i) :
            if i == outname : continue
            filelist.append(dir+'/'+i)

    filelist.sort()
    
    outfile = TFile(dir+'/'+outname,'recreate')
    for file in filelist :
        f = TFile(file,'read')
        CopyDirectoryContents(f,outfile,keyword_plot=keyword_plot)

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
def jobFinishedSendEmail(script,config,dir,eventselection='',time=''
                         ,configdicts=[]
                         ,sender=''
                         ,recipient='') :
    
    import os
    if not sender : sender = 'kBatch <%s@at3i00.upenn.edu>'%(os.getenv('USER'))
    
    if not recipient :
        recipient = os.getenv('EMAIL_RECIPIENT')
    if not recipient :
        print 'Job Notification Email Not Sent! To do so, set EMAIL_RECIPIENT environment variable.'
        return

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    subject = 'at3i00 %s, config %s, dir %s, complete.'%(script,config,dir)
    body    = 'script         : %sENTER'%script
    body   += 'config         : %sENTER'%config
    body   += 'dir            : %sENTER'%dir
    if eventselection :
        body   += 'eventselection : %sENTER'%eventselection
    if time :
        body   += 'elapsed time   : %sENTER'%time
    if configdicts :
        body   += printConfigs(configdicts,doPrint=False).replace('\n','ENTER')

    html  = '<html><font face=\"Courier New, Courier, monospace\">'
    html += body.replace('ENTER','<br>\n').replace(' ','&nbsp;')
    html += '</font></html>'

    body = body.replace('ENTER','\n')

    msg = MIMEMultipart('alternative')
    part1 = MIMEText(body, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    msg['Subject'] = subject
    msg['From']    = sender
    msg['To']      = recipient
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, [recipient], msg.as_string())
    s.quit()
    return

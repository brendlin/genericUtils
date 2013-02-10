import os
import subprocess
MYCASTOR = os.getenv('MYCASTOR')
MYCASTORROOT = os.getenv('MYCASTORROOT')

def main(DIR,GREP1,GREP2,OUTDIR) :

    files = subprocess.Popen('/afs/cern.ch/project/eos/installation/0.1.0-22d/bin/eos.select ls '+MYCASTOR+'/'+DIR+' | grep '+GREP1+' | grep '+GREP2,shell=True,stdout=subprocess.PIPE)
    output= files.communicate()[0].split('\n')
    for file in output:
        if file == '' : continue
        os.system('xrdcp '+MYCASTORROOT+'/'+DIR+'/'+file+' '+OUTDIR)

    return 0

if __name__ == "__main__":
    from optparse import OptionParser

    p = OptionParser()
    p.add_option('--dir',type='string',default='',dest='dir',help='dir')
    p.add_option('--grep1',type='string',default='\'\'',dest='grep1',help='grep1')
    p.add_option('--grep2',type='string',default='\'\'',dest='grep2',help='grep2')
    p.add_option('--outdir',type='string',default='\'\'',dest='outdir',help='outdir')
    (options,args) = p.parse_args()

    main(options.dir,options.grep1,options.grep2,options.outdir)

#!/bin/usr/env python
import os

def main(options,args) :

    for user in options.users.split(',') :
        cmd = 'rucio list-rules --account %s | grep UPENN_LOCALGROUPDISK'%(user)
        print cmd
        output = os.popen(cmd).readlines()

        print 'Making filename',"%s_deletion_script.txt"%(user)
        user_file = open("%s_deletion_script.txt"%(user),"w")
        
        user_dsets = []
        user_dset_nonumber = []
        for i in output :
            dset = i.split()[2]
            if ':' in dset :
                dset = dset.split(':')[1]
            if dset not in user_dsets :
                user_dsets.append(dset)
            #
            # extract the container name only
            #
            dset = '.'.join(dset.split('.')[:-1])
            dset = dset+'/'
            if dset not in user_dset_nonumber :
                user_dset_nonumber.append(dset)

        #
        # sort the full name by tag
        #       
        for i in range(len(user_dsets)) :
            tmp = user_dsets[i].split('.')
            user_dsets[i] = '.'.join(tmp[:-1])[::-1]+'.'+tmp[-1]
        user_dsets.sort()
        for i in range(len(user_dsets)) :
            tmp = user_dsets[i].split('.')
            user_dsets[i] = '.'.join(tmp[:-1])[::-1]+'.'+tmp[-1]
        for i in user_dsets :
            if options.tag in i :
                user_file.write('# dq2-delete-replicas %s UPENN_LOCALGROUPDISK\n'%(i))

        user_file.close()
        print 'file closed.'

        #
        # Sort the other list (user_dset_nonumber)
        #
        for i in range(len(user_dset_nonumber)) :
            user_dset_nonumber[i] = user_dset_nonumber[i][::-1]
        user_dset_nonumber.sort()
        for i in range(len(user_dset_nonumber)) :
            user_dset_nonumber[i] = user_dset_nonumber[i][::-1]

        #
        # get the size of a particular tag
        #
        user_summary = open("summary_%s.txt"%(user),"w")

        n = 0
        for i in user_dset_nonumber :
            if options.tag in i :
                user_summary.write('%s\n'%(i))
                cmd = 'dq2-ls -fpHL UPENN_LOCALGROUPDISK %s | grep total | grep size'%(i)
                output += os.popen(cmd).readlines()
                n += 1
            # if n > 2 : break

        size = 0
        for i in output :
            i = i.replace('\n','')
            if not len(i.split()) : continue
            if not 'total size' in i : continue
            factor = 1
            if   'GB'    in i : factor = 1.
            elif 'MB'    in i : factor = 0.001
            elif 'KB'    in i : factor = 0.000001
            elif 'bytes' in i : factor = 0.000000001
            else : 
                user_summary.write('ERROR do not understand %s\n'%(i))
            size += float(i.split()[-2])*factor
            
        user_summary.write('Total size of tag %s for user %s is %2.3f TB\n'%(options.tag,user,size/1000.))
        user_summary.close()
        
    print 'done'

if __name__ == "__main__":
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--tag',type  ='string',default='',dest='tag',help='tag that you want to check the size')
    p.add_option('--users',type  ='string',default='',dest='users',help='users (by grid name)')

    if not os.getenv('ATLAS_LOCAL_DQ2CLIENT_PATH') :
        print 'Error! localSetupDQ2Client and voms-proxy-init!'
        sys.exit()

    options,args = p.parse_args()

    main(options,args)


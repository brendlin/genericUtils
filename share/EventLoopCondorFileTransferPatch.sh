#!/bin/bash

cd $ROOTCOREBIN/../

echo ~~~
echo "Editing EventLoop/Root/BatchWorker.cxx"
echo ~~~

if grep -q "EventLoopCondorFileTransferPatch" EventLoop/Root/BatchWorker.cxx; then
    echo "Patch already applied. Did nothing."
    cd -
    return
fi

theheader="#include <SampleHandler\/DiskOutput.h>"
sed -i "s/$theheader/$theheader\\
#include \"TSystemDirectory.h\"/g" EventLoop/Root/BatchWorker.cxx

theline="      std::auto_ptr<TFile> inFile (TFile::Open (m_sample->files\[file\].c_str()));"
theline1="      \/\/std::auto_ptr<TFile> inFile (TFile::Open (m_sample->files\[file\].c_str()));"
sed -i "s/$theline/$theline1\\
      \/\/\\
      \/\/ This file has been edited by EventLoopCondorFileTransferPatch.sh to handle\\
      \/\/ file transfers\\
      \/\/\\
      char hostname\[1024\];\\
      hostname\[1023\] = \'\\\0\';\\
      gethostname(hostname, 1023);\\
      std::cout << \"Hostname is \" << hostname << std::endl;\\
      gSystem->MakeDirectory(\"tempdir\");\\
      gSystem->MakeDirectory((m_job->location+\"\/veto\").c_str());\\
      gSystem->Exec(\"ls\");\\
      \/\/ SRM File\\
      std::string orig_name = m_sample->files\[file\];\\
      std::string new_name = m_sample->files\[file\];\\
      std::string command;\\
      std::string vetodir = m_job->location+\"\/veto\";\\
      std::size_t found = new_name.find(\"root:\/\/hn.at3f\/\/srm\/\");\\
      if (found != std::string::npos) {\\
        new_name.replace(new_name.begin()+found,new_name.begin()+found+20,\"\");\\
      }\\
      found = new_name.find(\"\/\");\\
      while (found != std::string::npos){\\
        new_name.replace(new_name.begin()+found,new_name.begin()+found+1,\"_\");\\
        found = new_name.find(\"\/\");\\
      }\\
      command += \"xrdcp \";\\
      command += orig_name;\\
      command += \" tempdir\/\";\\
      command += new_name;\\
      std::cout << \"Old file name is \" << orig_name << std::endl;\\
      std::cout << \"New file name is \" << new_name << std::endl;\\
      std::cout << \"Copy command: \" << command << std::endl;\\
      std::cout << \"Job location: \" << m_job->location << std::endl;\\
      std::cout << \"Veto directory: \" << vetodir << std::endl;\\
      TSystemDirectory dir(vetodir.c_str(),vetodir.c_str());\\
      int nfiles = 0;\\
      while(true){ \\
        nfiles = dir.GetListOfFiles()->GetEntries();\\
        if (nfiles < 8+2) break; \/\/ Limit to 8 file transfers. \"..\" and \".\" are the +2\\
        std::cout << \"nfiles = \" << nfiles << \". waiting.\" << std::endl;\\
        sleep(5);\\
      }\\
      std::cout << \"Transfer begin for \" << new_name << std::endl;\\
      gSystem->Exec((\"touch \"+vetodir+\"\/\"+new_name).c_str());\\
      gSystem->Exec(command.c_str());\\
      gSystem->Exec((\"rm \"   +vetodir+\"\/\"+new_name).c_str());\\
      std::cout << \"Transfer end for \" << new_name << std::endl;\\
      std::auto_ptr<TFile> inFile (TFile::Open ((\"tempdir\/\"+new_name).c_str()));\\
      \/\//g" EventLoop/Root/BatchWorker.cxx

theline2="      algsEndOfFile ();"
sed -i "s/$theline2/$theline2\\
      inFile->Close();\\
      command = \"rm \";\\
      command += \" tempdir\/\";\\
      command += new_name;\\
      gSystem->Exec(command.c_str());/g" EventLoop/Root/BatchWorker.cxx

echo "Editing EventLoop/Root/BatchWorker.cxx done."

cd -

#!/bin/bash

cd $ROOTCOREBIN/../

echo ~~~
echo "Editing EventLoop/Root/BatchWorker.cxx"
echo ~~~

if grep -q "EventLoopCondorFileTransferPatch.sh" EventLoop/Root/BatchWorker.cxx; then
    echo "Patch already applied. Did nothing."
    cd -
    return
fi

theheader="#include <SampleHandler\/DiskOutput.h>"
sed -i "s/$theheader/$theheader\\
#include \"TSystemDirectory.h\"\\
#include <fstream>\\
#include <unistd.h>/g" EventLoop/Root/BatchWorker.cxx

theline="      std::unique_ptr<TFile> inFile = SH::openFile (m_sample->files\[file\], \*metaData());"
theline1="      \/\/std::unique_ptr<TFile> inFile = SH::openFile (m_sample->files\[file\], \*metaData());"
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
      \\
      \/\/ For local files\\
      std::size_t foundlocal = new_name.find(\"file:\/\/\");\\
      if (foundlocal != std::string::npos) {\\
        orig_name.replace(orig_name.begin()+foundlocal,orig_name.begin()+foundlocal+7,\"\");\\
        new_name.replace(new_name.begin()+foundlocal,new_name.begin()+foundlocal+7,\"\");\\
      }\\
      \\
      \/\/ For files stored on srm managed via a softlink from disk\\
      char buf_filelink\[1024\];\\
      std::size_t linkbufpos = ::readlink(orig_name.c_str(), buf_filelink, sizeof(buf_filelink)-1);\\
      if(linkbufpos != std::string::npos){\\
        buf_filelink\[linkbufpos\] = \'\\\0\';\\
        orig_name = std::string(buf_filelink);\\
        \\
        std::size_t replaceStr = orig_name.find(\"\/xrootd\/srm\/\");\\
        if(replaceStr != std::string::npos){\\
          orig_name.replace(orig_name.begin()+replaceStr, orig_name.begin()+replaceStr+12, \"\");\\
          orig_name = \"root:\/\/hn.at3f\/\/srm\/\" + orig_name;\\
        }\\
        new_name = orig_name;\\
      }\\
      \\
      std::string vetodir = m_job->location+\"\/veto\";\\
      std::string transfer_done_file = \"tempdir\/filetransfercomplete\";\\
      std::size_t found = new_name.find(\"root:\/\/hn.at3f\/\/srm\/\");\\
      if (found != std::string::npos) {\\
        new_name.replace(new_name.begin()+found,new_name.begin()+found+20,\"\");\\
      }\\
      found = new_name.find(\"\/\");\\
      while (found != std::string::npos){\\
        new_name.replace(new_name.begin()+found,new_name.begin()+found+1,\"_\");\\
        found = new_name.find(\"\/\");\\
      }\\
      std::string new_name_loc = \"tempdir\/\"+new_name;\\
      std::string vetofile = vetodir+\"\/\"+new_name;\\
      std::cout << \"Old file name is \" << orig_name << std::endl;\\
      std::cout << \"New file name is \" << new_name << std::endl;\\
      std::cout << \"Job location: \" << m_job->location << std::endl;\\
      std::cout << \"Veto directory: \" << vetodir << std::endl;\\
      TSystemDirectory dir(vetodir.c_str(),vetodir.c_str());\\
      int nfiles = 0;\\
      while(true){ \\
        nfiles = dir.GetListOfFiles()->GetEntries();\\
        if (nfiles >= 8+2) { \/\/ Limit to 8 file transfers. \"..\" and \".\" are the +2\\
          std::cout << \"nfiles = \" << nfiles << \". waiting.\" << std::endl;\\
          sleep(5); continue;\\
        }\\
        break;\\
      }\\
      std::fstream fs;\\
      \/\/fs.open (vetofile, std::fstream::in \| std::fstream::out \| std::fstream::app);\\
      fs.open(vetofile.c_str(),std::fstream::in | std::fstream::out | std::fstream::app);\\
      fs.close();\\
      TString command;\\
      char buffer[512];\\
      std::string popen_result = \"\";\\
      int ntries = 0;\\
      while(true){\\
        ntries ++;\\
        if (ntries>30){std::cout << \"Transfer failed 30 times. Exiting.\" << std::endl; break; }\\
        \\
        if(foundlocal != std::string::npos \&\& linkbufpos == std::string::npos){\\
          \/\/ i.e. local file that is not just a link\\
          command.Form(\"cp %s %s\",orig_name.c_str(),new_name_loc.c_str());\\
        }\\
        else{\\
          \/\/command.Form(\"xrdcp %s %s \&\& touch %s\",orig_name.c_str(),new_name_loc.c_str(),transfer_done_file.c_str());\\
          command.Form(\"xrdcp %s %s\",orig_name.c_str(),new_name_loc.c_str());\\
        }\\
        \\
        std::cout << \"Transfer begin for \" << new_name << std::endl;\\
        std::cout << command << std::endl;\\
        FILE* pipe = popen(command.Data(), \"r\"); sleep(5);\\
        if (!pipe) {\\
          std::cout << \"Error! xrd cmd failed.\" << std::endl; sleep(15);\\
          std::cout << \"Errno: \" << errno << std::endl;\\
          continue;\\
        }\\
        while(!feof(pipe)) { if(fgets(buffer, 512, pipe) != NULL) popen_result += buffer; }\\
        pclose(pipe);\\
        std::cout << \"Transfer end. xrd command result: \" << popen_result << std::endl;\\
        std::cout << \"Checking that file exists \" << \"tempdir\/\"+new_name << std::endl;\\
        \/\/if (std::ifstream(transfer_done_file.c_str())) { \\
        TFile* temp = TFile::Open(new_name_loc.c_str());\\
        if (!temp) { std::cout << \"File does not exist.\" << std::endl; sleep(10); continue; }\\
        if(!temp->IsZombie()) {\\
          temp->Close();\\
          std::cout << \"File exists: tempdir\/\" << new_name << std::endl;\\
          std::cout << \"Breaking out of queue after this many tries: \" << ntries << std::endl;\\
          break;\\
        } else {\\
          std::cout << \"Something went wrong. Closing file.\" << std::endl;\\
          temp->Close();\\
          std::cout << \"Something went wrong. Waiting 10s and Retrying.\" << std::endl;\\
          sleep(10);\\
        }\\
      }\\
      while(true){\\
        unlink((vetodir+\"\/\"+new_name).c_str());\\
        if (std::ifstream((vetodir+\"\/\"+new_name).c_str())) { \\
          std::cout << \"rm vetodir command failed. Retrying.\" << std::endl;\\
          sleep(5); continue;\\
        }\\
        break;\\
      }\\
      std::auto_ptr<TFile> inFile (TFile::Open ((\"tempdir\/\"+new_name).c_str()));\\
      \/\//g" EventLoop/Root/BatchWorker.cxx

theline2="      algsEndOfFile ();"
sed -i "s/$theline2/$theline2\\
      inFile->Close();\\
      while(true){\\
        \/\/unlink(transfer_done_file.c_str());\\
        unlink(new_name_loc.c_str());\\
        if (std::ifstream(transfer_done_file.c_str()) \|\|\\
            std::ifstream(new_name_loc.c_str())) { \\
          std::cout << \"rm ftc or root file command failed. Retrying.\" << std::endl;\\
          sleep(5); continue;\\
        }\\
        break;\\
      }\\
      \/\/gSystem->Exec(command.c_str());/g" EventLoop/Root/BatchWorker.cxx

echo "Editing EventLoop/Root/BatchWorker.cxx done."

cd -

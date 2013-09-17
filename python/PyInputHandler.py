##############################
#
#
#
##############################
import os
from ROOT import TChain, TFile, TTree

class Input:
    """


    """
    def __init__(self, config, messageHandler):
        """Initialize the input


        """
        self.mesHandler = messageHandler
        try:
            self.main_input = config['root input']
        except KeyError:
            self.mesHandler.warning("No input is defined in config!!", 0)


    def getInput(self):
        """Get the input format and file


        \param self
        \return tree The tree or TChain created from the input
        """
        tree = None
        if os.path.isdir(self.main_input):
            #make files into a chain
            self.mesHandler.message("Getting all root files from the directory "+str(self.main_input), 0)
            file_list = []
            for file in os.listdir(self.main_input):
                if file.endswith('.root'):  #Get rid of any files that dont end with .root
                    file_list.append(file)

            if len(file_list) > 0:
                self.mesHandler.message("Found "+str(len(file_list))+" root files.",0)
                tree = TChain('photon')
                for file in file_list:
                    tree.Add(self.main_input+file)
            else:
                self.mesHandler.warning("No root files found in the input directory",0)


        elif os.path.isfile(self.main_input):
            #get tree from the file
            if self.main_input.endswith('.root'):
                self.mesHandler.message("Using single file mode.",0)
                self.mesHandler.message("Opening "+str(self.main_input)+" for reading.",0)
                tree = TChain('photon')
                tree.Add(self.main_input)
                #file = TFile(self.main_input)
                #tree = file.Get('photon')
            else:
                self.mesHandler.warning("File does not appear to be a root file", 0)

        else:
            self.mesHandler.warning("Input is neither a directory or a file.",0)

        self.mesHandler.message(str(type(tree)),1)
        return tree

    def getOutput(self):
        """Get the output format and file


        \param self
        """
        raise NotImplementedError


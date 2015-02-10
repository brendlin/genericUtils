libraries = ['libegammaFrame'
             ,'libegammaID'
             ,'libegammaAnalysisUtils'
             ,'libegammaEvent'
             ,'libHiggsZZ4lUtils'
             ]

def loadLibrary(lib) :
    import sys,os
    try:
        import ROOT, PyCintex
    except:
        print 'Failed to import ROOT'
        sys.exit(-1)
        
    try:
        import os
        if os.getenv('ROOTCOREBIN') :
            from ROOT import gROOT
            if lib in ROOT.gSystem.GetLibraries() :
                #print 'skipping loading!'
                return
            gROOT.ProcessLine (".x $ROOTCOREBIN/scripts/load_packages.C");
            print 'Loaded ALL libraries (during attempt %s)'%lib
            return
        #do not load libraries multiple times
        libs = ROOT.gSystem.GetLibraries()
        l_so = lib+'.so'
        if libs.find(l_so) == -1 :
            ROOT.gSystem.Load(l_so)
            print 'Loaded',l_so
        l_dict_so = lib+'Dict.so'
        if libs.find(l_dict_so) == -1 :
            ROOT.gSystem.Load(l_dict_so)
            print 'Loaded',l_dict_so
    except:
        print 'Failed to load library',lib
        sys.exit(-1)

def loadLibraryNoDict(lib) :
    import sys,os
    try:
        import ROOT, PyCintex
    except:
        print 'Failed to import ROOT'
        sys.exit(-1)
        
    try:
        #do not load libraries multiple times
        libs = ROOT.gSystem.GetLibraries()
        l_so = lib+'.so'
        if libs.find(l_so) == -1 :
            ROOT.gSystem.Load(l_so)
            print 'Loaded',l_so
    except:
        print 'Failed to load library',lib
        sys.exit(-1)

def loadstl():
    import os,ROOT
    try:
        libs = ROOT.gSystem.GetLibraries()
        if libs.find('stl_loader_h.so') == -1 :
            _path_of_this_file = os.getenv('TestArea')+'/egammaFrame/python'
            _stl_loader_path = os.path.join(_path_of_this_file, 'stl_loader.h')
            print '.L %s+' % _stl_loader_path
            ROOT.gROOT.ProcessLine('.L %s+' % _stl_loader_path)
            print 'Loaded stl_loader.h'
    except:
        print 'Failed to load stl_loader.h'
        sys.exit(-1)

def loadPileupReweighting():
    loadLibraryNoDict('libPileupReweighting')
    return
        
def loadEgammaAnalysisUtils():
    loadLibrary('libegammaAnalysisUtils')
    return

def loadegammaAnalysisUtilsLocal():
    loadLibrary('libegammaAnalysisUtilsLocal')
    return


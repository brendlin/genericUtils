
categories = [
    'Inclusive',
    'M17_ggH_0J_Cen',        # 1
    'M17_ggH_0J_Fwd',        # 2
    'M17_ggH_1J_LOW',        # 3
    'M17_ggH_1J_MED',        # 4
    'M17_ggH_1J_HIGH',       # 5
    'M17_ggH_1J_BSM',        # 6
    'M17_ggH_2J_LOW',        # 7
    'M17_ggH_2J_MED',        # 8
    'M17_ggH_2J_HIGH',       # 9
    'M17_ggH_2J_BSM',        # 10
    'M17_VBF_HjjLOW_loose',  # 11
    'M17_VBF_HjjLOW_tight',  # 12
    'M17_VBF_HjjHIGH_loose', # 13
    'M17_VBF_HjjHIGH_tight', # 14
    'M17_VHhad_loose',       # 15
    'M17_VHhad_tight',       # 16
    'M17_qqH_BSM',           # 17
    'M17_VHMET_LOW',         # 18
    'M17_VHMET_HIGH',        # 19
    'M17_VHMET_BSM',         # 20
    'M17_VHlep_LOW',         # 21
    'M17_VHlep_HIGH',        # 22
    'M17_VHdilep_LOW',       # 23
    'M17_VHdilep_HIGH',      # 24
    'M17_tH_Had_4j2b',       # 25
    'M17_tH_Had_4j1b',       # 26
    'M17_ttH_Had_BDT4',      # 27
    'M17_ttH_Had_BDT3',      # 28
    'M17_ttH_Had_BDT2',      # 29
    'M17_ttH_Had_BDT1',      # 30
    'M17_ttH_Lep',           # 31
    'M17_tH_lep_1fwd',       # 32
    'M17_tH_lep_0fwd',       # 33
    ]

def weightscale_h015(tfile) :
    import re

    def weightscale_onefile(t_file) :
        fix_2DP20 = 1.

        for i in t_file.GetListOfKeys() :
            name = i.GetName()

            fix_re = '.*Sherpa_2DP20_myy_80_90_3jets_weighted'
            if re.match(fix_re,name) and not re.match('CutFlow_.*_noDalitz_weighted',name):
                print name,'-- applying fix.'
                # see https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/MxAODs
                fix_2DP20 = (0.49383)

            # get _weighted
            if not re.match('CutFlow_.*_weighted',name) :
                continue
            if re.match('CutFlow_.*_noDalitz_weighted',name) :
                continue
            j = i.ReadObj()
            #print j.GetName(),'(weighted)'
            tmp_xAOD = j.GetBinContent(1) # hopefully unskimmed MC sumw
            tmp_DxAOD = j.GetBinContent(2) # hopefully unskimmed MC sumw

        for i in t_file.GetListOfKeys() :
            name = i.GetName()
            # get _noDalitz_weighted
            if not re.match('CutFlow_.*_noDalitz_weighted',name) :
                continue
            j = i.ReadObj()
            #print j.GetName(),'(noDalitz_weighted)'
            tmp_Ntuple_DxAOD = j.GetBinContent(3) # hopefully unskimmed MC sumw

        tmp_DxAOD = tmp_DxAOD * fix_2DP20
        return tmp_xAOD,tmp_DxAOD,tmp_Ntuple_DxAOD

    if type(tfile) == type([]) :
        DxAOD = 0; xAOD = 0; Ntuple_DxAOD = 0;
        for f in tfile :
            tmp1,tmp2,tmp3 = weightscale_onefile(f)
            xAOD         += tmp1
            DxAOD        += tmp2
            Ntuple_DxAOD += tmp3
            #print xAOD,DxAOD,Ntuple_DxAOD

    else :
        xAOD,DxAOD,Ntuple_DxAOD = weightscale_onefile(tfile)
        
    # add 1000. for matching our fb lumi to the MxAOD cross section.
    #print 1000. * DxAOD / float( xAOD * Ntuple_DxAOD )
    return 1000. * DxAOD / float( xAOD * Ntuple_DxAOD )

stxs_bins = {
    'GG2H_FWDH'             : 100,
    'GG2H_VBFTOPO_JET3VETO' : 101,
    'GG2H_VBFTOPO_JET3'     : 102,
    'GG2H_0J'               : 103,
    'GG2H_1J_PTH_0_60'      : 104,
    'GG2H_1J_PTH_60_120'    : 105,
    'GG2H_1J_PTH_120_200'   : 106,
    'GG2H_1J_PTH_GT200'     : 107,
    'GG2H_GE2J_PTH_0_60'    : 108,
    'GG2H_GE2J_PTH_60_120'  : 109,
    'GG2H_GE2J_PTH_120_200' : 110,
    'GG2H_GE2J_PTH_GT200'   : 111,
    # "VBF"
    'QQ2HQQ_FWDH'             : 200,
    'QQ2HQQ_VBFTOPO_JET3VETO' : 201,
    'QQ2HQQ_VBFTOPO_JET3'     : 202,
    'QQ2HQQ_VH2JET'           : 203,
    'QQ2HQQ_REST'             : 204,
    'QQ2HQQ_PTJET1_GT200'     : 205,
    # qq -> WH
    'QQ2HLNU_FWDH'             : 300,
    'QQ2HLNU_PTV_0_150'        : 301,
    'QQ2HLNU_PTV_150_250_0J'   : 302,
    'QQ2HLNU_PTV_150_250_GE1J' : 303,
    'QQ2HLNU_PTV_GT250'        : 304,
    # qq -> ZH
    'QQ2HLL_FWDH'             : 400,
    'QQ2HLL_PTV_0_150'        : 401,
    'QQ2HLL_PTV_150_250_0J'   : 402,
    'QQ2HLL_PTV_150_250_GE1J' : 403,
    'QQ2HLL_PTV_GT250'        : 404,
    # gg -> ZH
    'GG2HLL_FWDH'           : 500,
    'GG2HLL_PTV_0_150'      : 501,
    'GG2HLL_PTV_GT150_0J'   : 502,
    'GG2HLL_PTV_GT150_GE1J' : 503,
    # ttH
    'TTH_FWDH' : 600,
    'TTH'      : 601,
    # bbH
    'BBH_FWDH' : 700,
    'BBH'      : 701,
    # tH
    'TH_FWDH' : 800,
    'TH'      : 801,
    }

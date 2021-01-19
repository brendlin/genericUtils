
llg = '#font[12]{ll}#kern[0.1]{#gamma}'
llg_subscript = '#font[12]{ll}#gamma'
gstar = '#gamma#kern[-0.2]{*}'
zllg = 'Z#kern[0.15]{#rightarrow}#kern[0.1]{#font[12]{ll}}#kern[0.2]{#gamma}'
hysy = 'H#kern[0.15]{#rightarrow}#kern[0.1]{#gamma}#kern[-0.2]{*}#gamma'
hyy  = 'H#kern[0.15]{#rightarrow}#kern[0.1]{#gamma#gamma}'
hysyllg = '%s#rightarrow#kern[0.1]{#font[12]{ll}}#kern[0.2]{#gamma}'%(hysy)
ystoee = '%s#kern[0.05]{#rightarrow}#kern[0.1]{ee}'%(gstar)
lt = '^{ }<^{ }'
plus = '^{ }+^{ }'
sigMuEquals1p46 = 'Sig (#font[152]{m}#kern[0.2]{=}#kern[0.01]{1.47})'
times1p46 = '#kern[0.3]{#scale[0.9]{#lower[-0.2]{#times}}}#kern[0.05]{1.47}'
sigTimes1p46 = 'Sig%s'%(times1p46)
mH = 'm#lower[0.5]{#scale[0.65]{H}}'
xsbr = '#sigma#kern[0.2]{#scale[0.7]{#lower[-0.3]{#times}}}#kern[0.1]{B}'
mu_xsbr = '%s/(%s)#scale[0.5]{#lower[0.4]{SM}}'%(xsbr,xsbr)
bkg_hyy = 'Bkg%s%s'%(plus,hyy)
#bkg_hyy_sigTimes1p46 = 'Bkg%s%s%s%s'%(plus,hyy,plus,sigTimes1p46)
#bkg_hyy_sigTimes1p46_1 = 'Bkg%s%s%sSig (#sigma#scale[0.5]{#lower[0.4]{SM}}%s)'%(plus,hyy,plus,times1p46)
bkg_hyy_sigMuEquals1p46 = 'Bkg%s%s%s%s'%(plus,hyy,plus,sigMuEquals1p46)

#bkg_sigTimes1p46 = 'Bkg%s%s'%(plus,sigTimes1p46)
bkg_sigMuEquals1p46 = 'Bkg%s%s'%(plus,sigMuEquals1p46)
pty = '#font[52]{p}_{T}#kern[-1.0]{#scale[0.75]{#lower[-0.95]{#gamma}}}'
ptystar = '#font[52]{p}_{T}#kern[-0.6]{#scale[0.75]{#lower[-0.6]{%s}}}'%(gstar)

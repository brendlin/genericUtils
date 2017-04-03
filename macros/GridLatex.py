#!/usr/bin/env python

import math

import os,sys
if len(sys.argv) < 2 :
    print 'Please specify a directory!'
    sys.exit()

plots = []

# One directory
if len(sys.argv) == 2 :
    for i in os.listdir(sys.argv[1]) :
        if not '.pdf' in i : continue
        plots.append(i)

# Two directories... one plot on top, one on bottom
if len(sys.argv) == 3 :
    plots_1 = []
    for i in os.listdir(sys.argv[1]) :
        if not '.pdf' in i : continue
        plots_1.append(i)
    plots_2 = []
    for i in os.listdir(sys.argv[2]) :
        if not '.pdf' in i : continue
        plots_2.append(i)
    for i in range(len(plots_1)) :
        plots.append(plots_1[i])
        if (not (i+1)%4) :
            for j in range(i-3,i+1) :
                plots.append(plots_2[j])
        if i == len(plots_1)-1 :
            while (i+1)%4 :
                plots.append('DNE.pdf')
                i += 1
            for j in range(i-3,i+1) :
                plots.append(plots_2[j])
                if j == len(plots_2)-1 :
                    while (j+1)%4 :
                        plots.append('DNE.pdf')
                        j += 1
                    break
            

template_8plots = """\documentclass[a4paper,12pt]{article}
\usepackage[paperwidth=1025px, paperheight=510px,top=0px,left=2px,bottom=0px,right=2px]{geometry}
\usepackage{graphicx}
\usepackage{subcaption}
\setlength{\\tabcolsep}{0px}

\\newcommand{\includeif}[2]{
  \IfFileExists{#1}{\includegraphics[width=254px]{#1}}{\hspace{254px}}\hspace{-9px}
}

\\newcommand{\myfigure}[5]{
\\noindent
\includeif{#1/#2}\\\\
\includeif{#1/#3}\\\\
\includeif{#1/#4}\\\\
\includeif{#1/#5}\\\\
}

\\begin{document}
\\thispagestyle{empty}
\myfigure{%s}{%s}{%s}{%s}{%s}

\\vspace{6mm}

\myfigure{%s}{%s}{%s}{%s}{%s}
\end{document}
"""

#  %%\caption{This is   some figure side by side}

for i in range(int(math.ceil(len(plots)/8.))) :

    tmp_sysargv2 = sys.argv[1]
    script_name = 'GridLatex_%s_%02d.tex'%(sys.argv[1],i)

    if len(sys.argv) > 2 :
        tmp_sysargv2 = sys.argv[2]
        script_name = 'GridLatex_%s_%s_%02d.tex'%(sys.argv[1],sys.argv[2],i)
        
    script = open(script_name,'w')
    p = plots[i*8:(i+1)*8]
    p += ['DNE.pdf']*8
    #print sys.argv[1],p
    #print template_8plots%(sys.argv[1],p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7])
    script.write(template_8plots%(sys.argv[1],p[0],p[1],p[2],p[3],
                                  tmp_sysargv2,p[4],p[5],p[6],p[7]))
    script.close()
    os.system('pdflatex %s'%script_name)
    os.system('rm %s'%(script_name))
    os.system('rm %s'%(script_name.replace('.tex','.log')))
    os.system('rm %s'%(script_name.replace('.tex','.aux')))

for p in plots :
    print p

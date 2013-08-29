#!/usr/bin/env python

import sys, os, re, shutil, string
from optparse import OptionParser

def check_ext(s, ext):
    "get filename with default extension"

    if os.access(s, os.R_OK): 
        return s
    elif os.access(s+ext, os.R_OK):
        return s+ext
    else:
        print "Can't find %s or %s."%(s,s+ext)
        exit(20)

def strip_comments(line):
    line = re.sub(r"^%.*\n?", '', line)
    line = re.sub(r"^(.*[^\\])%.*\n?", r"\1\n", line)
    return line

#################
#     MAIN      #
#################
if __name__ == '__main__':

    usage="usage: %prog [options] filename output_directory"
    description="Prepare files for submission to ApJ:  (1) Include all *.tex files inline, change name to ms.tex.  (2) Remove all comments.  (3) Change any \documentclass to \\documentclass[flushrt]{aastex}.  (4) Change environments: figure* to figure, deluxetable* to deluxetable.  (5) Change \\epsscale{*} to \\epsscale{1.}.  (6) Remove \\bibliographystyle command, replace \\bibliography{*} command with contents of *.bbl.  (7) Copy all figures that are used to 'output_directory'."

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-a", "--arxiv",
                  action="store_true", dest="arxiv", default=False,
                  help="Prep for submission to arxiv. Doesn't perform (3), (4), or (5) above.")
    (options, args) = parser.parse_args()

    ms_infn=args[0]
    outdir=args[1]
    ms_outfn="ms.tex"

    #check that outdir has correct ending and exists
    if outdir[-1]=='/': outdir=outdir[:-1]
    if not (os.path.exists(outdir) and os.path.isdir(outdir)):
        print "Output directory '%s' does not exist.\nExiting.\n"%outdir
        exit(20)

    #read lines from main file
    lines=[]
    ms_inf = open(ms_infn)
    for line in ms_inf: 
        line=strip_comments(line)
        if line == '\n': continue
        lines.append(line)
    ms_inf.close()

    #iteratively search for input files in each line
    inputs_may_exist = True
    while (inputs_may_exist):

        did_new_input=False
        for pos,line in enumerate(lines):
            line=strip_comments(line)
            if line == '\n': continue
            m = re.search(r"\\input\{(.*)\}", line) #search line
            if m:
                infile = m.groups()[0]
                infile = check_ext(infile, '.tex')
                pos2=0
                for line2 in open(infile):
                    line2=strip_comments(line2)
                    lines.insert(pos+pos2,line2)
                    pos2+=1
                lines[pos+pos2]=re.sub(r"\\input\{.*\}", '', line)
                print "Included %s"%infile
                did_new_input=True

        if not did_new_input: inputs_may_exist=False

    #process 'lines' line-by-line
    # NOTE can't handle things when commands are broken across lines
    list_of_figures=[]
    in_figure = False
    ms_outf = open("%s/%s"%(outdir,ms_outfn), 'w')
    for line in lines:

        # skip processing if blank
        if line == '\n':
            ms_outf.write(line)
            continue

        # remove the \NOTE command
        if re.match(r"\\newcommand\{\\NOTE\}",line): continue

        # change documentclass, figure*, deluxetable*, epsscale
        if not options.arxiv:
            line = re.sub(r"\\documentclass.*\{.*\}",
                          r"\\documentclass[flushrt]{aastex}",line)
            line = re.sub(r"\\begin\{figure\*\}",r"\\begin{figure}",line)
            line = re.sub(r"\\end\{figure\*\}",r"\\end{figure}",line)
            line = re.sub(r"\\begin\{deluxetable\*\}",r"\\begin{deluxetable}",
                          line)
            line = re.sub(r"\\end\{deluxetable\*\}",r"\\end{deluxetable}",line)
            line = re.sub(r"\\epsscale\{.+\}",r"\\epsscale{1.}",line)
        
        # get name of figure file:
        if re.match(r"\\begin\{figure\*?\}", line): in_figure = True
        if re.match(r"\\end\{figure\*?\}", line): in_figure = False
        if in_figure:
            m = re.match(r"[^%]*\\plotone\{(.*?)\}", line)
            if m: 
                list_of_figures.append(m.group(1))
                line=re.sub(m.group(1),m.group(1).split('/')[-1],line)
            m = re.match(r"[^%]*\\includegraphics(?:\[.*?\])?\{(.*?)\}", line)
            if m: 
                list_of_figures.append(m.group(1))
                line=re.sub(m.group(1),m.group(1).split('/')[-1],line)
            m = re.match(r"[^%]*\\plottwo\{(.*?)\}\{(.*?)\}", line)
            if m: 
                list_of_figures.append(m.group(1))
                list_of_figures.append(m.group(2))
                line=re.sub(m.group(1),m.group(1).split('/')[-1],line)
                line=re.sub(m.group(2),m.group(2).split('/')[-1],line)
 

        #remove \bibliographystyle command
        line = re.sub(r"\\bibliographystyle\{.*\}",'',line)

        #include bbl file instead of \bibliography{}
        m=re.search(r"\\bibliography\{(.*)\}", line)
        if m:
            infile = m.groups()[0]
            infile = check_ext(infile, '.bbl')
            for line2 in open(infile): ms_outf.write(line2)
            print "Included bibliography: %s"%(infile)
            line=re.sub(r"\\bibliography\{.*\}",'',line)
            
        ms_outf.write(line)


    print "Copying figures:"
    for figname in list_of_figures: 
        newfigname=outdir+'/'+figname.split('/')[-1]
        print "%s --> %s"%(figname,newfigname)
        shutil.copyfile(figname,newfigname)
        

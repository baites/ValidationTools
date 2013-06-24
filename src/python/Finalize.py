## @package Finalize
# \brief Formated web front for ValidationTools
#
# Developers:
#   Victor E. Bazterra
#   Kenneth James Smith


import os 
import threading 

## Implement formated front end.
class Beautify:

    ## Constructor
    def __init__(self):
        self.temp = None

    ## HTML creator
    def HTML(self, webdir=""):
        if webdir != "":
            os.chdir(webdir)
            #pac_file = open("index.html", 'w')
            pac_string_beg = '<html> \n\
            <body><center> \n\
            <image src="http://www.bo.infn.it/images/cms-logo.gif"> <br> \n\
            Which package would like to view? <br> \n\
            <br>\n\
            <br>\n'
            pac_string_mid = ""
            for Package in os.listdir(webdir):
                if "html" not in Package:
                    pac_string_mid = pac_string_mid + '<a href="http://home.fnal.gov/~kjsmith/'+Package+'/" target="middleleft">'+Package+'</a><br> \n'
                    os.chdir(webdir+'/'+Package+'/')
                    # rel_file = open("index.html", 'w')
                    rel_string_beg = '<html> \n\
                    <body><center><image src="http://www.bo.infn.it/images/cms-logo.gif"> <br> \n\
                    Which release would like to view? <br> \n\
                    <br>\n\
                    <br>\n'
                    dat_string_mid = ""
                    for dataset in os.listdir(webdir+'/'+Package+'/'):
                        if "html" not in dataset:
                            dat_string_mid = dat_string_mid + '<a href="http://home.fnal.gov/~kjsmith/'+Package+'/'+dataset+'/" target="middleright">'+dataset+'</a><br> \n'
                            dat_string_beg =  '<html> \n\
                            <body><center> \n\
                            <image src="http://www.bo.infn.it/images/cms-logo.gif"> <br> \n\
                            Which dataset would like to view? <br> \n\
                            <br>\n\
                            <br>\n'
                            rel_string_mid = ""
                            for Release in os.listdir(webdir+'/'+Package+'/'+dataset):
                                if ".htm" not in Release:
                                    rel_string_mid = rel_string_mid + '<a href="http://home.fnal.gov/~kjsmith/'+Package+'/'+dataset+'/'+Release+ '/" target="right">'+Release+'</a><br> \n'
                                    os.chdir(webdir+'/'+Package+'/'+dataset+'/'+Release+'/')
                                    # ref_file = open("index.html", 'w')
                                    ref_string_beg = '<html> \n\
                                    <body><center> <image src="http://www.bo.infn.it/images/cms-logo.gif"> <br> \n\
                                    Which reference would like to view?<br> \n\
                                    <br>\n\
                                    <br>\n'
                                    ref_string_mid = ""
                                    string_end = '</center></body></html>'
                                    for Reference in os.listdir(webdir+'/'+Package+'/'+dataset+'/'+Release+'/'):
                                        if "html" not in Reference:
                                            ref_string_mid = ref_string_mid + '<a href="http://home.fnal.gov/~kjsmith/'+Package+'/'+dataset+'/'+Release+'/'+Reference + '/" target="_parent" >'+Reference+'</a><br> \n'
                                        ref_string = ref_string_beg + ref_string_mid + string_end
                                        ref_file = open("index.html", 'w')
                                        ref_file.write(ref_string)
                                        ref_file.close()
                            
                                    rel_string = rel_string_beg + rel_string_mid + string_end
                            os.chdir(webdir+'/'+Package+'/'+dataset+'/')
                            rel_file = open("index.html", 'w')
                            rel_file.write(rel_string)
                            rel_file.close()
                        os.chdir(webdir+'/'+Package+'/')
                        dat_file = open("index.html", 'w')
                        dat_string = dat_string_beg + dat_string_mid + string_end
                        dat_file.write(dat_string)
                        dat_file.close()
                    pac_string = pac_string_beg + pac_string_mid + string_end
                    os.chdir(webdir)
                    pac_file = open("package.html", 'w')
                    pac_file.write(pac_string)
                    pac_file.close()


from sys import stdout, stderr
import smtplib
import inspect

class PyMessageHandler():
    """Class to handle messages.



    """
    def __init__(self, config):
        """Initialize the handler.

        
        \param self
        \param config configuration file with verbosity level and log file name(optional)
        """
        try:
            self.verbose = config['verbose']
        except KeyError:
            print "!!![Warning]:..... No verbosity set in config. Defaulting to level 0."
            self.verbose = 0
        try:
            self.do_debug = config['DEBUG']
        except KeyError:
            print "!!![Warning]:..... No DEBUG set in config. Defaulting to OFF."
            self.do_debug = False 
        try:
            self.log_file = config['log_file']
        except KeyError:
            print "[Info]:..... No Log file set. Sending to stdout."
            self.log_file = None
        self.output = stdout
        self.DEBUGout = stdout
        self.warout = stderr

        self.log_string = ''

        if self.log_file:
            self.log_output = open(self.log_file_name)
        else:
            self.log_output = stdout

    def log(self, msg):
        """Messages to send to the log file

        Will send messages to the stdout if no log file is set

        \param self
        \param msg message to be sent
        """
        out_str = None
        # More here later

    def getClassAndLineno(self,stackitem) :
        #
        # If your class is to be identified, it needs a __name__ assigned to it.
        #
        myclass = stackitem.f_locals.get('self',None)
        if myclass :
            return '[%s][line%d]'%(getattr(myclass,'__name__','NoName'),stackitem.f_lineno)
        return ''


    def message(self, msg, mlevel):
        """Messages to send to the stdout

        Sends messages to the stdout.

        \param self
        \param msg Message to be sent
        \param mlevel Verbosity level. If the is less than self.verbose, print message
        """
        out_str = None
        if self.verbose >= mlevel: 
            myclass = inspect.stack()[1][0].f_locals.get('self',None)
            out_str = ''
            out_str += self.getClassAndLineno(inspect.stack()[1][0])
            out_str += "[Info]:....."
            out_str += msg
            out_str += '\n'
        if out_str is not None:
            self.output.write(out_str)
            self.log_string += out_str
        
    def warning(self, msg, mlevel):
        """Messages to send to the stdout

        Sends messages to the stdout.

        \param self
        \param msg Message to be sent
        \param mlevel Verbosity level. If the is less than self.verbose, print message
        """
        out_str = None
        if self.verbose >= mlevel: 
            out_str = ''
            out_str += self.getClassAndLineno(inspect.stack()[1][0])
            out_str += "!!![WARNING]:....."
            out_str += msg
            out_str += '\n'
        if out_str is not None:
            self.warout.write(out_str)
            self.log_string += out_str
        
    def DEBUG(self, msg, mlevel):
        """Messages to send to the stdout

        Sends messages to the stdout.

        \param self
        \param msg Message to be sent
        \param mlevel Verbosity level. If the is less than self.verbose, print message
        """
        if self.do_debug:
            out_str = None
            if self.verbose >= mlevel: 
                out_str = ''
                out_str += self.getClassAndLineno(inspect.stack()[1][0])
                out_str += "***[DEBUG]:....."
                out_str += msg
                out_str += '\n'
            if out_str is not None:
                self.DEBUGout.write(out_str)
                self.log_string += out_str
        
    def mailLog(self, subject, message=''):
        """Email the log file 
        
        Send an email when the job finishes with the log of the output.

        \param self
        \param subject Subject line of the email
        \param message optional message to add to the begining of the email body
        """
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("mastercontrolprograminfo@gmail.com", "wolfbrother1")        

        msg = message + self.log_string
        headers = [ "From: Master Control Program\n",
                    "To: Whom it may concern\n",
                    "Subject: "+ subject +"\n"
                  ]
        server.sendmail("mastercontrolprograminfo@gmail.com", "robflet@sas.upenn.edu", "".join(headers) + "\n\r" + msg)



    def showPercent(self, current, total, message='', mlevel=0):
        """Get the percentege complete of the current task

        Show the percentage complete as the ratio of current over total
        with a message to be displated with the number.

        \param self
        \param current the step the job is currently on
        \param total   the total number of steps
        \message   short message to be added before the percent
        \mlevel   the verbosity level
        """
        perc = int((float(current)/total)*100)
        out_str = None
        if self.verbose >= mlevel: 
            out_str = "[Info]:....."
            out_str += message+" "
            out_str += str(perc)+'% completed'
            out_str += '\n'
        if out_str is not None:
            self.output.write(out_str)










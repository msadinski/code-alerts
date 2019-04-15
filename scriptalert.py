#############################################################
# This script sends you a text when your code is done running
# Usage: python scriptalert.py <pid> <user phone number>
# Triggered based on process id
# ms 04/15/2019
#############################################################

import os, sys, psutil
from socket import gethostname
from threading import Timer
from twilio.rest import Client

# Get id and token
twilio_sid = os.environ.get('TWILIO_SID')
twilio_token = os.environ.get('TWILIO_TOKEN')
twilio_number = os.environ.get('TWILIO_NUMBER')
client = Client(twilio_sid, twilio_token)

text = 'This is an automated notification that your code has finished running on ' + gethostname() 

class RecTimer(object):
    def __init__(self, interval, pid):
        self.pid = pid
        self.interval = interval
        self.__timer = None
        self.active = False

    def start(self):
        if not self.active:
            self.__timer = Timer(self.interval, self.__run)
            self.__timer.start()
            self.active = True
        
    def stop(self):
        self.__timer.cancel()
        self.active = False
 
    def __run(self):
        self.active = False
        self.start()
        self.check_pid()

    def check_pid(self):
        if not psutil.pid_exists(self.pid):
            print('Process', self.pid, 'finished')
            outgoing = client.messages.create(to='+1'+sys.argv[2], from_=twilio_number, body=text)
            self.stop()


checker = RecTimer(60, int(sys.argv[1]))
checker.start()

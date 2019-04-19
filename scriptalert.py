#############################################################
# This script sends you a text when your code is done running
# Triggered based on process ids
#############################################################

import os, psutil, argparse
from socket import gethostname
from threading import Timer
from twilio.rest import Client

# Get id and token
twilio_sid = os.environ.get('TWILIO_SID')
twilio_token = os.environ.get('TWILIO_TOKEN')
twilio_number = os.environ.get('TWILIO_NUMBER')
client = Client(twilio_sid, twilio_token)

# Configure based on input arguments
parser = argparse.ArgumentParser()
parser.add_argument('process_id', nargs='+', help='process ids to track')
parser.add_argument('-n', metavar='number', required=False, help='phone number to text (no spaces XXXXXXXXXX)')
parser.add_argument('-t', metavar='tail', required=False, help='text to tag on the end of default message')
args = parser.parse_args()

if args.t:
    text = 'This is an automated notification that your code has finished running on ' + gethostname() + '. ' + args.t 
else:
    text = 'This is an automated notification that your code has finished running on ' + gethostname() 

class RecTimer(object):
    def __init__(self, interval, pid):
        """
        A recursive timer that restarts every interval
        Stops when the given pid does not exist anymore
        """
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
            try:
                outgoing = client.messages.create(to='+1'+args.n, from_=twilio_number, body=text)
            except ValueError:
                print('Phone Number is Unverified.')
            self.stop()

for pp in args.process_id:
    checker = RecTimer(60, int(pp))
    checker.start()

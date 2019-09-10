#!/bin/sh
# -*- coding: latin1 -*-
# https://wiki.python.org.br/ExecutandoEmIntervalos

from threading import Thread
from time import sleep
import time
import threading

class IntervalRunner(Thread):
    def __init__(self, interval, function, *args, **kwargs):
        #super(self, IntervalRunner).__init__(self)
        super(IntervalRunner, self).__init__()
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.executing = False

    def run(self):
        self.executing = True
        while self.executing:
            self.function(*self.args, **self.kwargs)
            sleep(self.interval)

    def stop(self):
        self.executing = False

class TimerClass(threading.Thread):
    def __init__(self, interval, function, *args):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.count = interval
        self.function = function
        self.args = args

    def run(self):
        while self.count > 0 and not self.event.is_set():
            print self.count
            self.count -= 1
            self.event.wait(1)
        if self.count == 0:
            print 'timeout'
            self.function(*self.args)
        else:
            print 'finalizou antes do timeout'

    def stop(self):
        self.event.set()

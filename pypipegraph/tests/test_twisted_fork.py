"""
The MIT License (MIT)

Copyright (c) 2012, Florian Finkernagel <finkernagel@imt.uni-marburg.de>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from nose.twistedtools import reactor, deferred
import twisted.internet
import os
import sys
sys.path.append("..")

from twisted.internet import protocol
from twisted.internet.defer import Deferred
import twisted_fork
import unittest
print 'init'




class DataCollectingProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.deferred = Deferred()

    def connectionMade(self):
        self.stdout = ''
        self.stderr = ''
        pass

    def outReceived(self, data):
        self.stdout += data

    def errReceived(self, data):
        self.stderr += data

    #def childDataReceived(self, name, data):
        #protocol.ProcessProtocol.childDataReceived(self, name, data)

    def processExited(self, status):
        self.exit_code = status.value.exitCode
        self.deferred.callback(self)

class ForkedProcessTests(unittest.TestCase):

    @deferred(2)
    def test_exit_ok(self):
        def callback():
            sys.exit(0)
        collector = DataCollectingProcessProtocol()
        p = twisted_fork.ForkedProcess(reactor, callback, collector)
        def check_status(proto):
            assert proto.exit_code == 0
        collector.deferred.addCallback(check_status)
        return collector.deferred

    @deferred(2)
    def test_stdout_exit_ok(self):
        def callback():
            sys.stdout.write('hello world')
            sys.exit(0)
        collector = DataCollectingProcessProtocol()
        print 'hello'
        p = twisted_fork.ForkedProcess(reactor, callback, collector)
        def check_status(proto):
            assert proto.stdout == 'hello world'
            assert proto.exit_code == 0
        collector.deferred.addCallback(check_status)
        return collector.deferred

    @deferred(2)
    def test_print_exit_ok(self):
        def callback():
            print 'hello world' 
            sys.exit(0)
        collector = DataCollectingProcessProtocol()
        print 'hello'
        p = twisted_fork.ForkedProcess(reactor, callback, collector)
        def check_status(proto):
            assert proto.stdout == 'hello world\n'
            assert proto.exit_code == 0
        collector.deferred.addCallback(check_status)
        return collector.deferred

    @deferred(2)
    def test_stdout_exit_error(self):
        def callback():
            sys.stdout.write('hello world')
            sys.exit(5)
        collector = DataCollectingProcessProtocol()
        print 'hello'
        p = twisted_fork.ForkedProcess(reactor, callback, collector)
        def check_status(proto):
            assert proto.stdout == 'hello world'
            assert proto.exit_code == 5
        collector.deferred.addCallback(check_status)
        return collector.deferred

    @deferred(2)
    def test_stderr_exit_error(self):
        def callback():
            sys.stderr.write('hello world')
            sys.exit(5)
        collector = DataCollectingProcessProtocol()
        print 'hello'
        p = twisted_fork.ForkedProcess(reactor, callback, collector)
        def check_status(proto):
            assert proto.stderr == 'hello world'
            assert proto.exit_code == 5
        collector.deferred.addCallback(check_status)
        return collector.deferred


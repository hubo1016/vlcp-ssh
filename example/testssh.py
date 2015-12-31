'''
Created on 2015/12/31

:author: think
'''
from __future__ import print_function
from vlcp.server import main
from vlcp.server.module import Module
from vlcp.event.runnable import RoutineContainer
from vlcpssh.sshclient import SSHFactory
from vlcp.utils.connector import TaskPool
from vlcp.config.config import manager
import sys

# Modify following parameters before executing
TARGET = 'localhost'
USERNAME = 'root'
PASSWORD = ''

class MainRoutine(RoutineContainer):
    def printall(self, stream):
        while True:
            for m in stream.prepareRead(self):
                yield m
            try:
                print(stream.readonce())
            except EOFError:
                break
    def main(self):
        for m in self.sshfactory.connect(TARGET, username=USERNAME, password=PASSWORD):
            yield m
        for m in self.sshfactory.execute_command(self.retvalue, 'ls'):
            yield m
        chan = self.retvalue
        self.subroutine(self.printall(chan.stdout))
        self.subroutine(self.printall(chan.stderr))

class MainModule(Module):
    def __init__(self, server):
        Module.__init__(self, server)
        self.mainroutine = MainRoutine(self.scheduler)
        self.taskpool = TaskPool(self.scheduler)        
        self.sshfactory = SSHFactory(self.taskpool, self.mainroutine)
        self.mainroutine.sshfactory = self.sshfactory
        self.routines.append(self.mainroutine)
        self.routines.append(self.taskpool)

if __name__ == '__main__':
    #manager['server.debugging'] = True
    main(None, ())

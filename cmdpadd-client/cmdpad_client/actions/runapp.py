"""
Run a program
"""
import os
from cmdpad_client.actiontypes import *
import subprocess

__label__ = 'Run a program'
__config__ = (
	('program', 'Program', LooseFile("Choose an application...")),
	('arguments', 'Arguments', String()),
)

def run(options):
	os.system(options['command'])

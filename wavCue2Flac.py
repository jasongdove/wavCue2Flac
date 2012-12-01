__author__ = 'jason'

import os
import sys

# check for dependencies (cuebreakpoints, shnsplit, cuetag)
# programmatically rename by metadata ??

# find all wav files in directory
# find all cue files in directory
# find wav/cue of same name

# call 'cuebreakpoints | shnsplit'
# check for errors

def find_command(name):
    for dir in os.environ['PATH'].split(':'):
        command = os.path.join(dir, name)
        if os.path.exists(command): return command

flac = find_command('flac')
if flac is None:
    print('unable to find flac')
    sys.exit(1)

cuebreakpoints = find_command('cuebreakpoints')
if cuebreakpoints is None:
    print('unable to find cuebreakpoints (cuetools)')
    sys.exit(1)

shnsplit = find_command('shnsplit')
if shnsplit is None:
    print('unable to find shnsplit (shntool)')
    sys.exit(1)

print ('found all dependencies')
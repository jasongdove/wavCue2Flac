import os
import sys
import shlex
from subprocess import call

# programmatically rename by metadata (if possible)

def find_command(name):
    #print('checking for %s' % name)
    for dir in os.environ['PATH'].split(':'):
        command = os.path.join(dir, name)
        if os.path.exists(command): return command

def print_usage():
    print('usage: wavCue2Flac albumPath')

def find_cue_wav(path):
    print('checking for cue/wav in %s' % path)
    for root, dirs, files in os.walk(path):
        for file in files:
            cue = os.path.abspath(os.path.join(root, file))
            if cue.endswith('.cue'):
                for ext in ['.wav', '.wv']:
                    wav = cue.replace('.cue', ext)
                    if os.path.exists(wav):
                        return cue, wav

def split_album(path, cue, wav):
    print('splitting album with cuebreakpoints | shnsplit')
    os.chdir(path)
    ret = call(
        'cuebreakpoints %s | shnsplit -q -o "flac flac -s --best -o %%f -" %s' % (shlex.quote(cue), shlex.quote(wav)),
        shell=True)
    if ret != 0:
        print('error calling cuebreakpoints/shnsplit', file=sys.stderr)
        sys.exit(1)

def tag_tracks(cue, path):
    print('tagging tracks with cuetag')
    os.chdir(path)
    ret = call('cuetag %s split-track*.flac' % shlex.quote(cue), shell=True)
    if ret != 0:
        print('error calling cuetag', file=sys.stderr)
        sys.exit(1)

if len(sys.argv) != 2:
    print_usage()
    sys.exit(1)

albumPath = sys.argv[1]

flac = find_command('flac')
if flac is None:
    print('unable to find flac', file=sys.stderr)
    sys.exit(1)

cuebreakpoints = find_command('cuebreakpoints')
if cuebreakpoints is None:
    print('unable to find cuebreakpoints (cuetools)', file=sys.stderr)
    sys.exit(1)

shnsplit = find_command('shnsplit')
if shnsplit is None:
    print('unable to find shnsplit (shntool)', file=sys.stderr)
    sys.exit(1)

cuetag = find_command('cuetag')
if cuetag is None:
    print('unable to find cuetag (download from https://github.com/gumayunov/split-cue/blob/master/cuetag)', file=sys.stderr)
    sys.exit(1)

paths = find_cue_wav(albumPath)
if paths is None:
    print('folder does not contain cue/wav; nothing to do')
    sys.exit(0)

cue = paths[0]
wav = paths[1]

split_album(albumPath, cue, wav)
tag_tracks(cue, albumPath)

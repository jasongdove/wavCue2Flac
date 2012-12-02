import os
import pipes
import sys
import shlex
import glob
from mutagen.flac import FLAC
from subprocess import call

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
        'cuebreakpoints %s | shnsplit -q -o "flac flac -s --best -o %%f -" %s' % (pipes.quote(cue), pipes.quote(wav)),
        shell=True)
    if ret != 0:
        print >> sys.stderr, 'error calling cuebreakpoints/shnsplit'
        sys.exit(1)

def tag_tracks(cue, path):
    print('tagging tracks with cuetag')
    os.chdir(path)
    ret = call('cuetag %s split-track*.flac' % pipes.quote(cue), shell=True)
    if ret != 0:
        print >> sys.stderr, 'error calling cuetag'
        sys.exit(1)

def rename_tracks(path):
    print('renaming tracks')
    for name in glob.glob(os.path.join(path, 'split-track*.flac')):
        track = FLAC(name)
        title = track["TITLE"][0]
        artist = track["ARTIST"][0]
        num = track["TRACKNUMBER"][0]
        newName = '{0} - {1} - {2}.flac'.format(num.zfill(2), artist, title)
        newPath = os.path.join(path, newName)
        os.rename(name, newPath)

if len(sys.argv) != 2:
    print_usage()
    sys.exit(1)

albumPath = sys.argv[1]

flac = find_command('flac')
if flac is None:
    print >> sys.stderr, 'unable to find flac'
    sys.exit(1)

cuebreakpoints = find_command('cuebreakpoints')
if cuebreakpoints is None:
    print >> sys.stderr, 'unable to find cuebreakpoints (cuetools)'
    sys.exit(1)

shnsplit = find_command('shnsplit')
if shnsplit is None:
    print >> sys.stderr, 'unable to find shnsplit (shntool)'
    sys.exit(1)

cuetag = find_command('cuetag')
if cuetag is None:
    print >> sys.stderr, 'unable to find cuetag (download from https://github.com/gumayunov/split-cue/blob/master/cuetag)'
    sys.exit(1)

paths = find_cue_wav(albumPath)
if paths is None:
    print('folder does not contain cue/wav; nothing to do')
    sys.exit(0)

cue = paths[0]
wav = paths[1]

split_album(albumPath, cue, wav)
tag_tracks(cue, albumPath)
rename_tracks(albumPath)
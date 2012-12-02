import os
import pipes
import sys
import glob
from mutagen.flac import FLAC
from subprocess import call

def find_command(name):
    #print('checking for %s' % name)
    for path in os.environ['PATH'].split(':'):
        command = os.path.join(path, name)
        if os.path.exists(command):
            return command

def print_usage():
    print('usage: wavCue2Flac albumPath')

class Album:
    def __init__(self, album_path):
        self.album_path = album_path

    def find_cue_wav(self):
        print('checking for cue/wav in %s' % self.album_path)
        for root, dirs, files in os.walk(self.album_path):
            for file_entry in files:
                cue = os.path.abspath(os.path.join(root, file_entry))
                if cue.endswith('.cue'):
                    for ext in ['.wav', '.wv']:
                        wav = cue.replace('.cue', ext)
                        if os.path.exists(wav):
                            return cue, wav
        return None


    def split_album(self, cue, wav):
        print('splitting album with cuebreakpoints | shnsplit')
        os.chdir(self.album_path)
        ret = call(
            'cuebreakpoints %s | shnsplit -q -o "flac flac -s --best -o %%f -" %s'
            % (pipes.quote(cue), pipes.quote(wav)),
            shell=True)
        if ret != 0:
            print >> sys.stderr, 'error calling cuebreakpoints/shnsplit'
            sys.exit(1)


    def tag_tracks(self, cue):
        print('tagging tracks with cuetag')
        os.chdir(self.album_path)
        ret = call('cuetag %s split-track*.flac' % pipes.quote(cue), shell=True)
        if ret != 0:
            print >> sys.stderr, 'error calling cuetag'
            sys.exit(1)


    def rename_tracks(self):
        print('renaming tracks')
        for name in glob.glob(os.path.join(self.album_path, 'split-track*.flac')):
            track = FLAC(name)
            title = track["TITLE"][0]
            artist = track["ARTIST"][0]
            num = track["TRACKNUMBER"][0]
            new_name = '{0} - {1} - {2}.flac'.format(num.zfill(2), artist, title)
            new_path = os.path.join(self.album_path, new_name)
            os.rename(name, new_path)

    def process(self):
        paths = self.find_cue_wav()
        if paths is None:
            print('folder does not contain cue/wav; nothing to do')
            sys.exit(0)

        cue_path = paths[0]
        wav_path = paths[1]

        self.split_album(cue_path, wav_path)
        self.tag_tracks(cue_path)
        self.rename_tracks()

if len(sys.argv) < 2:
    print_usage()
    sys.exit(1)

if find_command('flac') is None:
    print >> sys.stderr, 'unable to find flac'
    sys.exit(1)

if find_command('cuebreakpoints') is None:
    print >> sys.stderr, 'unable to find cuebreakpoints (cuetools)'
    sys.exit(1)

if find_command('shnsplit') is None:
    print >> sys.stderr, 'unable to find shnsplit (shntool)'
    sys.exit(1)

if find_command('cuetag') is None:
    CUETAG_URL = 'https://github.com/gumayunov/split-cue/blob/master/cuetag'
    print >> sys.stderr, 'unable to find cuetag (download from %s)' % CUETAG_URL
    sys.exit(1)

Album(sys.argv[1]).process()

import subprocess as sp
import sys

src_path = sys.argv[1]

if len(sys.argv) > 3:
    dest_path = sys.argv[2]
else:
    dest_path = src_path.split('.')
    dest_path[0] += '_compressed'
    dest_path = '.'.join(dest_path)

print(src_path, ' to ', dest_path)

FFMPEG_BIN = 'ffmpeg\\bin\\ffmpeg.exe'

commmand = [ FFMPEG_BIN,
                '-i', src_path,
                '-s', '320x180',
                '-c:a', 'copy',
                '-filter:v', 'fps=20',
                dest_path,
                '-hide_banner'
            ]

pipe = sp.Popen(commmand, stdout=sp.PIPE)

pipe.stdout.readline()
pipe.terminate()
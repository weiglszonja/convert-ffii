import sys
import struct
import subprocess
import os
import time

def usage():
    print(sys.argv[0], '<path-with-.ffii-files>')
    quit()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        usage()

    folderpath = sys.argv[1]
    
    exten = '.ffii'
    nbFiles = 0
    
    start_time = time.time()
    
    for root, directories, filenames in os.walk(folderpath):
        for filename in filenames: 
            if filename.lower().endswith(exten):
                filename = os.path.join(root, filename)
                
                print('Converting %s...\n'%filename)
                
                of = filename[:-5]+'.avi'
    
                # Skip if .avi file already exists
                if os.path.exists(of):
                    print(f"Skipping {filename} (output {of} already exists)")
                    continue

                f = open(filename,'rb')
                m = f.read(8)
                height, width = struct.unpack(">2I", m)
                rate = "15"

                cmdstr = ('ffmpeg', '-y', '-r', rate,\
                        '-f', 'rawvideo',
                        '-pix_fmt', 'gray',
                        '-s', str(width)+"x"+str(height),
                        '-i', '-',
                        '-c:v', 'ffv1',  # Lossless codec
                        of)
                 
                p = subprocess.Popen(cmdstr, stdin=subprocess.PIPE, shell=False)
                try:
                    while True:
                        img = f.read(width*height)
                        if not img:
                            break
                        p.stdin.write(img)
                        m = f.read(8)
                        if not m:
                            break
                        height, width = struct.unpack(">2I", m)
                    p.stdin.close()
                    p.wait()
                except Exception as e:
                    print(f"Error during ffmpeg process: {e}")
                    p.kill()
                print('Saved in %s' % of)
                nbFiles += 1

print('Conversion of %i files over!'%nbFiles)
print("--- %.2f seconds elapsed ---" % (time.time() - start_time))

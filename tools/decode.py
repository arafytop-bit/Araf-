import subprocess, numpy as np, sys
src, out, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
N = int(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip())
mm = np.lib.format.open_memmap(out, mode='w+', dtype=np.uint8, shape=(N, H, W, 3))
p = subprocess.Popen(['ffmpeg','-v','error','-i',src,'-an','-vf',f'scale={W}:{H}:flags=area','-f','rawvideo','-pix_fmt','rgb24','-'], stdout=subprocess.PIPE, bufsize=10**8)
fs = W*H*3; i = 0
while i < N:
    b = p.stdout.read(fs)
    if len(b) < fs: break
    mm[i] = np.frombuffer(b, np.uint8).reshape(H, W, 3); i += 1
mm.flush(); print('frames', i)

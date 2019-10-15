import os
import shutil
import subprocess
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

pbar = tqdm(total=7200)


# todo : offload heavy calculation work to gpu using pyopencl
def make_frame(i, data_set, delta, frame_rate, duration, limits):
    plt.figure(figsize=(19.20, 10.80))
    plt.ylim(limits[0], limits[1])
    pbar.update(4)
    plt.plot(x, data_set + (i * 1.0 / (frame_rate * duration)) * delta)
    plt.savefig('.cache/img{:05d}'.format(i))
    plt.close()


# generate multiple frames at the same time using multiprocessing pool
# IT'S NOT ADVISED TO USE ALL AVAILABLE CPUS , THE PC MAY BECOME UNRESPONSIVE
# todo : add some still frames at the end of the video
def make_video(data_set, delta, frame_rate, duration):
    print('Building frames !', flush=True)
    if '.cache' not in os.listdir():
        os.mkdir('.cache')
    n_workers = cpu_count() // 2
    p = Pool(processes=n_workers)
    l1 = min(min(data_set), min(data_set + delta)) * 1.1
    l2 = max(max(data_set), max(data_set + delta)) * 1.1
    limits = (l1, l2)
    for i in np.arange(0, frame_rate * duration, 1):
        p.apply_async(make_frame, (i, data_set, delta, frame_rate, duration, limits))
    p.close()
    p.join()

    print('Concatenating frames !')

    # concatenate frames using ffmpeg
    commands = 'ffmpeg -y -framerate {} -i .cache/img%05d.png -c:v libx265 video.mkv'.format(frame_rate).split()
    null_file = open(os.devnull, 'w')
    child = subprocess.Popen(commands, stderr=null_file)
    child.wait()


def check_ffmpeg():
    child = subprocess.Popen(['ffmpeg'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if child.stderr is not None:
        s = child.stderr.readline()
        if not s.startswith(b'ffmpeg version'):
            raise OSError('ffmpeg not found in this environment ')


def main(original_data_set, new_data_set, duration=1, frame_rate=60):
    check_ffmpeg()
    delta = new_data_set - original_data_set
    make_video(original_data_set, delta, frame_rate, duration)
    print('Deleting cache files !')
    shutil.rmtree('.cache')
    print('Done !')


# example
x = np.arange(-10, 10, 0.01)
o = np.abs(x)
o2 = 3 * np.sin(x)

if __name__ == '__main__':
    main(original_data_set=o
         , new_data_set=o2)

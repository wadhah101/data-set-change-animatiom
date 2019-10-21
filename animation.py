import os
import shutil
import subprocess
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np


# todo proper tqdm implementation
# todo : offload heavy calculation work to gpu using pyopencl
# todo : add some still frames anextt the end of the video


def make_frame(i, data_set, delta, frame_rate, duration, limits):
    plt.figure(figsize=(19.20, 10.80))
    plt.ylim(limits[0], limits[1])
    plt.plot(x, data_set + (i * 1.0 / (frame_rate * duration)) * delta)
    plt.savefig(os.path.join('.cache', 'img{:07d}'.format(i)))
    plt.close()


# generate multiple frames at the same time using multiprocessing pool
# IT'S NOT ADVISED TO USE ALL AVAILABLE CPUS , THE PC MAY BECOME UNRESPONSIVE
def make_video(data_set, delta, frame_rate, duration):
    print('Building frames !')
    if '.cache' not in os.listdir():
        os.mkdir('.cache')
    n_workers = cpu_count() // 2
    p = Pool(processes=n_workers)
    l1 = min(min(data_set), min(data_set + delta)) * 1.1
    l2 = max(max(data_set), max(data_set + delta)) * 1.1
    limits = (l1, l2)
    for i in np.arange(0, frame_rate * duration, 1):
        args = (i, data_set, delta, frame_rate, duration, limits)
        p.apply_async(make_frame, args)
    p.close()
    p.join()

    print('Concatenating frames !')

    # concatenate frames using ffmpeg
    commands = 'ffmpeg -y -framerate {} -i .cache/img%07d.png -c:v libx265 video.mkv'.format(frame_rate).split()
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
y1 = np.sin(x)
y2 = np.sin(2 * x) + np.cos(x)

if __name__ == '__main__':
    main(original_data_set=y1
         , duration=5
         , frame_rate=60
         , new_data_set=y2)

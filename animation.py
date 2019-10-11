import os
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

import video_manager

image_folder_name = '.cache'


# todo : offload heavy calculation work to gpu using pyopencl
def make_frame(i, d, delta, frame_rate, duration, limits):
    plt.figure(figsize=(19.20, 10.80))
    plt.ylim(limits[0], limits[1])
    plt.plot(x, d + (i * 1.0 / (frame_rate * duration)) * delta)
    plt.savefig('{}/img{:05d}'.format(image_folder_name, i))
    plt.close()


# generate multiple frames at the same time using multiprocessing pool
# IT'S NOT ADVISED TO USE ALL AVAILABLE CPUS , THE PC MAY BECOME IRRESPONSIBLE
def make_video(d, delta, frame_rate, duration):
    print("Generating frames!")
    try:
        os.mkdir(image_folder_name)
    except:
        pass
    n_workers = cpu_count() - 1 if cpu_count() > 1 else 1
    p = Pool(processes=n_workers)
    l1 = min(min(d), min(d + delta)) * 1.1
    l2 = max(max(d), max(d + delta)) * 1.1
    limits = (l1, l2)

    for i in np.arange(0, frame_rate * duration, 1):
        p.apply_async(make_frame, (i, d, delta, frame_rate, duration, limits))
    p.close()
    p.join()

    print('Concatenating frames !')

    # concatenate frames using ffmpeg
    video_manager.make_vid_ffmpeg(image_folder_name, frame_rate, 'out.mkv')


def data_animation(original_data_set, new_data_set, duration=5, frame_rate=60):
    delta = new_data_set - original_data_set
    make_video(original_data_set, delta, frame_rate, duration)
    video_manager.delete_files(image_folder_name)
    os.rmdir(image_folder_name)
    print('Done !')


# example
x = np.arange(-10, 10, 0.001)
o = x ** 2
o2 = x * 0

data_animation(original_data_set=o
               , new_data_set=o2
               , duration=10
               , frame_rate=60)

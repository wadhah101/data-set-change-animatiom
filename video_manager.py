import cv2
import os
import multiprocessing as mp
import numpy as np
import subprocess


# make a video from files found in the specified folder
# note : files should be in alphabetic order
# note : folder name should NOT end with /
# ONLY a path to the folder is needed
def make_vid(folder_name, frame_Rate):
    list = os.listdir(folder_name)
    list.sort()
    frame_count = len(list)
    folder_name += '/'

    # video making code
    current_frame = 0
    im = cv2.imread(folder_name + list[0])
    height, width, layers = im.shape
    vid = cv2.VideoWriter('.vid.mkv', 0, frame_Rate, (width, height))
    for i in list:
        im = cv2.imread(folder_name + i)
        vid.write(im)
        current_frame += 1

        # progress bar
        # print('Making Video : {:.2f}%'.format(current_frame * 100 / frame_count))

    cv2.destroyAllWindows()
    vid.release()


# function to dispose of used frames
# inside the specifed folder
def delete_files(folder_name):
    l = os.listdir(folder_name)
    folder_name += '/'
    for i in l:
        os.remove(folder_name + i)

# use ffmpeg for compression (Drastically reduce file size  from 3gb to around 1 mb )
def compress_to_x265(video_in, output):
    print("Compressing video!")
    commands = 'ffmpeg -y -i {} -c:v libx265 -crf 28 -c:a aac -b:a 128k {}' \
        .format(video_in, output) \
        .split(sep=' ')
    null_file = open(os.devnull, 'w')
    subprocess.run(commands, stdout=null_file, stderr=null_file, stdin=null_file)

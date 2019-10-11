import os
import subprocess


# function to dispose of used frames
# inside the specifed folder
def delete_files(folder_name):
    l = os.listdir(folder_name)
    folder_name += '/'
    for i in l:
        os.remove(folder_name + i)


# make a video from files found in the specified folder
# note : files should be in alphabetic order
# note : folder name should NOT end with /
# ONLY a path to the folder is needed
def make_vid_ffmpeg(folder_name, frame_Rate, output):
    commands = 'ffmpeg -y -framerate {} -i {}/img%05d.png -c:v libx265 {}' \
        .format(frame_Rate, folder_name, output) \
        .split(sep=' ')
    null_file = open(os.devnull, 'w')
    child = subprocess.Popen(commands, stderr=null_file)
    child.wait()

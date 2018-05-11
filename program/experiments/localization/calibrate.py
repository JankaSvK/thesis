#!/usr/bin/python3
import os
from sys import argv

try:
    experiment_id = int(argv[1])
except Exception:
    experiment_id = 63

def command(video1, video2, chessboard):
    return "python ../../Main.py --video1={} --video2={} --chessboard={}".format(video1, video2, chessboard)

calib_videos = "../videos/calibration/"
if experiment_id == 38:
    chessboard = "7,8,22"
    video1 = calib_videos + "38/1.avi"
    video2 = calib_videos + "38/2.avi"
elif experiment_id == 16:
    chessboard = "7,8,22"
    video1 = calib_videos + "16/1.avi"
    video2 = calib_videos + "16/2.avi"
elif experiment_id == 43:
    chessboard = "6,9,26"
    video1 = calib_videos + "43/1.avi"
    video2 = calib_videos + "43/2.avi"
elif experiment_id == 63:
    chessboard = "7,8,22"
    video1 = calib_videos + "63/1.avi"
    video2 = calib_videos + "63/2.avi"
else:
    print("Not recognized set of videos")
    exit(0)

os.system(command(video1, video2, chessboard))

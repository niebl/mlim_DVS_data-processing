#!/bin/python3
import os
import re
import argparse
import cv2
import numpy

#define command line arguments
parser = argparse.ArgumentParser(description="combine DVS frames")

parser.add_argument('--src', metavar='source', default=".",
                    help='source directory of the image series')
parser.add_argument('--out', metavar='destination', default="./out",
                    help='Destination directory for processed image series')
parser.add_argument('-N', metavar='temporal range', type=int, default=100,
                    help='Amount of past frames to combine into current frame')
parser.add_argument('--no_split', action="store_true",
					help='Whether or not N should be split across two bands. will increase temporal resolution')
parser.add_argument('--quiet', action="store_true",
					help='don\'t show console outputs')

args = parser.parse_args()

imageCache = []

def status(string):
	if args.quiet == False:
		print(string)

def averageImages(imageDirs):
	#load images
	images = []
	for image in imageDirs:
		img = cv2.imread(args.src+"/"+image)
		images.append(img)
	
	#cv2.imshow("image00", images[0])
	# List of images, all must be the same size and data type.
	averagedFrame = numpy.mean(images, axis=0)
	averagedFrame = averagedFrame.astype(numpy.uint8)
	return averagedFrame

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

status("processing.")
#load a range of images
fileList = os.listdir(args.src)
fileList.sort()
status("videos sorted.")

#make sure to consider each video id seperately. We can't mix them!
#	This presupposes that the images are all named as such:
#	e.g.:	img_001_0000001.png
#		  video id^		  ^frame nr
videos = []
for filename in fileList:
	#sort each frame with its corresponding videos	
	videoId = re.search('img_(!?\d\d\d)', filename).group(0)
	videoFound = False
	for video in videos:
		if re.search('img_(!?\d\d\d)', video[0]).group(0) == videoId:
			video.append(filename)
			videoFound = True
			break
	if not videoFound:
		newVideo = []
		newVideo.append(filename)
		videos.append(newVideo)

status("videos grouped.")

#look for available video IDs, and loop through each
for j in range(len(videos)):
	video = videos[j]
	#then look for available frames of video IDs and process them
	status(f"processing video {j+1}")
	for i in range(len(video)):
		frame = video[i]
		frameImage = cv2.imread(args.src+"/"+frame)
		#start at the first image that can load a full range of images before it
		if i >= args.N:
			#for each image, load N images before it
			preceeding = video[i-args.N:i-1]
			averages = []
			
			combinedFrame = False
			#if split is selected, split the n images into two sets and calculate the average of each.
			if not args.no_split:
				preceedingImages = split_list(preceeding, 2)
				averages.append(averageImages(preceedingImages[0]))
				averages.append(averageImages(preceedingImages[1]))
				bA1, gA1, rA1 = cv2.split(averages[0])
				bA2, gA2, rA2 = cv2.split(averages[1])
				b, g, r = cv2.split(frameImage)  
				combinedFrame = cv2.merge([r, gA1, bA2]) 
			#else, just calculate the average			 
			else: 
				averages.append(averageImages(preceeding))
				bA, gA, rA = cv2.split(averages[0])
				b, g, r = cv2.split(frameImage)
				combinedFrame = cv2.merge([r, gA, bA]) 


			#if split, remove two bands from active image. replace bands with the two average frames
			#else, just replace one band

			cv2.imwrite(args.out+"/"+frame,combinedFrame)


#how this could be optimized:
# 1: don't keep reloading the images. save them in a cache, so openCV doesn't always have to do file operations
# 2: use a GPU process where numpy is working. perhaps palma will do that automatically
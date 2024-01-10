#!/bin/python3
import json
import os
import ffmpeg
import subprocess
import argparse
from random import sample 
import re

class BoundingBox:
	
	x: float
	y: float
	w: float
	h: float
	
	def __init__(self,x,y,w,h) -> None:
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def __str__(self) -> str:
		return f"{self.x} {self.y} {self.w} {self.h}"

	def resize(newX,newY) -> str:
		ratioX = newX/1920
		ratioY = newY/1080
		self.x = self.x/ratioX
		self.y = self.y/ratioY
		self.w = self.w/ratioX
		self.h = self.h/ratioY
		return f"{self.x} {self.y} {self.w} {self.h}"

class Annotation:
	name: str
	bounding_box: BoundingBox

	def __init__(self, name, bounding_box) -> None:
		self.name = name
		self.bounding_box = bounding_box

	def __str__(self) -> str:
		return "0 "+self.bounding_box.__str__()

	def resize(self):
		self.bounding_box.resize(1280,720)

	def resized(self) -> str:
		return "0 "+self.bounding_box.resize(1280, 720)

class AnnotationsVideo:

	frame:str
	annotations: [Annotation]

	def __init__(self,frame) -> None:
		self.frame = frame
		self.annotations = []

	def add_annotation(self, annotation):
		self.annotations.append(annotation)
	
	def save_to_file(self, dir: str,video_id: str) -> str:
		file_path = dir + f"img_{video_id}_{self.frame}.txt"
		with open(file_path, 'w') as f:
			f.write(self.__str__())    
		return file_path    
	def __str__(self) -> str:
		res = ""
		for bb in self.annotations:
			res += bb.__str__() +"\n"
		return res

def read_ndjson(path):
	return [json.loads(line) for line in open(path, 'r')]

def adjust_string_length(input_str, length, fill_char):
	"""
	Adjusts the length of the input string by appending characters from the left side if needed.

	Args:
	input_str (str): The input string.
	length (int): The desired length of the string.
	fill_char (str): The character to append to the left side if needed.

	Returns:
	str: The adjusted string.

	Raises:
	ValueError: If the length of the string is greater than the specified length.
	"""
	if len(input_str) < length:
		return fill_char * (length - len(input_str)) + input_str
	elif len(input_str) == length:
		return input_str
	else:
		raise ValueError(f"Invalid input: Length of the string '{input_str}' is greater than the specified length {length}.")

def create_directory(directory_path):
	# Check if the directory already exists
	if not os.path.exists(directory_path):
		# If not, create the directory
		os.makedirs(directory_path)
		#print(f"Directory '{directory_path}' created successfully")
	#else:
		#print(f"Directory '{directory_path}' already exists")    

def pick_n_random_items(input_list, n):
	# Ensure n is not greater than the length of the input list
	n = min(n, len(input_list))

	# Use random.sample to pick n items randomly
	picked_items = sample(input_list, n)

	# Create a list of non-picked items
	non_picked_items = [item for item in input_list if item not in picked_items]

	# Return a tuple containing the picked items and non-picked items
	return picked_items, non_picked_items

def extract_frames(input_file, output_directory, video_id):
	# Create output directory if it doesn't exist
	os.makedirs(output_directory, exist_ok=True)

	# Use ffmpeg to extract frames
	image = ffmpeg.input(input_file)
	image.output(os.path.join(output_directory, f"img_{video_id}_%06d.png")).run()

"""
Note to future Caro:
God help you if you ever have to troubleshoot this
"""
def process_resultRows(input_list, video_dir, dataset_dir, args):
	dir_name = "train"
	output_location = f"{dataset_dir}/{dir_name}/images_non-prepared"

	#create a list of processed video folders
	processed_series = []
	# video: {name: filename, frame_index}
	processed_videos = []

	#go through each row
	for i in range(len(input_list)):
		result = input_list[i]
		series = result["data_row"]["details"]["dataset_name"]
		videos = os.listdir(video_dir+"/"+series)
		#videos.sort()

		#print(series)
		#print(videos)

		#extract all frames of all videos
		if series not in processed_series:
			if not args.skip_extraction:
				for video in videos:
					#extract frames of each video
					if not any(video == c["name"] for c in processed_videos):
						video_location = video_dir+"/"+series+"/"+video
						extract_frames(video_location, output_location, video)
					
						processed_videos.append({'name': video, 'frame_index': 0})

			processed_series.append(series)

		#rename each frame to match the result row
		#this assumes all rows are in alphabetical order and there are no gaps
		current_video_id = result["data_row"]["external_id"]
		#print(current_video_id)
		current_snippet = re.findall("^(.*?)\_combined", current_video_id)[0]
		frame_upper = re.findall("_(\d*?)\.mp4", current_video_id)
		#print(frame_upper)
		frame_upper = int(frame_upper[0])
		new_video_id = adjust_string_length(str(i+1),3,"0")

		for video_name in videos:
			frames = os.listdir(output_location)
			frames = list(filter(lambda frame, video_name=video_name: (video_name in frame), frames))
			frames.sort()
			frames = frames[:frame_upper]
			frames.sort()

			video_status = list(filter(lambda video: (video["name"] == video_name), processed_videos))[0]
			#frame_start = video_status["frame_index"]



			if current_snippet in video_name:
				batch_renamed = False
				for frame_index in range(len(frames)):
					frame = frames[frame_index]
					#print(frame)

					if video_name in frame:
						batch_renamed = True
						frame_current = int(re.findall("_(\d*?)\.png", frame)[0])
						
						if(frame_current <= (frame_index+1)+(video_status["frame_index"]+1)):
							new_frame_id = adjust_string_length(str(frame_index+1),6,"0")
							new_name = f"img_{new_video_id}_{new_frame_id}.png"
							os.rename(f"{output_location}/{frame}", f"{output_location}/{new_name}")
						#else:
						#	print(f"not catching {i+1}: {frame}")
					else:
						print("video name not in frame")
				if batch_renamed:
					video_status["frame_index"] += frame_upper

def labelbox_bb_to_yolo(dict, width, height):
	center_x = dict["left"] + (dict["width"] /2)
	center_y = dict["top"] + (dict["height"] /2)
	
	center_x /= width
	center_y /= height
	
	width_bb = dict["width"] / width
	height_bb = dict["height"]/ height
	
	return BoundingBox(center_x,center_y,width_bb,height_bb)

def convert_to_coco_format(json_data) -> [AnnotationsVideo]:
	width, height = json_data["media_attributes"]["width"],json_data["media_attributes"]["height"]
	if len(json_data["projects"]['clor41l0i03gi07znfo8051e3']["labels"]) == 0:
		frames = []
	else:
		frames = json_data["projects"]['clor41l0i03gi07znfo8051e3']["labels"][0]["annotations"]["frames"]
	annotations = []
	for frame in frames:
		annotations_frame = AnnotationsVideo(adjust_string_length(frame, 6, "0"))
		objects = frames[frame]["objects"]
		for objectKey in objects:
			a = Annotation(objects[objectKey]["name"],labelbox_bb_to_yolo(objects[objectKey]["bounding_box"],width,height))      
			annotations_frame.add_annotation(a)
			
		annotations.append(annotations_frame)
	return annotations


def convert_labels(input_list, dataset_dir):
	dir_name = "train"
	for i in range(len(input_list)):
		video_id = adjust_string_length(str(i+1),3,"0")
		frames : [AnnotationsVideo] = convert_to_coco_format(input_list[i])
		for frame in frames:
			frame.save_to_file(f"{dataset_dir}/{dir_name}/labels/",video_id)



if __name__ == "__main__":
	#This script assumes the given DVS data is 720p


	#define command line arguments
	parser = argparse.ArgumentParser(description="combine DVS frames")

	parser.add_argument('--src', metavar='source', default=".",
					help='source directory of the videos')
	parser.add_argument('--out', metavar='source', default=".",
					help='output directory directory of the cropped image series & bounding boxes')
	parser.add_argument('--skip_extraction', action="store_true",
					help='skips the frame extraction step if flagged')
	args = parser.parse_args()

	#specify file paths:
	dataset_dir = args.out+"/dataset/insects/"
	video_dir = args.src+"/videos"
	annotation_location = args.src+"/annotations/export-result.ndjson"
	exportResult = read_ndjson(annotation_location)

	# Create directories
	create_directory(dataset_dir)
	create_directory(os.path.join(dataset_dir, "train"))
	create_directory(os.path.join(dataset_dir, "val"))
	for dir in ["train","val"]:
		create_directory(os.path.join(dataset_dir,dir,"images"))
		create_directory(os.path.join(dataset_dir,dir,"images_non-prepared"))
		create_directory(os.path.join(dataset_dir,dir,"labels"))

	# Copy input into data.yaml
	with open(os.path.join(dataset_dir,"data.yaml"),"w") as f:
		f.write(
			"""
train: ./train/images 
val: ./val/images
nc: 1 
names: ['insect']
			"""
		)

	#this needs to be done AFTER the fact
	#val_videos, training_videos = pick_n_random_items(exportResult,5)

	#sort all the export results first, so the frames are extracted correctly
	exportResult.sort(key= lambda row: row["data_row"]["external_id"])
	#val_videos.sort(key= lambda row: row["data_row"]["external_id"])
	#training_videos.sort(key= lambda row: row["data_row"]["external_id"])

	process_resultRows(exportResult, video_dir, dataset_dir, args=args)
	convert_labels(exportResult, dataset_dir)

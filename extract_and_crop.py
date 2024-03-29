#!/bin/python3

# original by Jakob Marten Danel

import json
import os
import ffmpeg
import subprocess
import argparse
#import cv2

#define command line arguments
parser = argparse.ArgumentParser(description="combine DVS frames")

parser.add_argument('--src', metavar='source', default=".",
					help='source directory of the videos')
parser.add_argument('--out', metavar='source', default=".",
					help='output directory directory of the cropped image series & bounding boxes')
parser.add_argument('--raw_dvs', action="store_true",
					help='use this flag when you use the raw 720p DVS data. This will also resize the bounding boxes')

args = parser.parse_args()

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

def get_video_location(base_dir: str, json_row:dict) -> str:
	dir_name = json_row["data_row"]["details"]["dataset_name"]
	file_name = json_row["data_row"]["external_id"]
	return f"{base_dir}/{dir_name}/{file_name}"

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
	
def labelbox_bb_to_yolo(dict, width, height):
	left = dict["left"]
	top = dict["top"]
	width_in = dict["width"]
	height_in = width_in * (9/16) #16:9 aspect ratio

	center_x = left + (width_in /2)
	center_y = top + (dict["height"] /2)
	
	center_x /= width
	center_y /= height
	
	width_bb = dict["width"] / width
	height_bb = dict["height"]/ height
	
	return BoundingBox(center_x,center_y,width_bb,height_bb)


def convert_to_coco_format(json_data, resize=False) -> [AnnotationsVideo]:
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
			#if resize:
			#	a.resize()        
			annotations_frame.add_annotation(a)
			
		annotations.append(annotations_frame)
	return annotations

def extract_frames(input_file, output_directory,video_id, cropping = True):
	# Create output directory if it doesn't exist
	os.makedirs(output_directory, exist_ok=True)

	# Use ffmpeg to extract frames
	image = ffmpeg.input(input_file)
	if cropping:
		image = image.crop(0,0,1920,1080)
	image.output(os.path.join(output_directory, f"img_{video_id}_%06d.png")).run()

from random import sample 

def pick_n_random_items(input_list, n):
	# Ensure n is not greater than the length of the input list
	n = min(n, len(input_list))

	# Use random.sample to pick n items randomly
	picked_items = sample(input_list, n)

	# Create a list of non-picked items
	non_picked_items = [item for item in input_list if item not in picked_items]

	# Return a tuple containing the picked items and non-picked items
	return picked_items, non_picked_items


def write_data_row(data_row:dict,video_id:int,dataset_dir:str, video_base_dir:str, isTraining: bool = True, resize = False):
	dir_name = "train" if isTraining else "val"
	video_id = adjust_string_length(str(video_id),3,"0")
	cropping = not resize
	frames : [AnnotationsVideo] = convert_to_coco_format(data_row, cropping)        
	for frame in frames:
		frame.save_to_file(f"{dataset_dir}/{dir_name}/labels/",video_id)
	
	video_location = get_video_location(video_base_dir, data_row)
	extract_frames(video_location,f"{dataset_dir}/{dir_name}/images_non-prepared",video_id, resize)
	
def create_directory(directory_path):
	# Check if the directory already exists
	if not os.path.exists(directory_path):
		# If not, create the directory
		os.makedirs(directory_path)
		print(f"Directory '{directory_path}' created successfully")
	else:
		print(f"Directory '{directory_path}' already exists")    
	
	
if __name__ == "__main__":
	dataset_dir = args.out+"/dataset/insects/"
	video_dir = args.src+"/videos"
	anotation_location = args.src+"/annotations/export-result.ndjson"
	
	data = read_ndjson(anotation_location)
	
	# Create directory structure
	create_directory(dataset_dir)
	create_directory(os.path.join(dataset_dir, "train"))
	create_directory(os.path.join(dataset_dir, "val"))
	
	# Copy input into data.yaml
	with open(os.path.join(dataset_dir,"data.yaml"),"w") as f:
		f.write(
"""train: ./train/images 
val: ./val/images
nc: 1 
names: ['insect']"""
		)
		
	for dir in ["train","val"]:
		create_directory(os.path.join(dataset_dir,dir,"images"))
		create_directory(os.path.join(dataset_dir,dir,"images_non-prepared"))
		create_directory(os.path.join(dataset_dir,dir,"labels"))
	
	val_videos, training_videos = pick_n_random_items(data,5)
	

#For now, this script doesn't assign eval data. that will be done via shell script

	for i in range(len(training_videos)):
		write_data_row(data[i],(i+1),dataset_dir,video_dir, args.raw_dvs)

	for i in range(len(val_videos)):
		write_data_row(data[i],(i+1),dataset_dir,video_dir, args.raw_dvs)
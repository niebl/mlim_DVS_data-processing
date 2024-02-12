#instructions.

#have the following directory structure for convert-to-yolo:
#
#exampleDir/
#├── *script location*
#├── input
#│	├── videos
#│	│	└── *video sources*
#│	└── annotations
#│		└── *export-result.ndjson*
#└── output

#convert-to-yolo results in the following directory structure
#exampleDir/
#├── *script location*
#├── input
#│	 └── [...]
#└── output
# 	 └── dataset
#		 └── insects
#			 ├── train
#			 │	 ├── images
#			 │	 │	 └── *output for onion_skinner*
#			 │	 ├── images_non-prepared
#			 │	 │	 └── *raw extracted frames*
#			 │	 └── labels
#			 ├── val
#			 │	 ├── images
#			 │	 └── labels
#			 └── test
# 				 ├── images
#				 └── labels

#PREPROCESSING
#run the following command
python ./convert_to_yolo.py --src input --out output

python ./onion_skinner.py \
	--src output/dataset/insects/train/images_non-prepared \
	--out output/dataset/insects/train/images -N 200 --proc 20
	#proc is the amount of subprocesses to be spawned. lower that number if the process crashes due to insufficient RAM

#val-dataset A
mv output/dataset/insects/train/images/img_001_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_001_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_002_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_002_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_003_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_003_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_004_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_004_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_005_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_005_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_006_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_006_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_007_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_007_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_008_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_008_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_009_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_009_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_010_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_010_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_011_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_011_* output/dataset/insects/val/labels

##test-dataset A
#mv output/dataset/insects/train/images/img_034_* output/dataset/insects/test/images
#mv output/dataset/insects/train/images/img_036_* output/dataset/insects/test/images
#mv output/dataset/insects/train/images/img_042_* output/dataset/insects/test/images
#mv output/dataset/insects/train/labels/img_034_* output/dataset/insects/test/labels
#mv output/dataset/insects/train/labels/img_036_* output/dataset/insects/test/labels
#mv output/dataset/insects/train/labels/img_042_* output/dataset/insects/test/labels

#val-dataset B
mv output/dataset/insects/train/images/img_012_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_012_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_013_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_013_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_014_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_014_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_015_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_015_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_016_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_016_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_017_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_017_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_018_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_018_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_019_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_019_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_020_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_020_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_021_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_021_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_022_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_022_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_023_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_023_* output/dataset/insects/val/labels

##test-dataset B
#mv output/dataset/insects/train/images/img_009_* output/dataset/insects/test/images
#mv output/dataset/insects/train/images/img_010_* output/dataset/insects/test/images
#mv output/dataset/insects/train/images/img_011_* output/dataset/insects/test/images
#mv output/dataset/insects/train/labels/img_009_* output/dataset/insects/test/labels
#mv output/dataset/insects/train/labels/img_010_* output/dataset/insects/test/labels
#mv output/dataset/insects/train/labels/img_011_* output/dataset/insects/test/labels





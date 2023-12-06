instructions.

#have the following directory structure:
#
#exampleDir/
#├── *script location*
#├── input
#│	├── videos
#│	│	└── *video sources*
#│	└── annotations
#│		└── *.ndjson*
#└── output

#PREPROCESSING
#run the following command
python ./extract_and_crop.py --src input --out output && \
python ./onion_skinner.py \
	--src output/dataset/insects/train/images_non-prepared \
	--out output/dataset/insects/train/images -N 200

#SETTING RANDOM DATASETS ASIDE FOR VAL
# so far, just do it manually. I'll make a shell command for it later
#instructions.

#have the following directory structure:
#
#exampleDir/
#├── *script location*
#├── input
#│	├── videos
#│	│	└── *video sources*
#│	└── annotations
#│		└── *export-result.ndjson*
#└── output

#PREPROCESSING
#run the following command
python ./extract_and_crop.py --src input --out output

python ./onion_skinner.py \
	--src output/dataset/insects/train/images_non-prepared \
	--out output/dataset/insects/train/images -N 200

#SETTING RANDOM DATASETS ASIDE FOR VAL
# for now, quite naive code
VIDEO_AMOUNT=33
RAND1=$((1 + RANDOM % VIDEO_AMOUNT))
RAND2=$((1 + RANDOM % VIDEO_AMOUNT))
RAND3=$((1 + RANDOM % VIDEO_AMOUNT))
RAND4=$((1 + RANDOM % VIDEO_AMOUNT))
RAND5=$((1 + RANDOM % VIDEO_AMOUNT))
mv output/dataset/insects/train/images/img_*${RAND1}_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_*${RAND1}_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_*${RAND2}_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_*${RAND2}_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_*${RAND3}_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_*${RAND3}_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_*${RAND4}_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_*${RAND4}_* output/dataset/insects/val/labels
mv output/dataset/insects/train/images/img_*${RAND5}_* output/dataset/insects/val/images
mv output/dataset/insects/train/labels/img_*${RAND5}_* output/dataset/insects/val/labels

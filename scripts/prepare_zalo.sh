HOME=~/joanna
REPO=$HOME/zalo/Entity-Relation-As-Multi-Turn-QA
PRETRAINED_MODEL_PATH=vinai/phobert-base

python3 $REPO/preprocess_zalo.py \
--data_dir $REPO/data/raw_data/zalo/train \
--dataset_tag zalo \
--window_size 220 \
--overlap 45 \
--threshold 1 \
--max_distance 90 \
--output_base_dir $REPO/data/cleaned_data/zalo/ \
--pretrained_model_path  $PRETRAINED_MODEL_PATH 

python3 $REPO/preprocess_zalo.py \
--data_dir $REPO/data/raw_data/zalo/dev \
--dataset_tag zalo \
--output_base_dir $REPO/data/cleaned_data/zalo/ \
--pretrained_model_path  $PRETRAINED_MODEL_PATH \
--is_test

python3 $REPO/preprocess_zalo.py \
--data_dir $REPO/data/raw_data/zalo/test \
--dataset_tag zalo \
--output_base_dir $REPO/data/cleaned_data/zalo/ \
--pretrained_model_path  $PRETRAINED_MODEL_PATH \
--is_test

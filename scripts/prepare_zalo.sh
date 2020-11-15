HOME=~/joanna
REPO=$HOME/zalo/multi_qa/Entity-Relation-As-Multi-Turn-QA
# PRETRAINED_MODEL_PATH=$HOME/zalo/single_qa/weights/phobert_base/checkpoint-8500
# PRETRAINED_MODEL_PATH=bert-base-multilingual-uncased
PRETRAINED_MODEL_PATH=vinai/phobert-base

#training data
python3 $REPO/preprocess_zalo.py \
--data_dir $REPO/data/raw_data/zalo/train \
--dataset_tag zalo \
--window_size 235 \
--overlap 15 \
--threshold 1 \
--max_distance 45 \
--output_base_dir $REPO/data/cleaned_data/Zalo \
--pretrained_model_path  $PRETRAINED_MODEL_PATH 

#test data
python3 $REPO/preprocess_zalo.py \
--data_dir $REPO/data/raw_data/zalo/dev \
--dataset_tag zalo \
--output_base_dir $REPO/data/cleaned_data/Zalo \
--pretrained_model_path  $PRETRAINED_MODEL_PATH \
--is_test

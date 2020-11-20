export CUDA_VISIBLE_DEVICES=1
HOME=~/joanna
REPO=$HOME/zalo/Entity-Relation-As-Multi-Turn-QA
PRETRAINED_MODEL=vinai/phobert-large


python3 $REPO/train.py \
--dataset_tag zalo \
--train_path $REPO/data/cleaned_data/zalo/train.json \
--train_batch 10 \
--test_path $REPO/data/cleaned_data/zalo/dev.json \
--test_batch 10 \
--pretrained_model_path $PRETRAINED_MODEL \
--max_epochs 10 \
--warmup_ratio 0.1 \
--lr 2e-5 \
--theta 0.25 \
--window_size 220 \
--overlap 45 \
--threshold 1 \
--max_grad_norm 1 \
--seed 0 \
--amp

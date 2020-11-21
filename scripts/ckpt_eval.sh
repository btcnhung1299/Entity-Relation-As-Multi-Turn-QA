export CUDA_VISIBLE_DEVICES=3
HOME=~/joanna
REPO=$HOME/zalo/Entity-Relation-As-Multi-Turn-QA

python $REPO/ckpt_eval.py \
--window_size 220 \
--overlap 20 \
--checkpoint_path $REPO/checkpoints/zalo/2020_11_21_02_42_20/checkpoint_7.ckpt \
--test_path $REPO/data/cleaned_data/zalo/dev.json \
--test_batch 40 \
--threshold 1

export CUDA_VISIBLE_DEVICES=3
HOME=~/joanna
REPO=$HOME/zalo/Entity-Relation-As-Multi-Turn-QA

python $REPO/ckpt_eval.py \
--window_size 220 \
--overlap 10 \
--checkpoint_path $REPO/checkpoints/zalo/2020_11_20_02_16_22/checkpoint_1.ckpt \
--test_path $REPO/data/cleaned_data/zalo/dev.json \
--test_batch 20 \
--threshold 1

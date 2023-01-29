# Counter-GAP

The Counter-GAP dataset is located in `data/`, where 'C-GAP.tsv' is the dataset used in our experiments and `C-GAP-withdot.tsv` is the original dataset with a "." after titles ({e.g.}, Mr., Mrs., etc.).
The implementation of coreference resolution models in `coref/` are directly copied from , with the only change of the `read_tsv` method in `coref/gap_to_jsonlines.py`. [Dense Passage Retrieval for Open-Domain Question Answering.](https://arxiv.org/abs/2004.04906)

## Debiased Models
You can download our aCDA/nCDA-debiased BERT/SpanBERT checkpoints from the follwoing links (checkpoints fine-tuned on the original training set can be downloaded from the link in `coref/`):

|                | aCDA-debiased | nCDA-debiased |
| -------------  |:-------------:| -------------:|
| BERT-base      |               |               |
| BERT-large     |               |               |              
| SpanBERT-base  |               |               |
| SpanBERT-large |               |               |

Or if you want to debias the original models yourself, you could first download the OntoNotes datasets (following the instructions in `coref/`) and
generate the aCDA/nCDA version of the training set (assuming the training set `train.english.v4_gold_conll` is in `data/`): 
```bash
cd cda
python -c "from name import *;m=NameMapping()"
python word_swapper.py > acda-train.english.v4_gold_conll
python word_swapper.py --name > ncda-train.english.v4_gold_conll
```
Next, subsitute the original training set (`train.english.v4_gold_conll`) with `acda-train.english.v4_gold_conll` or `ncda-train.english.v4_gold_conll`, and follow the instructions in `coref/` to fine-tune a pre-trained BERT/SpanBERT on them to obtain the debiased checkpoints.  

## Evaluation on Counter-GAP
For each `debiasing_type` in `("none", "acda", "ncda")`, download the checkpoints for each `model_name` in `("bert_base", "bert_large", "spanbert_base", "spanbert_large")` to the corresponding dirs in `data/`, and run the following commands:
```bash
cd coref
python gap_to_jsonlines.py ../data/C-GAP.tsv ../data/${model_name}/vocab.txt
CUDA_VISIBLE_DEVICES=0 python predict.py ${model_name} ../data/C-GAP.jsonlines ../data/${model_name}_output.jsonlines
python to_gap_tsv.py ../data/${model_name}_output.jsonlines
mv ../data/${model_name}_output.tsv ../results/${debiasing_type}/${model_name}_output.tsv
mv ../data/C-GAP.tsv ../results/${debiasing_type}/C-GAP.tsv
```
Next, calculate the evaluation metrics:
```bash
cd ..
python scorer.py --model ${model_name} --debias ${debiasing_type}
```


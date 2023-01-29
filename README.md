# CounterGAP

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
For each model_type in `{none, acda, ncda}`, download the checkpoints of each model_name in `{bert_base, bert_large, spanbert_base, spanbert_large}` to `data/`, and run the following commands:
```bash
cd coref
python gap_to_jsonlines.py ../data/C-GAP.tsv ../data/{model_name}/vocab.txt
CUDA_VISIBLE_DEVICES=0 python predict.py {model_name} ../data/C-GAP.jsonlines ../data/{model_name}_output.jsonlines
python to_gap_tsv.py ../data/{model_name}_output.jsonlines


```

## Calculating Evaluation Metrics

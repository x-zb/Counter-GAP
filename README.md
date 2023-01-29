# CounterGAP

## Generating Counterfactually Augmented Training Data
Generate the debiasing training set:
```bash
cd cda
python -c "from name import *;m=NameMapping()"
python word_swapper.py > acda-train.english.v4_gold_conll
python word_swapper.py --name > ncda-train.english.v4_gold_conll
```
Subsitute the original training set (train.english.v4_gold_conll) with the debiasing training set (acda-train.english.v4_gold_conll or ncda-train.english.v4_gold_conll) and fine-tune a pre-trained BERT/SpanBERT on them 
## Debiasing

## Evaluation on Counter-GAP
You can download our aCDA/nCDA-debiased BERT/SpanBERT checkpoints from the follwoing links:

|                | aCDA-debiased | nCDA-debiased |
| -------------  |:-------------:| -------------:|
| BERT-base      |               |               |
| BERT-large     |               |               |              
| SpanBERT-base  |               |               |
| SpanBERT-large |               |               |

## Calculating Evaluation Metrics

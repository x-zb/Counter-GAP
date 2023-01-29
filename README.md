# CounterGAP

## Generating Counterfactually Augmented Training Data

## Debiasing

## Evaluation on Counter-GAP
You can download our aCDA/nCDA-debiased BERT/SpanBERT checkpoints from the follwoing links (the original checkpoints can be downloaded in the repository):

|                | aCDA-debiased | nCDA-debiased |
| -------------  |:-------------:| -------------:|
| BERT-base      |               |               |
| BERT-large     |               |               |              
| SpanBERT-base  |               |               |
| SpanBERT-large |               |               |

Or if you want to debias the original models yourself, you could first generate the aCDA/nCDA version of the OntoNotes training set (assuming the file train.english.v4_gold_conll is in data/): 
```bash
cd cda
python -c "from name import *;m=NameMapping()"
python word_swapper.py > acda-train.english.v4_gold_conll
python word_swapper.py --name > ncda-train.english.v4_gold_conll
```
Next, subsitute the original training set (train.english.v4_gold_conll) with the debiasing training set (acda-train.english.v4_gold_conll or ncda-train.english.v4_gold_conll) to fine-tune a pre-trained BERT/SpanBERT. Please refer to the instructions in  
## Calculating Evaluation Metrics

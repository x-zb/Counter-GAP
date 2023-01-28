import math
import os
import csv
from scipy.stats import spearmanr, pearsonr
from argparse import ArgumentParser
from utils import Gender, PRONOUNS, GAP_FIELDNAMES
from annotation_utils import id2num


parser=ArgumentParser(description='C-GAP')
parser.add_argument('--model',type=str,default='') # bert_base,bert_large,spanbert_base,spanbert_large
parser.add_argument('--src',type=str,default='both') # gb,bc,both
# parser.add_argument('--version',type=str,default='full') # 'control','swap'
parser.add_argument('--debias',type=str,default='none') # 'none','acda','ncda'
args=parser.parse_args()


gold_scores = {}
id2gender = {} # contains only original ids
str2bool = {'TRUE':True,'True':True,'FALSE':False,'False':False}

# collect gold results
label_cnt = {'TF':0,'FT':0,'FF':0}
with open(os.path.join('results','C-GAP.tsv'),'r',encoding='utf-8') as f1:
	reader = csv.DictReader(f1,fieldnames=GAP_FIELDNAMES,delimiter='\t')
	# Skip the header line
	next(reader, None)
	row_no = 1
	for row in reader:
		gold_scores[row['ID']] = {}
		gold_scores[row['ID']]['A-coref'] = str2bool[row['A-coref']]
		gold_scores[row['ID']]['B-coref'] = str2bool[row['B-coref']]	
		if ('swap' not in row['ID']) and ('control' not in row['ID']): 
			id2gender[row['ID']] = PRONOUNS[row['Pronoun'].lower()]
			if  row['A-coref']=='TRUE' and row['B-coref']=='FALSE':
				label_cnt['TF']+=1
			elif row['A-coref']=='FALSE' and row['B-coref']=='TRUE':
				label_cnt['FT']+=1
			else:
				assert row['A-coref']=='FALSE' and row['B-coref']=='FALSE'
				label_cnt['FF']+=1



results = {}
# id_range = {'gb':range(0,1401),'bc':range(1401,2650),'both':range(0,2650)}
with open(os.path.join('results',args.debias,args.model+'_output.tsv'),'r',encoding='utf-8') as f1:
	reader = csv.DictReader(f1,fieldnames=['ID','A-coref','B-coref','output'],delimiter='\t')
	# Skip the header line
	next(reader, None)
	for row in reader:
		if id2num(row['ID']) not in results:
			results[id2num(row['ID'])] = {id2num(row['ID']):-1,
										id2num(row['ID'])+'-control':-1,
										id2num(row['ID'])+'-swap-1':-1,
										id2num(row['ID'])+'-swap-2':-1}
		results[id2num(row['ID'])][row['ID']] = (str2bool[row['A-coref']]==gold_scores[row['ID']]['A-coref']) and (str2bool[row['B-coref']]==gold_scores[row['ID']]['B-coref'])

N = len(results)

distribution = {-2:[],-1:[],0:[],1:[],2:[]}

orig_gender = 0 # acc
counter_gender = 0 # acc

acc = 0
acc_male = 0
acc_female = 0

inconsist_male = 0
inconsist_female = 0
inconsist_within = 0

inconsist_m2f = 0
inconsist_f2m = 0
inconsist_across = 0

x = {-0.5:[],0:[],1:[]}

for id_ in results:
	orig_gender += int(results[id_][id_]+results[id_][id_+'-control'])
	counter_gender += int(results[id_][id_+'-swap-1']+results[id_][id_+'-swap-2'])
	inconsist_within += abs(results[id_][id_]-results[id_][id_+'-control'])+abs(results[id_][id_+'-swap-1']-results[id_][id_+'-swap-2'])
	# inconsist_across += abs(results[id_][id_]-results[id_][id_+'-swap-1'])+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
	inconsist_across += (abs(results[id_][id_]-results[id_][id_+'-swap-1'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_]-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-1'])
		)

	diff = int(results[id_][id_]+results[id_][id_+'-control']-results[id_][id_+'-swap-1']-results[id_][id_+'-swap-2'])
	acc += int(results[id_][id_]+results[id_][id_+'-control']+results[id_][id_+'-swap-1']+results[id_][id_+'-swap-2'])
	if id2gender[id_] == Gender.MASCULINE:
		# results[id_]['diff'] = diff
		distribution[diff].append(id_)
		acc_male += int(results[id_][id_]+results[id_][id_+'-control'])
		acc_female += int(results[id_][id_+'-swap-1']+results[id_][id_+'-swap-2'])
		inconsist_male += abs(results[id_][id_]-results[id_][id_+'-control'])
		inconsist_female += abs(results[id_][id_+'-swap-1']-results[id_][id_+'-swap-2'])
		inconsist_m2f += (abs(results[id_][id_]-results[id_][id_+'-swap-1'])
			+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
			+abs(results[id_][id_]-results[id_][id_+'-swap-2'])
			+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-1'])
			)
	else:
		assert id2gender[id_]==Gender.FEMININE
		# results[id_]['diff'] = -diff
		distribution[-diff].append(id_)
		acc_female += int(results[id_][id_]+results[id_][id_+'-control'])
		acc_male += int(results[id_][id_+'-swap-1']+results[id_][id_+'-swap-2'])
		inconsist_female += abs(results[id_][id_]-results[id_][id_+'-control'])
		inconsist_male += abs(results[id_][id_+'-swap-1']-results[id_][id_+'-swap-2'])
		inconsist_f2m += (abs(results[id_][id_]-results[id_][id_+'-swap-1'])
			+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
			+abs(results[id_][id_]-results[id_][id_+'-swap-2'])
			+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-1'])
			)
	x[(abs(results[id_][id_]-results[id_][id_+'-swap-1'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_]-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-1'])
		)/4 - 
		(abs(results[id_][id_]-results[id_][id_+'-control'])
		+abs(results[id_][id_+'-swap-1']-results[id_][id_+'-swap-2'])
		)/2].append(id_)

acc /= (N*4)
acc_male /= (N*2)
acc_female /= (N*2)

inconsist_male /= N
inconsist_female /= N
inconsist_within /= (N*2)

orig_gender /= (N*2)
counter_gender /= (N*2)

inconsist_m2f /= (N*2)
inconsist_f2m /= (N*2)
# inconsist_across /= (N*2)
inconsist_across /= (N*4)

def compute_bias(distribution):
	sample_size = sum([len(distribution[key]) for key in distribution])
	mean = 0
	abs_mean = 0
	second_geometric_moment = 0
	prop = 0
	var = 0
	print('distribution',[(key,len(distribution[key])) for key in distribution])
	print('distribution',[(key,len(distribution[key])/sample_size) for key in distribution])
	for key in distribution:
		mean += len(distribution[key])*(key/2)
		abs_mean += len(distribution[key])*abs(key/2)
		second_geometric_moment += ((key/2)**2)*len(distribution[key])
		prop += len(distribution[key]) if key!=0 else 0
	mean /= sample_size # unbiased estimate for E[x]
	abs_mean /= sample_size
	second_geometric_moment /= sample_size
	prop /= sample_size

	for key in distribution:
		var += ((key/2-mean)**2)*len(distribution[key])
	
	var /= (sample_size-1) # unbiased estimate for var[x] = E[x^2]-(Ex)^2
	# second_geometric_moment = var+mean**2 # unbiased estimate for E[x^2]

	print('sample_size',sample_size)
	# print('p(B!=0) = {:.2f}%'.format(prop*100)) # Jaccard distance
	# print('abs_mean: {:.4f}'.format(abs_mean)) # counterfactual individual bias
	# print('sample mean: {:.4f}'.format(mean)) # equivalent to overall acc
	# print('sample std: {:.4f}'.format(math.sqrt(var)))
	# print('sample sqrt of second_geometric_moment: {:.4f}'.format(math.sqrt(second_geometric_moment)))
	# print('')



# calculate dataset statistics
male_num = 0
female_num = 0
for id_ in results:
	if id2gender[id_]==Gender.MASCULINE:
		male_num+=1
	else: 
		assert id2gender[id_]==Gender.FEMININE
		female_num+=1
print('=== Statistics ===')
print('source corpus: '+args.src)
print('male',male_num)
print('female',female_num)
print('label_cnt:',label_cnt) # TF=318, FT=663, FF=43
print('')

print('===Model Tested: '+args.model+'===')
print('\n=== Counter-GAP ===')
compute_bias(distribution)

print('Overall acc: {:.2f}%'.format(acc*100)) # overall acc
print('Male acc: {:.2f}%'.format(acc_male*100))
print('Female acc: {:.2f}%'.format(acc_female*100))
print('Diff: {:.2f}%'.format((acc_male-acc_female)*100)) # group fairness, equality of odds
print('')

print('Inconsistency within genders: {:.2f}%'.format(inconsist_within*100))
print('Male inconsistency: {:.2f}%'.format(inconsist_male*100))
print('Female inconsistency: {:.2f}%'.format(inconsist_female*100))
print('Diff: {:.2f}%'.format((inconsist_male-inconsist_female)*100))
print('')

print('Inconsistency across genders: {:.2f}%'.format(inconsist_across*100))
print('M2F inconsistency: {:.2f}%'.format(inconsist_m2f*100))
print('F2M inconsistency: {:.2f}%'.format(inconsist_f2m*100))
print('Diff: {:.2f}%'.format((inconsist_m2f -inconsist_f2m)*100))
print('')
print('delta I: {:.2f}%'.format((inconsist_across - inconsist_within)*100))
print('')

print('Original-gender acc: {:.2f}%'.format(orig_gender*100))
print('Counterfactual-gender acc: {:.2f}%'.format(counter_gender*100))
print('Diff: {:.2f}%'.format((orig_gender - counter_gender)*100))

print('')


# I_list = []
# B_list = []
# for key in distribution:
# 	for id_ in distribution[key]:
# 		if id2gender[id_]==Gender.MASCULINE:
# 			I_list.append(1)
# 		else:
# 			I_list.append(-1)
# 		B_list.append(key)
# print('Pearson\'s r:',pearsonr(I_list,B_list))
# print('Spearman\'s rho:',spearmanr(I_list,B_list))


I_list = []
B_list = []
for key in distribution:
	for id_ in distribution[key]:
		if id2gender[id_]==Gender.MASCULINE:
			I_list.append(1)
		else:
			I_list.append(-1)
		B_list.append((abs(results[id_][id_]-results[id_][id_+'-swap-1'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_]-results[id_][id_+'-swap-2'])
		+abs(results[id_][id_+'-control']-results[id_][id_+'-swap-1'])
		))
print('Pearson\'s r:',pearsonr(I_list,B_list))
print('Spearman\'s rho:',spearmanr(I_list,B_list))


acc_1 = 0
acc_male_1 = 0
acc_female_1 = 0
for id_ in results:
	acc_1 += int(results[id_][id_])
	if id2gender[id_] == Gender.MASCULINE:
		acc_male_1 += int(results[id_][id_])
	else:
		assert id2gender[id_]==Gender.FEMININE
		acc_female_1 += int(results[id_][id_])
acc_1 /= N
acc_male_1 /= (N/2)
acc_female_1 /= (N/2)
print('\n=== GAP (ours) ===')
print('Overall acc: {:.2f}%'.format(acc_1*100)) # overall acc
print('Male acc: {:.2f}%'.format(acc_male_1*100))
print('Female acc: {:.2f}%'.format(acc_female_1*100))
print('Diff: {:.2f}%'.format((acc_male_1-acc_female_1)*100)) # group fairness, equality of odds
print('')


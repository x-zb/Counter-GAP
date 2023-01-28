import os
import csv
from enum import Enum
from argparse import ArgumentParser

# constants

class Gender(Enum):
	UNKNOWN = 0
	MASCULINE = 1
	FEMININE = 2

# Mapping of (lowercased) pronoun form to gender value. Note that reflexives
# are not included in GAP, so do not appear here.
PRONOUNS = {
	'she': Gender.FEMININE,
	'her': Gender.FEMININE,
	'hers': Gender.FEMININE,
	'he': Gender.MASCULINE,
	'his': Gender.MASCULINE,
	'him': Gender.MASCULINE
}

GAP_FIELDNAMES = [
    'ID', 'Text', 'Pronoun', 'Pronoun-offset', 'A', 'A-offset', 'A-coref', 'B',
    'B-offset', 'B-coref', 'Book'
]


def logging(s:str,log_=True,print_=True):
	if print_:
		print(s)
	if log_:
		with open('log.txt','a+') as f_log:
			f_log.write(s + '\n')



def ins2gaptsv(instances,filename='unannotated-instances.tsv'):
	with open(filename,'w',newline='',encoding='utf-8') as f:
		writer = csv.DictWriter(f,fieldnames=GAP_FIELDNAMES,delimiter='\t')
		writer.writeheader()
		for ins in instances:
			data = dict.fromkeys(GAP_FIELDNAMES,'')
			data['ID'] = ins['ID']
			data['Text'] = ins['Text']
			data['Pronoun'] = ins['Pronoun']
			data['Pronoun-offset'] = str(ins['Pronoun-offset'])
			data['A'] = ins['A']
			data['A-offset'] = str(ins['A-offset'])
			data['A-coref'] = ins['A-coref']
			data['B'] = ins['B']
			data['B-offset'] = str(ins['B-offset'])
			data['B-coref'] = ins['B-coref']
			data['Book'] = ins['Book']
			writer.writerow(data)

def gaptsv2ins(filename):
	instances = []
	with open(filename,'r',encoding='utf-8') as f1:
		reader = csv.DictReader(f1,fieldnames=GAP_FIELDNAMES,delimiter='\t')
		# Skip the header line
		next(reader, None)
		for row in reader:
			data = dict.fromkeys(GAP_FIELDNAMES,'')
			data['ID'] = row['ID']
			data['Text'] = row['Text']
			data['Pronoun'] = row['Pronoun']
			data['Pronoun-offset'] = int(row['Pronoun-offset'])
			data['A'] = row['A']
			data['A-offset'] = int(row['A-offset'])
			data['A-coref'] = row['A-coref']
			data['B'] = row['B']
			data['B-offset'] = int(row['B-offset'])
			data['B-coref'] = row['B-coref']
			data['Book'] = row['Book']
			instances.append(data)
	return instances

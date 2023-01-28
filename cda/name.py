
import codecs
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite

class NameMapping():
	
	COUNTRIES = u"""great_britain ireland usa italy malta portugal spain france 
					belgium luxembourg the_netherlands east_frisia germany austria 
					swiss iceland denmark norway sweden finland estonia latvia 
					lithuania poland czech_republic slovakia hungary romania 
					bulgaria bosniaand croatia kosovo macedonia montenegro serbia 
					slovenia albania greece russia belarus moldova ukraine armenia 
					azerbaijan georgia the_stans turkey arabia israel china india 
					japan korea vietnam other_countries
				""".split()

	def __init__(self, filename = None):	
		self.names = {}
		self.anonymize = {}
		self.gender_name_set = {'male':[],'female':[],'mostly_male':[],'mostly_female':[]}
		self.map = {}
		self._parse('nam_dict.txt')

		for name in self.names:
			if len(self.names[name])>1:
				max_sum = 0
				max_gender = ''
				for gender in self.names[name].keys():
					cur_sum = np.linalg.norm(self.names[name][gender],ord=1)
					if cur_sum>max_sum:
						max_sum = cur_sum
						max_gender = gender
				self.names[name] = {max_gender:self.names[name][max_gender]}

		self._set_anonymize()
		if filename!=None:
			with codecs.open(filename, encoding="utf-8") as f:
				for line in f:
					(name1,name2) = line.strip().split('\t')
					self.map[name1] = name2
		else:
			self._set_map(max_n=2e4)
			with open('nam_map.txt', 'w', encoding="utf-8") as f:
				for (name1,name2) in self.map.items():
					f.write(name1+'\t'+name2+'\n')

	def _parse(self, filename):
		"""Opens data file and for each line, calls _eat_name_line"""
		with codecs.open(filename, encoding="utf-8") as f:
			for line in f:
				self._eat_name_line(line.strip())

	def _eat_name_line(self, line):
		"""Parses one line of data file"""
		if line[0] not in "#=":
			parts = line.split()
			country_values = line[31:-1]
			name = parts[1]

			if parts[0] == "M":
				self._set(name, u"male", country_values)
			elif parts[0] == "1M" or parts[0] == "?M":
				self._set(name, u"mostly_male", country_values)
			elif parts[0] == "F":
				self._set(name, u"female", country_values)
			elif parts[0] == "1F" or parts[0] == "?F":
				self._set(name, u"mostly_female", country_values)
			elif parts[0] == "?":
				self._set(name, u"andy", country_values)
			else:
				raise "Not sure what to do with a sex of %s" % parts[0]

	def _set(self, name, gender, country_values):
		"""Sets gender and relevant country values for names dictionary of detector"""
		if '+' in name:
			for replacement in ['', ' ', '-']:
				self._set(name.replace('+', replacement), gender, country_values)
		else:
			if name not in self.names:
				self.names[name] = {}
			self.names[name][gender] = np.array([0 if c==' ' else int(c,base=16) for c in country_values])

	def _set_anonymize(self):
		name_set = set(self.names.keys())
		for i,name in enumerate(name_set):
			self.anonymize[name] = 'E'+str(i)

	def _set_map(self, max_n):
		for name in self.names:
			gender = list(self.names[name].keys())[0]
			if gender in ['male','female','mostly_male','mostly_female']:
				country_vector = self.names[name][gender]
				self.gender_name_set[gender].append((name,country_vector))
		matches_1 = self._bipartite_match(self.gender_name_set['male'],self.gender_name_set['female'],max_n)
		matches_2 = self._bipartite_match(self.gender_name_set['mostly_male'],self.gender_name_set['mostly_female'],max_n)
		self.map = dict(list(matches_1.items())+list(matches_2.items()))


	def _bipartite_match(self, list1, list2, max_n):
		
		def distance(v1,v2,alpha=(12/11)):
			d = np.linalg.norm(v1-v2,ord=2)
			cos = np.dot(v1,v2)/(np.linalg.norm(v1,ord=2)*np.linalg.norm(v2,ord=2)+1e-10)
			return d*(alpha-cos)

		list1.sort(key=lambda ele:np.linalg.norm(ele[1],ord=1),reverse=True) # sum of frequency over all the countries
		list2.sort(key=lambda ele:np.linalg.norm(ele[1],ord=1),reverse=True)
		n = min([len(list1),len(list2),max_n])
		B = nx.Graph() # undirected graph, edges are symetric
		B.add_nodes_from([name for (name,country_vector) in list1[:n]], bipartite=0)
		B.add_nodes_from([name for (name,country_vector) in list2[:n]], bipartite=1)
		B.add_edges_from([(name1,name2,{"weight": distance(v1,v2)}) for (name1,v1) in list1[:n] for (name2,v2) in list2[:n]])
		matches = bipartite.minimum_weight_full_matching(B)
		print(n,len(matches)) # including inverse map 
		# 18506, 37012 for male/female; 568, 1136 for mostly_male/female
		return matches
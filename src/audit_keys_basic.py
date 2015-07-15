import xml.etree.cElementTree as ET
import pprint
import sys
import re
import json

filename = '../data/file.osm'

# Print the head of the XML document
def printhead(filename, num_of_lines):

	print '\n *** Head of the OSM document (first {} lines) ***\n'.format(num_of_lines)

	i = 0
	head = ''
	with open(filename) as r:
		for line in r:
			if i < num_of_lines:
				head += line
				i += 1
			else:
				break
	print(head)

# Count the number of different elements existing in the XML file
def count_elements(filename):
	tag_dict = {}
	for event, elem in ET.iterparse(filename):
		if elem.tag in tag_dict:
			tag_dict[elem.tag] += 1
		else:
			tag_dict[elem.tag] = 1

	pprint.pprint(tag_dict)

# Count the number of different tags within the nodes or ways elements
def count_tags(filename):
	tag_dict = {}
	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.findall('tag'):
				if tag.attrib['k'] in tag_dict:
					tag_dict[tag.attrib['k']] += 1
				else:
					tag_dict[tag.attrib['k']] = 1

	pprint.pprint(tag_dict)

# Print out the users that have eddited the file
def unique_users(filename):
	users = set()
	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way', 'relation']:
			users.add(elem.attrib['user'])
	pprint.pprint(users)

# Count the type of keys inside tag elements regarding its "structure" (regx pattern)
def type_of_keys(filename):
	lower = re.compile(r'^([a-z]|_)*$')
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

	keys = {'lower': 0, 'lower_colon': 0, 'problemchars': 0, 'other': 0}
	other = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag == 'tag':
			k = elem.attrib['k']
			if lower.match(k):
				keys['lower'] += 1
			elif lower_colon.match(k):
				keys['lower_colon'] += 1
			elif problemchars.match(k):
				keys['problemchars'] += 1
			else:
				if k in other:
					other[k] += 1
				else:
					other[k] = 1
				keys['other'] += 1
	pprint.pprint(keys)

# Count the type of keys inside tag elements regarding its "structure" (regx pattern)
# Also count the type of keys inside those patterns
def type_of_keys_and_tags(filename):

	lower = re.compile(r'^([a-z]|_)*$')
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

	keys_num = {'lower': 0, 'lower_colon': 0, 'problemchars': 0, 'other': 0}
	keys = {'lower': {}, 'lower_colon': {}, 'problemchars': {}, 'other': {}}
	for event, elem in ET.iterparse(filename):
		if elem.tag == 'tag':
			k = elem.attrib['k']
			if lower.match(k):
				keys_num['lower'] += 1
				sum_to_dict(keys['lower'], k)
			elif lower_colon.match(k):
				keys_num['lower_colon'] += 1
				sum_to_dict(keys['lower_colon'], k)
			elif problemchars.match(k):
				keys_num['problemchars'] += 1
				sum_to_dict(keys['problemchars'], k)
			else:
				keys_num['other'] += 1
				sum_to_dict(keys['other'], k)
	print 'Patterns on tags:\n'
	pprint.pprint(keys_num)
	print '\n\nKinds of tags'
	pprint.pprint(keys)

# Count the type of keys inside tag elements regarding its "structure" (regx pattern)
# Also count the type of keys inside those patterns
# Also classify (nest) depending on the type of "root" element (node or way)
def type_of_keys_and_tags_by_element(filename, elements=['node', 'way']):

	lower = re.compile(r'^([a-z]|_)*$')
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	lower_colon2 = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
	problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

	elements_dict = {k: {'lower': {}, 'lower_colon': {}, 'lower_colon2': {}, 'problemchars': {}, 'other': {}} for k in elements}
	elements_dict_num = {k: {'lower': 0, 'lower_colon': 0, 'lower_colon2': 0, 'problemchars': 0, 'other': 0} for k in elements}

	for event, elem in ET.iterparse(filename):
		if elem.tag in elements:
			for tag_elem in elem.findall():
				if tag_elem.tag == 'tag':
					k = tag_elem.attrib['k']
					if lower.match(k):
						elements_dict_num[elem.tag]['lower'] += 1
						sum_to_dict(elements_dict[elem.tag]['lower'], k)
					elif lower_colon.match(k):
						elements_dict_num[elem.tag]['lower_colon'] += 1
						sum_to_dict(elements_dict[elem.tag]['lower_colon'], k)
					elif lower_colon2.match(k):
						elements_dict_num[elem.tag]['lower_colon2'] += 1
						sum_to_dict(elements_dict[elem.tag]['lower_colon2'], k)
					elif problemchars.match(k):
						elements_dict_num[elem.tag]['problemchars'] += 1
						sum_to_dict(elements_dict[elem.tag]['problemchars'], k)
					else:
						elements_dict_num[elem.tag]['other'] += 1
						sum_to_dict(elements_dict[elem.tag]['other'], k)

	print 'Patterns on tags:\n'
	pprint.pprint(elements_dict_num)

	print '\n\nKinds of tags'
	pprint.pprint(elements_dict)

	#save_json(elements_dict_num, 'keys_num')
	#save_json(elements_dict, 'keys')

# Once we have the keys we want to ckeck for each Element (node or ways) we print it out to see if there's any problem
def check_weird_keys(filename):
	weirdkeys = {'node': ['CODIGO', 'FIXME', 'naptan:CommonName', 'naptan:Indicator', 'naptan:Street', 'ref:RRG'],
				 'way': ['FIXME', 'N', u'Torre\xf3n del castillo de los Salazar', 'fuel:']}
	for event, elem in ET.iterparse(filename):
		if elem.tag in weirdkeys.keys():
			for elem_tag in elem.findall():
				if elem_tag.tag == 'tag':
					k = elem_tag.attrib['k']
					if k in weirdkeys[elem.tag]:
						print ET.tostring(elem)
						print k, elem_tag.attrib['v']
						print ''

# If the my_key exists in my_dict, add 1 to the value; create it with value 1 otherwise
def sum_to_dict(my_dict, my_key):
	if my_key in my_dict:
		my_dict[my_key] += 1
	else:
		my_dict[my_key] = 1

# Save dictionary as JSON on '../data/'
def save_json(my_dict, json_name):
	with open('../data/' + json_name + '.json', 'w') as json_file:
		json.dump(my_dict, json_file)

# Save a list of dicionaries on a JSON Lines on '../data/'
def save_json_list(my_dict_list, json_name):
	with open('../data/' + json_name + '.jsonl', 'w') as json_file:
		for json_doc in my_dict_list:
			json_file.write(json.dumps(json_doc) + '\n')

def main():
	#printhead(filename, 500)
	#count_elements(filename)
	#count_tags(filename)
	#type_of_keys(filename)
	#unique_users(filename)
	#type_of_keys_and_tags(filename)
	#type_of_keys_and_tags_by_element(filename)
	#check_weird_keys(filename)
	print ''


main()
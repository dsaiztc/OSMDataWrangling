import xml.etree.cElementTree as ET
import pprint
import sys
import re

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

	return tag_dict

# Count the number of different tags within the nodes or ways elements
def count_tags(filename):
	tag_dict = {}
	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				if tag.attrib['k'] in tag_dict:
					tag_dict[tag.attrib['k']] += 1
				else:
					tag_dict[tag.attrib['k']] = 1

	return tag_dict

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
	pprint.pprint(other)
	return keys

def type_of_keys_and_tags(filename, node_or_way='both'):

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

def sum_to_dict(my_dict, value):
	if value in my_dict:
		my_dict[value] += 1
	else:
		my_dict[value] = 1

def unique_users(filename):
	users = set()
	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way', 'relation']:
			users.add(elem.attrib['user'])
	return users

def main():
	#printhead(filename, 500)
	#tags = count_elements(filename)
	#tags = count_tags(filename)
	#keys = type_of_keys(filename)
	#users = unique_users(filename)
	type_of_keys_and_tags(filename)

main()
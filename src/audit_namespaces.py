import re
import xml.etree.cElementTree as ET
from audit1 import sum_to_dict
import pprint


filename = '../data/file.osm'

def check_namespaces(filename):

	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	lower_colon2 = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')

	tags_with_namespace = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if lower_colon.match(k) or lower_colon2.match(k):
					sum_to_dict(tags_with_namespace, k)
					#sum_to_dict(tags_with_namespace, k.split(':')[0])
	pprint.pprint(tags_with_namespace)

def get_tags_with_namespace_and_without(filename):
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	lower_colon2 = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')

	tags_with_namespace = {}
	tags_with_namespace_and_without = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if lower_colon.match(k) or lower_colon2.match(k):
					sum_to_dict(tags_with_namespace, k.split(':')[0])

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if lower_colon.match(k) or lower_colon2.match(k):
					pass
				else:
					if k in tags_with_namespace:
						sum_to_dict(tags_with_namespace_and_without, k)

	pprint.pprint(tags_with_namespace_and_without)
	return tags_with_namespace_and_without.keys()


def main():
	#check_namespaces(filename)
	print get_tags_with_namespace_and_without(filename)

main()
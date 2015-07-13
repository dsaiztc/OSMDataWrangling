import re
import xml.etree.cElementTree as ET
from audit1 import sum_to_dict
import pprint
import sys


filename = '../data/file.osm'

# Count tags that have namespaces within its keys
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

# Get tags that have both namespace and not namespace (within the same element)
# filename: osm (XML) file to analyze
# showelements: print elements on screen or not
# elementtoshow: print only this element on screen (or None to print all)
def get_tags_with_namespace_and_without(filename, showelements=False, elementtoshow=None):
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	lower_colon2 = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')

	tags_with_namespace_and_without = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			with_namespace = set()
			without_namespace = set()
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if lower_colon.match(k) or lower_colon2.match(k):
					with_namespace.add(k.split(':')[0])
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if lower_colon.match(k) or lower_colon2.match(k):
					pass
				else:
					without_namespace.add(k)
			my_list = list(with_namespace.intersection(without_namespace))
			if len(my_list) != 0 and showelements:
				if elementtoshow is None:
					print my_list
					print ET.tostring(elem)
					print ''
				elif elementtoshow in my_list:
					print my_list
					print ET.tostring(elem)
					print ''
			for i in list(with_namespace.intersection(without_namespace)):
				sum_to_dict(tags_with_namespace_and_without, i)

	#pprint.pprint(tags_with_namespace_and_without)
	return tags_with_namespace_and_without.keys()


def main():
	#check_namespaces(filename)
	print get_tags_with_namespace_and_without(filename, showelements=True, elementtoshow=sys.argv[1])

main()
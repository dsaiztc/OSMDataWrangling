#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import xml.etree.cElementTree as ET
from audit_keys_basic import sum_to_dict
import pprint
import sys


filename = '../data/file.osm'

# Count tags that have namespaces within its keys
def get_tags_with_namespace(filename):

	tags_with_namespace = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.findall('tag'):
				k = tag.attrib['k']
				if key_has_namespace(k):
					sum_to_dict(tags_with_namespace, k)
					#sum_to_dict(tags_with_namespace, k.split(':')[0])
	pprint.pprint(tags_with_namespace)
	return tags_with_namespace.keys()

# Get tags that have both namespace and not namespace (within the same element)
# filename: osm (XML) file to analyze
# showelements: print elements on screen or not
# elementtoshow: print only this element on screen (or None to print all)
def get_tags_with_namespace_and_without(filename, showelements=False, elementtoshow=None):
	tags_with_namespace_and_without = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			with_namespace = set()
			without_namespace = set()
			for tag in elem.findall('tag'):
				k = tag.attrib['k']
				if key_has_namespace(k):
					with_namespace.add(k.split(':')[0])
			for tag in elem.findall('tag'):
				k = tag.attrib['k']
				if key_has_namespace(k):
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

# Check if a key of a tag has a namespace (one or two prefixes)
def key_has_namespace(key):
	lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
	lower_colon2 = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')

	return lower_colon.search(key) or lower_colon2.search(key)

def main():
	#print get_tags_with_namespace(filename)
	#print get_tags_with_namespace_and_without(filename, showelements=True, elementtoshow=sys.argv[1])
	print get_tags_with_namespace_and_without(filename)

main()
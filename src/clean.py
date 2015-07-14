#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET

def clean_file(filename):
	for event, elem in ET.iterparse():
		if elem.tag in ['node', 'way']:
			clean_element(elem)

def clean_element(element):
	dict_element = {
		'id': element.attrib['id'],
		'visible': element.attrib['visible'],
		'created': {
			'user': element.attrib['user'],
		    'uid': element.attrib['uid'],
		    'timestamp': element.attrib['timestamp'],
		    'version': element.attrib['version'],
		    'changeset': element.attrib['changeset']
		    }
	}

	if element.tag == 'node':
		dict_element['type'] = 'node'
		add_pos(element, dict_element)
	elif element.tag == 'way':
		dict_element['type'] = 'way'
		add_node_references(element, dict_element)

	# Tags
	clean_tags(element, dict_element)


def add_pos(element, dict_element):
	dict_element['pos'] = [float(element.attrib['lon']), float(element.attrib['lat'])]

def add_node_references(element, dict_element):
	dict_element['node_refs'] = []
	for node_ref in element.iter('nd'):
		ref = int(node_ref.attrib['ref'])
		dict_element['node_refs'].add()

def clean_tags(element, dict_element):

	fix_namespaces(element)

	for tag in element.iter('tag'):

		fix_tag(tag)

		k = tag.attrib['k']
		v = tag.attrib['v']

		if len(k.split(':')) == 1: 
			# no namespace
			dict_element[k] = v
		else:
			# with namespace
			clean_tag_with_namespace(tag, dict_element)

def fix_namespaces(element):

	# level1:level2:level3
	namespaces_set_l1 = set()
	namespaces_set_l2 = set()

	for tag in element.iter('tag'):
		k = tag.attrib['k']
		kl = k.split(':')
		if len(kl) == 2:
			namespaces_set_l1.add(kl[0])
		elif len(kl) == 3:
			namespaces_set_l2.add(kl[1])

	for tag in element.iter('tag'):
		k = tag.attrib['k']
		kl = k.split(':')
		if len(kl) == 1:
			if k in namespaces_set_l1:
				tag.attrib['k'] = k + ':default'
		elif len(kl) == 2:
			if kl[1] in namespaces_set_l2:
				tag.attrib['k'] = k + ':default'

def fix_tag(tag):
	# keys we've seen that have to be cleaned
	if tag.attrib['k'] == 'Torreón del castillo de los Salazar':
		tag.attrib['k'] = 'name'
		tag.attrib['v'] = 'Torreón del castillo de los Salazar'
	elif tag.attrib['k'] == 'N':
		tag.attrib['k'] = 'name'
		tag.attrib['v'] = 'Calle Real'

# Nest attributes and fix errors
def clean_tag_with_namespace(tag, dict_element):
	
	k = tag.attrib['k']
	v = tag.attrib['v']
	kl = k.split(':')

	if len(kl) == 2:
		fix_level1_tag(tag)
		if kl[0] not in dict_element.keys():
			dict_element[kl[0]] = {}
		dict_element[kl[0]][kl[1]] = v

	elif len(kl) == 3:
		if kl[0] not in dict_element.keys():
			dict_element[kl[0]] = {}
		if kl[1] not in dict_element[kl[0]].keys():
			dict_element[kl[0]][kl[1]] = {}
		dict_element[kl[0]][kl[1]][kl[2]] = v

def fix_level1_tag(tag):
	kl = tag.attrib['k'].split(':')

	if kl[0] == 'addr':
		if kl[1] == 'housenumber':
			if tag.attrib['v'] == '46, BIS':
				tag.attrib['v'] = '46 BIS'
			elif tag.attrib['v'] == '8, 1\xba D':
				tag.attrib['v'] = '8'
		elif kl[1] == 'postcode':
			if tag.attrib['v'] == 'Larrabetzu':
				tag.attrib['v'] = '48195'
			elif tag.attrib['v'] == '48001;48002;48003;48004;48005;48006;48007;48008;48009;48010;48011;48012;48013;48014;48015':
				tag.attrib['v'] = '48001;48002;48003;48004;48005;48006;48007;48008;48009;48010;48011;48012;48013;48014;48015'.split(';')
		elif kl[1] == 'housename':
			if tag.attrib['v'] == '1':
				


# Cleaning script
filename = '../data/file.osm'
clean_file(filename)
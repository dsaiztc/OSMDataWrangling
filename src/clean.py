#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import json
import os
import re

# Clean the entire osm file (for 'Las Merindades' zone)
def clean_file(filename):
	json_list_name = 'cleaned'
	remove_json_list(json_list_name)
	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			json_elem = clean_element(elem)
			add_to_json_list(json_elem, json_list_name)

# Remove previous version of the JSON file if they exists
def remove_json_list(json_list_name):
	try:
		os.remove('../data/' + json_list_name + '.jsonl')
	except OSError:
		pass

# Clean and correct an Element (Way or Node) within the osm document
def clean_element(element):
	dict_element = {
		'id': element.attrib['id'],
		'visible': get_attribute(element, 'visible'),
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

	return dict_element

# For some reason there are attribute that coulb not be present inside an Element
def get_attribute(element, attribute):
	if attribute in element.attrib.keys():
		return element.attrib[attribute]
	else:
		return None

# Add the longitude-latitude position as an array for future geospational queries
def add_pos(element, dict_element):
	dict_element['pos'] = [float(element.attrib['lon']), float(element.attrib['lat'])]

# Add node references within an array (for Ways Element only)
def add_node_references(element, dict_element):
	dict_element['node_refs'] = []
	for node_ref in element.findall('nd'):
		ref = int(node_ref.attrib['ref'])
		dict_element['node_refs'].append(ref)

# Clean and correct tags within an element
def clean_tags(element, dict_element):

	fix_elements(element)
	fix_namespaces(element)

	for tag in element.findall('tag'):

		k = tag.attrib['k']
		v = tag.attrib['v']

		if k == 'addr:street':
			map_street_type(tag)

		if len(k.split(':')) == 1: 
			# no namespace
			dict_element[k] = v
		else:
			# with namespace
			clean_tag_with_namespace(tag, dict_element)

# Fix those elements we've seen that are wrong in some way
def fix_elements(element):
	element_id = element.attrib['id']
	if element_id == '1247189817':
		tag = element.find("tag[@k='addr:housename']")
		tag.attrib['addr:housename'] = 'Bar Irrintzi'
		element.append(ET.Element('tag', {'k': 'addr:street', 'v': 'Calle Santa María'}))
		element.append(ET.Element('tag', {'k': 'addr:housenumber', 'v': '8'}))
		element.append(ET.Element('tag', {'k': 'addr:postcode', 'v': '48005'}))
		element.append(ET.Element('tag', {'k': 'addr:city', 'v': 'Bilbao'}))
	elif element_id == '2251334795':
		tag = element.find("tag[@k='addr:housename']")
		tag.attrib['k'] = 'addr:housenumber'
	elif element_id == '2497160669':
		tag = element.find("tag[@k='addr:housenumber']")
		tag.attrib['v'] = '8'
		element.append(ET.Element('tag', {'k': 'addr:housenumber', 'v': '8'}))
		element.append(ET.Element('tag', {'k': 'addr:floor', 'v': '1'}))
		element.append(ET.Element('tag', {'k': 'addr:door', 'v': 'D'}))
		element.append(ET.Element('tag', {'k': 'addr:full', 'v': 'Avenida Bilbao 8, 1º D'}))
	elif element_id == '2666662355':
		tag = element.find("tag[@k='addr:housenumber']")
		tag.attrib['v'] = '46 BIS'
	elif element_id == '2685469617':
		tag = element.find("tag[@k='addr:housename']")
		tag.attrib['k'] = 'addr:full'
		element.append(ET.Element('tag', {'k': 'club', 'v': 'charity'}))
	elif element_id == '233784177':
		tag = element.find("tag[@v='water']")
		element.remove(tag)
		element.append(ET.Element('tag', {'k': 'name', 'v': 'Torreón del castillo de los Salazar'}))
	elif element_id == '244038482':
		tag = element.find("tag[@k='addr:housename']")
		tag.attrib['k'] = 'addr:street'
	elif element_id == '297172400':
		tag = element.find("tag[@k='N']")
		tag.attrib['k'] = 'addr:street'
	elif element_id == '299032372':
		tag = element.find("tag[@k='addr:city']")
		tag.attrib['v'] = 'Villasana de Mena'
	elif element_id == '334490093':
		tag = element.find("tag[@k='addr:street']")
		tag.attrib['k'] = 'addr:full'

# Add a sublevel default for those tags that have both namespace and not namespace 
#    For example: if we have 'addr' and 'addr:street' then we create 'addr:default' 
#    (so then we can nest both inside one attribute in the JSON document)
def fix_namespaces(element):

	# level1:level2:level3
	namespaces_set_l1 = set()
	namespaces_set_l2 = set()

	for tag in element.findall('tag'):
		k = tag.attrib['k']
		kl = k.split(':')
		if len(kl) == 2:
			namespaces_set_l1.add(kl[0])
		elif len(kl) == 3:
			namespaces_set_l2.add(kl[1])

	for tag in element.findall('tag'):
		k = tag.attrib['k']
		kl = k.split(':')
		if len(kl) == 1:
			if k in namespaces_set_l1:
				tag.attrib['k'] = k + ':default'
		elif len(kl) == 2:
			if kl[1] in namespaces_set_l2:
				tag.attrib['k'] = k + ':default'

# Maps street types to the corrected ones
def map_street_type(tag):

	mapping_street_types = {
		'ACCESO': 'Acceso',
		'AU': u'Autovía',
		'AUTOVIA': u'Autovía',
		'AVENIDA': 'Avenida',
		'BARRIO': 'Barrio',
		'B\xba': 'Barrio',
		'C/': 'Calle',
		'CALLE': 'Calle',
		'CARRETERA': 'Carretera',
		'CL': 'Calle',
		'CR': 'Carretera',
		'CRTA.': 'Carretera',
		'CTRA.N-623,BURGOS-SANTANDER': 'Carretera N-623, Burgos-Santander',
		'Carretera/Carrera': 'Carretera',
		'Kalea': 'kalea',
		'PLAZA': 'Plaza',
		'POLIGONO': u'Polígono',
		'Urbanizaci\xc3\xb3n': u'Urbanización',
		'Urbanizaci\xf3n': u'Urbanización'
	}

	v = tag.attrib['v']

	for key, value in mapping_street_types.iteritems():
		if re.search(key, v):
			tag.attrib['v'] = re.sub(key, value, v)
			break

# Nest attributes and fix errors
def clean_tag_with_namespace(tag, dict_element):
	
	k = tag.attrib['k']
	v = tag.attrib['v']
	kl = k.split(':')

	# keys with one namespace (one prefix)
	if len(kl) == 2:
		if kl[0] not in dict_element.keys():
			dict_element[kl[0]] = {}
		dict_element[kl[0]][kl[1]] = v
	# keys with two namespaces (two prefix)
	elif len(kl) == 3:
		if kl[0] not in dict_element.keys():
			dict_element[kl[0]] = {}
		if kl[1] not in dict_element[kl[0]].keys():
			dict_element[kl[0]][kl[1]] = {}
		dict_element[kl[0]][kl[1]][kl[2]] = v

# Save dictionary as JSON on '../data/'
def save_json(my_dict, json_name):
	with open('../data/' + json_name + '.json', 'w') as json_file:
		json.dump(my_dict, json_file)

# Save a list of dicionaries on a JSON Lines on '../data/'
def save_json_list(my_dict_list, json_name):
	with open('../data/' + json_name + '.jsonl', 'w') as json_file:
		for json_doc in my_dict_list:
			json_file.write(json.dumps(json_doc) + '\n')

# Add JSON to a JSON Lines document on '.../data/'
def add_to_json_list(my_dict, json_name):
	with open('../data/' + json_name + '.jsonl', 'a') as json_file:
		json.dump(my_dict, json_file)
		json_file.write('\n')


# Cleaning script
filename = '../data/file.osm'
clean_file(filename)
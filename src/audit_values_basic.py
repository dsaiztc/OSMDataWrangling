#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from audit_keys_basic import sum_to_dict
import pprint
import re

filename = '../data/file.osm'

# Number of tags with keys prefix = addr (distribution of them)
def get_keys_address(filename):

	address_dict = {}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if 'addr' in k:
					sum_to_dict(address_dict, k)

	pprint.pprint(address_dict)
	return address_dict.keys()

def get_sets_depending_on_address_keys(filename, addr_keys):
	dict_addr_keys = {k: set() for k in addr_keys}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				if 'addr' in k:
					dict_addr_keys[k].add(tag.attrib['v'])
	pprint.pprint(dict_addr_keys)

# Numeric fields for address distribution
def analyze_numeric_fields_of_address(filename, fields=['addr:housenumber', 'addr:postcode']):
	whole_number = re.compile(r'^[0-9]+$')
	have_number = re.compile(r'[0-9]+')

	numeric_fields = {k: {'whole_number': 0, 'have_number': 0, 'no_number': 0} for k in fields}

	weird_fields = {k: {'have_number': set(), 'no_number': set()} for k in fields}

	for _, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				v = tag.attrib['v']
				if k in fields:
					if whole_number.match(v):
						numeric_fields[k]['whole_number'] += 1
					elif have_number.match(v):
						numeric_fields[k]['have_number'] += 1
						weird_fields[k]['have_number'].add(v)
					else:
						numeric_fields[k]['no_number'] += 1
						weird_fields[k]['no_number'].add(v)
	pprint.pprint(numeric_fields)
	pprint.pprint(weird_fields)

# Numeric fields for address distribution, grouping valid housenumber values
#  return weird values
def analyze_numeric_fields_of_address2(filename, fields=['addr:housenumber', 'addr:postcode']):
	whole_number = re.compile(r'^[0-9]+$')
	have_number = re.compile(r'^[0-9]+( |[A-Za-z])*$')

	numeric_fields = {k: {'whole_number': 0, 'have_number': 0, 'no_number': 0} for k in fields}

	weird_fields = {k: {'have_number': set(), 'no_number': set()} for k in fields}

	for _, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				v = tag.attrib['v']
				if k in fields:
					if whole_number.match(v):
						numeric_fields[k]['whole_number'] += 1
					elif have_number.match(v):
						numeric_fields[k]['have_number'] += 1
						weird_fields[k]['have_number'].add(v)
					else:
						numeric_fields[k]['no_number'] += 1
						weird_fields[k]['no_number'].add(v)
	pprint.pprint(numeric_fields)
	pprint.pprint(weird_fields)
	print weird_fields
	return list(weird_fields)

def check_text_values(filename, cases_to_check=['addr:city', 'addr:housename', 'addr:street']):
	categories = {
		'all_capital': re.compile(r'^([A-Z]| )+$'),
		'all_small': re.compile(r'^([a-z]| )+$'),
		'unicode_text': re.compile(r'[0-9]+'),
		'other': re.compile(r'\S')
		}
	keys = categories.keys()

	categories_set = {j: {k: set() for k in keys} for j in cases_to_check}

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				v = tag.attrib['v']
				if k in cases_to_check:
					if categories['all_capital'].match(v):
						categories_set[k]['all_capital'].add(v)
					elif categories['all_small'].match(v):
						categories_set[k]['all_small'].add(v)
					elif categories['unicode_text'].match(v) is None:
						categories_set[k]['unicode_text'].add(v)
					else:
						categories_set[k]['other'].add(v)

	pprint.pprint(categories_set)

def type_of_street(filename):
	types = set()

	kalea = re.compile(r'(k|K)alea$')

	for event, elem in ET.iterparse(filename):
		if elem.tag in ['node', 'way']:
			for tag in elem.iter('tag'):
				k = tag.attrib['k']
				v = tag.attrib['v']
				if k == 'addr:street':
					if kalea.search(v):
						types.add(v.split()[-1])
					else:
						types.add(v.split()[0])
	print types
	pprint.pprint(types)
	return list(types)

mapping_street_types = {
	'ACCESO': 'Acceso',
	'AU': 'Autovía',
	'AUTOVIA': 'Autovía',
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
	'POLIGONO': 'Polígono',
	'Urbanizaci\xc3\xb3n': 'Urbanización',
	'Urbanizaci\xf3n': 'Urbanización'
}


'''
addr_keys = get_keys_address(filename)
get_sets_depending_on_address_keys(filename, addr_keys)

weird_values = analyze_numeric_fields_of_address2(filename)
print weird_values


check_text_values(filename, cases_to_check=['addr:street'])
'''

types_of_street = type_of_street(filename)


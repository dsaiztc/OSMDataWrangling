# OpenStreetMaps Data Wrangling

> This project has been developed in order to pursue the [Data Analyst Nanodegree](https://www.udacity.com/course/data-analyst-nanodegree--nd002) offered by Udacity. Specifically, the project aims to use the knowledges acquired in the second course of this Nanodegree: [Data Wrangling with MongoDB](https://www.udacity.com/course/ud032-nd).
> 
> The *Project Report* about the data wrangling can be found [here](https://github.com/dsaiztc/OSMDataWrangling/blob/master/ProjectReport.md).

## Introduction

The goal of this project is to choose any area of the world in [https://www.openstreetmap.org](https://www.openstreetmap.org/) and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the *OpenStreetMap* data for a part of the world, converting it from XML to JSON format, importing the clean file into a *MongoDB* database and run some queries against it.

## Obtaining the data

To obtain the data I have made a query to `http://overpass-api.de/query_form.html` after searching for *Las Merindades*, which is the region where my hometown belongs to. The query is the following:

``` 
(node(42.5966, -4.2339, 43.2832, -2.7370);<;);out meta;
```

And the resulting `osm` (or `xml`) data is stored on `/data/file.xml`, which is a *355,3 MB* file.

## Structure of the OSM file

In the [OSM XML page](http://wiki.openstreetmap.org/wiki/OSM_XML) we can see the format of the XML document, which is basically a list of instances of their data primitives or [Elements](http://wiki.openstreetmap.org/wiki/Elements): [nodes](http://wiki.openstreetmap.org/wiki/Node), [ways](http://wiki.openstreetmap.org/wiki/Way) and [relations](http://wiki.openstreetmap.org/wiki/Relation). 

Those *Elements* have several [common attributes](http://wiki.openstreetmap.org/wiki/Elements#Common_attributes): **id** (identify the element within a type -node, way or relation-), **user** (display name of the  user), **uid** (numeric user id), **timestamp** (time of the last modification), **visible** (whether the object is deleted or not in the database), **version** (edit version of the object) and **changeset** (the [changeset](http://wiki.openstreetmap.org/wiki/Changeset) in which the object was created or updated).

Furthermore, each one of those *categories* has its own attributes:

- *Nodes*: **lat** (latitude coordinates in degrees), **lon** (longitude coordinates in degrees) and a bunch of different [tags](http://wiki.openstreetmap.org/wiki/Tags) (a set of key/value pairs).
- *Ways*: an ordered list of *Nodes* (as XML elements with **nd** tag and an attribute named *ref* with a reference to the *node id*). Normally it has also at least one [tag](http://wiki.openstreetmap.org/wiki/Tags).
- *Relations*: one or more [tags](http://wiki.openstreetmap.org/wiki/Tags) and also an ordered list of one or more *nodes*, *ways* and *relations* as members.

So our interest will be on the first two kind of *Elements*: *nodes* and *ways*. The majority of the *common attributes* make a reference to the *creation* process of that element. So in our *document-oriented* model we could aggregate those values within an attribute of our document. Also, due to the fact that there is going to be a unique collection for all documents, we should differentiate between *nodes* and *ways*.

``` 
{
...
'type': 'node OR way',
'id': 'some_id',
'visible': 'some_visible',
'created': {
	'user': 'some_user',
    'uid': 'some_uid',
    'timestamp': 'some_timestamp',
    'version': 'some_version',
    'changeset': 'some_changeset'
    }
}
```

In the case of *nodes*, we could add a *position* attribute. MongoDB offers a number of [indexes and query](http://docs.mongodb.org/manual/applications/geospatial-indexes/) mechanisms to handle geospatial information, that allows us to create [2d Geospatial Indexes](http://docs.mongodb.org/v2.2/core/geospatial-indexes/) if we storage the GPS data with the following format:

``` 
'pos' : [ longitude, latitude ]
```

*NOTE:* the name of the attribute could be whatever we want, *pos* is an option but it could be *loc* or *position*. In our case the name of this attribute will be *pos* (for no specific reason).

In the case of *ways*, we could create an attribute for storing all the *nd* values within an array:

From

``` 
<way ...>
	<nd ref='ref1'/>
    <nd ref='ref2'/>
    ...
</way>
```

to

``` 
{
...
'node_refs': [ 'ref1', 'ref2', ... ]
}
```

### Tags

As we have seen before, a [tag](http://wiki.openstreetmap.org/wiki/Tags) is a key/value pair that describes a specific feature of a data *Element*. In our transformation to JSON-like documents we should include all these tags as attributes. However, there are some of this *tags* whose *key* can be modified to include a [namespace](http://wiki.openstreetmap.org/wiki/Namespace) (a prefix, infix or suffix using a colon `:` as separator). One example of these *namespaces* could be the *tags* that contain part of an address, which have a prefix *addr*. In these cases we could create an attribute in our document that aggregate all different characteristics for a given prefix, which in the case of an address could be:

From

``` 
<node ...>
  ...
  <tag k='addr:street' v='some_street'/>
  <tag k='addr:postcode' v='some_postcode'/>
  <tag k='addr:housenumber' v='some_housenumber'/>
</node>
```

to

``` 
{
'type': 'node',
...
'address': {
	'street': 'some_street',
    'postcode': 'some_postcode',
    'housenumber': 'some_housenumber'
    }
}
```

## Auditing the data

Kind of elements:

``` 
{'member': 29931,
 'meta': 1,
 'nd': 1980250,
 'node': 1758177,
 'note': 1,
 'osm': 1,
 'relation': 1881,
 'tag': 393799,
 'way': 97206}
```

Kind of keys in tags:

``` 
Patterns on tags:

{'lower': 302335, 'lower_colon': 90667, 'other': 797, 'problemchars': 0}


Kinds of tags
{'lower': {'abandoned': 20,
           'abutters': 75,
           'access': 1445,
           'admin_level': 1020,
           'aerialway': 12,
           'aeroway': 40,
           'agricultural': 3,
           'alt_name': 312,
           'amenity': 5267,
           'animal': 6,
           'architect': 1,
           'area': 454,
           'artist_name': 8,
           'artwork_type': 6,
           'atm': 149,
           'automated': 1,
           'backrest': 87,
           'barrier': 4473,
           'beds': 1,
           'bench': 118,
           'bicycle': 1003,
           'bicycle_parking': 22,
           'board_type': 34,
           'boat': 9,
           'bollard': 1,
           'border_type': 12,
           'boundary': 870,
           'branch': 1,
           'brand': 36,
           'bridge': 2427,
           'building': 26428,
           'bus': 79,
           'cables': 115,
           'capacity': 42,
           'capital': 216,
           'castle_type': 2,
           'clothes': 1,
           'colour': 109,
           'comment': 3,
           'construction': 47,
           'content': 2,
           'conveying': 2,
           'covered': 75,
           'craft': 9,
           'created_by': 11868,
           'crop': 3,
           'crossing': 246,
           'crossing_ref': 42,
           'cuisine': 144,
           'cutting': 8,
           'cycleway': 30,
           'date': 3,
           'delivery': 2,
           'denomination': 1159,
           'denotation': 1,
           'depth': 2,
           'description': 24,
           'designation': 68,
           'destination': 121,
           'dispensing': 80,
           'distance': 58,
           'disused': 53,
           'drinking_water': 8,
           'drive_through': 1,
           'drt': 1,
           'easy_overtaking': 1,
           'ele': 1601,
           'electrified': 676,
           'email': 82,
           'embankment': 4,
           'emergency': 247,
           'enforcement': 12,
           'entrance': 3724,
           'escalator_dir': 2,
           'exit_to': 126,
           'fax': 35,
           'fee': 106,
           'fence_type': 1474,
           'fireplace': 16,
           'fixme': 212,
           'foot': 985,
           'footway': 217,
           'ford': 87,
           'frequency': 539,
           'from': 12,
           'fuel': 2,
           'gauge': 998,
           'genus': 20,
           'gml_featuretype': 18,
           'goods': 54,
           'handrail': 1,
           'hazard': 4,
           'height': 1558,
           'hgv': 99,
           'highspeed': 10,
           'highway': 52672,
           'hiking': 265,
           'historic': 390,
           'hoops': 1,
           'horse': 407,
           'image': 1,
           'incline': 22,
           'indoor': 26,
           'industrial': 1,
           'information': 356,
           'inscription': 2,
           'int_name': 1,
           'int_ref': 381,
           'intermittent': 462,
           'internet_access': 40,
           'is_in': 3307,
           'junction': 475,
           'label': 2,
           'landuse': 6126,
           'lane': 7,
           'lanes': 2449,
           'layer': 3048,
           'leaf_cycle': 4,
           'leaf_type': 1791,
           'leisure': 1914,
           'length': 10,
           'level': 2,
           'lit': 54,
           'loc_name': 24,
           'local_ref': 4,
           'location': 102,
           'lodging': 2,
           'man_made': 1437,
           'map_size': 28,
           'map_type': 33,
           'material': 175,
           'maxheight': 5,
           'maxspeed': 1612,
           'maxstay': 3,
           'maxweight': 11,
           'maxwidth': 4,
           'megalith_type': 28,
           'memorial': 2,
           'microbrewery': 1,
           'motor_vehicle': 473,
           'motorcar': 179,
           'motorcycle': 106,
           'motorroad': 7,
           'mountain_pass': 58,
           'mtb': 197,
           'name': 34588,
           'nat_ref': 882,
           'natural': 5721,
           'network': 269,
           'nick': 2,
           'noexit': 294,
           'note': 3616,
           'office': 41,
           'official_name': 33,
           'old_name': 49,
           'old_ref': 8,
           'one': 1,
           'oneway': 8466,
           'opening_hours': 125,
           'operator': 658,
           'organic': 6,
           'overtaking': 51,
           'owner': 1,
           'parent_basin': 1,
           'park_ride': 15,
           'parking': 261,
           'passing_places': 2,
           'phone': 234,
           'pilgrimage': 1,
           'pk': 4,
           'place': 14994,
           'place_name': 14,
           'platforms': 10,
           'pond_use': 32,
           'population': 1326,
           'postal_code': 921,
           'power': 4740,
           'protect_class': 3,
           'psv': 10,
           'public_transport': 170,
           'railway': 1695,
           'ramp': 1,
           'recording': 8,
           'recycling_type': 23,
           'ref': 5984,
           'religion': 1228,
           'repair': 2,
           'resource': 1,
           'restriction': 1005,
           'rooms': 1,
           'roundtrip': 31,
           'route': 227,
           'ruins': 56,
           'sac_scale': 1123,
           'sac_scale_ref': 1,
           'safety_inspection': 1,
           'seats': 11,
           'second_hand': 3,
           'section': 1,
           'segregated': 43,
           'self_service': 1,
           'service': 1653,
           'service_times': 1,
           'services': 2,
           'share_taxi': 1,
           'shelter': 179,
           'shelter_type': 21,
           'shop': 945,
           'sidewalk': 237,
           'site': 5,
           'site_type': 42,
           'ski': 16,
           'smoking': 18,
           'smoothness': 37,
           'snowmobile': 15,
           'social_facility': 7,
           'social_facility_for': 4,
           'source': 27378,
           'sport': 690,
           'stamps': 1,
           'stars': 42,
           'start_date': 3,
           'state_code': 1,
           'step_count': 2,
           'structure': 1,
           'studio': 1,
           'substation': 3,
           'subway': 12,
           'supervised': 35,
           'surface': 5802,
           'surveillance': 4,
           'sym': 1,
           'symbol': 4,
           'tactile_paving': 7,
           'takeaway': 3,
           'taxi': 3,
           'time': 1,
           'timezone': 2,
           'to': 12,
           'toll': 360,
           'tomb': 2,
           'tourism': 952,
           'track': 1,
           'track_visibility': 2,
           'tracks': 13,
           'tracktype': 14053,
           'traffic_calming': 23,
           'traffic_sign': 15,
           'trail_visibility': 840,
           'train': 5,
           'transformer': 9,
           'tunnel': 918,
           'turn': 8,
           'type': 2026,
           'undefined': 1,
           'url': 1,
           'usage': 198,
           'value': 1,
           'vehicle': 8,
           'vending': 8,
           'via': 2,
           'vists': 1,
           'voltage': 619,
           'wall': 12,
           'water': 109,
           'waterway': 3416,
           'way': 2,
           'website': 367,
           'wetland': 5,
           'wheelchair': 242,
           'width': 177,
           'wifi': 2,
           'wikidata': 8,
           'wikipedia': 910,
           'wood': 239},
 'lower_colon': {'addr:city': 1675,
                 'addr:country': 945,
                 'addr:country_code': 86,
                 'addr:full': 13,
                 'addr:housename': 33,
                 'addr:housenumber': 4804,
                 'addr:inclusion': 3,
                 'addr:interpolation': 145,
                 'addr:place': 2,
                 'addr:postcode': 1703,
                 'addr:state': 5,
                 'addr:street': 4912,
                 'aerialway:capacity': 5,
                 'alt_name:de': 1,
                 'alt_name:es': 6,
                 'alt_name:eu': 8,
                 'alt_name:fr': 1,
                 'area:highway': 12,
                 'atm:network': 72,
                 'atm:operator': 34,
                 'building:colour': 3,
                 'building:levels': 4781,
                 'building:material': 3,
                 'building:min_level': 3,
                 'building:part': 24,
                 'building:use': 2,
                 'capacity:disabled': 3,
                 'catastro:ref': 1790,
                 'communication:mobile_phone': 200,
                 'communication:television': 2,
                 'communication:tv': 1,
                 'community:gender': 1,
                 'contact:email': 1,
                 'contact:phone': 2,
                 'contact:website': 2,
                 'crossing:barrier': 17,
                 'crossing:light': 6,
                 'description:en': 1,
                 'destination:lanes': 10,
                 'diet:dairy': 1,
                 'diet:vegan': 2,
                 'diet:vegetarian': 1,
                 'disused:landuse': 1,
                 'disused:railway': 1,
                 'fire_hydrant:couplings': 88,
                 'fire_hydrant:position': 100,
                 'fire_hydrant:type': 175,
                 'fuel:biodiesel': 13,
                 'fuel:diesel': 80,
                 'fuel:lpg': 1,
                 'generator:method': 142,
                 'generator:source': 698,
                 'generator:type': 102,
                 'handrail:center': 1,
                 'idee:name': 212,
                 'ideewfs:convergencia': 18,
                 'ideewfs:latitud': 18,
                 'ideewfs:longitud': 18,
                 'ideewfs:nombre': 18,
                 'ign:latitud': 173,
                 'ign:longitud': 173,
                 'ign:red': 173,
                 'ine:ccaa': 4,
                 'ine:municipio': 204,
                 'ine:provincia': 6,
                 'ine:ref': 418,
                 'internet_access:fee': 16,
                 'is_in:city': 4,
                 'is_in:comarca': 69,
                 'is_in:comarca_code': 18,
                 'is_in:continent': 2153,
                 'is_in:country': 3264,
                 'is_in:country_code': 1741,
                 'is_in:municipality': 2254,
                 'is_in:municipality_code': 16,
                 'is_in:province': 2356,
                 'is_in:province_code': 1530,
                 'is_in:region': 2288,
                 'is_in:region_code': 97,
                 'is_in:state': 13068,
                 'is_in:state_code': 13067,
                 'is_in:town': 4,
                 'is_in:village': 239,
                 'isced:level': 3,
                 'kml:guid': 2,
                 'lanes:backward': 48,
                 'lanes:forward': 92,
                 'maxspeed:backward': 327,
                 'maxspeed:forward': 402,
                 'monitoring:air_quality': 3,
                 'monitoring:noise': 3,
                 'monitoring:water_level': 9,
                 'mtb:scale': 255,
                 'mtb:type': 6,
                 'name:an': 4,
                 'name:ar': 9,
                 'name:ast': 2,
                 'name:be': 3,
                 'name:bg': 4,
                 'name:botanical': 24,
                 'name:br': 5,
                 'name:bs': 1,
                 'name:ca': 38,
                 'name:ce': 2,
                 'name:ckb': 2,
                 'name:cy': 2,
                 'name:da': 1,
                 'name:de': 10,
                 'name:el': 4,
                 'name:en': 22,
                 'name:eo': 1,
                 'name:es': 792,
                 'name:et': 2,
                 'name:eu': 1195,
                 'name:ext': 2,
                 'name:fa': 3,
                 'name:fi': 1,
                 'name:fr': 42,
                 'name:frp': 2,
                 'name:fy': 1,
                 'name:ga': 1,
                 'name:gl': 4,
                 'name:gr': 1,
                 'name:he': 4,
                 'name:hr': 2,
                 'name:hu': 1,
                 'name:hy': 2,
                 'name:id': 1,
                 'name:is': 1,
                 'name:it': 2,
                 'name:ja': 5,
                 'name:ka': 2,
                 'name:kk': 2,
                 'name:ko': 3,
                 'name:la': 13,
                 'name:lb': 1,
                 'name:lt': 1,
                 'name:mhr': 2,
                 'name:mn': 2,
                 'name:mr': 2,
                 'name:ms': 2,
                 'name:nl': 5,
                 'name:oc': 3,
                 'name:old': 1,
                 'name:os': 2,
                 'name:pl': 5,
                 'name:pms': 2,
                 'name:pt': 18,
                 'name:ru': 20,
                 'name:sr': 2,
                 'name:th': 2,
                 'name:uk': 12,
                 'name:uz': 8,
                 'name:war': 2,
                 'name:xmf': 2,
                 'name:zh': 13,
                 'naptan:verified': 1,
                 'note:es': 1,
                 'note:website': 1,
                 'observatory:type': 1,
                 'official_name:es': 4,
                 'official_name:eu': 4,
                 'official_name:fr': 2,
                 'old_name:es': 1,
                 'old_name:eu': 2,
                 'osmc:symbol': 103,
                 'overtaking:hgv': 2,
                 'payment:account_cards': 2,
                 'payment:bitcoin': 3,
                 'payment:coins': 11,
                 'payment:credit_cards': 2,
                 'payment:debit_cards': 2,
                 'payment:electronic_purses': 2,
                 'payment:telephone_cards': 1,
                 'piste:difficulty': 17,
                 'piste:grooming': 1,
                 'piste:type': 17,
                 'population:date': 1276,
                 'public_transport:version': 2,
                 'ramp:wheelchair': 1,
                 'recording:automated': 4,
                 'recording:remote': 8,
                 'recycling:batteries': 7,
                 'recycling:cans': 21,
                 'recycling:clothes': 8,
                 'recycling:computers': 1,
                 'recycling:glass': 23,
                 'recycling:glass_bottles': 2,
                 'recycling:paper': 24,
                 'recycling:plastic': 2,
                 'recycling:plastic_bottles': 1,
                 'recycling:plastic_packaging': 1,
                 'recycling:scrap_metal': 7,
                 'recycling:waste': 2,
                 'rednap:altitudortometrica': 226,
                 'rednap:codigoine': 227,
                 'rednap:ficha': 227,
                 'rednap:grupo': 227,
                 'rednap:latitud': 227,
                 'rednap:longitud': 227,
                 'rednap:nodo': 227,
                 'rednap:numero': 227,
                 'rednap:posicion': 227,
                 'rednap:tipo': 227,
                 'ref:ine': 1087,
                 'roof:shape': 1,
                 'seamark:construction': 4,
                 'seamark:name': 6,
                 'seamark:type': 6,
                 'social_facility:for': 2,
                 'source:date': 9955,
                 'source:ele': 1078,
                 'source:file': 1079,
                 'source:filename': 19,
                 'source:maxspeed': 13,
                 'source:name': 1334,
                 'source:population': 2,
                 'source:ref': 195,
                 'source:url': 859,
                 'source:wfs': 227,
                 'summit:cross': 7,
                 'telescope:type': 1,
                 'tiger:county': 1,
                 'to:es': 1,
                 'toilets:disposal': 5,
                 'toilets:position': 3,
                 'tower:type': 261,
                 'townhall:type': 2,
                 'turn:lanes': 49,
                 'wheelchair:description': 1,
                 'wiki:symbol': 1,
                 'wikipedia:ca': 1,
                 'wikipedia:de': 5,
                 'wikipedia:en': 4,
                 'wikipedia:es': 797,
                 'wikipedia:fr': 3,
                 'wikipedia:pt': 2},
 'other': {'CODIGO': 3,
           'FIXME': 5,
           'ISO3166-2': 4,
           'N': 1,
           u'Torre\xf3n del castillo de los Salazar': 1,
           'class:bicycle:mtb': 39,
           'destination:lanes:forward': 2,
           'fuel:GTL_diesel': 47,
           'fuel:HGV_diesel': 2,
           'fuel:diesel_B': 26,
           'fuel:diesel_C': 1,
           'fuel:octane_91': 1,
           'fuel:octane_95': 79,
           'fuel:octane_98': 56,
           'generator:output:electricity': 100,
           'ideewfs:alturaElipsoidal': 18,
           'ideewfs:factorEscala': 18,
           'ideewfs:fechaCompensacion': 18,
           'ideewfs:husoUTM': 18,
           'ideewfs:numeroROI': 18,
           'ideewfs:xUTM': 18,
           'ideewfs:yUTM': 18,
           'maxspeed:lanes:backward': 23,
           'maxspeed:lanes:forward': 15,
           'mtb:scale:imba': 31,
           'mtb:scale:uphill': 40,
           'naptan:CommonName': 1,
           'naptan:Indicator': 1,
           'naptan:Street': 1,
           'plant:output:electricity': 2,
           'ref:NUTS-2': 3,
           'ref:RRG': 18,
           'seamark:beacon_lateral:category': 1,
           'seamark:beacon_lateral:colour': 1,
           'seamark:beacon_lateral:height': 1,
           'seamark:beacon_lateral:shape': 1,
           'seamark:beacon_lateral:system': 1,
           'seamark:light:character': 5,
           'seamark:light:colour': 5,
           'seamark:light:group': 4,
           'seamark:light:height': 6,
           'seamark:light:period': 5,
           'seamark:light:range': 5,
           'seamark:light:reference': 5,
           'seamark:light:sequence': 5,
           'seamark:light_minor:colour': 4,
           'seamark:light_minor:height': 4,
           'service:bicycle:rental': 2,
           'service:bicycle:repair': 12,
           'service:bicycle:retail': 15,
           'source:maxspeed:backward': 1,
           'source:maxspeed:forward': 1,
           'turn:lanes:backward': 47,
           'turn:lanes:forward': 38},
 'problemchars': {}}
```
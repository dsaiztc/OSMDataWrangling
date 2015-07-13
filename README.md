# OpenStreetMaps Data Wrangling

> This project has been developed in order to pursue the [Data Analyst Nanodegree](https://www.udacity.com/course/data-analyst-nanodegree--nd002) offered by Udacity. Specifically, the project aims to use the knowledges acquired in the second course of this Nanodegree: [Data Wrangling with MongoDB](https://www.udacity.com/course/ud032-nd).
> 
> The *Project Report* about the data wrangling can be found [here](https://github.com/dsaiztc/OSMDataWrangling/blob/master/ProjectReport.md).

## 1. Introduction

The goal of this project is to choose any area of the world in [https://www.openstreetmap.org](https://www.openstreetmap.org/) and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the *OpenStreetMap* data for a part of the world, converting it from XML to JSON format, importing the clean file into a *MongoDB* database and run some queries against it.

## 2. Obtaining the data

To obtain the data I have made a query to `http://overpass-api.de/query_form.html` after searching for *Las Merindades*, which is the region where my hometown belongs to. The query is the following:

``` 
(node(42.5966, -4.2339, 43.2832, -2.7370);<;);out meta;
```

And the resulting `osm` (or `xml`) data is stored on `/data/file.osm`, which is a *355,3 MB* file (that can be downloaded also [here](https://www.dropbox.com/s/9d8io7q19lkq2b1/merindades.osm?dl=0)). A *sample* of that file (created with the [sample.py](./src/sample.py)) can be accessed [here](./data/sample.osm).

## 3. Structure of the OSM file

In the [OSM XML page](http://wiki.openstreetmap.org/wiki/OSM_XML) we can see the format of the XML document, which is basically a list of instances of their data primitives or [Elements](http://wiki.openstreetmap.org/wiki/Elements): [nodes](http://wiki.openstreetmap.org/wiki/Node), [ways](http://wiki.openstreetmap.org/wiki/Way) and [relations](http://wiki.openstreetmap.org/wiki/Relation). 

### 3.1 Elements

Those *Elements* have several [common attributes](http://wiki.openstreetmap.org/wiki/Elements#Common_attributes): **id** (identify the element within a type -node, way or relation-), **user** (display name of the  user), **uid** (numeric user id), **timestamp** (time of the last modification), **visible** (whether the object is deleted or not in the database), **version** (edit version of the object) and **changeset** (the [changeset](http://wiki.openstreetmap.org/wiki/Changeset) in which the object was created or updated).

Furthermore, each one of those *categories* has its own attributes:

- *Nodes*: **lat** (latitude coordinates in degrees), **lon** (longitude coordinates in degrees) and a bunch of different [tags](http://wiki.openstreetmap.org/wiki/Tags) (a set of key/value pairs).
- *Ways*: an ordered list of *Nodes* (as XML elements with **nd** tag and an attribute named *ref* with a reference to the *node id*). Normally it has also at least one [tag](http://wiki.openstreetmap.org/wiki/Tags).
- *Relations*: one or more [tags](http://wiki.openstreetmap.org/wiki/Tags) and also an ordered list of one or more *nodes*, *ways* and *relations* as members.

So our interest will be on the first two kind of *Elements*: *nodes* and *ways*. The majority of the *common attributes* make a reference to the *creation* process of that element. So in our *document-oriented* model we could aggregate those values within an attribute of our document. Also, due to the fact that there is going to be a unique collection for all documents, we should differentiate between *nodes* and *ways*.

``` json
{
...
'type': 'node OR way',
'id': 'some_id',
'visible': 'true OR false',
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

``` json
'pos' : [ longitude, latitude ]
```

*NOTE:* the name of the attribute could be whatever we want, *pos* is an option but it could be *loc* or *position*. In our case the name of this attribute will be *pos* (for no specific reason).

In the case of *ways*, we could create an attribute for storing all the *nd* values within an array:

From

``` xml
<way ...>
	<nd ref='ref1'/>
    <nd ref='ref2'/>
    ...
</way>
```

to

``` json
{
...
'node_refs': [ 'ref1', 'ref2', ... ]
}
```

### 3.2 Tags

As we have seen before, a [tag](http://wiki.openstreetmap.org/wiki/Tags) is a key/value pair that describes a specific feature of a data *Element*. In our transformation to JSON-like documents we should include all these tags as attributes. However, there are some of this *tags* whose *key* can be modified to include a [namespace](http://wiki.openstreetmap.org/wiki/Namespace) (a prefix, infix or suffix using a colon `:` as separator). One example of these *namespaces* could be the *tags* that contain part of an address, which have a prefix *addr*. In these cases we could create an attribute in our document that aggregate all different characteristics for a given prefix, which in the case of an address could be:

From

``` xml
<node ...>
  ...
  <tag k='addr:street' v='some_street'/>
  <tag k='addr:postcode' v='some_postcode'/>
  <tag k='addr:housenumber' v='some_housenumber'/>
</node>
```

to

``` json
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

## 4. Auditing the data

We are going to assume that **all the attributes except for the *tags* are going to be correct**. That is, the *common attributes*, the GPS positions for the *nodes* and the list of nodes for the *ways* are not going to be sanity checked.

As we have seen before, each *tag* has a *key/value pair* referring a specific characteristic of that *node* or *way*. We are going to audit first the *keys*, and then we will continue with the *values*.

### 4.1 Analyzing the different *keys*

#### 4.1.1 Structure (applying *regular expressions*)

> This analysis has been performed with different functions within the [audit_keys_basic.py](./src/audit_keys_basic.py) script.

If we take a look at the *tags* presented in the document, classifying their *key* depending on the kind of *Element* (*node* or *way*) and also the structure (if all the characters are correct or if it has a namespace, for example) we get the following structure:

``` json
{'node': {'lower': 89359,
          'lower_colon': 53673,
          'lower_colon2': 171,
          'other': 344,
          'problemchars': 0},
 'way': {'lower': 206635,
         'lower_colon': 34756,
         'lower_colon2': 250,
         'other': 23,
         'problemchars': 0}}
```

In this case we have made a count of the different categories: ***lower*** represents all the *keys* that are composed by lower case characters or the underscore (ex. `admin_level`), ***lower_colon*** represents all the *keys* that have the same structure as the previous but that also includes one namespace (ex. `addr:city`), *lower_colon2* **represents** all the *keys* that have the same structure as *lower* but that includes two namespaces (ex. `maxspeed:lanes:forward`), ***problemchars*** represents all the values with one or more problematic characters (other than `a-z` or `_`) and finally ***other*** represents all the other cases.

As we said before, we can nest the keys with namespaces within attributes of our JSON-like document. So the *tags* in the categories ***lower_colon*** and ***lower_colon2*** could be treated that way. In the case of the ***lower*** category, we can add directly the *tags* as attributes to our document. As we have not found any problematic character, there is nothing to fix in that area.

Regarding the ***other*** category, we should check what kind of *tags* we have. Following the last procedure, we are going to count how many different *keys* we have for those *tags*:

``` json
{'node': {'lower': { ... },
 		 'lower_colon': { ... },
         'lower_colon2': { ... },
         'probemchars': {},         
         'other': {'CODIGO': 3,
                   'FIXME': 2,
                   'fuel:GTL_diesel': 45,
                   'fuel:HGV_diesel': 2,
                   'fuel:diesel_B': 25,
                   'fuel:diesel_C': 1,
                   'fuel:octane_91': 1,
                   'fuel:octane_95': 70,
                   'fuel:octane_98': 48,
                   'ideewfs:alturaElipsoidal': 18,
                   'ideewfs:factorEscala': 18,
                   'ideewfs:fechaCompensacion': 18,
                   'ideewfs:husoUTM': 18,
                   'ideewfs:numeroROI': 18,
                   'ideewfs:xUTM': 18,
                   'ideewfs:yUTM': 18,
                   'naptan:CommonName': 1,
                   'naptan:Indicator': 1,
                   'naptan:Street': 1,
                   'ref:RRG': 18}},
 'way': {'lower': { ... },
 		 'lower_colon': { ... },
         'lower_colon2': { ... },
         'probemchars': {},
         'other': {'FIXME': 1,
                   'N': 1,
                   u'Torre\xf3n del castillo de los Salazar': 1,
                   'fuel:GTL_diesel': 2,
                   'fuel:diesel_B': 1,
                   'fuel:octane_95': 9,
                   'fuel:octane_98': 8}}}
```

As we can see, most of the cases have been classified into this category because they have capital letters or even numbers. The [OSM wiki](http://wiki.openstreetmap.org/wiki/Tags) specifies that *both the key and value are free format text fields*, however it is not a common practice to include such kind of characters on the *key*. We are going to analyze each one of those values to understand what they mean.

The [**FIXME**](http://wiki.openstreetmap.org/wiki/Key:fixme) *key* *"allows contributors to mark objects and places that need further attention”*. The **CODIGO** *key* does not seem to have any meaning, we will try to understand what it means later. The **N** *key* seems to be some kind of error, we will try to discover its meaning later too. The **naptan** namespace references the [NaPTAN and NPTG](http://wiki.openstreetmap.org/wiki/NaPTAN) datasets for bus stops and places which the [UK Department for Transport](http://www.dft.gov.uk/) and [Traveline](http://www.traveline.org.uk/aboutTL.htm) have offered to make available to OpenStreetMap project, so given that this region belongs to Spain, I suppose these values should not be there. The [**ideewfs**](http://wiki.openstreetmap.org/wiki/ES:RGN) *key* refers to the *Web Feature Services* (WFS) of the *Infraestructura de Datos Espaciales de España* (IDEE - Spatial Data Infrastructure of Spain), which is a web service to consult geographic features of Spain, so this data refers to data that belongs to the *Red Geodésica Nacional* (RGN - National Geodetic Network). The [**ref**](http://wiki.openstreetmap.org/wiki/Key:ref) *key* is used for reference numbers or codes (as we have seen for referencing the *nodes* within a *way*), which in this case has the **RRG** namespace, that is referenced on the RGN (as the **ideewfs**). Nevertheless, I have not found any reference about what it means, so we will treat them the same way as others. The penultimate element is the [**fuel**](http://wiki.openstreetmap.org/wiki/Key:fuel) *key*, which describes which fuels are available at [amenity](http://wiki.openstreetmap.org/wiki/Key:amenity)=[fuel](http://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfuel) sites. Finally we have a value `u'Torre\xf3n del castillo de los Salazar'` that clearly should not be there because it refers to a name of some kind of castle-like building, so it has to be within the *value* of a **[historic](http://wiki.openstreetmap.org/wiki/Key:historic):castle** *key* (for example).

Summarizing, we can proceed to storage as attributes in our document the *keys* **FIXME** (because we do not know what that user was referring to) and **fuel**. In the case of **ideewfs** and **ref:RRG**, it turns out that these *nodes* has a *tag* with a **source** *key* pointing to the IDEE, so both reference to the same source. However, we are not sure about the meaning of those *tags*, so we will further analysis of the *keys*. The case **CODIGO** refers to a some specific trees that are protected by the Basque Government and have a unique identifier that can be consulted [here](http://www.uragentzia.euskadi.net/u81-ecoaguas/es/u95aWar/lugaresJSP/U95aVolverLugares.do?u95aMigasPan=L,1,1,1,3,1,1;L,2,13674,018;H,2,14021,016;L,2,13745,002;EN,1,9,1,300;L,2,13733,007;). They are under the [*Primary Feature* **natural**](http://wiki.openstreetmap.org/wiki/Map_Features#Natural) so we can treat these values as other attributes within our object.

In the castle-case, effectively we have the following wrong *tag*: `<tag k="Torreón del castillo de los Salazar" v="water" />`. We do not know what the user wanted to say with the *water* value, but it is clear that the *key* in this case should be moved to a *tag* with a *name key*: `<tag k="name" v="Torreón del castillo de los Salazar" />`. The **N** *key* refers to a street name as the *tag* states: `<tag k="N" v="Calle Real" />`, so we should change it for `<tag k="name" v="Calle Real" />`.

#### 4.1.2 *Namespaces* and aggregating attributes

> This analysis has been performed with different functions within the [audit_keys_namespaces.py](./src/audit_keys_namespaces.py) script.

As we stated before, the *tags* that belong to a *namespace* are going to be nested within attributes in our JSON document. However, there are some cases where we have a specific *key* and also other *keys* with that same *key* as prefix, for example:

``` xml
<node changeset="12512900" id="571400447" lat="43.2249805" lon="-2.8184747" timestamp="2012-07-27T15:24:07Z" uid="53891" user="nubarron" version="6">
    <tag k="is_in" v="Bizkaia;Euskadi;Spain;Europe" />
    <tag k="is_in:continent" v="Europe" />
    <tag k="is_in:country" v="Spain" />
    <tag k="is_in:municipality" v="Usansolo" />
    <tag k="is_in:province" v="Bizkaia" />
    <tag k="is_in:region" v="Euskadi" />
    <tag k="name" v="Trokarro" />
    <tag k="place" v="suburb" />
  </node>
```

Here we have serval *tags* with the **is_in** prefix and one without *namespace*. Moreover, in this case, the *tag* without *namespace* has all the other values separated by a semicolon, so we should probably remove it. This behavior is not always the same, for example:

``` xml
<node changeset="30014663" id="560565243" lat="43.2607099" lon="-2.9271508" timestamp="2015-04-06T12:44:22Z" uid="251029" user="Voidoid" version="5">
    <tag k="amenity" v="bank" />
    <tag k="atm" v="yes" />
    <tag k="atm:network" v="Euro 6000" />
    <tag k="name" v="BBK" />
  </node>
```

In this case the *tag* without *namespace* only states that there is an **atm** (and that we will probably have other *tags* with **atm** as prefix). In this case we should also remove the "plain" *tag* as we know that this point do have an atm because it will have an **atm** attribute.

The complete list of *tags* that follow this pattern can be shown below:

``` python
['building', 'population', 'maxspeed', 'lanes', 'name', 'aerialway', 'area', 'social_facility', 'wheelchair', 'atm', 'wikipedia', 'recording', 'source', 'alt_name', 'internet_access', 'is_in']
```

Nevertheless, each individual case could be different. In the case of the [**name**](http://wiki.openstreetmap.org/wiki/Names) for example, we could have a **name** *tag* for the default name and localized names in different languages with suffixes to that *tag* (**name:es** for the spanish name).

After examining all these values, I would conclude that the most reasonable approach is to create a **default** value for the *tag* without *namespace* and add the rest with their corresponding *namespace*. In the example of the **atm**:

``` json
{
...
'atm': {
		'default': 'yes',
        'network': 'Euro 6000'
	   }
}
```

### 4.2 Analyzing the *values*

Now it is time to analyze all the *values* within the *tags* of the different *Elements*. Given the large amount of different attributes, we are going to focus in those that could be checked in some way, like the
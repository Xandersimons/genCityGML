'''
Created: 2016-03-17
Last modified: 2016-12-23

@author: simons

For an easy and correct usage of the script please read the README.
The original source of the file "genCityGML.py" is the Random3Dcity (http://github.com/tudelft3d/Random3Dcity) generateCityGML.py,
a tool developed by Filip Biljecki at TU Delft. Version: 2015-10-05.
It has been reduced and modified to work with postgis data bases to generate
buildings as LoD1 solids or LoD1 with surface type information (LoD2 like)
from OSM-footprints which are stored in a table. 

This script for generating CityGML uses postgis functios. The postgis extension is needed.
This script is not using any postgis-SFCGAL functions. The postgis-sfcgal extension is NOT needed.
'''

'''
Chose the LoD you would like to generate
'''
LoD = "2"

'''
Input Parameter for DB-Connection
'''

database    = ""
user        = "postgres"
password    = ""
host        = "localhost"
port        = "5432"

#########

'''
Table Attributes of building data set
'''
tableName   = "tpk_karlsruhe"
buiUUID     = "id"
elevation   = 'elevation'
'''IMPORTANT: does your buildings height information come from '''
''' building height'''
buiHeight   = ""
''' of building floor number '''
buiFloorN   = "floor_no"
''' average floor height, unit Meter'''
avg_floorH = 3

''' *optional if needed* WHERE condition: e.g. id = 1cf'''
where = ""


def buiHeightAttrib():
    ''' Function for DB querying with the right height input parameter
        used by module objGenerator
    '''
    if buiHeight == "":
#        print  buiFloorN
        return buiFloorN
    else:
#        print  buiHeight
        return buiHeight

# if __name__ == "__main__":
#     buiHeightAttrib()
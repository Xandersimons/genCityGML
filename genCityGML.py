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
from lxml import etree
import objGenerator.objGenerator as oG
import getData.getData as gD
import inputPara.inputPara as iP
import time
import uuid

start = time.time()
start_time = oG.timeNow()
print ("Start surface calculation start at", start_time)

#-- Name spaces
ns_citygml = "http://www.opengis.net/citygml/2.0"

ns_gml = "http://www.opengis.net/gml"
ns_bldg = "http://www.opengis.net/citygml/building/2.0"
ns_tran = "http://www.opengis.net/citygml/transportation/2.0"
ns_veg = "http://www.opengis.net/citygml/vegetation/2.0"
ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
ns_xlink = "http://www.w3.org/1999/xlink"
ns_dem = "http://www.opengis.net/citygml/relief/2.0"
ns_fme = "http://www.safe.com/xml/xmltables"

nsmap = {
    None: ns_citygml,
    'gml': ns_gml,
    'bldg': ns_bldg,
    'tran': ns_tran,
    'veg': ns_veg,
    'xsi': ns_xsi,
    'xAL': ns_xAL,
    'xlink': ns_xlink,
    'dem': ns_dem,
    'fme': ns_fme
}

#-- Functions

def createCityGML():
    """Creates a CityGML foundation to be filled later by the remaining part of the script."""
    startCM = time.time()
    print ("Generating CityModel and BBox")
    CityModel = etree.Element("CityModel", nsmap=nsmap)
    citymodelname = etree.SubElement(CityModel, "{%s}name" % ns_gml)
    citymodelname.text = str("Prototype")
    boundedBy = etree.SubElement(CityModel, "{%s}boundedBy" % ns_gml)
    Envelope = etree.SubElement(boundedBy, "{%s}Envelope" % ns_gml)
    Envelope.attrib["srsName"] = "EPSG:"+str(gD.getSRID())
    Envelope.attrib["srsDimension"] = "3"
    lowercorner = etree.SubElement(Envelope, "{%s}lowerCorner" % ns_gml)
    lowercorner.text = oG.lCorner()
    uppercorner = etree.SubElement(Envelope, "{%s}upperCorner" % ns_gml)
    uppercorner.text = oG.uCorner()
    print ("Creating CityModel and BBox took ",time.time()-startCM, "seconds.")
    return CityModel

def CityGMLbuildingLOD1(CityModel):
    """
    Generate a cityObjectMember representing a building in LOD1.
    Input: ID, building surfaces
    Output: CityGML code of the cityObjectMember as a lod1Solid of CompositeSurface's.
    """
    startBui = time.time()
    print ("Started generating Buildings")
    building = oG.createSurfaces()
    srid = str(gD.getSRID())
    for bui in building:
        cityObject = etree.SubElement(CityModel, "cityObjectMember")
        bldg = etree.SubElement(cityObject, "{%s}Building" % ns_bldg)
        bldg.attrib['{%s}id' % ns_gml] = bui[0]    
        lod1Solid = etree.SubElement(bldg, "{%s}lod1Solid" % ns_bldg)
        Solid = etree.SubElement(lod1Solid, "{%s}Solid" % ns_gml)
        Solid.attrib["srsName"] = "EPSG:"+srid
        Solid.attrib["srsDimension"] = "3"
        exterior = etree.SubElement(Solid, "{%s}exterior" % ns_gml)
        compSurface = etree.SubElement(exterior, "{%s}CompositeSurface" % ns_gml)
        surfClltn = bui[1]
        for surf in surfClltn:
            pLine = ' '.join(surf)    
            surfaceMember = etree.SubElement(compSurface, "{%s}surfaceMember" % ns_gml)
            sPolygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
            exterior = etree.SubElement(sPolygon, "{%s}exterior" % ns_gml)
            LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            posList = etree.SubElement(LinearRing, "{%s}posList" % ns_gml)
            posList.attrib["srsDimension"] = "3"
            posList.text = pLine

    print ("Generating Buildings took ",time.time()-startBui, "seconds.")  
    return CityModel

def lod2MultiSurface(lod2rep, surf):
        """
        Generates a MultiSurface for an LoD2 surface type
        Input: building surfaces
        Output: CityGML code of MultiSurface object.
        """
        pLine = ' '.join(surf)
        multiS = etree.SubElement(lod2rep, "{%s}MultiSurface" % ns_gml)
        multiS.attrib['{%s}id' % ns_gml] = "geomID"+str(uuid.uuid4())
        multiS.attrib['{%s}srsDimension' % ns_gml] = "3"
        surfaceMember = etree.SubElement(multiS, "{%s}surfaceMember" % ns_gml)
        polygoN = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
        polygoN.attrib['{%s}id' % ns_gml] = "polyID"+str(uuid.uuid4())
        exterior = etree.SubElement(polygoN, "{%s}exterior" % ns_gml)
        LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
        LinearRing.attrib['{%s}id' % ns_gml] = "ringID"+str(uuid.uuid4())
        posList = etree.SubElement(LinearRing, "{%s}posList" % ns_gml)
        posList.text = pLine  
    
def CityGMLbuildingLOD2(CityModel):
    """
    Generate a cityObjectMember representing a building in LOD1 with sufraceType structure.
    Input: ID, building surfaces
    Output: CityGML code of the cityObjectMember as a lod2Multisurface.
    """
    startBui = time.time()
    print ("Started generating Buildings")
    building = oG.createSurfaces()
    for bui in building:
        cityObject = etree.SubElement(CityModel, "cityObjectMember")
        bldg = etree.SubElement(cityObject, "{%s}Building" % ns_bldg)
        bldg.attrib['{%s}id' % ns_gml] = bui[0]
        surfClltn = bui[1]
        numSurf = len(surfClltn)
        countSurf= 0
        for surf in surfClltn:
            countSurf = countSurf+1
            if countSurf == 1:                       
                ## - Ground surface
                boundedBy = etree.SubElement(bldg, "{%s}boundedBy" % ns_bldg)
                groundS = etree.SubElement(boundedBy, "{%s}GroundSurface" % ns_bldg)
                groundS.attrib['{%s}id' % ns_gml] = "surfaceID"+str(uuid.uuid4())
                lod2rep = etree.SubElement(groundS, "{%s}lod2MultiSurface" % ns_bldg)
                lod2rep = lod2MultiSurface(lod2rep, surf)
            elif countSurf < numSurf:  
                ## - Wall surface
                boundedBy = etree.SubElement(bldg, "{%s}boundedBy" % ns_bldg)
                wallS = etree.SubElement(boundedBy, "{%s}WallSurface" % ns_bldg)
                wallS.attrib['{%s}id' % ns_gml] = "surfaceID"+str(uuid.uuid4())
                lod2rep = etree.SubElement(wallS, "{%s}lod2MultiSurface" % ns_bldg)
                lod2rep = lod2MultiSurface(lod2rep, surf)
            elif countSurf == numSurf:
                ## - Roof surface
                boundedBy = etree.SubElement(bldg, "{%s}boundedBy" % ns_bldg)
                roofS = etree.SubElement(boundedBy, "{%s}RoofSurface" % ns_bldg)
                roofS.attrib['{%s}id' % ns_gml] = "surfaceID"+str(uuid.uuid4())
                lod2rep = etree.SubElement(roofS, "{%s}lod2MultiSurface" % ns_bldg)
                lod2rep = lod2MultiSurface(lod2rep, surf)

    print ("Generating Buildings took ",time.time()-startBui, "seconcfds.")
    return CityModel

def storeCityGML(CityModel):
    startWr = time.time()
    print ("Writing the CityGML file.")
    citygml = etree.tostring(CityModel, pretty_print=True)
    #-- Write the CityGML file    
    fname = iP.tableName+"_EPSG-"+gD.getSRID()+'_lod'+iP.LoD+'.gml'
#    fname = iP.tableName+'_'+gD.getSRID()+'_lod2.gml'
    citygmlFile = open(fname, "w")
    #-- Header of the XML
    citygmlFile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
    citygmlFile.write("<!-- Generated by genCityGML v.2.1, a tool developed by Alexander Simons \
at European Institute for Energy Redsearch Karlsruhe with modificated \
script parts of Random3Dcity (http://github.com/tudelft3d/Random3Dcity), \
a tool developed by Filip Biljecki at TU Delft. Version: 2015-10-05. -->\n")
    citygmlFile.write(citygml.decode('utf-8'))
    citygmlFile.close()
    print ("CityGML-File '"+fname+"' has been created. Writing took ",time.time()-startWr, "seconds.")
    end = time.time()
    end_time = oG.timeNow()
    print ("Script genCityGML v 2.1 finished at, ", end_time)
    duration = end-start
    print ("run time = ", time.time() - start, "seconds")
    print ("It took in total %i h, %i min, %i s seconds" %(int(duration/60/60), int((duration/60)%60), duration%60))

if __name__ == "__main__":
    CityModel = createCityGML()
    if iP.LoD == "1":
        CityModel = CityGMLbuildingLOD1 (CityModel)
    elif iP.LoD == "2":
        CityModel = CityGMLbuildingLOD2 (CityModel)
    storeCityGML(CityModel)
#    print etree.tostring(CityModel, pretty_print=True)
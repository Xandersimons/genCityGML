'''
Created: 2016-03-17
Last modified: 2016-09-26

@author: simons

FYI:
If you have POLYGON objects in your table change the lines 53-54 and 102-103.
The functions for creating the polygons which describe the envelope of the building 
are working currently with MULTIPOLYGON. This is done because the DB-Manger of QGIS 2.8 or higher imports polygons from
shapes as MULTIPOLYGON. 
'''

import getData.getData as gD
import inputPara.inputPara as iP
import time
import re

def timeNow():
    ''' Just a wanted to know what time it is. '''
    return time.strftime("%H:%M:%S", time.localtime())

def createSurfaces():
    ''' 
    Checking the given type of height information for creating the building structures
    called function generates the vertices of the building objects
    '''
    if iP.buiHeight == "":
        building = createWithFloorN()
        return building
    else:
        building = createWithBuiHeight()
        return building
        
def createWithFloorN():
    '''
    creating the polygons which describe the envelope of the building object as a LoD1 cube
    uses the floor number information to create the height for the building by multiplying with the value 3
    repackages them into a list in a certain order for the genCityGML.py
    '''
    start = time.time()
    print ("Start generating Surfaces")
    rows = gD.getBuiAttrib()
    building = []
    for row in rows:
        buiInfo = []
        objUUID = str(row[0])
        polyString = row[1]
        buiHeight = row[2]
        elevation = row[3]         
        storePS = re.split(';', polyString)      
        strMultyP = storePS[1]
        spMP = strMultyP.replace("MULTIPOLYGON(((", "")
#        spMP = strMultyP.replace("POLYGON(((", "")
        spMP = spMP.replace(")))", "")
        spMP = re.split(',', spMP)    
        groundS = []
        for i in spMP:
            groundS.append(i+" "+str(elevation))
            
        roofS =  []    
        for i in spMP:
            roofH = elevation+(buiHeight*iP.avg_floorH)
            roofS.append(i+" "+str(roofH))
            
        reVroofS = roofS[::-1]                            
        surfCllctn = []
        surfCllctn.append(groundS)
        nuW = len(groundS)-1
        num = 1        
        while num <= nuW:
            wallS = [groundS[num], groundS[num-1], roofS[num-1], roofS[num], groundS[num]]
            surfCllctn.append(wallS)
            num = num+1
        
        surfCllctn.append(reVroofS)        
        buiInfo.append(objUUID)    
        buiInfo.append(surfCllctn)
        building.append(buiInfo)

    print ("Generating Surfaces took ",time.time() - start, "seconds")
    return building

def createWithBuiHeight():
    '''
    creating the polygons which describe the envelope of the building object as a LoD1 cube
    uses the building height information to create the height for the building
    repackages them into a list in a certain order for the genCityGML.py
    '''
    start = time.time()
    print ("Start generating Surfaces")
    rows = gD.getBuiAttrib()
    building = []
    for row in rows:
        buiInfo = []
        objUUID = str(row[0])
        polyString = row[1]
        buiHeight = row[2]
        elevation = row[3]         
        storePS = re.split(';', polyString)      
        strMultyP = storePS[1]
        spMP = strMultyP.replace("MULTIPOLYGON(((", "")
#        spMP = strMultyP.replace("POLYGON(((", "")
        spMP = spMP.replace(")))", "")
        spMP = re.split(',', spMP)    
        groundS = []
        for i in spMP:
            groundS.append(i+" "+str(elevation))
            
        roofS =  []    
        for i in spMP:
            roofH = elevation+(buiHeight)
            roofS.append(i+" "+str(roofH))
            
        reVroofS = roofS[::-1]                            
        surfCllctn = []
        surfCllctn.append(groundS)
        nuW = len(groundS)-1
        num = 1        
        while num <= nuW:
            wallS = [groundS[num], groundS[num-1], roofS[num-1], roofS[num], groundS[num]]
            surfCllctn.append(wallS)
            num = num+1
        
        surfCllctn.append(reVroofS)        
        buiInfo.append(objUUID)    
        buiInfo.append(surfCllctn)
        building.append(buiInfo)

    print ("Genrating Surfaces took ",time.time() - start, "seconds")
    return building

def createBBox():
    ''' 
    Generates lower and upper point with x,y,z for the bounding box 
    for the whole area of the region in which the model is located
    '''
    rows = gD.getExtent()
    for row in rows:
        extent = str(row[0])
        floorN = row[1]
        elevMax = row[2]
        elevMin = row[3]
        
        store = extent.replace("BOX(", "")
        store = store.replace(")", "")                         
        store = re.split(',', store)
        
        lCorner = store[0]
        uCorner = store[1]
        
        lCz = elevMin
        uCz = elevMax+(floorN*3)

        lCorner = lCorner+" "+str(lCz)
        uCorner = uCorner+" "+str(uCz)
        
        gBBox = []
        gBBox.append(lCorner)
        gBBox.append(uCorner)
        return gBBox
        
def lCorner():
    ''' gives back the lover corner '''
    gBBox = createBBox()
    lCorner = gBBox[0]
    print ("Bounding box is defined with:")
    print (lCorner)
    return (lCorner)
        
def uCorner():
    ''' gives back the upper corner '''
    gBBox = createBBox()
    uCorner = gBBox[1]
    print (uCorner)
    return (uCorner)

#if __name__ == '__main__':
#    lCorner()
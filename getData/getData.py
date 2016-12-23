'''
Created: 2016-03-17
Last modified: 2016-09-26

@author: simons
'''

import psycopg2.extras
import sys
import time
import inputPara.inputPara as iP

def getBuiAttrib_rhr():
    '''
    NOT IN USE
    Function is useful if some polygons are oriented the wrong way. 
    Use this function if you have problems with surfaces facing into the wrong direction.
    BUT: Causes problems for (multi-)polygons with a donut shaped structures
    '''
    start = time.time()
    print ("Querying data from DB")
    try:
        con = psycopg2.connect(database = iP.database , user = iP.user, password = iP.password, host = iP.host, port = iP.port)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT \
              "+ iP.tableName +"."+ iP.buiUUID +", \
              ST_AsEWKT(ST_Force2D(ST_ForceRHR("+ iP.tableName +".geom))), \
              "+ iP.tableName +"."+ iP.buiHeightAttrib()+", \
              "+ iP.tableName +"."+ iP.elevation +" \
            FROM \
              public."+ iP.tableName +" \
            "+ iP.where +";")
        con.commit()        
        rows = cursor.fetchall()
#        for row in rows:
#            print row
        print ("Querying data took ",time.time() - start, "seconds")          
        return rows
                
    except psycopg2.DatabaseError as e:
        print ('Error %s' % e)
        sys.exit(1)
       
    finally:
        if con:
            con.close()
            
def getBuiAttrib():
    '''
    Function queries for needed attributes to generate 3d objects.
    If your polygons are 3D (have a z-value) they will get forced to 2D. Z-value will be added through the attribute 
    elevation which should be contained in your db-table. This is done for avoid creating non planar surfaces.   
    '''
    start = time.time()
    print ("Querying data from DB")
    try:
        con = psycopg2.connect(database = iP.database , user = iP.user, password = iP.password, host = iP.host, port = iP.port)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT \
              "+ iP.tableName +"."+ iP.buiUUID +", \
              ST_AsEWKT(ST_Force2D("+ iP.tableName +".geom)), \
              "+ iP.tableName +"."+ iP.buiHeightAttrib()+", \
              "+ iP.tableName +"."+ iP.elevation +" \
            FROM \
              public."+ iP.tableName +" \
            "+ iP.where +";")
        con.commit()        
        rows = cursor.fetchall()
#        for row in rows:
#            print row
        print ("Querying data took ",time.time() - start, "seconds")  
        print (len(rows), "buildings where found." )     
        return rows
                
    except psycopg2.DatabaseError as e:
        print ('Error %s' % e)
        sys.exit(1)
       
    finally:
        if con:
            con.close()
           
def getSRID():
    '''
    Retrieves the SRID / EPSG code of your polygons for setting the information of the reference system into the 
    bounding box in the CityGML file. This is done once for all objects in your data set.
    '''
    try:
        conn = psycopg2.connect(database = iP.database , user = iP.user, password = iP.password, host = iP.host, port = iP.port)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT \
                      ST_SRID("+ iP.tableName +".geom) \
                    FROM \
                      public."+ iP.tableName +" \
                    GROUP BY \
                      ST_SRID("+ iP.tableName +".geom);")
        conn.commit()    
        rows = cursor.fetchall()
        rows = str(rows)
        rows = rows.replace("[[","")
        rows = rows.replace("]]","")
        print ("Data is referenced in EPSG:",rows)
        return (rows)
                 
    except psycopg2.DatabaseError as e:
        print ('Error %s' % e)
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()

def getExtent():
    '''
    Retrieves information for generating a 3D bounding box that describes the extent of the whole 3D model.
    The extend is an approximation: The upper Z value gets calculated from the two maximum values of
    building height and elevation found in the db-table. This results often it to high bounding boxes.
    '''
    try:
        con = psycopg2.connect(database = iP.database , user = iP.user, password = iP.password, host = iP.host, port = iP.port)
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT \
                        st_extent("+ iP.tableName +".geom), \
                        max("+ iP.tableName +"."+ iP.buiHeightAttrib()+") as floorN, \
                        max("+ iP.tableName +"."+ iP.elevation +") as elev_max, \
                        min("+ iP.tableName +"."+ iP.elevation +") as elev_min \
                      FROM \
                        public."+ iP.tableName +" \
                        LIMIT 1 ;")
        con.commit()
        rows = cursor.fetchall()
#        print rows
        return rows
                
    except psycopg2.DatabaseError as e:
        print ('Error %s' % e)
        sys.exit(1)
       
    finally:
        if con:
            con.close()
                
if __name__ == "__main__":
    getSRID()
    getExtent()
    getBuiAttrib()        
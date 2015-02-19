# -*- coding: utf-8 -*-

"""
***************************************************************************
*   Thanks to original ideas and codes from :                             *
*   Javier Martinez Garcia 2014                                           *
*   Gui ideas from by Jonathan Wiedemann 2014                             *
*   Jonathan Wiedemann for view codes                                     *
*   galou_breizh for macro which creates a circle from 3 selected points  *
*   Eriossoltero for macro Ellipse-Center+2Points                         *
*   Many Thanks to wmayer for his active help on testing and debbuging    *
*   Special thanks to Mario52 for FCCamera code                           * 
*      for bounding box codes, advices, diverse pieces of codes           * 
*      and all discussions...merci Mario                                  *
***************************************************************************
***************************************************************************
*   FreeCAD Work Features / version 2015-01                               *
*   Copyright (c) 2014, 2015 <rentlau_64>                                 *
*   Code rewrite by <rentlau_64>                                          *
*   Copyright (c) 2014 Javier Martinez Garcia                             *
*   Copyright (c) 2013, 2014 Jonathan Wiedemann                           *
*   Copyright (c) 2014, 2015 Mario52                                      *
*   Copyright (c) 2013 galou_breizh                                       *
*   Copyright (c) Eriossoltero                                            *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the COPYING and COPYING.LESSER text files.             *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA or see <http://www.gnu.org/licenses/>                             *
***************************************************************************
"""
# First two lines to be able to launch with python
import sys
# change this by your own FreeCAD lib path import FreeCAD
if not sys.path.__contains__("/usr/lib/freecad/lib"): 
    sys.path.append("/usr/lib/freecad/lib")     
 
import WFGui_2015 as WFGui
global myRelease
myRelease = "2105_02_17"

import os.path
import math
    
import FreeCAD as App
import FreeCADGui as Gui
from pivy.coin import *
import Part
import Draft
from FreeCAD import Base 

from PySide import QtCore, QtGui

####################################################################################

# assume the Icons directory in the same directory as this MACRO file
ICONS_PATH = os.path.dirname(__file__) + "/Icons"
# use "icons" as prefix which we used in the .ui file  
QtCore.QDir.setSearchPaths("icons", [ICONS_PATH]) 

# LineColor
red   = 1.0  # 1 = 255
green = 0.0  #
blue  = 0.0  #
flag_for_face=True

# Some Global variables
global myDialog
myDialog = None
global myObject
myObject = None
global centerOfMass
centerOfMass=True
global verbose
verbose=0

m_numberLinePart = 2
m_distanceLinePoint = 0.0
m_extensionTwoPointsAxis = 0.0
m_extensionLinePointAxis = 0.0
m_radiusCircle = 10.0
m_extensionFaceNormal = 10.0
m_extensionPlanePointPlane = 0.0
m_anglePlaneAxisPlane = 0.0
m_lengthPlane = 10.0
m_diameterCylinder = 2.0
m_lengthCylinder = 20.0 
m_lengthCube = 2.0
m_widthCube = 2.0
m_heightCube = 20.0 
m_widthPlane = 10.0

m_cut_selectObjects = []
m_angleCutObject = 0.0
m_thicknessCutObject = 0.0

m_callback = None
m_stack = []

error_msg = "Not yet Developped !"
           
####################################################################################
           
#Create a simple QMessageBox dialog for error messages.
def gui_errorDialog(msg):
    """ Create a simple QMessageBox dialog for error messages.
    """
    m_script = os.path.basename(os.path.realpath(__file__))
    # The first argument indicates the icon used:
    # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'Error in ' +
      str(m_script), msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    diag.exec_()


#Print a message on console.   
def print_msg(message):
    """ Print a message on console.
    """
    print message
    App.Console.PrintMessage( message + "\n")


#Print a ERROR message on console.   
def printError_msg(message):
    """ Print a ERROR message on console.
    """
    print message
    App.Console.PrintError("\nERROR : " + message)
    try :
        gui_errorDialog(message)
    except:
        App.Console.PrintError("\nERROR : Not able to launch a QT dialog !" )
        raise(Exception(message))


#Print x,y and z of a point:vector.
def print_point(point, msg=""):
    """ Print x,y and z of a point:vector.
    """
    if point.__class__.__name__ != "Vector":
        print_msg("Not a Vector to print !")
        return
    #print_msg(str(point))
    #m_type = point.__class__.__name__
    #print_msg(str(m_type))
    print_msg(str(msg) +
              "x =" + str(point.x) + ", "
              "y =" + str(point.y) + ", "
              "z =" + str(point.z))
    return


#Print x,y and z of 2 points:segment.
def print_segment(segment, msg=""):
    """ Print x,y and z of 2 points:segment.
    """
    point1 = segment[0]
    point2 = segment[1]
    if point1.__class__.__name__ != "Vector":
        print_msg("Not a Vector to print !")
        return 
    if point2.__class__.__name__ != "Vector":
        print_msg("Not a Vector to print !")
        return    
    print_msg(str(msg) +
              "x1 =" + str(point1.x) + ", "
              "y1 =" + str(point1.y) + ", "
              "z1 =" + str(point1.z) + ", "               
              "x2 =" + str(point2.x) + ", "
              "y2 =" + str(point2.y) + ", "
              "z2 =" + str(point2.z))
    return

def verbose_toggled(flag):
    """ Respond to the change of verbose flag.
    """
    global verbose
    verbose=0
    if flag == True:
        verbose=1

def init_min_max():
    """ Return min and max values from System.
    min_val, max_val = init_min_max
    """
    import sys
    if sys.version < '3.0.0':    
        max_val = sys.maxint
        min_val = -sys.maxint - 1
    else:# for python 3.0 use sys.maxsize
        max_val = sys.maxsize
        min_val = -sys.maxsize - 1
    return min_val, max_val


def alignCamera(sub0,sub1,reverse=False,info=0):
    """ Align the camera along an Axis crossing 2 points.
    """
    # Build vectors difference
    if reverse:
        v=sub0.sub(sub1)
    else:
        v=sub1.sub(sub0)
    if info != 0:
        print_msg("Vectors difference is :" + str(v)) 
    r=App.Rotation(App.Vector(0,0,1),v)
    if info != 0:
        print_msg("App.Rotation :" + str(r))
    # App.Rotation.Q : the rotation element as Quaternion
    Gui.ActiveDocument.ActiveView.setCameraOrientation(r.Q)
 
           
def createFolders(folder=None):
    """ Create WorkFeatures folders if needed.
    """
    if not(App.ActiveDocument.getObject("WorkFeatures")):   
        try:
            App.ActiveDocument.addObject("App::DocumentObjectGroup","WorkFeatures")    
        except:
            printError_msg("Could not Create 'WorkFeatures' Objects Group!")
    m_list_dirs = ['Origin','WorkPoints','WorkAxis','WorkPlanes','WorkCircles','WorkBoxes','WorkObjects']
    for m_dir in m_list_dirs:     
        if folder == m_dir:
            if not(App.ActiveDocument.getObject(str(m_dir))):
                try:
                    App.ActiveDocument.getObject("WorkFeatures").newObject("App::DocumentObjectGroup", str(m_dir))
                except:
                    printError_msg("Could not Create '"+ str(m_dir) +"' Objects Group!")
    return


def get_ActiveDocument(info=0):
    """ Return the active document
    """
    m_actDoc=App.activeDocument()
    if m_actDoc == None:
        printError_msg("No Active document selected !")
        return None
    if info != 0:
        message = "Active Document is : " + str(m_actDoc.Name)
        print_msg(message)   
    return m_actDoc

    
def get_ActiveView(info=0):
    """ Return the active View of active Document
    """
    m_actView=Gui.activeDocument().activeView()
    if m_actView == None:
        printError_msg("No Active view selected !")
        return None
    if info != 0:
        message = "Active View is : " + str(m_actView)
        print_msg(message)   
    return m_actView
  
    
def get_InfoObjects(info=0, printError=True):
    """ Return info on objects selected:
    num, selEx, objs, objNames
    num     : number of objects
    selEx   : a list of Selected Objects
    objs    : a list of the .Object
    objNames: a list of the .ObjectName
    """
    m_actDoc=get_ActiveDocument()
    if m_actDoc == None:
        if printError:
            printError_msg("No active document !")
        return 0, 0, 0, 0
    # Return a list of Selected Objects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_objNames = [selobj.ObjectName for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num < 1:
        if printError:
            printError_msg("Select at least one object !")
        return 0, 0, 0, 0
    if info != 0:
        print_msg("m_num=" + str(m_num) +
                  ", m_selEx=" + str(m_selEx) +
                  ", m_objs=" + str(m_objs) +
                  ", m_objNames=" + str(m_objNames))
    return m_num, m_selEx, m_objs, m_objNames

    
def get_SelectedObjects(info=0, printError=True):
    """ Return selected objects as
        Selection = (Number_of_Points, Number_of_Edges, Number_of_Planes,
                    Selected_Points, Selected_Edges, Selected_Planes)
    """
    m_actDoc=get_ActiveDocument(info=1)
    
    if m_actDoc.Name:    
        # Return a list of SelectionObjects for a given document name.
        # "getSelectionEx" Used for selecting subobjects
        m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
        m_objs = [selobj.Object for selobj in m_selEx]
        m_objNames = [selobj.ObjectName for selobj in m_selEx]
        m_num = len(m_objs)  
        m_num = len(m_selEx)
        if m_num >= 1: 
            Selected_Points = []
            Selected_Edges = []
            Selected_Planes = []
            for m_i in range(m_num):        
                Sel_i_Object = m_selEx[m_i]
                SubObjects_Inside = Sel_i_Object.SubObjects
                for n in range(len(SubObjects_Inside)):
                    SubObject = SubObjects_Inside[n]
                    if info != 0:
                        message = "Processing : " + str(m_objNames[m_i]) + " : " + str(SubObject.ShapeType)
                        print_msg(message)
                    if SubObject.ShapeType == "Vertex":
                        Selected_Points.append(SubObject)
                    if SubObject.ShapeType == "Edge":
                        Selected_Edges.append(SubObject) 
                    if SubObject.ShapeType == "Face":
                        Selected_Planes.append(SubObject)
            Number_of_Points = len(Selected_Points)
            Number_of_Edges = len(Selected_Edges)
            Number_of_Planes = len(Selected_Planes)
            Selection = (Number_of_Points, Number_of_Edges, Number_of_Planes,
                    Selected_Points, Selected_Edges, Selected_Planes)
            if info != 0:
                print_msg("Number_of_Points, Number_of_Edges, Number_of_Planes," +
                           "Selected_Points, Selected_Edges, Selected_Planes = " + str(Selection))
            return Selection
        else:
            if printError:
                printError_msg("Select at least one object !")
            return None
    else:
        printError_msg("No active document !")
    return 


def definePropOfActiveObj():
    Gui.activeDocument().activeObject().LineColor = (red, green, blue)
    Gui.activeDocument().activeObject().ShapeColor = (0.33,1.00,1.00)
    Gui.activeDocument().activeObject().Transparency = (50)
    
    
def addObjectToGrp(obj,grp,info=0):
    m_obj = obj
    m_grp = grp
    m_grp.addObject(m_obj) # adds object to the group
    if info != 0:
        print_msg("Object " + str(m_obj) + " added to Group : " + str(m_grp))
    
def addObjectToGrp2(obj,grp,info=0):
    m_obj = obj
    m_grp = grp
    m_grp.addObject(m_obj) # adds object to the group
    m_wire,m_del=Draft.downgrade(m_obj ,delete=True)
    m_num = len(m_wire)
    for m_i in range(m_num): 
        m_grp.addObject(m_wire[m_i]) # adds object to the group
        m_face,m_del1=Draft.upgrade(m_wire[m_i] ,delete=True)
        m_num = len(m_face)
        for m_i in range(m_num):
            m_grp.addObject(m_face[m_i]) # adds object to the group
    
    
def minMaxVectorsLimits(vertx,info=0):
    """ Return the min and max limits along the 3 Axis for all selected objects.
    """
    xmax = xmin = ymax = ymin = zmax = zmin = 0
    if vertx == None:
        print_msg("ERROR : vertx=None, leaving minMaxVectorsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin
    m_vertx = vertx
    m_num = len(m_vertx)
    if m_num < 1:
        print_msg("ERROR : len(m_vertx) <1 , leaving minMaxVectorsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin

    min_val, max_val = init_min_max()        
    xmin = ymin = zmin = max_val
    xmax = ymax = zmax = min_val
    #print_msg(str(xmin))
    #print_msg(str(xmax))
    if info != 0:
         print_msg("Vectors = " +str(m_vertx))
    for m_vert in m_vertx:
        xmax = max(xmax, m_vert.x)
        xmin = min(xmin, m_vert.x)
        ymax = max(ymax, m_vert.y)
        ymin = min(ymin, m_vert.y)
        zmax = max(zmax, m_vert.z)
        zmin = min(zmin, m_vert.z)
    if info != 0:
        print_msg("Limits along the 3 Axis of all vectors selected are :")    
        print_msg("xmax =" + str(xmax) + ", "
                  "xmin =" + str(xmin) + ", "
                  "ymax =" + str(ymax) + ", "
                  "ymin =" + str(ymin) + ", "
                  "zmax =" + str(zmax) + ", "
                  "zmin =" + str(zmin))    
    return xmax, xmin, ymax, ymin, zmax, zmin


def meanObjects(objs,info=0):
    """ Return the mean of centers of mass of all selected objects.    
    """
    mean = App.Vector(0.0,0.0,0.0)
    
    return mean
    
def minMaxObjectsLimits(objs,info=0):
    """ Return the min and max limits along the 3 Axis for all selected objects.
    """
    xmax = xmin = ymax = ymin = zmax = zmin = 0
    if objs == None:
        print_msg("ERROR : objs=None, leaving minMaxObjectsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin
        
    m_objs = objs
    m_num = len(m_objs)
    if m_num < 1:
        print_msg("ERROR : len(m_objs) <1 , leaving minMaxObjectsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin

    import sys
    if sys.version < '3.0.0':    
        max_val = sys.maxint
        min_val = -sys.maxint - 1
    else:# for python 3.0 use sys.maxsize
        max_val = sys.maxsize
        min_val = -sys.maxsize - 1        
    xmin = ymin = zmin = max_val
    xmax = ymax = zmax = min_val 
    #print_msg(str(xmin))
    #print_msg(str(xmax))
    m_doc=get_ActiveDocument()
    
    for m_obj in m_objs:
        if hasattr(m_obj, 'TypeId'):
            m_type = m_obj.TypeId
        else:
            m_type = m_obj.Type
        #pm_type = m_obj.TypeId        
        if info != 0:
            print_msg("m_obj        : " + str(m_obj))
            #print_msg("m_obj.Type   : " + str(m_obj.Type))
            #print_msg("m_obj.TypeId : " + str(m_obj.TypeId))
            print_msg("m_obj.TypeId : " + str(m_type))

        #if m_obj.TypeId[:6] == "Length":
        if m_type[:6] == "Length":
            if info != 0:
                print_msg("Found a Length object!")
            box = m_obj.Shape.BoundBox
        #elif m_obj.TypeId[:4] == "Mesh":
        elif m_type[:4] == "Mesh":
            if info != 0:
                print_msg("Found a Mesh object!")
            box = m_obj.Mesh.BoundBox
        #elif m_obj.TypeId[:6] == "Points":
        elif m_type[:6] == "Points":
            if info != 0:
                print_msg("Found a Points object!")
            box = m_obj.Points.BoundBox
        #elif m_obj.TypeId[:4] == "Part":
        elif m_type[:4] == "Part":
            if info != 0:
                print_msg("Found a Part object!")
            box = m_obj.Shape.BoundBox
        #elif m_obj.TypeId[:6] == "Sketch":
        elif m_type[:6] == "Sketch":
            if info != 0:
                print_msg("Found a Sketch object!")
            #box = Draft.draftify(m_obj,delete=False).Shape.BoundBox    
            m_wire = Draft.draftify(m_obj,delete=False)
            if info != 0:
                print_msg("m_wire = " + str(m_wire))
            if type(m_wire) is list:
                for m_sub_wire in m_wire:
                    if info != 0:
                        print_msg("m_sub_wire = " + str(m_sub_wire))
                    box = m_sub_wire.Shape.BoundBox
                    xmax = max(xmax, box.XMax)
                    xmin = min(xmin, box.XMin)
                    ymax = max(ymax, box.YMax)
                    ymin = min(ymin, box.YMin)
                    zmax = max(zmax, box.ZMax)
                    zmin = min(zmin, box.ZMin)                    
                    App.getDocument(str(m_doc.Name)).removeObject(str(m_sub_wire.Label))
            else:    
                box = m_wire.Shape.BoundBox          
                App.getDocument(str(m_doc.Name)).removeObject(str(m_wire.Label))
        else:
            continue
        if info != 0:
            print_msg("box = " + str(box))
        xmax = max(xmax, box.XMax)
        xmin = min(xmin, box.XMin)
        ymax = max(ymax, box.YMax)
        ymin = min(ymin, box.YMin)
        zmax = max(zmax, box.ZMax)
        zmin = min(zmin, box.ZMin)
    if info != 0:
        print_msg("Limits of all objects selected are :")    
        print_msg("xmax =" + str(xmax) + ", "
                  "xmin =" + str(xmin) + ", "
                  "ymax =" + str(ymax) + ", "
                  "ymin =" + str(ymin) + ", "
                  "zmax =" + str(zmax) + ", "
                  "zmin =" + str(zmin))               
    return xmax, xmin, ymax, ymin, zmax, zmin



def baseObjectPoint(obj,info=0):
    """ Return the base point of selected Object.
    """
    placement = App.Placement(obj.Placement)
    base = placement.Base
    #rotation = placement.Rotation
    if info != 0:
        print_point(base,"Base of object selected is :")           
    return base

def meanVectorsPoint(vertx,info=0):
    """ Return the mean point of all selected Vectors. 
    """
    mean = App.Vector(0.0,0.0,0.0)
    m_vertx = vertx
    m_num = len(m_vertx)
    if info != 0:
        print_msg("m_vertx = " + str(m_vertx))
        print_msg("m_num   =  " + str(m_num))
    if m_num < 1:
        print_msg("ERROR : len(m_vertx) <1 , meanVectorsPoint()")
        return mean
    m_list = []
    for m_vert in m_vertx:
        m_list.append(m_vert.x)
        m_list.append(m_vert.y)
        m_list.append(m_vert.z)
        
    import numpy
    V=numpy.array(m_list)    
    Vre = V.reshape(m_num,3)
    C=sum(Vre,0)/m_num
    
    if info != 0:
        print_msg("V = " + str(V))
        print_msg("Vre = " + str(Vre))
        print_msg("C = " + str(C))
    
    mean = App.Vector(C[0], C[1] , C[2])
    if info != 0:
        print_point(mean,"Mean of all vectors selected is : ")
    return mean
            
def centerBBVectorsPoint(vertx,info=0):
    """ Return the center point of the bounding box of all selected Vectors. 
    """
    center = None
    xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(vertx,info=info)
       
    center = App.Vector((xmax+xmin)/2.0, (ymax+ymin)/2.0, (zmax+zmin)/2.0)
    
    if info != 0:
        print_point(center,"Center of all vectors selected is : ")
    return center

    
def centerObjectsPoint(objs,info=0):
    """ Return the center point of all selected Objects.
    """
    center = None
    xmax, xmin, ymax, ymin, zmax, zmin = minMaxObjectsLimits(objs,info=info) 
    center = App.Vector((xmax+xmin)/2.0, (ymax+ymin)/2.0, (zmax+zmin)/2.0)
    if info != 0:
        print_point(center,"Center of all objects selected is : ")
    return center
    
def centerLinePoints(edge, index, number,info=0):
    """ Return the point at index/number of the Line.
    """
    Vector_A = None
    distance = edge.Length / 2
    if number != 0:
        distance = index * (edge.Length / number)
    Vector_A = edge.valueAt( distance )   
    if info != 0:
        print_point(Vector_A,"Point of line selected is : ") 
    return Vector_A

    
def centerLinePoint(edge,info=0):
    """ Return the center point of the Line.
    """
    center = None
    Vector_A=edge.valueAt( 0.0 )
    Vector_B=edge.valueAt( edge.Length )
    Vector_MidPoint = Vector_B + Vector_A
    center = Vector_MidPoint.multiply(0.5)
    if info != 0:
        print_point(center,"Center of line selected is : ") 
    return center


def centerCirclePoint(edge,info=0):
    """ Return the center point of the circle.
    """
    center = None
    center = edge.centerOfCurvatureAt( 0.0 )
    if info != 0:
        print_point(center,"Center of circle selected is :") 
    return center


def distanceBetween(A, B):
    """ return the distance between 2 points
    """
    line = Part.Line(A,B)
    edge = line.toShape()
    return edge.Length
    

def colinearVectors(A, B, C, info=0, precision=1e-12):
    """ Return true if the 3 points are aligned.
    """
    Vector_1 = B - A
    Vector_2 = C - B
    if info != 0:
        print_point(Vector_1, msg="Vector_1 : ")
        print_point(Vector_2, msg="Vector_2 : ")
    Vector_3 = Vector_1.cross(Vector_2)
    if info != 0:
        print_point(Vector_3, msg="Vector_1.cross(Vector_2) : ")
        
    if abs(Vector_3.x) <= precision and abs(Vector_3.y) <= precision and abs(Vector_3.z) <= precision:
        if info != 0:
            print_msg("Colinear Vectors !")
        return True
    else:
        if info != 0:
            print_msg("NOT Colinear Vectors !")
        return False
    return 


def intersecPoints(shape1, shape2, info=0):
    """ Return the intersection points between 2 shapes
    (Number_of_Points, Intersec_Points)
    or None
    """
    #s1 = shape1.Shape
    #s2 = shape2.Shape       
    s1 = shape1
    s2 = shape2
    cs = s1.common(s2)  
    sec = s1.section(s2)
    if info != 0:
        print_msg("s1 = " + str(s1))
        print_msg("s2 = " + str(s2))
        print_msg("s1.common(s2) = " + str(cs))
        print_msg("s1.common(s2).ShapeType = " + str(cs.ShapeType))
        print_msg("s1.section(s2) = " + str(sec))
        print_msg("s1.section(s2).Wires = " + str(sec.Wires))
        print_msg("s1.section(s2).Edges = " + str(sec.Edges))
    Intersec_Points = []
    if cs.Vertexes:
        for v in cs.Vertexes:
            Intersec_Points.append(v.Point)
            if info != 0:
                print_point(v.Point,"Intersection point : ")
        Number_of_Points = len(Intersec_Points)
        Intersections = (Number_of_Points, Intersec_Points)
        return Intersections
    else:
        error_msg = "Can't find any intersection point !"
        printError_msg(error_msg)
        return None
    return 

def getClickedPoint2(info):
    view = Gui.ActiveDocument.ActiveView
    down = (info["State"] == "DOWN")
    pos = info["Position"]
    global m_stack
    global m_callback
    if (down):
        point = view.getPoint(pos[0],pos[1])
        obj   = view.getObjectInfo(pos)
        if obj == None:
            m_stack.append(point)
        else:
            m_stack.append(App.Vector(obj["x"],obj["y"],obj["z"]))
        if len(m_stack) == 1:
            name = "Point"
            part = "Part::Feature"
            plot_point(m_stack[-1], part, name)
            print_point(m_stack[-1],"Click point at :")
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            del m_stack[:]

            
def getClickedNormal(info):
    msg=0
    view = Gui.ActiveDocument.ActiveView
    down = (info["State"] == "DOWN")
    pos = info["Position"]
    if msg != 0:
        print_msg("info['Position'] : " + str(pos))
    global m_stack
    global m_callback
    global m_extensionFaceNorma
    part = "Part::Feature"    
    if (down):
        point = view.getPoint(pos[0],pos[1])        
        obj   = view.getObjectInfo(pos)
        if msg != 0:
            print_msg("view.getPoint(pos[0],pos[1] : " + str(point))
            print_msg("view.getObjectInfo(pos) : " + str(obj))
        if obj == None:
            printError_msg("No Object selected !")
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            return None
        else:
            m_sel = Gui.Selection.getSelection()[0]
            m_face = m_sel.Shape.Faces[0]
            m_surf = m_face.Surface
            m_p = App.Vector(obj["x"],obj["y"],obj["z"])
            m_uv = m_surf.parameter(m_p)
            u,v = m_uv[0], m_uv[1]
            m_p1 = m_face.valueAt(u,v)
            m_p2 = m_face.normalAt(u,v)
            m_p3 = m_p1 + m_p2.normalize().multiply(m_extensionFaceNormal)
            createFolders('WorkAxis')
            name = "Normal"
            plot_axis(m_p1,m_p3, part, name)
            createFolders('WorkPoints')
            name = "Point"
            plot_point(m_p1, part,  name)
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            
def getClickedTangent(info):
    msg=0
    view = Gui.ActiveDocument.ActiveView
    down = (info["State"] == "DOWN")
    pos = info["Position"]
    if msg != 0:
        print_msg("info['Position'] : " + str(pos))
    global m_stack
    global m_callback
    global m_extensionFaceNorma
    part = "Part::Feature"    
    if (down):
        point = view.getPoint(pos[0],pos[1])        
        obj   = view.getObjectInfo(pos)
        if msg != 0:
            print_msg("view.getPoint(pos[0],pos[1] : " + str(point))
            print_msg("view.getObjectInfo(pos) : " + str(obj))
        if obj == None:
            printError_msg("No Object selected !")
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            return None
        else:
            m_sel = Gui.Selection.getSelection()[0]
            m_face = m_sel.Shape.Faces[0]
            m_surf = m_face.Surface
            m_p = App.Vector(obj["x"],obj["y"],obj["z"])
            m_uv = m_surf.parameter(m_p)
            u,v = m_uv[0], m_uv[1]
            m_p1 = m_face.valueAt(u,v)
            m_p2 = m_face.normalAt(u,v)
            m_p3 = m_p1 + m_p2.normalize().multiply(m_extensionFaceNormal)
            Plane_Normal = m_p3 - m_p1
            createFolders('WorkPlanes')
            name = "Tangent"
            Plane_User_Name, plane = plot_plane(m_lengthPlane, m_widthPlane, m_p1, Plane_Normal, part, name)            
            #createFolders('WorkAxis')
            #name = "Normal"
            #plot_axis(m_p1,m_p3, part, name)
            createFolders('WorkPoints')
            name = "Point"
            plot_point(m_p1, part,  name)
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
    
    
def getClickedPoint(event_cb):
    event = event_cb.getEvent()
    view = Gui.ActiveDocument.ActiveView
    stack = []
    global m_callback
    if event.getState() == SoMouseButtonEvent.DOWN:
        pos = event.getPosition()
        point = view.getPoint(pos[0],pos[1])
        stack.append(point)
        if len(stack) == 1:
            name = "Point"
            part = "Part::Feature"
            plot_point(stack[-1], part, name)
            view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),m_callback)
            
            
def getClickedAxis(event_cb):
    event = event_cb.getEvent()
    view = Gui.ActiveDocument.ActiveView
    global m_stack
    global m_callback
    if event.getState() == SoMouseButtonEvent.DOWN:
        pos = event.getPosition()
        point = view.getPoint(pos[0],pos[1])
        m_stack.append(point)
        if len(m_stack) == 2:
            name = "Line"
            part = "Part::Feature"
            Axis_User_Name, axis = plot_axis(m_stack[-2], m_stack[-1], part, name)
            view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),m_callback)
            del m_stack[:]

def getClickedPlane2(info):
    view = Gui.ActiveDocument.ActiveView
    down = (info["State"] == "DOWN")
    pos = info["Position"]
    global m_stack
    global m_callback
    if (down):
        point = view.getPoint(pos[0],pos[1])
        obj   = view.getObjectInfo(pos)
        if obj == None:
            m_stack.append(point)
        else:
            m_stack.append(App.Vector(obj["x"],obj["y"],obj["z"]))
        if len(m_stack) == 1:
            name = "Plane"
            part = "Part::Feature"
            # return view direction as a vector
            Plane_Normal = Gui.ActiveDocument.ActiveView.getViewDirection()
            # Set the base of the plane at location of mouse click
            Plane_Point = m_stack[-1]
            # Create a Plane
            Plane_User_Name, plane = plot_plane(m_lengthPlane, m_widthPlane, Plane_Point, Plane_Normal, part, name)
        
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            del m_stack[:]

            
def getClickedPlane(event_cb):
    event = event_cb.getEvent()
    view = Gui.ActiveDocument.ActiveView
    global m_stack
    global m_callback
    if event.getState() == SoMouseButtonEvent.DOWN:
        pos   = event.getPosition()
        point = view.getPoint(pos[0],pos[1])
        m_stack.append(point)
        if len(m_stack) == 1:
            name = "Plane"
            part = "Part::Feature"
            # return view direction as a vector
            Plane_Normal = Gui.ActiveDocument.ActiveView.getViewDirection()
            # Set the base of the plane at location of mouse click
            Plane_Point = m_stack[-1]
            # Create a Plane
            Plane_User_Name, plane = plot_plane(m_lengthPlane, m_widthPlane, Plane_Point, Plane_Normal, part, name)
        
            view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),m_callback)
            del m_stack[:]
            
#==============================================================================
# def intersecLineLine(A, B, C, D, info=0):            
#     """ Return the intersection between the Line L1 defined by A and B
#     and the Line L2 defined by C and D, if exists.
#     """
#     # L1 is the line defined by 2 points A(ax, ay, az) and B(bx, by, bz), and
#     # may be also defined as the line crossing A(ax, ay, az) and along the 
#     # direction AB = U1(bx-ax, by-ay, bz-az)
#     # If U1(u1x, u1y, u1z) = U1(bx-ax, by-ay, bz-az) the Line L1 is the set of 
#     # points M1 as defined by eq(1):
#     # Vector(M1A) = k1 * Vector(U1)
#     # with k1 Real 
#     if A == B:
#         return None
#     ax, ay, az = A.x, A.y, A.z
#     bx, by, bz = B.x, B.y, B.z
#     u1x, u1y, u1z = bx - ax, by - ay, bz - az
#         
#     # L2 is the line defined by 2 points C(cx, cy, cz) and D(dx, dy, dz), and
#     # may be also defined as the line crossing C(cx, cy, cz) and along the 
#     # direction CD = U2(dx-cx, dy-cy, dz-cz)
#     # If U2(u2x, u2y, u2z) = U2(dx-cx, dy-cy, dz-cz) the Line L1 is the set of 
#     # points M2 as defined by eq(2):
#     # Vector(M2C) = k2 * Vector(U2)
#     # with k2 Real     
#     if C == D:
#         return None
#     cx, cy, cz = C.x, C.y, C.z
#     dx, dy, dz = D.x, D.y, D.z
#     u2x, u2y, u2z = dx - cx, dy - cy, dz - cz
#     
#     # We look for point T(tx, ty, tz) as eq(3):
#     #Vector(TA) = k1 * Vector(U1) and 
#     #Vector(TC) = k2 * Vector(U2)
#     tx = ax + k * ux 
# 
#     ty = ay + k * uy
#     tz = az + k * uz
#     
#     return T
#==============================================================================    
def intersecPerpendicularLine(A, B, C, info=0):
    """ Return the intersection between the Line L defined by A and B
    and the Line perpendicular crossing the point C.
    """
    # L is the line defined by 2 points A(ax, ay, az) and B(bx, by, bz), and
    # may be also defined as the line crossing A(ax, ay, az) and along the 
    # direction AB = U(bx-ax, by-ay, bz-az)
    # If U(ux, uy, uz) = U(bx-ax, by-ay, bz-az) the Line L is the set of 
    # points M as defined by eq(1):
    # Vector(MA) = k * Vector(U)
    # with k Real 
    if A == B:
        return None
    ax, ay, az = A.x, A.y, A.z
    bx, by, bz = B.x, B.y, B.z
    cx, cy, cz = C.x, C.y, C.z
    ux, uy, uz = bx - ax, by - ay, bz - az
    #U = App.Vector(ux, uy, uz)
    # We look for T(tx, ty, tz) on the Line L
    # eq(1) in parametric form; k exists and follows eq(2):
    # tx = ax + k * ux 
    # ty = ay + k * uy
    # tz = az + k * uz
    
    # and vector V(vx, vy, vz) defined by point C and point T
    # vx, vy, vz = tx - cx, ty - cy, tz - cz
    # V must be perpendicular to the Line L 
    # We consider Dot product between U and V and give us eq(3) 
    # U.V = 0
    # so ux * vx + uy * vy + uz * vz = 0
    # ux * (tx - cx) + uy * (ty - cy) + uz * (tz - cz) = 0
    # ux * (ax + k * ux  - cx) + uy * (ay + k * uy - cy) + uz * (az + k * uz  - cz) = 0
    # ux*ax + ux*(k*ux) - ux*cx + uy*ay + uy*(k*uy) - uy*cy +  uz*az + uz*(k*uz) - uz*cz = 0
    if (ux*ux + uy*uy + uz*uz) == 0.0:
        return None
    k = (ux*cx + uy*cy + uz*cz - ux*ax - uy*ay - uz*az)/(ux*ux + uy*uy + uz*uz)   
    tx = ax + k * ux 
    ty = ay + k * uy
    tz = az + k * uz
    T = App.Vector(tx, ty, tz)
    vx, vy, vz = tx - cx, ty - cy, tz - cz
    V = App.Vector(vx, vy, vz)
    distance = math.sqrt(V.dot(V))
    Tprime = T + V
    if info == 1:
        print_point(T, msg="Intersection Point at distance of " +
                    str(distance) + " is : ")
    return T, distance, Tprime
    
    
def intersecLinePlane(A, B, Plane_Normal, Plane_Point, info=0):
    """ Return the intersection between the Line L defined by A and B
    and the Plane defined by Plane_Normal and Plane_Point.
    """
    # Plane Equation is eq(0) P(x, y, z): 
    # a * x + b * y + c * z + d = 0     
    # where Normal to P is  N(a, b, c)
    N = Plane_Normal
    if info == 1:
        print_point(N,"N is : ")
    #if N == App.Vector(0.0, 0.0, 0.0):
    #    return None   
    a, b, c = N.x, N.y, N.z
    if info == 1:
        print_msg("a = " + str(a) + " b = " + str(b) + " c = " + str(c))
    # p1(px,py,pz) belongs to the plane P, so
    # a * px + b * py + c * pz + d = 0 and
    # d = -(a * px + b * py + c * pz)
    p1 = Plane_Point
    d = -((a * p1.x) + (b * p1.y) + (c * p1.z))
    if info == 1:
        print_msg("d = "+ str(d))
    # L is the line defined by 2 points A(ax, ay, az) and B(bx, by, bz), and
    # may be also defined as the line crossing A(ax, ay, az) and along 
    # the direction AB = U(bx-ax, by-ay, bz-az)
    # If U(ux, uy, uz) = U(bx-ax, by-ay, bz-az) the Line L is the set of 
    # points M as defined by eq(1):
    # Vector(MA) = k * Vector(U)
    # with k Real
    if A == B:
        return None
    ax, ay, az = A.x, A.y, A.z
    bx, by, bz = B.x, B.y, B.z
    ux, uy, uz = bx - ax, by - ay, bz - az
    U = App.Vector(ux, uy, uz)
    if info == 1:
        print_point(U,"U is : ")
    # We consider Dot product between U and N 
    # 1> U.N = 0
    if info == 1:
        print_msg("U.dot(N) =" + str(U.dot(N)))
    
    if U.dot(N) == 0.0:
        # if A belongs to P : the full Line L is included in the Plane
        if (a * ax) + (b * ay) + (c * az) + d == 0.0:
            if info == 1:
                print_msg("The full Line is included in the Plane !")
            return A
        # if not the Plane and line are paralell without intersection
        else:
            if info == 1:
                print_msg("The Plane and the line are paralell without intersection !")
            return None
    # 2> U.N != 0
    else:
        # We look for T(tx, ty, tz) on the Line L
        # eq(1) in parametric form; k exists and follows eq(2):
        # tx = ax + k * ux 
        # ty = ay + k * uy
        # tz = az + k * uz
        # and T(tx, ty, tz) on the plane too so eq(1) is
        # a * tx + b * ty + c * tz + d = 0
        # by pasting the tx, ty and tz expressions into eq(1) we have a first 
        # deg equation with one unknow 'k':
        # a * (ax + k * ux) + b * (ay + k * uy) + c * (az + k * uz) + d = 0
        # so 
        # a * ax + a * k * ux + b * ay + b * k * uy + c * az + c * k * uz + d = 0
        # k * ( a * ux + b * uy  c *uz ) + a * ax + b * ay + c * az  + d = 0
        # k = -1 * (a * ax + b * ay + c * az  + d) / ( a * ux + b * uy + c *uz )
        if ( a * ux + b * uy + c *uz ) == 0.0:
            if info == 1:
                print_msg("a * ux + b * uy + c *uz == " + str(a * ux + b * uy + c *uz))
            return None
        k = -1 * (a * ax + b * ay + c * az  + d) / ( a * ux + b * uy + c *uz )
        tx = ax + k * ux 
        ty = ay + k * uy
        tz = az + k * uz
        if info == 1:
            print_msg("tx =" + str(tx) + " ty=" + str(ty) + " tz=" + str(tz))
        T = App.Vector(tx, ty, tz)
        if info == 1:
            print_point(T, msg="Intersection Point is : ")
        return T


def intersecPlanePlane(Plane_Normal1, Plane_Point1, Plane_Normal2, Plane_Point2, info=0): 
    """ Return the intersection Line between two Planes.
    """
    # Plane Equation is eq(0) P1(x, y, z): 
    # a1 * x + b1 * y + c1 * z + d1 = 0     
    # where Normal to P1 is  N1(a1, b1, c1)
    N1 = Plane_Normal1
    if info == 1:
        print_point(N1,"N1 is : ")
    a1, b1, c1 = N1.x, N1.y, N1.z
    if info == 1:
        print_msg("a1 = " + str(a1) + " b1 = " + str(b1) + " c1 = " + str(c1))
    # Plane Equation is eq(1) P2(x, y, z): 
    # a2 * x + b2 * y + c2 * z + d2 = 0     
    # where Normal to P2 is  N2(a2, b2, c2)
    N2 = Plane_Normal2
    if info == 1:
        print_point(N2,"N2 is : ")
    a2, b2, c2 = N2.x, N2.y, N2.z
    if info == 1:
        print_msg("a2 = " + str(a2) + " b2 = " + str(b2) + " c2 = " + str(c2))
    
    # p1(p1x,p1y,p1z) belongs to the plane P1, so
    # a1 * p1x + b1 * p1y + c1 * p1z + d1 = 0 and
    # d1 = -(a1 * p1x + b1 * p1y + c1 * p1z)
    p1 = Plane_Point1
    d1 = -((a1 * p1.x) + (b1 * p1.y) + (c1 * p1.z))
    if info == 1:
        print_msg("d1 = "+ str(d1))
    
    # p2(p2x,p2y,p2z) belongs to the plane P2, so
    # a2 * p2x + b2 * p2y + c2 * p2z + d2 = 0 and
    # d2 = -(a2 * p2x + b2 * p2y + c2 * p2z)
    p2 = Plane_Point2
    d2 = -((a2 * p2.x) + (b2 * p2.y) + (c2 * p2.z))
    if info == 1:
        print_msg("d2 = "+ str(d2))
        
    U = N2.cross( N1 )   
    if abs(U.x) <= 1.e-16 and abs(U.y) <= 1.e-16 and abs(U.z) <= 1.e-16:
        U.x, U.y, U.z  = 0.0, 0.0, 0.0  
    
    if info == 1:
        print_point(U,"N2.cross( N1 ) : ")
        
    if abs(U.x) == 0.0 and abs(U.y) == 0.0 and abs(U.z) == 0.0:
        if a1/a2 == d1/d2:
            if info == 1:
                print_msg("The 2 Planes are unique !")
            return None, "The 2 Planes are unique !"
        else:
            if info == 1:
                print_msg("The 2 Planes are parallel !")
            return None, "The 2 Planes are parallel !"
    else:
        return U

#============================================================================== 

       
def plot_point(Vector_point, part, name, grp="WorkPoints"):
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)
    point = App.ActiveDocument.addObject( part, name )
    point.Shape = Part.Vertex( Vector_point )
    App.ActiveDocument.getObject( grp ).addObject(point)
    point_User_Name = point.Label                
    Gui.ActiveDocument.getObject( point_User_Name ).PointColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( point_User_Name ).PointSize = 5.00
    return point_User_Name


def plot_axis(Vector_A, Vector_B, part, name, grp="WorkAxis"):
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)
    axis = App.ActiveDocument.addObject(part, name)
    axis.Shape = Part.makeLine(Vector_A, Vector_B)
    App.ActiveDocument.getObject( grp ).addObject(axis)
    axis_User_Name = axis.Label
    Gui.ActiveDocument.getObject(axis_User_Name).LineColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject(axis_User_Name).PointColor = (1.00,0.67,0.00)    
    return axis_User_Name, axis 


def plot_circle(Radius, Position, Direction, part= "Part::Feature", name= "Circle", grp="Circles"):
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)    
    circle = App.ActiveDocument.addObject(part, name)
    circle.Shape = Part.makeCircle(Radius, Position, Direction)
    App.ActiveDocument.getObject( grp ).addObject(circle)
    circle_User_Name = circle.Label
    Gui.ActiveDocument.getObject(circle_User_Name).LineColor = (1.00,0.67,0.00)  
    return circle_User_Name, circle 
    

def plot_ellipse(S1, S2, Center, part= "Part::Feature", name= "Ellipse", grp="Circles"):
    """Creates an ellipse centered on the point Center, where
    the plane of the ellipse is defined by Center, S1 and S2,
    its major axis is defined by Center and S1,
    its major radius is the distance between Center and S1, and
    its minor radius is the distance between S2 and the major axis.
    """
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)    
    ellipse = App.ActiveDocument.addObject(part, name)
    
    print_point(Center,"Center = :")
    print_point(S1,"S1 = :")
    print_point(S2,"S2 = :")

    P1C = (Center - S1).Length
    P2C = (Center - S2).Length
    if P1C > P2C:
        e = Part.Ellipse(S1,S2,Center)
    else:
    #e = Part.Ellipse(S1+Center,S2,Center)
        e = Part.Ellipse(S2,S1,Center)
    #e = Part.Ellipse()
    print_msg(str(e))
    
    ellipse.Shape = e.toShape()
    App.ActiveDocument.getObject( grp ).addObject(ellipse)
    ellipse_User_Name = ellipse.Label    
    Gui.ActiveDocument.getObject(ellipse_User_Name).LineColor = (1.00,0.67,0.00)
    return ellipse_User_Name, ellipse
       
    
def plot_plane(Edge_Length1, Edge_Length2, Plane_Point, Plane_Normal, part, name, grp="WorkPlanes"):
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)
    
    plane = App.ActiveDocument.addObject(part, name)
    
    Plane_face = Part.makePlane( Edge_Length1, Edge_Length2, Plane_Point, Plane_Normal )
    Plane_Center = Plane_face.CenterOfMass
    Plane_Translate =  Plane_Point - Plane_Center
    Plane_face.translate( Plane_Translate )
    plane.Shape = Plane_face
    
    App.ActiveDocument.getObject( grp ).addObject( plane )
    plane_User_Name = plane.Label
    Gui.ActiveDocument.getObject( plane_User_Name ).PointColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( plane_User_Name ).LineColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( plane_User_Name ).ShapeColor = (0.00,0.33,1.00)
    Gui.ActiveDocument.getObject( plane_User_Name ).Transparency = 75        
    return plane_User_Name, plane
    


def plot_cube(length, width, height, point, axis, part, name, grp="WorkObjects"):    
    """ Creating a Cube in the view.
    One of the Cube's extremities will be at the given point location.
    The Cube's axis will be along given axis
    Function used : makeBox(length,width,height,[pnt,axis]).
    By default pnt=Vector(0,0,0) and axis=Vector(0,0,1) 
    """
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)
         
    cube = App.ActiveDocument.addObject(part, name)
    
    Cube = Part.makeBox(length, width, abs(height), point, axis )
    Cube_Center = Cube.CenterOfMass
    Cube_Translate =  point - Cube_Center
    Cube.translate( Cube_Translate )
    Cube_Translate = axis.normalize().multiply(height/2.)
    Cube.translate( Cube_Translate )
    cube.Shape = Cube
    
    App.ActiveDocument.getObject( grp ).addObject( cube )    
    cube_User_Name = cube.Label
    
    Gui.ActiveDocument.getObject( cube_User_Name ).PointColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( cube_User_Name ).LineColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( cube_User_Name ).ShapeColor = (0.00,0.33,1.00)
    Gui.ActiveDocument.getObject( cube_User_Name ).Transparency = 75        
    return cube_User_Name, cube
  
    
def plot_cylinder(radius, height, point, axis, part, name, grp="WorkObjects"):
    """ Creating a Cylinder in the view.
    One of the Cylinder's extremities will be at the given point location.
    The Cylinder's axis will be along given axis
    Function used : makeCylinder(radius,height,[pnt,axis,angle]). 
    By default pnt=Vector(0,0,0),axis=Vector(0,0,1) and angle=360 
    """
    if not(App.ActiveDocument.getObject( grp )):
        App.ActiveDocument.addObject("App::DocumentObjectGroup", grp)
    
    cylinder = App.ActiveDocument.addObject(part, name)
    
    Cylinder = Part.makeCylinder( radius, abs(height), point, axis )
    Cylinder_Center = Cylinder.CenterOfMass
    Cylinder_Translate =  point - Cylinder_Center
    Cylinder.translate( Cylinder_Translate )
    Cylinder_Translate = axis.normalize().multiply(height/2.)
    Cylinder.translate( Cylinder_Translate )
    cylinder.Shape = Cylinder
    
    App.ActiveDocument.getObject( grp ).addObject( cylinder )
    cylinder_User_Name = cylinder.Label
    Gui.ActiveDocument.getObject( cylinder_User_Name ).PointColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( cylinder_User_Name ).LineColor = (1.00,0.67,0.00)
    Gui.ActiveDocument.getObject( cylinder_User_Name ).ShapeColor = (0.00,0.33,1.00)
    Gui.ActiveDocument.getObject( cylinder_User_Name ).Transparency = 75        
    return cylinder_User_Name, cylinder


def bounding_box(grp,ori_X,ori_Y,ori_Z,length_X,length_Y,length_Z,info=0):
    """ Create a bounding box.
    """
    m_grp = grp
    m_l_X = length_X
    m_l_Y = length_Y
    m_l_Z = length_Z
    m_o_X = ori_X
    m_o_Y = ori_Y
    m_o_Z = ori_Z
    global flag_for_face
    flag_for_face = True

    if info != 0:
        print_msg("Xmin, Ymin, Zmin : \n" +
        str(m_o_X) + " , " + str(m_o_Y) + " , " + str(m_o_Z))
        print_msg("Lengths m_l_X , m_l_Y , m_l_Z : \n" +
        str(m_l_X) + " , " + str(m_l_Y) + " , " + str(m_l_Z))
    
    if (m_l_X != 0.0) and (m_l_Y != 0.0):
        try:
            m_pl_0 = App.Placement(App.Vector(m_o_X,m_o_Y,m_o_Z),
                                App.Rotation(0.0,0.0,0.0))
            m_rect = Draft.makeRectangle(length=m_l_X,height=m_l_Y,
                                placement=m_pl_0,face=flag_for_face,support=None)
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()     
        except:
            printError_msg("Rectangle 0 not done !")
        try:
            m_pl_1 = App.Placement(App.Vector(m_o_X,m_o_Y,m_o_Z+m_l_Z),
                                App.Rotation(0.0,0.0,0.0))
            m_rect = Draft.makeRectangle(length=m_l_X,height=m_l_Y,
                                placement=m_pl_1,face=flag_for_face,support=None)                
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()        
        except:
            printError_msg("Rectangle 1 not done !")
            
    if (m_l_X != 0.0) and (m_l_Z != 0.0):
        try:
            m_pl_2 = App.Placement(App.Vector(m_o_X,m_o_Y,m_o_Z),
                                App.Rotation(0.0,0.0,90))
            m_rect = Draft.makeRectangle(length=m_l_X,height=m_l_Z,
                                placement=m_pl_2,face=flag_for_face,support=None)
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()          
        except:
            printError_msg("Rectangle 2 not done !")
        try:
            m_pl_3 = App.Placement(App.Vector(m_o_X,m_o_Y+m_l_Y,m_o_Z),
                                App.Rotation(0.0,0.0,90))
            m_rect = Draft.makeRectangle(length=m_l_X,height=m_l_Z,
                                placement=m_pl_3,face=flag_for_face,support=None)
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()       
        except:
            printError_msg("Rectangle 3 not done !")
            
    if (m_l_Y != 0.0) and (m_l_Z != 0.0):
        try:
            m_pl_4 = App.Placement(App.Vector(m_o_X,m_o_Y,m_o_Z),
                                App.Rotation(90,0.0,90))
            m_rect = Draft.makeRectangle(length=m_l_Y,height=m_l_Z,
                                placement=m_pl_4,face=flag_for_face,support=None)
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()         
        except:
            printError_msg("Rectangle 4 not done !")
        try:
            m_pl_5 = App.Placement(App.Vector(m_o_X+m_l_X,m_o_Y,m_o_Z),
                                App.Rotation(90,0.0,90))
            m_rect = Draft.makeRectangle(length=m_l_Y,height=m_l_Z,
                                placement=m_pl_5,face=flag_for_face,support=None)
            addObjectToGrp(m_rect,m_grp,info=info)
            definePropOfActiveObj()       
        except:
            printError_msg("Rectangle 5 not done !")
      
    #if (m_l_X != 0.0) and (m_l_Y != 0.0) and (m_l_Z != 0.0):
    try: 
        if (m_l_X == 0.0):
            m_l_X = 0.5
            m_o_X = m_o_X - 0.25
        if (m_l_Y == 0.0):
            m_l_Y = 0.5
            m_o_Y = m_o_Y - 0.25
        if (m_l_Z == 0.0):
            m_l_Z = 0.5
            m_o_Z = m_o_Z - 0.25
        m_pnt = App.Vector(m_o_X ,m_o_Y,m_o_Z)
        print_point(m_pnt, msg="m_pnt")
        # adds object to the document group
        box = App.ActiveDocument.addObject("Part::Feature", "BBox")
        #By default pnt=Vector(0,0,0) and dir=Vector(0,0,1) 
        Box_face = Part.makeBox(m_l_X,m_l_Y,m_l_Z,m_pnt)
        #print_msg("Box_face :" + str(Box_face) )            
        box.Shape = Box_face
        m_grp.addObject( box )
        Gui.activeDocument().activeObject().Transparency = (50)           
        print_msg("Bounding Box created !")
    except:
        printError_msg("Bounding Box not created !")
#==============================================================================

    
def plot_originObject():
    createFolders('Origin')
    try:    
        if not(App.ActiveDocument.getObject("Origin_Point")): 
            Line_Color = (1.00,0.33,0.00)
            Shape_Color =  (0.00,1.00,0.50)
            Transparency = 75
            # Origin
            Origin = Base.Vector(0, 0, 0)
            Origin_Vertex = Part.Vertex(Origin)
            Origin = App.ActiveDocument.addObject("Part::Feature","Origin_Point")
            App.ActiveDocument.getObject("Origin").addObject(Origin)
            Origin.Shape = Origin_Vertex
            Origin_User_Name = Origin.Label
            Gui.ActiveDocument.getObject(Origin_User_Name).PointColor = (0.33, 0.00, 1.00)
            Gui.ActiveDocument.getObject(Origin_User_Name).PointSize = 4.00
            Gui.ActiveDocument.getObject("Origin_Point").Visibility=False
            
            #Work-AxisX
            AX_Length = 300
            PX_A = Base.Vector(AX_Length, 0, 0)
            PX_B = Base.Vector(-AX_Length, 0, 0)
            Axis_X = Part.makeLine(PX_A, PX_B)
            Axis = App.ActiveDocument.addObject("Part::Feature","Ori_X_Axis")
            Axis.Shape = Axis_X
            App.ActiveDocument.getObject("Origin").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (1.00,0.00,0.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (1.00,0.00,0.00)
            Gui.ActiveDocument.getObject("Ori_X_Axis").Visibility=False
            
            #Work-AxisY
            AY_Length = 300
            PY_A = Base.Vector(0, AY_Length, 0)
            PY_B = Base.Vector(0, -AY_Length, 0)
            Axis_Y = Part.makeLine(PY_A, PY_B)
            Axis = App.ActiveDocument.addObject("Part::Feature","Ori_Y_Axis")
            Axis.Shape = Axis_Y
            App.ActiveDocument.getObject("Origin").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (0.00,0.67,0.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (0.00,0.67,0.00)
            Gui.ActiveDocument.getObject("Ori_Y_Axis").Visibility=False
            
            #Work-AxisZ
            AZ_Length = 300
            PZ_A = Base.Vector(0,0 , AZ_Length)
            PZ_B = Base.Vector(0, 0, -AZ_Length)
            Axis_Z = Part.makeLine(PZ_A, PZ_B)
            Axis = App.ActiveDocument.addObject("Part::Feature","Ori_Z_Axis")
            Axis.Shape = Axis_Z
            App.ActiveDocument.getObject("Origin").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor =  (0.33,0.00,1.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor =  (0.33,0.00,1.00)
            Gui.ActiveDocument.getObject("Ori_Z_Axis").Visibility=False
            
            # Work-PlaneXY
            PXY_A_SIZE = 300
            PXY_A = Base.Vector(PXY_A_SIZE, PXY_A_SIZE, 0)
            PXY_B = PXY_A + Base.Vector(-2.0*PXY_A_SIZE, 0, 0)
            PXY_C = PXY_A + Base.Vector(-2.0*PXY_A_SIZE, -2.0*PXY_A_SIZE, 0)
            PXY_D = PXY_A + Base.Vector(0, -2.0*PXY_A_SIZE, 0)
            PlaneXY_list = [PXY_A, PXY_B, PXY_C, PXY_D, PXY_A]
            PlaneXY_wire = Part.makePolygon(PlaneXY_list)
            PlaneXY_face = Part.Face(PlaneXY_wire)
            PlaneXY = App.ActiveDocument.addObject("Part::Feature", "XY_WPlane")
            PlaneXY.Shape = PlaneXY_face
            App.ActiveDocument.getObject("Origin").addObject(PlaneXY)
            PlaneXY_User_Name = PlaneXY.Label
            Gui.ActiveDocument.getObject(PlaneXY_User_Name).PointColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneXY_User_Name).LineColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneXY_User_Name).ShapeColor = Shape_Color
            Gui.ActiveDocument.getObject(PlaneXY_User_Name).Transparency = Transparency
            Gui.ActiveDocument.getObject("XY_WPlane").Visibility=False
            
            # Work-PlaneXY
            PXZ_A_SIZE = 300 
            PXZ_A = Base.Vector(PXZ_A_SIZE, 0, PXZ_A_SIZE)
            PXZ_B = PXZ_A + Base.Vector(-2.0*PXZ_A_SIZE, 0, 0)
            PXZ_C = PXZ_A + Base.Vector(-2.0*PXZ_A_SIZE, 0, -2.0*PXZ_A_SIZE)
            PXZ_D = PXZ_A + Base.Vector(0, 0, -2.0*PXZ_A_SIZE)
            PlaneXZ_list = [PXZ_A, PXZ_B, PXZ_C, PXZ_D, PXZ_A]
            PlaneXZ_wire = Part.makePolygon(PlaneXZ_list)
            PlaneXZ_face = Part.Face(PlaneXZ_wire)
            PlaneXZ = App.ActiveDocument.addObject("Part::Feature", "XZ_WPlane")
            PlaneXZ.Shape = PlaneXZ_face
            App.ActiveDocument.getObject("Origin").addObject(PlaneXZ)
            PlaneXZ_User_Name = PlaneXZ.Label
            Gui.ActiveDocument.getObject(PlaneXZ_User_Name).PointColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneXZ_User_Name).LineColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneXZ_User_Name).ShapeColor = Shape_Color
            Gui.ActiveDocument.getObject(PlaneXZ_User_Name).Transparency = Transparency
            Gui.ActiveDocument.getObject("XZ_WPlane").Visibility=False
            
            # Work-PlaneZY
            PYZ_A_SIZE = 300
            PYZ_A = Base.Vector(0, PYZ_A_SIZE, PYZ_A_SIZE)
            PYZ_B = PYZ_A + Base.Vector(0, -2.0*PYZ_A_SIZE, 0)
            PYZ_C = PYZ_A + Base.Vector(0, -2.0*PYZ_A_SIZE, -2.0*PYZ_A_SIZE)
            PYZ_D = PYZ_A + Base.Vector(0, 0, -2.0*PYZ_A_SIZE)
            PlaneYZ_list = [PYZ_A, PYZ_B, PYZ_C, PYZ_D, PYZ_A]
            PlaneYZ_wire = Part.makePolygon(PlaneYZ_list)
            PlaneYZ_face = Part.Face(PlaneYZ_wire)
            PlaneYZ = App.ActiveDocument.addObject("Part::Feature", "YZ_WPlane")
            PlaneYZ.Shape = PlaneYZ_face
            App.ActiveDocument.getObject("Origin").addObject(PlaneYZ)
            PlaneYZ_User_Name = PlaneYZ.Label
            Gui.ActiveDocument.getObject(PlaneYZ_User_Name).PointColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneYZ_User_Name).LineColor = Line_Color
            Gui.ActiveDocument.getObject(PlaneYZ_User_Name).ShapeColor = Shape_Color
            Gui.ActiveDocument.getObject(PlaneYZ_User_Name).Transparency = Transparency
            Gui.ActiveDocument.getObject("YZ_WPlane").Visibility=False
    except:
        printError_msg("Could not Create Origin objects !")   

def bBox_toggled(flag):
    """ Respond to the change of bounding box flag.
    """
    global centerOfMass
    centerOfMass = True
    if flag == True:
        centerOfMass = False
    
def plot_centerObjectPoint():
    """ Create a Point at center location of all selected Object(s).
    if flag centerOfMass=True
        This point is the MEAN location of all center of Mass (if exist) of all objects. 
    if flag centerOfMass=False
        This point is the center of the Global X,Y,Z bounding box of all objects.
        This bounding box alway exists (especially for draft objects).
        Be aware this point is not necessary the center of Mass of all Objects!
    """
    global centerOfMass
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Point of Object(s) : \nSelect at least one Object !"
    flag_centerOfMass=centerOfMass
    if flag_centerOfMass:
        result_msg = " : Mean of Center of Mass of Object(s) created !"
        name = "MeanCenterMass"
    else:
        result_msg = " : Center Point of global bounding box of Object(s) created !"
        name = "CenterBBObject"
    part = "Part::Feature"

    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
         
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_objNames = [selobj.ObjectName for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num >= 1:
        if msg != 0:            
            print_msg( str(m_num) + " object(s) selected :\n" + str(m_objNames) )
        if flag_centerOfMass:
            m_i = 0
            m_list = []
            m_c = None
            Center_User_Name = None
            for m_obj in m_objs:
                if msg != 0:
                    print_msg( "Processing : " + str(m_objNames[m_i]) )   
                try:
                    m_c = m_obj.Shape.CenterOfMass
                    if msg != 0:
                        print_msg( str(m_c) )
                                         
                    Center_User_Name = plot_point(m_c, part, name)
                    m_list.append(m_c)
                except:
                    printError_msg( str(m_objNames[m_i]) + "\nThis object has no attribute 'Center of Mass' !\nSelect another one !\n")
                    break
            if len(m_list) >=2:
                m_mean = meanVectorsPoint(m_list,info=msg)
                Center_User_Name = plot_point(m_mean, part, name)
                print_point(m_mean,str(Center_User_Name) + result_msg + " at :")
            else:
                print_point(m_c,str(Center_User_Name) + result_msg + " at :")
        else:
            Vector_Objects_Center = centerObjectsPoint(m_objs,info=msg)
            if Vector_Objects_Center != None:
                Center_User_Name = plot_point(Vector_Objects_Center, part, name)
                print_point(Vector_Objects_Center,str(Center_User_Name) + result_msg + " at :")
            else:
                printError_msg(error_msg)            
    else:
        printError_msg(error_msg)

            
def plot_NpointsPoint():
    """Create a Point at mean location of all selected points.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Point of Points : \nSelect at least 2 points !"
    result_msg = " : Center Point of Points created !"
    name = "CenterPoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection      
        Number_of_Points = SelectedObjects[0]
        if msg != 0:
            print_msg("Number_of_Points=" + str(Number_of_Points))
        points = []
        if Number_of_Points >= 2 :
            Point_List = SelectedObjects[3]
            for m_point in Point_List:
                points.append(m_point.Point)
                if msg != 0:
                    print_point(m_point.Point, msg="Point : ")
            Vector_Center = meanVectorsPoint(points,info=1)
            
            Center_User_Name = plot_point(Vector_Center, part, name)
            print_point(Vector_Center,str(Center_User_Name) + result_msg + " at :")                
    except:
        printError_msg(error_msg)

               
def plot_extremaLinePoint():
    """ Create Points at start and end location of each selected Line(s).
    """ 
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create First and Last Line Point(s) : \nSelect at least one Line !"
    result_msg = " : First and Last Line Point(s) created !"
    name = "extremumPoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:        
        SelectedObjects = Selection
        Number_of_Edges = SelectedObjects[1]        
        #print_msg("Number_of_Edges=" + str(Number_of_Edges))
        if Number_of_Edges >= 1:
            Edge_List = SelectedObjects[4]            
            for i in range( Number_of_Edges ):
                #print_msg(str(Edge_List[i]))
                edge = Edge_List[i]
                Vector_A = edge.valueAt( 0.0 )
                Vector_B = edge.valueAt( edge.Length )
                #print_point(Vector_A, msg="First Point : ")
                #print_point(Vector_B, msg="Last Point : ")
                
                Center_User_Name = plot_point(Vector_A, part, name)
                print_point(Vector_A,str(Center_User_Name) + result_msg + " at :")
                Center_User_Name = plot_point(Vector_B, part, name)
                print_point(Vector_B,str(Center_User_Name) + result_msg + " at :")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def numberLinePart(value):
    """ Respond to the change in extension value from the spin box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_numberLinePart
        if str(value) == '-':
            return
        m_numberLinePart  = int(value)
        print_msg("New number is :" + str(m_numberLinePart))
    except ValueError:
        printError_msg("Number must be valid !")     


def plot_centerLinePoint():
    """ Create a Point at mid point location of each selected Line(s).
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Mid Line Point(s) : \nSelect at least one Line !"
    result_msg = " : Mid Line Point(s) created !"
    name = "MidPoint"
    part = "Part::Feature"
    global m_numberLinePart
    if not (m_numberLinePart >= 2 and m_numberLinePart <= 10) :
        m_numberLinePart = 2
    Selection = get_SelectedObjects(info=msg, printError=False)    
    try:        
        SelectedObjects = Selection
        Number_of_Edges = SelectedObjects[1]        
        #print_msg("Number_of_Edges=" + str(Number_of_Edges))
        if Number_of_Edges >= 1:
            Edge_List = SelectedObjects[4]
            for i in range( Number_of_Edges ):
                if m_numberLinePart == 2:
                    #print_msg(str(Edge_List[i]))
                    Vector_Line_Center = centerLinePoint(Edge_List[i],info=1)
                    #print_point(Vector_Line_Center, msg="MidPoint : ")
                    
                    Center_User_Name = plot_point(Vector_Line_Center, part, name)
                    print_point(Vector_Line_Center,str(Center_User_Name) + result_msg + " at :")
                else:
                    for j in range( 1, m_numberLinePart ):
                        Vector_Line_Center = centerLinePoints(Edge_List[i], j , m_numberLinePart, info=1)
                        Center_User_Name = plot_point(Vector_Line_Center, part, name)
                        print_point(Vector_Line_Center,str(Center_User_Name) + result_msg + " at :")
                    pass
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)
        
        
def plot_centerLinePoint2():
    """ Create a Point at mid point location of each selected Line(s).
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Mid Line Point(s) : \nSelect at least one Line !"
    result_msg = " : Mid Line Point(s) created !"
    name = "MidPoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)    
    try:        
        SelectedObjects = Selection
        Number_of_Edges = SelectedObjects[1]        
        #print_msg("Number_of_Edges=" + str(Number_of_Edges))
        if Number_of_Edges >= 1:
            Edge_List = SelectedObjects[4]
            for i in range( Number_of_Edges ):
                #print_msg(str(Edge_List[i]))
                Vector_Line_Center = centerLinePoint(Edge_List[i],info=1)
                #print_point(Vector_Line_Center, msg="MidPoint : ")
                
                Center_User_Name = plot_point(Vector_Line_Center, part, name)
                print_point(Vector_Line_Center,str(Center_User_Name) + result_msg + " at :")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def distanceLinePoint(value):
    """ Respond to the change in distance value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_distanceLinePoint
        if str(value) == '-':
            return
        m_distanceLinePoint  = float(value)
        print_msg("New distance is :" + str(m_distanceLinePoint))
        #plot_alongLinePoint()
    except ValueError:
        printError_msg("Distance must be valid number !")


def plot_alongLinePoint():
    """ Plot a point at a certain distance along the line respecting to the choosen 
    reference starting point.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create a point along a Line : \nSelect one Edge and one Point only!"
    result_msg = " : Point along a Line created !"
    name = "PointLine"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)    
    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points) == 1 :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C = Point_List[0].Point
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            if msg != 0:
                print_point(Vector_C, msg="Reference Point : ")
                print_point(Vector_A, msg="Point A : ")
                print_point(Vector_B, msg="Point B : ")
            if colinearVectors(Vector_A, Vector_B, Vector_C, info=1):
                Vector_Translate = (Vector_B - Vector_A)
                #print_point(Vector_Translate, msg="Vector_Translate")
                Vector_Translate = Vector_Translate.normalize() * m_distanceLinePoint
                #print_point(Vector_Translate, msg="Vector_Translate")
                Vector_Line_Point = Vector_C + Vector_Translate
                
                Center_User_Name = plot_point(Vector_Line_Point, part, name)
                print_point(Vector_Line_Point,str(Center_User_Name) + result_msg + " at :")
            else:
                printError_msg("The Point and the line MUST be aligned !")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)

def plot_centerCirclePoint():
    """ Plot the center point of all selected Circles and Ellipses.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Circle Point(s) : \nSelect at least one Edge of Circle !"
    result_msg = " : Center Circle Point(s) created !"
    name = "CenterCircle"
    part = "Part::Feature"

    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None

    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_objNames = [selobj.ObjectName for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num >= 1:
        if msg != 0:            
            print_msg( str(m_num) + " object(s) selected :\n" + str(m_objNames) )
        m_i = 0
        for m_obj in m_objs:
            if msg != 0:
                print_msg( "Processing : " + str(m_objNames[m_i]) )
            
            try:
                m_c = m_obj.Shape.Curve.Center                                    
                Center_User_Name = plot_point(m_c, part, name)
                print_point(m_c,str(Center_User_Name) + result_msg + " at :")
            except AttributeError:
                SelectedObjects = get_SelectedObjects()
                Number_of_Edges = SelectedObjects[1]
                if Number_of_Edges >= 1:
                    Edge_List = SelectedObjects[4]
                    for i in range( Number_of_Edges ):
                        try:
                            Edge_List[i].Curve.Radius 
                            Vector_Circle_Center = centerCirclePoint(Edge_List[i],info=0)                                               
                            Center_User_Name = plot_point(Vector_Circle_Center, part, name)
                            print_point(Vector_Circle_Center,str(Center_User_Name) + result_msg + " at :")  
                        except:
                            printError_msg("Found One or More Non-Circular Edges")
                else:
                    printError_msg(error_msg)            
    
    else:
        printError_msg(error_msg)
             

def plot_centerFacePoint():
    """ Plot the center point of all selected Planes.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Face Point(s) : \nSelect at least one Plane surface !"
    result_msg = " : Center Face Point(s) created !"
    name = "CenterFace"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)     
    try:
        SelectedObjects = Selection
        Number_of_Planes = SelectedObjects[2]
        if Number_of_Planes >= 1:
            Plane_List = SelectedObjects[5]
            for i in range( Number_of_Planes ):
                try:
                    Selected_Plane = Plane_List[i]
                    Vector_Plane_Center = Selected_Plane.CenterOfMass
                    
                    Center_User_Name = plot_point(Vector_Plane_Center, part, name)
                    print_point(Vector_Plane_Center,str(Center_User_Name) + result_msg + " at :")
                except:
                    printError_msg("Non Planar Surface !")
        else:
            printError_msg(error_msg) 
    except:
        printError_msg(error_msg) 


def plot_lineFacePoint():
    """ Plot the intersection point between one Line and one plane.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create (Line,Face) Intersection : \nSelect one Line and one Plane surface !"
    result_msg = " : (Line,Face) Intersection created !"
    name = "LineFacePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg)
    try:        
        SelectedObjects = Selection
        Number_of_Edges  = SelectedObjects[1]
        Number_of_Planes = SelectedObjects[2]
        #print_msg("Number_of_Edges=" + str(Number_of_Edges) + " Number_of_Planes=" + str(Number_of_Planes))
        if (Number_of_Edges == 1) and (Number_of_Planes) == 1 :
            Edge_List  = SelectedObjects[4]
            Plane_List = SelectedObjects[5]
            #print_msg(str(Edge_List))
            #print_msg(str(Plane_List))
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            print_point(Vector_A, msg="Point A : ")
            print_point(Vector_B, msg="Point B : ")
            Reference_Plane = Plane_List[0]
            Plane_Normal = Reference_Plane.normalAt(0,0)
            print_msg("Plane_Normal is : " + str(Plane_Normal))            
            Plane_Point = Reference_Plane.CenterOfMass
            print_point(Plane_Point,"Plane_Point is : ")
            
            Vector_T = intersecLinePlane(Vector_A, Vector_B, Plane_Normal, Plane_Point, info=0)
            
            Center_User_Name = plot_point(Vector_T, part, name)
            print_point(Vector_T,str(Center_User_Name) + result_msg + " at :")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)

     
def plot_pointLinePoint():
    """ Plot the intersection point T on a Line given one Line and One Point C.
    The Vector TC is perpendicular to the line.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create (Point,Line) Intersection : \nSelect one Line and one Point not on the Line !"
    result_msg = " : (Point,Line) Intersection and symetric are created !"
    name = "PointLinePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg)
    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if (Number_of_Points == 1) and (Number_of_Edges == 1):
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            Vector_C = Point_List[0].Point
            
            Vector_T, Distance, Vector_Tprime = intersecPerpendicularLine(Vector_A, Vector_B, Vector_C, info=0)
            
            Center_User_Name = plot_point(Vector_T, part, name)
            print_point(Vector_T,str(Center_User_Name) + result_msg + " at :")
            Center_User_Name2 = plot_point(Vector_Tprime, part, name)
            print_point(Vector_Tprime,str(Center_User_Name2) + result_msg + " at :")
            
            print_msg(str(Center_User_Name) + result_msg + " at a distance from the line of " + str(Distance))
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_pointFacePoint():
    """ Plot the intersection point T on a Plane given one Plane and One Point C.
    The Vector TC is perpendicular to the plane.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create (Point,Face) Intersection : \nSelect one Face and one Point not on the Face !"
    result_msg = " : (Point,Face) Intersection and symetric are created !"
    name = "PointFacePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg)
    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Planes = SelectedObjects[2]
        #print_msg(" Number_of_Points=" + str(Number_of_Points))
        #print_msg(" Number_of_Planes=" + str(Number_of_Planes))
        if (Number_of_Points == 1) and (Number_of_Planes == 1):
            Point_List = SelectedObjects[3]
            Plane_List = SelectedObjects[5]
            
            Selected_Plane = Plane_List[0]
            Vector_C = Point_List[0].Point
            
            Plane_Point = Selected_Plane.CenterOfMass
            Plane_Normal = Selected_Plane.normalAt(0,0)
            
            Vector_B = Vector_C + Plane_Normal
            
            Vector_T = intersecLinePlane(Vector_C, Vector_B, Plane_Normal, Plane_Point, info=0)
            
            Center_User_Name = plot_point(Vector_T, part, name)
            print_point(Vector_T,str(Center_User_Name) + result_msg + " at :")
            
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_2LinesPoint():
    """ Plot one or two Point(s) at minimum distance of two Lines. 
    """ 
    msg=0   
    createFolders('WorkPoints')
    error_msg = "Unable to create (Line,Line) Intersection(s) : \nSelect two Lines !"
    result_msg = " : (Line,Line) Intersection(s) are created !"
    name = "Intersection"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg)
    try:        
        SelectedObjects = Selection
        Number_of_Edges  = SelectedObjects[1]
        if Number_of_Edges == 2:
            Edge_List  = SelectedObjects[4]
            f1 = Edge_List[0]
            f2 = Edge_List[1]
            #print_msg(str(f1))
            #print_msg(str(f2))
            d = f1.distToShape(f2)
            #print_msg(str(d))
            Distance = d[0]
            Vector_A = d[1][0][0]
            #print_point(Vector_A,"Vector_A is : ")
            Vector_B = d[1][0][1]
            if abs(Distance) <= 1.e-14: 
                Center_User_Name = plot_point(Vector_A, part, name)
                print_msg(str(Center_User_Name) + result_msg ) 
            else:
                Center_User_Name = plot_point(Vector_A, part, name)
                print_point(Vector_A,str(Center_User_Name) + result_msg + " at :")
                Center_User_Name = plot_point(Vector_B, part, name)
                print_point(Vector_B,str(Center_User_Name) + result_msg + " at :")
                print_msg(str(Center_User_Name) + result_msg + " at a distance of " + str(Distance))
        else:
            printError_msg(error_msg)
        
    except:
        printError_msg(error_msg)


def plot_clickForPoint():
    """ Plot a Point at location of a mouse click. 
    """
    createFolders('WorkPoints')
    global m_callback
    #print_msg("plot_clickForPoint" )
    #view = Gui.ActiveDocument.ActiveView
    view = get_ActiveView()
    #m_callback = view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),getClickedPoint)
    m_callback = view.addEventCallback("SoMouseButtonEvent",getClickedPoint2)


def plot_baseObjectPoint():
    """ Plot base point of all selected objects.
    """
    msg=0
    createFolders('WorkPoints')
    error_msg = "Unable to create Base point of Object(s): \nSelect at least one Object !"
    result_msg = " : Base point of Object(s) created !"
    name = "BasePoint"
    part = "Part::Feature"
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
    
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num >= 1:
        for m_i in range(0,m_num): 
            m_base = m_objs[m_i].Placement.Base
            if m_base != None:
                Center_User_Name = plot_point(m_base, part, name)
                print_point(m_base,str(Center_User_Name) + result_msg + " at :")
    else:
        printError_msg(error_msg)        


def plot_centerObjectAxes():
    """ Create 3 Axes XY, and Z at center point of all selected objects.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Axes : \nSelect at least one object !"
    result_msg = " : Axes created !"

    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num < 1:
        printError_msg(error_msg)
        return
    Center = centerObjectsPoint(m_objs)
    if Center != None:
        xmax, xmin, ymax, ymin, zmax, zmin = minMaxObjectsLimits(m_objs)
        #Work-AxisX
        if xmax != xmin:
            AX_Length = (xmax - xmin)*1.3
        else:
            AX_Length = 10.
        PX_A = Base.Vector(AX_Length, 0, 0)
        PX_B = Base.Vector(-AX_Length, 0, 0)
        Axis_X = Part.makeLine(Center+PX_A, Center+PX_B)             
        Axis = App.ActiveDocument.addObject("Part::Feature","X_Axis")
        Axis.Shape = Axis_X
        App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
        Axis_User_Name = Axis.Label
        Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (1.00,0.00,0.00)
        Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (1.00,0.00,0.00)
        Gui.ActiveDocument.getObject("X_Axis").Visibility=True
        print_msg(str(Axis_User_Name) + result_msg )
        #Work-AxisY
        if ymax != ymin:
            AY_Length = (ymax - ymin)*1.3
        else:
            AY_Length = 10.
        PY_A = Base.Vector(0, AY_Length, 0)
        PY_B = Base.Vector(0, -AY_Length, 0)
        Axis_Y = Part.makeLine(Center+PY_A, Center+PY_B)
        Axis = App.ActiveDocument.addObject("Part::Feature","Y_Axis")
        Axis.Shape = Axis_Y
        App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
        Axis_User_Name = Axis.Label
        Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (0.00,0.67,0.00)
        Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (0.00,0.67,0.00)
        Gui.ActiveDocument.getObject("Y_Axis").Visibility=True
        print_msg(str(Axis_User_Name) + result_msg )
        #Work-AxisZ
        if zmax != zmin:
            AZ_Length = (zmax - zmin)*1.3
        else:
            AZ_Length = 10.
        PZ_A = Base.Vector(0,0 , AZ_Length)
        PZ_B = Base.Vector(0, 0, -AZ_Length)
        Axis_Z = Part.makeLine(Center+PZ_A, Center+PZ_B)
        Axis = App.ActiveDocument.addObject("Part::Feature","Z_Axis")
        Axis.Shape = Axis_Z
        App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
        Axis_User_Name = Axis.Label
        Gui.ActiveDocument.getObject(Axis_User_Name).LineColor =  (0.33,0.00,1.00)
        Gui.ActiveDocument.getObject(Axis_User_Name).PointColor =  (0.33,0.00,1.00)
        Gui.ActiveDocument.getObject("Z_Axis").Visibility=True
        print_msg(str(Axis_User_Name) + result_msg )
    else:
        printError_msg(error_msg)


def extensionTwoPointsAxis(value):
    """ Respond to the change in extension value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_extensionTwoPointsAxis
        if str(value) == '-':
            return
        m_extensionTwoPointsAxis  = float(value)
        print_msg("New extension is :" + str(m_extensionTwoPointsAxis))
    except ValueError:
        printError_msg("Extension must be valid number !")    


def plot_2PointsAxis():
    """ Create an Axis with the 2 points selected as ends.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis : \nSelect two points only !"
    result_msg = " : Axis created !"
    name = "Line from 2 Points"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False) 
    try:
        SelectedObjects = Selection        
        Number_of_Points = SelectedObjects[0]
        #print_msg(" Number_of_Points=" + str(Number_of_Points))
        if Number_of_Points == 2:
            Point_List = SelectedObjects[3]
            #print_msg(str(Point_List))
            Axis_A = Point_List[0].Point
            Axis_B = Point_List[1].Point
            Axis_dir = Axis_B - Axis_A
            Axis_E1 = Axis_B            
            Axis_E2 = Axis_A

            if m_extensionTwoPointsAxis != 0.0:
                Axis_E1 = Axis_B +  Axis_dir.normalize().multiply(m_extensionTwoPointsAxis)
                if m_extensionTwoPointsAxis >= 0.0:            
                    Axis_E2 = Axis_A -  Axis_dir.normalize().multiply(m_extensionTwoPointsAxis)
                else:
                    Axis_E2 = Axis_A +  Axis_dir.normalize().multiply(m_extensionTwoPointsAxis)
            
            Axis_User_Name, axis = plot_axis(Axis_E1, Axis_E2, part, name)

            print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)

        
def plot_cylinderAxis():
    msg=1
    createFolders('WorkAxis')
    error_msg = "Unable to create Cylinder Axis : \nSelect one cylindrical face only !"
    result_msg = " : Cylinder Axis created !"
    name = "Cylinder Axis"
    part = "Part::Feature"
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    Selection = get_SelectedObjects(info=msg, printError=False) 
    try:
        SelectedObjects = Selection
        Number_of_Faces = SelectedObjects[2]
        Number_of_Edges = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Faces=" + str(Number_of_Faces))
            print_msg("Number_of_Edges=" + str(Number_of_Edges))
        if Number_of_Faces == 1:
            Face_list = SelectedObjects[5]
            Face = Face_list[0]
            Face_Wire = Face.OuterWire
            Face_Edges = Face_Wire.Edges
            try:
                Circle_Center_1 = None
                Circle_Center_2 = None
                for i in range(len(Face_Edges)):
                    Current_Edge = Face_Edges[i]
                    Edge_Info = Current_Edge.Curve
                    Edge_Type_Name = str(Edge_Info)
                    #print_msg("Edge_Type_Name = " + str(Edge_Type_Name))
                    Edge_Circle = Edge_Type_Name[0:6]
                    Edge_Line = Edge_Type_Name[1:5]
                    if Edge_Circle == "Circle":
                        Circle_Axis = Current_Edge.Curve.Axis
                        Circle_Axis = Circle_Axis.normalize()
                        if Circle_Center_1 == None:
                            Circle_Center_1 = Current_Edge.Curve.Center
                            #Circle_Radius_1 = Current_Edge.Curve.Radius
                        else:
                            Circle_Center_2 = Current_Edge.Curve.Center
                            #Circle_Radius_2 = Current_Edge.Curve.Radius
                    if Edge_Line == "Line":
                        Line_Start = Current_Edge.Curve.StartPoint
                        Line_End = Current_Edge.Curve.EndPoint
                        Edge_Length = ( Line_End - Line_Start ).Length
            except:
                printError_msg("Not valid cylinder !")
            #print_msg("Circle_Center_1 = " + str(Circle_Center_1))
            #print_msg("Circle_Center_2 = " + str(Circle_Center_2))                       
            Axis_A = Circle_Center_1
            Axis_B = Circle_Center_2
            Axis_dir = Axis_B - Axis_A
            Axis_E1 = Axis_B + Axis_dir.multiply(0.1)
            Axis_E2 = Axis_A - Axis_dir.multiply(0.9)
            
            Axis_User_Name, axis = plot_axis(Axis_E1, Axis_E2, part, name)
                      
            print_msg(str(Axis_User_Name) + result_msg )
        elif Number_of_Edges >= 1:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
            m_objs = [selobj.Object for selobj in m_selEx]
            for m_obj in m_objs:
#==============================================================================
#            look for sketch
#                 if hasattr(m_obj, 'TypeId'):
#                     m_type = m_obj.TypeId
#                 else:
#                     m_type = m_obj.Type
#                 if msg != 0:
#                     print_msg("m_obj.Type   : " + str(m_obj.Type))
#==============================================================================
                    
                if hasattr(m_obj.Shape.Curve, 'Radius'):
                    print_msg('Radius')
                    m_r = m_obj.Shape.Curve.Radius 
                if hasattr(m_obj.Shape.Curve, 'MajorRadius'):
                    print_msg('MajorRadius')
                    m_r = m_obj.Shape.Curve.MajorRadius
                m_a = m_obj.Shape.Curve.Axis
                m_c = m_obj.Shape.Curve.Center                    
                if m_r :
                    m_mult = m_r * 0.5
                else:
                    m_mult = 5
                Center_User_Name = plot_point(m_c, part, name)
                Axis_User_Name, axis = plot_axis(m_c, m_c + m_a.multiply(m_mult), part, name)
                Axis_User_Name, axis = plot_axis(m_c, m_c - m_a, part, name)

                print_msg(str(Axis_User_Name) + result_msg )             
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)
        
        
def plot_2LinesAxis():
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis between 2 Lines : \nSelect two lines only !"
    result_msg = " : Axis between 2 Lines created !"
    name = "MidLine"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Edges  = SelectedObjects[1]
        #print_msg("Number_of_Edges=" + str(Number_of_Edges))
        if (Number_of_Edges == 2):
            Edge_List  = SelectedObjects[4]
            #print_msg(str(Edge_List))
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            #print_point(Vector_A, msg="Point A : ")
            #print_point(Vector_B, msg="Point B : ")
            
            Vector_C = Edge_List[1].valueAt( 0.0 )
            Vector_D = Edge_List[1].valueAt( Edge_List[1].Length )
            #print_point(Vector_C, msg="Point C : ")
            #print_point(Vector_D, msg="Point D : ")
            
            Vector_edge_1 = Vector_A + Vector_C
            Vector_edge_2 = Vector_B + Vector_D
            
            Axis_E1 = Vector_edge_1.multiply(0.5)
            Axis_E2 = Vector_edge_2.multiply(0.5)
                        
            Axis_User_Name, axis = plot_axis(Axis_E1, Axis_E2, part, name)

            print_msg(str(Axis_User_Name) + result_msg )
    except:
        printError_msg(error_msg)


def plot_planeAxis():
    """ Plot 2 Axis perpendicular to a Plane and passing trougth center.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Plane Axis : \nSelect at least one plane face !"
    result_msg = " : Plane Axis created !"
    name = "Axis"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Planes = SelectedObjects[2]
        #print_msg(" Number_of_Planes=" + str(Number_of_Planes))
        if (Number_of_Planes) >= 1 :
            Plane_List = SelectedObjects[5]
            for i in range( Number_of_Planes ):
                try:
                    Selected_Plane = Plane_List[i]
                    #print_msg(str(Selected_Plane))
                    Point_A = Selected_Plane.CenterOfMass
                    Length = Selected_Plane.Length * 0.1                    
                    #print_point(Point_A, msg="Point_A : ")
                    #print_msg("Length = " + str(Length))
                    Normal = Selected_Plane.normalAt(0,0)
                    Normal = Normal.normalize().multiply(Length)
                    #print_point(Normal, msg="Normal : ")
                    Point_B = App.Vector(Point_A) + Normal
                    Point_Bprime = App.Vector(Point_A) - Normal                                                           
                    #Point_B = Point_B.normalize().multiply(Length)
                    
                    Axis_User_Name, axis = plot_axis(Point_B, Point_A, part, name)
                    print_msg(str(Axis_User_Name) + result_msg )
                    Axis_User_Name, axis = plot_axis(Point_Bprime, Point_A, part, name)
                    print_msg(str(Axis_User_Name) + result_msg )
                except:
                    printError_msg("Non Planar Surface !")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)  
        

def extensionFaceNormal(value):
    """ Respond to the change in extension value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_extensionFaceNormal
        if str(value) == '-':
            return
        m_extensionFaceNormal  = float(value)
        print_msg("New extension is :" + str(m_extensionFaceNormal))
    except ValueError:
        printError_msg("Extension must be valid number !")
        

def plot_faceNormal():
    """Create a normal Axis at click location of a Face.
    """
    global m_callback
    view = Gui.ActiveDocument.ActiveView
    m_callback = view.addEventCallback("SoMouseButtonEvent",getClickedNormal)
    
    
def extensionLinePointAxis(value):
    """ Respond to the change in extension value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_extensionLinePointAxis
        if str(value) == '-':
            return
        m_extensionLinePointAxis  = float(value)
        print_msg("New extension is :" + str(m_extensionLinePointAxis))
    except ValueError:
        printError_msg("Extension must be valid number !")
        

def plot_linePointAxis():
    """ Plot an Axis perpendicular to an other axis and passing trougth a Point.
    """ 
    msg=0   
    createFolders('WorkAxis')
    error_msg = "Unable to create Perpendicular Axis : \nSelect one Point and one Line only !"
    result_msg = " : Perpendicular Axis created !"
    name = "Perpendicular Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points) == 1 :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C      = Point_List[0].Point
            Vector_A      = Edge_List[0].valueAt( 0.0 )
            Vector_B      = Edge_List[0].valueAt( Edge_List[0].Length )
            
            Vector_T, Distance, Vector_Tprime = intersecPerpendicularLine(Vector_A, Vector_B, Vector_C, info=msg)
            
            print_msg("Distance from the Point to the Axis is : " + str(Distance) )
            
            Axis_dir = Vector_C - Vector_T
            Axis_E1 = Vector_C            
            Axis_E2 = Vector_T
            
            if m_extensionLinePointAxis != 0.0:
                Axis_E1 = Vector_C +  Axis_dir.normalize().multiply(m_extensionLinePointAxis)
                if m_extensionLinePointAxis >= 0.0:            
                    Axis_E2 = Vector_T -  Axis_dir.normalize().multiply(m_extensionLinePointAxis)
                else:
                    Axis_E2 = Vector_T +  Axis_dir.normalize().multiply(m_extensionLinePointAxis)
            
            Axis_User_Name, axis = plot_axis(Axis_E1, Axis_E2, part, name)

            print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg) 
    except:
        printError_msg(error_msg)
    
    
def plot_pointLineAxis():
    """ Plot an Axis paralell to an other axis and passing trougth a Point.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Parallel Axis : \nSelect one Point and one Line only !"
    result_msg = " : Paralell Axis created !"
    name = "Parallel Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        #print_msg("Number_of_Edges=" + str(Number_of_Edges) + " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points) == 1 :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            #print_msg(str(Point_List))
            #print_msg(str(Edge_List))
            Vector_Cprime = Point_List[0].Point
            Vector_A      = Edge_List[0].valueAt( 0.0 )
            Vector_B      = Edge_List[0].valueAt( Edge_List[0].Length )
            Vector_C      = centerLinePoint(Edge_List[0],info=1)
            Vector_Translate = (Vector_Cprime - Vector_C)
            Vector_Aprime = Vector_A + Vector_Translate
            Vector_Bprime = Vector_B + Vector_Translate
            
            Axis_User_Name, axis = plot_axis(Vector_Aprime, Vector_Bprime, part, name)

            print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg) 
    except:
        printError_msg(error_msg)


def plot_linePlaneAxis():
    """ Plot an Axis on a Plane by projection from another Axis.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create projection Axis onto a Plane : \nSelect one Plane and one Line !"
    result_msg = " : Projection Axis onto a Plane created !"
    name = "Line"
    part = "Part::Feature"    
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Edges = SelectedObjects[1]
        Number_of_Planes = SelectedObjects[2]
        #print_msg("Number_of_Edges=" + str(Number_of_Edges) + " Number_of_Planes=" + str(Number_of_Planes))
        if Number_of_Planes == 1 and Number_of_Edges == 1:
            Edge_List = SelectedObjects[4]
            Plane_List = SelectedObjects[5]
            Point_A = Edge_List[0].valueAt(0.0)
            Point_B = Edge_List[0].valueAt(Edge_List[0].Length)
            #print_point(Point_A, msg="Point_A : ")
            #print_point(Point_B, msg="Point_B : ")
            Selected_Plane = Plane_List[0]
            Plane_Point = Selected_Plane.CenterOfMass
            Plane_Normal = Selected_Plane.normalAt(0,0)
            # Projection of A and B onto the Plane Aprime and Bprime
            Vector_A = Point_A + Plane_Normal
            Vector_B = Point_B + Plane_Normal
            
            Point_Aprime = intersecLinePlane(Point_A, Vector_A, Plane_Normal, Plane_Point, info=0)
            Point_Bprime = intersecLinePlane(Point_B, Vector_B, Plane_Normal, Plane_Point, info=0)
            # Plot them
            plot_point(Point_Aprime, part, "PointFacePoint")
            plot_point(Point_Bprime, part, "PointFacePoint")
            Axis_User_Name, axis = plot_axis(Point_Aprime, Point_Bprime, part, name)
            
            print_msg(str(Axis_User_Name) + result_msg )
        else: 
            printError_msg(error_msg) 
    except:
        printError_msg(error_msg)
        

def plot_clickForAxis():
    """ Plot an axis at location of 2 mouse clicks.. 
    """
    global m_callback
    #print_msg("plot_clickForAxis" )
    view = Gui.ActiveDocument.ActiveView
    m_callback = view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),getClickedAxis)

    
def plot_2PlanesAxis():
    """ Plot the intersection Axis between two planes.
    """
    msg=0
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis between 2 Planes : \nSelect two Planes not parallel !"
    result_msg = " : Axis between 2 Planes created !"
    name = "Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=0)
    m_xmax, m_xmin, m_ymax, m_ymin, m_zmax, m_zmin = minMaxObjectsLimits(m_objs,info=0)
    try:
        SelectedObjects = Selection
        Number_of_Planes = SelectedObjects[2]
        #print_msg("Number_of_Planes=" + str(Number_of_Planes))
        if (Number_of_Planes) >= 2 :
            Plane_List = SelectedObjects[5]
            Selected_Plane1 = Plane_List[0]
            Selected_Plane2 = Plane_List[1]
            #print_msg(str(Selected_Plane1))
            #print_msg(str(Selected_Plane2))
            Plane_Normal1 = Selected_Plane1.normalAt(0,0)
            Plane_Normal2 = Selected_Plane2.normalAt(0,0)
            #print_point(Plane_Normal1, msg="Normal1 : ")
            #print_point(Plane_Normal2, msg="Normal2 : ")
            Plane_Point1  = Selected_Plane1.CenterOfMass
            Plane_Point2  = Selected_Plane2.CenterOfMass
            #print_point(Plane_Point1 , msg="Plane_Point1 : ")
            #print_point(Plane_Point2 , msg="Plane_Point2 : ")
            
            Axis_dir = intersecPlanePlane(Plane_Normal1, Plane_Point1, Plane_Normal2, Plane_Point2, info=0)
            #print_point(Axis_dir , msg="Axis_dir : ")

            # Intersection Line found
            if Axis_dir != None:
                #print_msg("Selected_Plane1=" + str(Selected_Plane1))
                #print_msg("Selected_Plane1.Edges=" + str(Selected_Plane1.Edges))
                Number_of_Edges = len(Selected_Plane1.Edges)
                #print_msg("Number_of_Edges=" + str(Number_of_Edges))
                Vertx = []
                Vertx.append(App.Vector(0.0, 0.0, 0.0))
                Vertx.append(App.Vector(0.0, 0.0, 0.0))
                
                min_val, max_val = init_min_max()
                dist_to_center_min = max_val
                # For the first plane look after all edges and look at 
                # intersections of the edges with the second plane
                for j in range(Number_of_Edges):
                    A = Selected_Plane1.Edges[j].valueAt( 0.0 )
                    B = Selected_Plane1.Edges[j].valueAt(Selected_Plane1.Edges[j].Length )
                    #print_point(A , msg="A : ")
                    #print_point(B , msg="B : ")
                    T = intersecLinePlane(A, B, Plane_Normal2, Plane_Point2, info=0)                    
                    if T != None:
                        print_point(T , msg="T : ")
                        D = T - Plane_Point1                       
                        dist_to_center = math.sqrt(D.dot(D))                        
                        #print_msg("D=" + str(D))
                        #print_msg("dist_to_center=" + str(dist_to_center))
                        if dist_to_center < dist_to_center_min:
                            dist_to_center_min = dist_to_center
                            Vertx[0] = T                            
                #Center_User_Name = plot_point(Vertx[0], part, name)
                #print_msg("Selected_Plane2=" + str(Selected_Plane2))
                #print_msg("Selected_Plane2.Edges=" + str(Selected_Plane2.Edges))
                Number_of_Edges = len(Selected_Plane2.Edges)
                #print_msg("Number_of_Edges=" + str(Number_of_Edges))
                dist_to_center_min = max_val
                for j in range(Number_of_Edges):
                    A = Selected_Plane2.Edges[j].valueAt( 0.0 )
                    B = Selected_Plane2.Edges[j].valueAt(Selected_Plane2.Edges[j].Length )
                    #print_point(A , msg="A : ")
                    #print_point(B , msg="B : ")
                    T = intersecLinePlane(A, B, Plane_Normal1, Plane_Point1, info=0)
                    if T != None:
                        #print_point(T , msg="T : ")
                        D = T - Plane_Point2
                        dist_to_center = math.sqrt(D.dot(D))
                        #print_msg("D=" + str(D))
                        #print_msg("dist_to_center=" + str(dist_to_center))
                        if dist_to_center < dist_to_center_min:
                            dist_to_center_min = dist_to_center
                            Vertx[1] = T  

                #Center_User_Name = plot_point(Vertx[1], part, name)
                #print_msg("Selected_Points=" + str(Vertx))
                #Number_of_Points = len(Vertx)
                #print_msg("Number_of_Points=" + str(Number_of_Points))    
                #C = centerBBVectorsPoint(Vertx,info=0)
                C = meanVectorsPoint(Vertx,info=1)
                #print_point(C , msg="C : ")

                if C != None:
                    extension = m_xmax - m_xmin
                    if extension < m_ymax - m_ymin:
                        extension = m_ymax - m_ymin                        
                    if extension < m_zmax - m_zmin:
                        extension = m_zmax - m_zmin
                    extension = extension/2
                    A = C -  Axis_dir.normalize().multiply(extension*1.3)
                    B = C +  Axis_dir
                    Axis_User_Name, axis = plot_axis(A, B, part, name)
                    print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
        
    except:
        printError_msg(error_msg) 

    
def plot_baseObjectAxes():
    msg=0
    createFolders('Origin')
    error_msg = "Unable to create Axes : \nSelect at least one object !"
    result_msg = " : Axes created !"

    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num < 1:
        printError_msg(error_msg)
        return
    CommonCenter = centerObjectsPoint(m_objs,info=1)
    for m_i in range(0,m_num): 
        m_base = m_objs[m_i].Placement.Base
        print_msg("Base  =" + str(m_base))
        print_msg("Center=" + str(CommonCenter))
        if m_base != None:
            xmax, xmin, ymax, ymin, zmax, zmin = minMaxObjectsLimits(m_objs)
            #Work-AxisX
            if xmax != xmin:
                AX_Length = (xmax - xmin)*1.3
            else:
                AX_Length = 10.
            PX_A = Base.Vector(AX_Length, 0, 0)
            PX_B = Base.Vector(-AX_Length, 0, 0)
            Axis_X = Part.makeLine(m_base+PX_A, m_base+PX_B)             
            Axis = App.ActiveDocument.addObject("Part::Feature","X_Axis")
            Axis.Shape = Axis_X
            App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (1.00,0.00,0.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (1.00,0.00,0.00)
            Gui.ActiveDocument.getObject("X_Axis").Visibility=True
            print_msg(str(Axis_User_Name) + result_msg )
            #Work-AxisY
            if ymax != ymin:
                AY_Length = (ymax - ymin)*1.3
            else:
                AY_Length = 10.
            PY_A = Base.Vector(0, AY_Length, 0)
            PY_B = Base.Vector(0, -AY_Length, 0)
            Axis_Y = Part.makeLine(m_base+PY_A, m_base+PY_B)
            Axis = App.ActiveDocument.addObject("Part::Feature","Y_Axis")
            Axis.Shape = Axis_Y
            App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor = (0.00,0.67,0.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor = (0.00,0.67,0.00)
            Gui.ActiveDocument.getObject("Y_Axis").Visibility=True
            print_msg(str(Axis_User_Name) + result_msg )
            #Work-AxisZ
            if zmax != zmin:
                AZ_Length = (zmax - zmin)*1.3
            else:
                AZ_Length = 10.
            PZ_A = Base.Vector(0,0 , AZ_Length)
            PZ_B = Base.Vector(0, 0, -AZ_Length)
            Axis_Z = Part.makeLine(m_base+PZ_A, m_base+PZ_B)
            Axis = App.ActiveDocument.addObject("Part::Feature","Z_Axis")
            Axis.Shape = Axis_Z
            App.ActiveDocument.getObject("WorkAxis").addObject(Axis)
            Axis_User_Name = Axis.Label
            Gui.ActiveDocument.getObject(Axis_User_Name).LineColor =  (0.33,0.00,1.00)
            Gui.ActiveDocument.getObject(Axis_User_Name).PointColor =  (0.33,0.00,1.00)
            Gui.ActiveDocument.getObject("Z_Axis").Visibility=True
            print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg)


def radiusCircle(value):
    """ Respond to the change in radius value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_radiusCircle
        if str(value) == '-':
            return
        m_radiusCircle  = float(value)
        print_msg("New extension is :" + str(m_radiusCircle))
    except ValueError:
        printError_msg("Extension must be valid number !")


def plot_linecenterCircle():
    """Select an Axis and a Point to create a Circle
    centered on the Point, perpendicular to the Axis 
    with the given radius.
    """
    msg=0
    global m_radiusCircle
    createFolders('WorkCircles')
    error_msg = "Unable to create a Circle : \nSelect one Edge and one Point only!"
    result_msg = " : Circle centered on a Point created !"
    name = "Circle"
    part = "Part::Feature"
    grp = "WorkCircles"
    Selection = get_SelectedObjects(info=msg, printError=False)

    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points) == 1 :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C = Point_List[0].Point
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            Vector_dir = (Vector_B - Vector_A)

            Circle_User_Name, circle = plot_circle(m_radiusCircle, Vector_C, Vector_dir, part, name, grp)
            print_msg(str(Circle_User_Name) + result_msg )
        else:
            printError_msg(error_msg)    
    except:
        printError_msg(error_msg)


def plot_linepointCircle():
    """Select an Axis and a Point to create a Circle
    centered on the Axis and tangenting the Point.
    """
    msg=0
    createFolders('WorkCircles')
    error_msg = "Unable to create a Circle : \nSelect one Edge and one Point only!"
    result_msg = " : Circle tangented to a Point created !"
    name = "Circle"
    part = "Part::Feature"
    grp = "WorkCircles"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points) == 1 :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C   = Point_List[0].Point
            Vector_A   = Edge_List[0].valueAt( 0.0 )
            Vector_B   = Edge_List[0].valueAt( Edge_List[0].Length )
            Vector_dir = (Vector_B - Vector_A)
            
            Vector_T, Distance, Vector_Tprime = intersecPerpendicularLine(Vector_A, Vector_B, Vector_C, info=msg)
            
            Circle_User_Name, circle = plot_circle(Distance, Vector_T, Vector_dir, part, name, grp)
            print_msg(str(Circle_User_Name) + result_msg )
            
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_3pointsCircle():
    """Select 3 Points  to create a Circle.
    """
    msg=0
    createFolders('WorkCircles')
    error_msg = "Unable to create a Circle : \nSelect 3 Points only!"
    result_msg = " : Circle from 3 points created !"
    name = "Circle"
    part = "Part::Feature"
    grp = "WorkCircles"
    Selection = get_SelectedObjects(info=msg, printError=False)    
    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        if Number_of_Points == 3:
            Point_List = SelectedObjects[3]

            P1 = Point_List[0].Point
            P2 = Point_List[1].Point
            P3 = Point_List[2].Point
                            
            l = ((P1 - P2).cross(P2 - P3)).Length
                           
            P1P2 = (P2 - P1).Length
            P2P3 = (P3 - P2).Length
            P3P1 = (P1 - P3).Length                 
            r=0.0
            try:
                # Circle radius.
                r = P1P2 * P2P3 * P3P1 / 2 / l
            except:
                printError_msg("The three points are aligned !")
            else:
                # Normal
                Vector1 = P2 - P1
                Vector2 = P3 - P1
                V_Normal = Vector1.cross( Vector2 )        
                # Sphere center.
                a = P2P3**2 * (P1 - P2).dot(P1 - P3) / 2 / l**2
                b = P3P1**2 * (P2 - P1).dot(P2 - P3) / 2 / l**2
                c = P1P2**2 * (P3 - P1).dot(P3 - P2) / 2 / l**2
                P1.multiply(a)
                P2.multiply(b)
                P3.multiply(c)
                Center = P1 + P2 + P3
             
                Circle_User_Name, circle = plot_circle(r, Center, V_Normal, part, name, grp )
                print_msg(str(Circle_User_Name) + result_msg + "radius = " + str(r))
        else:
            printError_msg(error_msg)   
    except:
        printError_msg(error_msg)

    
def plot_3pointsEllipse():
    """Select a center and 2 Points to create an Ellipse.
    """
    msg=0
    createFolders('WorkCircles')
    error_msg = "Unable to create a Ellipse : \nSelect one Center and 2 Points only!"
    result_msg = " : Ellipse from 3 points created !"
    name = "Ellipse"
    part = "Part::Feature"
    grp = "WorkCircles"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:        
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        if (Number_of_Points == 3):
            Point_List = SelectedObjects[3]
            if msg != 0:
                print_msg(str(Point_List))
            P1 = Point_List[0].Point
            Center = P1
            P2 = Point_List[1].Point
            P3 = Point_List[2].Point
            if msg != 0:
                print_point(Center,"Center = :")
                print_point(P2,"P2 = :")
                print_point(P3,"P3 = :")    

            Ellipse_User_Name, ellipse = plot_ellipse(P2, P3, Center, part, name, grp)
            print_msg(str(Ellipse_User_Name) + result_msg )
        else:
            printError_msg(error_msg)      
    except:
        printError_msg(error_msg)
    
  
def plot_3PointsPlane():
    """ Create a Plane from 3 Points.
    """
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect three points only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False) 
    try:
        SelectedObjects = Selection      
        Number_of_Points = SelectedObjects[0]
        if msg != 0:
            print_msg("Number_of_Points=" + str(Number_of_Points))
        points = []
        if Number_of_Points == 3 :
            Point_List = SelectedObjects[3]
            if msg != 0:
                print_msg(str(Points_List))
                
            Point_A = Point_List[0].Point
            points.append(Point_A)
            Point_B = Point_List[1].Point
            points.append(Point_B)
            Point_C = Point_List[2].Point
            points.append(Point_C)
            if msg != 0:
                print_point(Point_A, msg="Point_A : ")
                print_point(Point_B, msg="Point_B : ")
                print_point(Point_C, msg="Point_C : ")
            
            Vector_Center = meanVectorsPoint(points,info=msg)
            #Vector_Center = centerBBVectorsPoint(points, info=0)
            xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(points,info=0)
            #print_point(Vector_Center, msg="Center of A, B and C : ")
  
            length = xmax - xmin
            if (ymax - ymin) > length:
                length = ymax - ymin
            if (zmax - zmin) > length:
                length = zmax - zmin
            print_msg("length = " +str(length))
            
            Edge_Vector = Point_B - Point_A
            #Edge_Length = Edge_Vector.Length
            Edge_Length = length * 1.5
            AC_Vector = Point_C - Point_A
            Plane_Point = Vector_Center
            Plane_Normal = Edge_Vector.cross( AC_Vector )
            
            Plane_User_Name, plane = plot_plane(Edge_Length, Edge_Length, Plane_Point, Plane_Normal, part, name)
            print_msg(str(Plane_User_Name) + result_msg )
    except:
        printError_msg(error_msg)

 
def plot_axisPointPlane():
    """ Create a plane passing trougth a Line and a Point.
    """
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Line and one Point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False) 
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges = SelectedObjects[1]
        #print_msg("Number_of_Points=" + str(Number_of_Points) + " Number_of_Edges=" + str(Number_of_Edges))
        points = []
        if (Number_of_Points == 1) and (Number_of_Edges == 1):
            Points_List = SelectedObjects[3]
            Edge_List = SelectedObjects[4]
            #print_msg(str(Points_List))
            #print_msg(str(Edge_List))
            Point_C = Points_List[0].Point
            points.append(Point_C)
            Point_A = Edge_List[0].valueAt(0.0)
            points.append(Point_A)
            Point_B = Edge_List[0].valueAt(Edge_List[0].Length)
            points.append(Point_B)
            #print_point(Point_A, msg="Point_A : ")
            #print_point(Point_B, msg="Point_B : ")
            #print_point(Point_C, msg="Point_C : ")
            
            #Vector_Center = centerBBVectorsPoint(points, info=0)
            Vector_Center = meanVectorsPoint(points,info=0)
            xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(points,info=0)
            #print_point(Vector_Center, msg="Center of A, B and C : ")
            
            length = xmax - xmin
            if (ymax - ymin) > length:
                length = ymax - ymin
            if (zmax - zmin) > length:
                length = zmax - zmin
            print_msg("length = " +str(length))
            
            Edge_Vector = Point_B - Point_A
            Edge_Length = length * 1.5
            AC_Vector = Point_C - Point_A
            Plane_Point = Vector_Center
            Plane_Normal = Edge_Vector.cross( AC_Vector )
                        
            Plane_User_Name, plane = plot_plane(Edge_Length, Edge_Length, Plane_Point, Plane_Normal, part, name)
            print_msg(str(Plane_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_perpendicularAxisPointPlane():
    """ Create a Plane perpendicular to a Line a crossing a Point.
    """    
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Line and one point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection      
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges = SelectedObjects[1]
        #print_msg("Number_of_Points=" + str(Number_of_Points) + " Number_of_Edges=" + str(Number_of_Edges))
        if (Number_of_Points == 1) and (Number_of_Edges == 1):
            Point_List = SelectedObjects[3]
            Edge_List = SelectedObjects[4]
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            Vector_C = Point_List[0].Point
            #print_point(Vector_A, msg="Vector_A : ")
            #print_point(Vector_B, msg="Vector_B : ")
            #print_point(Vector_C, msg="Vector_C : ")
            # Intersection point T on a Line given one Line and One Point C.
            if colinearVectors(Vector_A, Vector_B, Vector_C, info=1): 
                Vector_T = Vector_C
                Distance = Edge_List[0].Length
            else:
                Vector_T, Distance, Vector_Tprime = intersecPerpendicularLine(Vector_A, Vector_B, Vector_C, info=0)
            #print_point(Vector_T, msg="Intersection point T : ")
            Plane_Normal = Vector_B - Vector_A
            Plane_Point = Vector_T +  (Vector_C - Vector_T).multiply(0.5)
            Edge_Length = Distance * 1.5
            
            Plane_User_Name, plane = plot_plane(Edge_Length, Edge_Length, Plane_Point, Plane_Normal, part, name)
            print_msg(str(Plane_User_Name) + result_msg )
    except: 
        printError_msg(error_msg)
    
    
def extensionPlanePointPlane(value):
    """ Respond to the change in extension value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_extensionPlanePointPlane
        if str(value) == '-':
            return
        m_extensionPlanePointPlane  = float(value)
        print_msg("New extension is :" + str(m_extensionPlanePointPlane))
    except ValueError:
        printError_msg("Extension must be valid number !")
        
        
def plot_planePointPlane():
    """ Create a plane passing through a Point and parallel to a given Plane.
    """    
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Plane and one Point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Planes = SelectedObjects[2]
        #print_msg("Number_of_Points=" + str(Number_of_Points) + " Number_of_Planes=" + str(Number_of_Planes))
        if Number_of_Points == 1 and Number_of_Planes == 1:
            Points_List = SelectedObjects[3]
            Plane_List = SelectedObjects[5]
            #print_msg(str(Points_List))
            #print_msg(str(Plane_List))      
            Point_C = Points_List[0].Point
            Reference_Plane = Plane_List[0]
            Edge_Length = Reference_Plane.Length / 4.0 + m_extensionPlanePointPlane
            Plane_Normal = Reference_Plane.normalAt(0,0)
            Plane_Point = Point_C
            
            Plane_User_Name, plane = plot_plane(Edge_Length, Edge_Length, Plane_Point, Plane_Normal, part, name)
            print_msg(str(Plane_User_Name) + result_msg )
        else:
            printError_msg(error_msg) 
    except:
        printError_msg(error_msg)        


def anglePlaneAxisPlane(value):
    """ Respond to the change in angle value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_anglePlaneAxisPlane
        if str(value) == '-':
            return
        m_anglePlaneAxisPlane  = float(value)
        print_msg("New angle in degrees is :" + str(m_anglePlaneAxisPlane))
    except ValueError:
        printError_msg("Angle must be valid number !")


def plot_planeAxisPlane():
    """ Use a plane and a line to create Plane perpedicular 
    to the first Plane and crossing the Line
    """
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Planes : \nSelect one Line and one Plane only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=msg, printError=False)
    try:
        SelectedObjects = Selection
        #Number_of_Points = SelectedObjects[0]
        Number_of_Edges = SelectedObjects[1]
        Number_of_Planes = SelectedObjects[2]
        #print_msg("Number_of_Points=" + str(Number_of_Points))
        #print_msg("Number_of_Edges=" + str(Number_of_Edges) + " Number_of_Planes=" + str(Number_of_Planes))
        if Number_of_Planes == 1 and Number_of_Edges == 1:
            Edge_List = SelectedObjects[4]
            Plane_List = SelectedObjects[5]
            Point_A = Edge_List[0].valueAt(0.0)
            Point_B = Edge_List[0].valueAt(Edge_List[0].Length)
            #print_point(Point_A, msg="Point_A : ")
            #print_point(Point_B, msg="Point_B : ")
            Selected_Plane = Plane_List[0]
            Plane_Point = Selected_Plane.CenterOfMass
            Plane_Normal = Selected_Plane.normalAt(0,0)
            # Projection of A and B onto the Plane Aprime and Bprime
            Vector_A = Point_A + Plane_Normal
            Vector_B = Point_B + Plane_Normal
            
            Point_Aprime = intersecLinePlane(Point_A, Vector_A, Plane_Normal, Plane_Point, info=0)
            Point_Bprime = intersecLinePlane(Point_B, Vector_B, Plane_Normal, Plane_Point, info=0)
            # Plot them
            #plot_point(Point_Aprime, part, "PointFacePoint")
            #plot_point(Point_Bprime, part, "PointFacePoint")
            #plot_axis(Point_Aprime, Point_Bprime, part, "Line from 2 Points")
            
            Edge_Vector = Point_Bprime - Point_Aprime
            Edge_Length = Edge_List[0].Length * 1.3
            
            Point_MidPoint = Point_Bprime + Point_Aprime
            Point_MidPoint = Point_MidPoint.multiply(0.5)           
                                   
            Vector_Normal = Edge_Vector.cross(Plane_Normal)
        
            Plane_User_Name, plane = plot_plane(Edge_Length, Edge_Length, Point_MidPoint, Vector_Normal, part, name)
            
            print_msg("New plane is :" + str(plane))
            if m_anglePlaneAxisPlane != 0.0:
                rot_angle = m_anglePlaneAxisPlane
                rot_axis = Edge_Vector
                m_center = Point_MidPoint
                m_rot = App.Rotation(rot_axis,rot_angle)
                print_msg("rotation  =       " + str(m_rot))
                print_msg("rotation axis   = " + str(rot_axis))
                m_place = App.Placement(plane.Placement)
                m_base1 = m_place.Base                
                print_msg("base1   = " + str(m_base1))
                m_rot1 = m_place.Rotation
                print_msg("rot1   = " + str(m_rot1))
                m_rot = m_rot.multiply(m_rot1)
                m_newplace = App.Placement(m_base1,m_rot,m_center-m_base1)
                plane.Placement = m_newplace
                
            print_msg(str(Plane_User_Name) + result_msg )
        else: 
            printError_msg(error_msg)         
    except:
        printError_msg(error_msg)


def lengthPlane(value):
    """ Respond to the change in Plane length value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_lengthPlane
        if str(value) == '-':
            return
        m_lengthPlane  = float(value)
        print_msg("New Plane length is :" + str(m_lengthPlane))
    except ValueError:
        printError_msg("Plane length must be valid number !")


def widthPlane(value):
    """ Respond to the change in Plane length value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_widthPlane
        if str(value) == '-':
            return
        m_widthPlane  = float(value)
        print_msg("New Plane length is :" + str(m_widthPlane))
    except ValueError:
        printError_msg("Plane length must be valid number !")


def plot_faceTangentPlane():
    """Create a tanget Plane at click location of a Face.
    """
    global m_callback
    view = Gui.ActiveDocument.ActiveView
    m_callback = view.addEventCallback("SoMouseButtonEvent",getClickedTangent)

    
def plot_clickForPlane():
    """ Create a Plane at location of one mouse click in the view or 
    onto a clicked object or
    at a pre-selected point location.
    """
    msg=0
    createFolders('WorkPlanes')
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    if len(m_selEx) >= 1:
        SelectedObjects = get_SelectedObjects(info=1)
        Number_of_Points = SelectedObjects[0]
        if (Number_of_Points == 1) :
            Point_List = SelectedObjects[3]
            name = "Plane"
            part = "Part::Feature"
            # return view direction as a vector
            Plane_Normal = Gui.ActiveDocument.ActiveView.getViewDirection()
            # Set the base of the plane at location of mouse click
            Plane_Point = Point_List[-1].Point
            # Create a Plane
            Plane_User_Name, plane = plot_plane(m_lengthPlane, m_widthPlane, Plane_Point, Plane_Normal, part, name)            
        else:
            printError_msg("Either select first one Point and Click the button or \n" +
              "Click the button and one free mouse click in the view or" +
              "Click the button and one mouse click on an object of the view !")    
    else:
        global m_callback        
        #view = Gui.ActiveDocument.ActiveView
        view = get_ActiveView()
        #m_callback = view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),getClickedPlane)
        m_callback = view.addEventCallback("SoMouseButtonEvent",getClickedPlane2)

        
def plot_centerObjectPlanes():
    """ Create 3 Planes XY, YZ and XZ at center point of all selected objects.
    """
    msg=0
    createFolders('WorkPlanes')
    error_msg = "Unable to create Planes : \nSelect at least one objec !"
    result_msg = " : Planes created !"

    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    Line_Color = (1.00,0.33,0.00)
    Shape_Color =  (0.00,1.00,0.50)
    Transparency = 75          
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num < 1:
        printError_msg(error_msg)
        return
    Center = centerObjectsPoint(m_objs)
    if Center != None:
        xmax, xmin, ymax, ymin, zmax, zmin = minMaxObjectsLimits(m_objs, info=1)
        
        # Work-PlaneXY
        if xmax != xmin:
            PXY_A_SIZE = (xmax - xmin)*1.3
        else:
            PXY_A_SIZE = 10.
        if PXY_A_SIZE < (ymax - ymin)*1.3:
            PXY_A_SIZE = (ymax - ymin)*1.3
        PXY_A = Center + Base.Vector(PXY_A_SIZE, PXY_A_SIZE, 0)
        PXY_B = PXY_A + Base.Vector(-2.0*PXY_A_SIZE, 0, 0)
        PXY_C = PXY_A + Base.Vector(-2.0*PXY_A_SIZE, -2.0*PXY_A_SIZE, 0)
        PXY_D = PXY_A + Base.Vector(0, -2.0*PXY_A_SIZE, 0)
        PlaneXY_list = [PXY_A, PXY_B, PXY_C, PXY_D, PXY_A]
        PlaneXY_wire = Part.makePolygon(PlaneXY_list)
        PlaneXY_face = Part.Face(PlaneXY_wire)
        PlaneXY = App.ActiveDocument.addObject("Part::Feature", "XY_WPlane")
        PlaneXY.Shape = PlaneXY_face
        App.ActiveDocument.getObject("WorkPlanes").addObject(PlaneXY)
        PlaneXY_User_Name = PlaneXY.Label
        Gui.ActiveDocument.getObject(PlaneXY_User_Name).PointColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneXY_User_Name).LineColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneXY_User_Name).ShapeColor = Shape_Color
        Gui.ActiveDocument.getObject(PlaneXY_User_Name).Transparency = Transparency
        Gui.ActiveDocument.getObject(PlaneXY_User_Name).Visibility=True
        #Gui.ActiveDocument.getObject("XY_WPlane").Visibility=True
        print_msg(str(PlaneXY_User_Name) + result_msg )
        # Work-PlaneXZ
        if xmax != xmin:
            PXZ_A_SIZE = (xmax - xmin)*1.3
        else:
            PXZ_A_SIZE = 10.
        if PXZ_A_SIZE < (zmax - zmin)*1.3:
            PXZ_A_SIZE = (zmax - zmin)*1.3
        PXZ_A = Center + Base.Vector(PXZ_A_SIZE, 0, PXZ_A_SIZE)
        PXZ_B = PXZ_A + Base.Vector(-2.0*PXZ_A_SIZE, 0, 0)
        PXZ_C = PXZ_A + Base.Vector(-2.0*PXZ_A_SIZE, 0, -2.0*PXZ_A_SIZE)
        PXZ_D = PXZ_A + Base.Vector(0, 0, -2.0*PXZ_A_SIZE)
        PlaneXZ_list = [PXZ_A, PXZ_B, PXZ_C, PXZ_D, PXZ_A]
        PlaneXZ_wire = Part.makePolygon(PlaneXZ_list)
        PlaneXZ_face = Part.Face(PlaneXZ_wire)
        PlaneXZ = App.ActiveDocument.addObject("Part::Feature", "XZ_WPlane")
        PlaneXZ.Shape = PlaneXZ_face
        App.ActiveDocument.getObject("WorkPlanes").addObject(PlaneXZ)
        PlaneXZ_User_Name = PlaneXZ.Label
        Gui.ActiveDocument.getObject(PlaneXZ_User_Name).PointColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneXZ_User_Name).LineColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneXZ_User_Name).ShapeColor = Shape_Color
        Gui.ActiveDocument.getObject(PlaneXZ_User_Name).Transparency = Transparency
        Gui.ActiveDocument.getObject(PlaneXZ_User_Name).Visibility=True
        #Gui.ActiveDocument.getObject("XZ_WPlane").Visibility=True
        print_msg(str(PlaneXZ_User_Name) + result_msg )
        # Work-PlaneZY
        if zmax != zmin:
            PYZ_A_SIZE = (zmax - zmin)*1.3
        else:
            PYZ_A_SIZE = 10
        if PYZ_A_SIZE < (ymax - ymin)*1.3:
            PYZ_A_SIZE = (ymax - ymin)*1.3
        PYZ_A = Center + Base.Vector(0, PYZ_A_SIZE, PYZ_A_SIZE)
        PYZ_B = PYZ_A + Base.Vector(0, -2.0*PYZ_A_SIZE, 0)
        PYZ_C = PYZ_A + Base.Vector(0, -2.0*PYZ_A_SIZE, -2.0*PYZ_A_SIZE)
        PYZ_D = PYZ_A + Base.Vector(0, 0, -2.0*PYZ_A_SIZE)
        PlaneYZ_list = [PYZ_A, PYZ_B, PYZ_C, PYZ_D, PYZ_A]
        PlaneYZ_wire = Part.makePolygon(PlaneYZ_list)
        PlaneYZ_face = Part.Face(PlaneYZ_wire)
        PlaneYZ = App.ActiveDocument.addObject("Part::Feature", "YZ_WPlane")
        PlaneYZ.Shape = PlaneYZ_face
        App.ActiveDocument.getObject("WorkPlanes").addObject(PlaneYZ)
        PlaneYZ_User_Name = PlaneYZ.Label
        Gui.ActiveDocument.getObject(PlaneYZ_User_Name).PointColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneYZ_User_Name).LineColor = Line_Color
        Gui.ActiveDocument.getObject(PlaneYZ_User_Name).ShapeColor = Shape_Color
        Gui.ActiveDocument.getObject(PlaneYZ_User_Name).Transparency = Transparency
        Gui.ActiveDocument.getObject(PlaneYZ_User_Name).Visibility=True
        #Gui.ActiveDocument.getObject("YZ_WPlane").Visibility=True
        print_msg(str(PlaneYZ_User_Name) + result_msg )   
    else:
        printError_msg(error_msg)


def get_all_from_bounding_box(ori_X,ori_Y,ori_Z,length_X,length_Y,length_Z,info=0,plot=0):
    """ Returns 8 points ,12 edges and 6 planes from the bounding box
    """
    m_l_X = length_X
    m_l_Y = length_Y
    m_l_Z = length_Z
    m_o_X = ori_X
    m_o_Y = ori_Y
    m_o_Z = ori_Z
    Points = []
    Edges = []
    Faces = []
    
    Points.append(App.Vector(m_o_X,m_o_Y      ,m_o_Z            ))
    Points.append(App.Vector(m_o_X,m_o_Y+m_l_Y,m_o_Z            ))
    Points.append(App.Vector(m_o_X,m_o_Y      ,m_o_Z+m_l_Z      ))
    Points.append(App.Vector(m_o_X,m_o_Y+m_l_Y,m_o_Z+m_l_Z      ))
    
    Points.append(App.Vector(m_o_X+m_l_X,m_o_Y      ,m_o_Z      ))
    Points.append(App.Vector(m_o_X+m_l_X,m_o_Y+m_l_Y,m_o_Z      ))
    Points.append(App.Vector(m_o_X+m_l_X,m_o_Y      ,m_o_Z+m_l_Z))
    Points.append(App.Vector(m_o_X+m_l_X,m_o_Y+m_l_Y,m_o_Z+m_l_Z))
    
    m_list_of_edges = [ ( 0, 1), ( 1, 3), ( 3, 2), ( 2, 0),
                ( 4, 5), ( 5, 7), ( 7, 6), ( 6, 4),
                ( 0, 4), ( 1, 5), ( 3, 7), ( 2, 6) ]

    for i in m_list_of_edges:
        if info != 0:
            print_msg( str(i) )
        line = Part.Line(Points[i[0]], Points[i[1]])
        edge = line.toShape()
        wire = Part.Wire([edge])
        if info != 0:
            Part.show(wire)
        mid_point = wire.CenterOfMass
        length = wire.Length
        Edges.append( ( i[0], i[1], (Points[i[0]], Points[i[1]]), edge, mid_point, length ) )

    m_list_of_faces = [ (2, 11, 6, 10),
                        (0,  8, 4,  9),
                        (3,  8, 7, 11),
                        (1,  9, 5, 10),
                        (7,  4, 5,  6),
                        (3,  0,  1, 2) ]
                
    for i in m_list_of_faces:
        if info != 0:
            print_msg( str(i) )
        wire = Part.Wire([Edges[i[0]][3], Edges[i[1]][3], Edges[i[2]][3], Edges[i[3]][3] ])
        if wire.isClosed():
            face = Part.Face(wire)
            mid_point = face.CenterOfMass
            length = face.Length
            if info != 0:
                Part.show(face)
            Faces.append( ( i[0], i[1], i[2], i[3], (Edges[i[0]][3],Edges[i[1]][3],Edges[i[2]][3],Edges[i[3]][3]), face, mid_point, length ) ) 
     
    # Print info if needed               
    if info != 0:
        for m_i in range(len(Points)):
            print_point(Points[m_i], msg="Point_" + str(m_i) + " : ")
        for m_i in range(len(Edges)):
            print_msg("segment : " + str(Edges[m_i]))
        for m_i in range(len(Faces)):
            print_msg("face : " + str(Faces[m_i]))

    # Plot them if needed
    if plot != 0:
        for m_i in range(len(Points)):
            plot_point(Points[m_i], "Part::Feature", "point")
        for m_i in range(len(Edges)):
            #( 2, 6, (Points[2], Points[6]), edge, mid_point, length )
            plot_axis(Edges[m_i][2][0], Edges[m_i][2][1], "Part::Feature", "axis")
        #for m_i in range(len(Faces)):
            # ( 3,  0,  1, 2, (Edges[3][3],Edges[0][3],Edges[1][3],Edges[2][3]), face, mid_point, length )
            #print_msg("face : " + str(Faces[m_i])) 
    
    return Points, Edges, Faces

  
def plot_boundingBoxes():
    """Create bounding boxes around each of selected object(s).
    """
    msg=0
    createFolders('WorkBoxes')
    error_msg  = "Select at least one object !"
    result_msg = "Bounding box created !"
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    # Return a list of SelectionObjects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_objNames = [selobj.ObjectName for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num >= 1:
        if msg != 0:            
            print_msg( str(m_num) + " object(s) selected :\n" + str(m_objNames) )
        m_i = 0
        for m_obj in m_objs:
            m_dir=str(m_objNames[m_i])+"_BBox"
            if msg != 0:
                print_msg( "Processing : " + str(m_objNames[m_i]) )
            # Create a group
            try:
                App.ActiveDocument.getObject("WorkBoxes").newObject("App::DocumentObjectGroup", str(m_dir))
            except:
                printError_msg("Could not Create '"+ str(m_dir) +"' Objects Group!")
                return None
            m_grp=m_actDoc.getObject( str(m_dir) )
            # Create a solid out of the shells of a shape
            try:
              m_s = m_obj.Shape
            except:
              printError_msg( "This object has no attribute 'Shape' !\nSelect another one !\n")
              break
            # Get a boundBox A bounding box is an orthographic cube which is a way to describe outer boundaries
            m_boundBox = m_s.BoundBox
            if msg != 0:
                print_msg("BoundBox([Xmin,Ymin,Zmin,Xmax,Ymax,Zmax])\n" + str(m_boundBox))
            # Length of BoundBox in X, Y and Z dimensions
            m_length_X = m_boundBox.XLength
            m_length_Y = m_boundBox.YLength
            m_length_Z = m_boundBox.ZLength
            m_ori_X = m_boundBox.XMin
            m_ori_Y = m_boundBox.YMin
            m_ori_Z = m_boundBox.ZMin

            bounding_box(m_grp,m_ori_X,m_ori_Y,m_ori_Z,m_length_X,m_length_Y,m_length_Z,info=msg)

            m_actDoc.recompute()
            m_i = m_i +1
            
        print_msg(result_msg)
    else:
        printError_msg(error_msg)


def plot_boundingBox():
    """ Create one bounding box around all of selected object(s).
    """
    msg=0
    createFolders('WorkBoxes')
    error_msg  = "Select at least one object !"
    result_msg = "Bounding box created !"
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc == None:
        return
        
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=msg)
    Center = centerObjectsPoint(m_objs)
    if Center != None:
        m_dir=str("BoundingBox")
        # Create a group
        try:
            m_obj = App.ActiveDocument.getObject("WorkBoxes").newObject("App::DocumentObjectGroup", str(m_dir))
        except:
            printError_msg("Could not Create '"+ str(m_dir) +"' Objects Group!")
        m_grp = m_actDoc.getObject( m_obj.Name )
        #print_msg("m_grp = " + str(m_grp)) 
        m_xmax, m_xmin, m_ymax, m_ymin, m_zmax, m_zmin = minMaxObjectsLimits(m_objs,info=0) 
        # Length of BoundBox in X, Y and Z dimensions
        m_length_X = m_xmax - m_xmin
        m_length_Y = m_ymax - m_ymin
        m_length_Z = m_zmax - m_zmin
        m_ori_X = m_xmin
        m_ori_Y = m_ymin
        m_ori_Z = m_zmin
        bounding_box(m_grp,m_ori_X,m_ori_Y,m_ori_Z,m_length_X,m_length_Y,m_length_Z,info=msg)
        m_actDoc.recompute()
        print_msg(result_msg)
        
    else:
        printError_msg(error_msg)   

    
def diameterCylinder(value):
    """ Respond to the change in diameter value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_diameterCylinder
        if str(value) == '-':
            return
        m_diameterCylinder  = float(value)
        print_msg("New diameter is :" + str(m_diameterCylinder))
    except ValueError:
        printError_msg("Diameter must be valid number !")


def lengthCylinder(value):
    """ Respond to the change in length value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_lengthCylinder
        if str(value) == '-':
            return
        m_lengthCylinder  = float(value)
        print_msg("New diameter is :" + str(m_lengthCylinder))
    except ValueError:
        printError_msg("Diameter must be valid number !")


def plot_axisPointCylinder():
    """ Plot a cylinder with axis aligned on the selected axis and with center at the
    selected point.
    """
    msg=0
    createFolders('WorkObjects')
    error_msg = "Unable to create a Cylinder : \nSelect one Axis and one point only!"  
    result_msg = " : Cylinder created !"
    name = "Cylinder"
    part = "Part::Feature"    
    global m_diameterCylinder
    global m_lengthCylinder
      
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    Selection = get_SelectedObjects(info=msg, printError=False)
    if Selection == None:
        return None
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points == 1) :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C = Point_List[0].Point
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            if msg != 0:
                print_point(Vector_C, msg="Reference Point : ")
                print_point(Vector_A, msg="Point A : ")
                print_point(Vector_B, msg="Point B : ")
            
            Cyl_User_Name, cylinder = plot_cylinder(m_diameterCylinder, m_lengthCylinder, Vector_C, Vector_A - Vector_B, part, name)
            print_msg(str(Cyl_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)

  
def sectionCube(value):
    """ Respond to the change in lenght,width value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        print_msg(str(value))
        global m_lengthCube
        global m_widthCube
        values = value.split(',')
        m_lengthCube  = abs(float(values[0]))
        m_widthCube  = abs(float(values[1]))
        print_msg("New lenght,width are :" + str(m_lengthCube) + ", "  + str(m_widthCube))
    except ValueError:
        printError_msg("Lenght,width must be valid number !")


def heightCube(value):
    """ Respond to the change in heigth value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_heightCube
        if str(value) == '-':
            return
        m_heightCube  = float(value)
        print_msg("New height is :" + str(m_heightCube ))
    except ValueError:
        printError_msg("Height must be valid number !")
        
        
def plot_axisPointCube():
    """ Plot a cube with axis aligned on the selected axis and with center at the
    selected point.
    """
    msg=0
    createFolders('WorkObjects')
    error_msg = "Unable to create a Cube : \nSelect one Axis and one point only!"  
    result_msg = " : Cube created !"
    name = "Cuboid"
    part = "Part::Feature"    
    global m_lengthCube
    global m_widthCube
    global m_heightCube
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        return None
        
    Selection = get_SelectedObjects(info=msg, printError=False)
    if Selection == None:
        return None
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        Number_of_Edges  = SelectedObjects[1]
        if msg != 0:
            print_msg("Number_of_Edges=" + str(Number_of_Edges) +
                      " Number_of_Points=" + str(Number_of_Points))
        if (Number_of_Edges == 1) and (Number_of_Points == 1) :
            Point_List = SelectedObjects[3]
            Edge_List  = SelectedObjects[4]
            if msg != 0:
                print_msg(str(Point_List))
                print_msg(str(Edge_List))
            Vector_C = Point_List[0].Point
            Vector_A = Edge_List[0].valueAt( 0.0 )
            Vector_B = Edge_List[0].valueAt( Edge_List[0].Length )
            if msg != 0:
                print_point(Vector_C, msg="Reference Point : ")
                print_point(Vector_A, msg="Point A : ")
                print_point(Vector_B, msg="Point B : ")     
            
            Cube_User_Name, cube = plot_cube(m_lengthCube, m_widthCube, m_heightCube, Vector_C, Vector_A - Vector_B, part, name)
            print_msg(str(Cube_User_Name) + result_msg )    
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)    

        
def angleCutObject(value):
    """ Respond to the change in angle value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_angleCutObject
        if str(value) == '-':
            return
        m_angleCutObject  = float(value)
        print_msg("New angle in degrees is :" + str(m_angleCutObject))
    except ValueError:
        printError_msg("Angle must be valid number !")


def thicknessCutObject(value):
    """ Respond to the change in extension value from the text box.
    """        
    try:
        # First we check if a valid number have been entered
        global m_thicknessCutObject
        if str(value) == '-':
            return
        m_thicknessCutObject  = float(value)
        print_msg("New thickness is :" + str(m_thicknessCutObject))
    except ValueError:
        printError_msg("Thickness must be valid number !") 


def cut_selectObject():
    """ Select the Object to cut.    
    """
    global myDialog
    global m_cut_selectObjects
    msg=0
    error_msg = "Select in order:\n"+ \
                "First, one Object to cut and click 'Select Object' button,\n"+ \
                "Second, one cutting Line and click 'Select Cut Line' button,\n"+ \
                "Last, a reference Plane and click 'Select Ref. Plane' button!" 
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=msg, printError=False)
    if m_num == 1:
        m_cut_selectObjects.append([m_selEx, m_objs, m_objNames])
        m_text=str(m_objNames[0])
        myDialog.ui.info_cut_select_object.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8))        
 
    else:
        printError_msg(error_msg)
        return
        
    # Activate the button_cut_select_line
    myDialog.ui.button_cut_select_line.setEnabled(True) 


def cut_selectLine():
    """ Select the Line to cut the Object along.
    """
    global myDialog
    global m_cut_selectObjects
    msg=0
    error_msg = "Select in order:\n"+ \
                "First, one Object to cut and click 'Select Object' button,\n"+ \
                "Second, one cutting Line and click 'Select Cut Line' button,\n"+ \
                "Last, a reference Plane and click 'Select Ref. Plane' button!"   
    # TODO : check if really a line     
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=msg, printError=False)
    if m_num == 1:
        m_cut_selectObjects.append([m_selEx, m_objs, m_objNames])        
        m_text=str(m_objNames[0]) 
        myDialog.ui.info_cut_select_axis.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8)) 
     
    else:
        printError_msg(error_msg)
        return
        
    # Activate the button_cut_select_plane
    myDialog.ui.button_cut_select_plane.setEnabled(True) 
    

def cut_selectPlane():
    """ Select the reference Plane to cut the Object from.
    """  
    global myDialog
    global m_cut_selectObjects
    msg=0
    error_msg = "Select in order:\n"+ \
                "First, one Object to cut and click 'Select Object' button,\n"+ \
                "Second, one cutting Line and click 'Select Cut Line' button,\n"+ \
                "Last, a reference Plane and click 'Select Ref. Plane' button!" 
    # TODO : check if really a plane   
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=msg, printError=False)
    if m_num == 1:
        m_cut_selectObjects.append([m_selEx, m_objs, m_objNames])    
        m_text=str(m_objNames[0])
        myDialog.ui.info_cut_select_plane.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8)) 
    else:
        printError_msg(error_msg)
        return
        
    # Activate the button_cut_apply
    myDialog.ui.button_cut_apply.setEnabled(True) 


def cut_reset():
    """ Select the reference Plane to cut the Object from.
    """  
    global myDialog
    global m_cut_selectObjects
    del m_cut_selectObjects[:]
    m_text=""

    # deActivate the button_cut_select_line
    myDialog.ui.button_cut_select_line.setEnabled(False) 
    # deActivate the button_cut_select_plane
    myDialog.ui.button_cut_select_plane.setEnabled(False)         
    # deActivate the button_cut_apply
    myDialog.ui.button_cut_apply.setEnabled(False)
    myDialog.ui.info_cut_select_object.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8))
    myDialog.ui.info_cut_select_axis.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8))
    myDialog.ui.info_cut_select_plane.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8))   

    
def plot_cutObject():
    """ Cut an object in 2 pieces, based on a cut line, a plane, 
    an angle regarding this plane and a thickness of the line.
    """ 
    global myDialog
    global m_cut_selectObjects
    global m_angleCutObject
    global m_thicknessCutObject
    global verbose
    msg=verbose
    createFolders('WorkObjects')
    error_msg = "Select in order:\n"+ \
                "First, one Object to cut and click 'Select Object' button,\n"+ \
                "Second, one cutting Line and click 'Select Cut Line' button,\n"+ \
                "Last, a reference Plane and click 'Select Ref. Plane' button!"
    result_msg = "Cut object done into WorkFeatures/WorkObjects/"
    name = "Part"
    part = "Part::Feature"
    
    m_actDoc = get_ActiveDocument(info=0)
    if m_actDoc == None:
        return

    m_num = len(m_cut_selectObjects)
    if m_num == 3:
        #[m_selEx, m_objs, m_objNames]
        # Get the Object
        m_cut_obj = m_cut_selectObjects[0]
        # Get the Line
        m_cut_line = m_cut_selectObjects[1]
        # Get the Plane
        m_ref_plane = m_cut_selectObjects[2]
        if msg == 1:
            print_msg("Object to cut =" + str(m_cut_obj[2]) +
                      "\nCutting Line  =" + str(m_cut_line[2]) +
                      "\nRef. Plane    =" + str(m_ref_plane[2]))
        # Check if we have correct shapes
        SubObjects_Inside = m_cut_line[0][0].SubObjects
        SubObject = SubObjects_Inside[0]
        if msg == 1:
            print_msg( "SubObject = " + str(SubObject) )
        if SubObject.ShapeType != "Edge":
            printError_msg(error_msg)
            return
        m_Edge = SubObject
        SubObjects_Inside = m_ref_plane[0][0].SubObjects
        SubObject = SubObjects_Inside[0]
        if msg == 1:
            print_msg( "SubObject = " + str(SubObject) )
        if SubObject.ShapeType != "Face":
            printError_msg(error_msg)
            return
        m_Plane = SubObject
        
        m_Obj = m_cut_obj[1][0]
        try:                
            m_Obj.Shape 
        except:
            printError_msg( "This object has no attribute 'Shape' ! Select another one !\n")
            return
        m_Obj_name = m_cut_obj[2][0]
        try:
            m_dir=str(m_Obj_name)+"_Cut"
            m_newdir=App.ActiveDocument.getObject("WorkObjects").newObject("App::DocumentObjectGroup", str(m_dir))
            m_dir=m_newdir.Name
        except:
            printError_msg("Could not Create '"+ str(m_dir) +"' Objects Group!")
            return
            
        if msg == 1:
            print_msg( "Processing : " + str(m_Obj_name))
            print_msg( "Into the group : " + str(m_dir))        
        
        # Get Line's limits          
        Point_A = m_Edge.valueAt(0.0)
        Point_B = m_Edge.valueAt(m_Edge.Length)
        Point_C = centerLinePoint(m_Edge)
        if msg == 1:
            print_msg( "\nGet Line's limits") 
            Point_A_User_Name = plot_point(Point_A, part, "Point_A", grp=str(m_dir))
            print_point(Point_A, msg=str(Point_A_User_Name) + ", (internal Point_A) : ")
            Point_B_User_Name = plot_point(Point_B, part, "Point_B", grp=str(m_dir))
            print_point(Point_B, msg=str(Point_B_User_Name) + ", (internal Point_B) : ")
            Point_C_User_Name = plot_point(Point_C, part, "Point_C", grp=str(m_dir))
            print_point(Point_C, msg=str(Point_C_User_Name) + ", (internal Point_C) : ")
            print_msg( "Distance : " + str(m_Edge.Length))
            

        # Get object's limits
        m_xmax, m_xmin, m_ymax, m_ymin, m_zmax, m_zmin = minMaxObjectsLimits(m_cut_obj[1][0:],info=0)
        
        # Length of BoundBox in X, Y and Z dimensions
        m_length_X = m_xmax - m_xmin
        m_length_Y = m_ymax - m_ymin
        m_length_Z = m_zmax - m_zmin
        m_length_list = [m_length_X, m_length_Y, m_length_Z]
        m_length_max = max(m_length_list)
        m_ori_X = m_xmin
        m_ori_Y = m_ymin
        m_ori_Z = m_zmin

        # Get Points, Edges, Faces from the bounding box Object dimensions
        Points, BB_Edges, Faces = get_all_from_bounding_box(m_ori_X,m_ori_Y,m_ori_Z,m_length_X,m_length_Y,m_length_Z,info=0,plot=0)
        
#==============================================================================                    
        # Looking for the min distance between center of line and center 
        # of faces of the bounding box. An selection of this Plane
        min_val, max_val = init_min_max()
        m_min_distance = max_val
        Plane_Point1 = None
        Plane_Normal1 = None
        Selected_Plane1 = Faces[0][5]
        for m_i in range(len(Faces)):               
            #( 3,  0,  1, 2, (BB_Edges[3][3],BB_Edges[0][3],BB_Edges[1][3],BB_Edges[2][3]), face, mid_point, length )                
            m_distance = distanceBetween(Point_C, Faces[m_i][6])                 
            if m_distance < m_min_distance:
                m_min_distance = m_distance
                Selected_Plane1 = Faces[m_i][5]
                Plane_Point1 = Faces[m_i][6]
                Plane_Normal1 = Selected_Plane1.normalAt(0,0)
        if Plane_Point1 == None:
            printError_msg("Plane_Point1 is Null!")
            return
        if Plane_Normal1 == None:
            printError_msg("Plane_Normal1 is Null!")
            return
#==============================================================================
                
#==============================================================================        
        # Select the second plane of the bounding box parallel to this first one 
        Plane_Point2 = None
        Plane_Normal2 = None
        Selected_Plane2 = Faces[0][5]
        for m_i in range(len(Faces)):
            Plane_Normal = Faces[m_i][5].normalAt(0,0)
            if Plane_Normal != Plane_Normal1:
                cross_product = Plane_Normal.cross(Plane_Normal1)
                if abs(cross_product.x) <= 1e-12 and abs(cross_product.y) <= 1e-12 and abs(cross_product.z) <= 1e-12:
                    Selected_Plane2 = Faces[m_i][5]
                    Plane_Point2 = Faces[m_i][6]
                    Plane_Normal2 = Selected_Plane2.normalAt(0,0)
                    break
        if Plane_Point2 == None:
            printError_msg("Plane_Point2 is Null!")
            return
        if Plane_Normal2 == None:
            printError_msg("Plane_Normal2 is Null!")
            return        
        if msg == 1:
            print_msg( "\nGet Bounding Planes info")
            print_msg( "MIN Distance : " + str(m_min_distance) )
            Point_Face01_User_Name = plot_point(Plane_Point1, part, "Point_Face01", grp=str(m_dir))
            print_point(Plane_Point1, msg=str(Point_Face01_User_Name) + ", (internal Point_Face01) : ")
            Point_Face02_User_Name = plot_point(Plane_Point2, part, "Point_Face02", grp=str(m_dir))
            print_point(Plane_Point2, msg=str(Point_Face02_User_Name) + ", (internal Point_Face02) : ")

#==============================================================================
            
#==============================================================================
        # Build The Plane Crossing the Line and making an angle with the Ref. Plane
        Ref_Plane = m_Plane
        Plane_Point = Ref_Plane.CenterOfMass
        Plane_Normal = Ref_Plane.normalAt(0,0)
        # Projection of A and B onto the Ref Plane A0 and B0
        Vector_A = Point_A + Plane_Normal
        Vector_B = Point_B + Plane_Normal
        Point_A0 = intersecLinePlane(Point_A, Vector_A, Plane_Normal, Plane_Point, info=0)
        Point_B0 = intersecLinePlane(Point_B, Vector_B, Plane_Normal, Plane_Point, info=0)
        # Plot them if needed
        if msg == 1:
            print_msg( "\nProjection of A and B onto the Ref Plane in A0 and B0")
            Point_A0_User_Name = plot_point(Point_A0, part, "Point_A0", grp=str(m_dir))
            Point_B0_User_Name = plot_point(Point_B0, part, "Point_B0", grp=str(m_dir))
            print_point(Point_A0, msg=str(Point_A0_User_Name) + ", (internal Point_A0) : ")
            print_point(Point_B0, msg=str(Point_B0_User_Name) + ", (internal Point_B0) : ")
            
        AxisA0B0_User_Name, AxisA0B0 = plot_axis(Point_A0, Point_B0, part, "LineA0-B0", grp=str(m_dir))
        
        Point_A1 = Point_A0
        Point_B1 = Point_B0
        # Get intersections of this line with the Edges of the Ref. Plane
        # To update  points A0 and B0 into A1 and B1
        Number_of_Intersec, Intersec_Points = intersecPoints(AxisA0B0.Shape, Ref_Plane, info=0)
        if msg == 1:
            print_msg( "\nIntersections of A0B0 line with the edges of Ref. Plane : A1 and B1")
            print_msg("Number_of_Intersec = " + str(Number_of_Intersec))
        if Number_of_Intersec == 0:
            printError_msg("No intersection point between projection of the Line and Object !")
            return
        if Number_of_Intersec == 1:
            printError_msg("Only one intersection point between projection of the Line and Object ! No cut possible !")
            return            
        if Number_of_Intersec == 2:
            Point_A1 = Intersec_Points[0]
            Point_B1 = Intersec_Points[1]
            if msg == 1:
                Point_A1_User_Name = plot_point(Point_A1, part, "Point_A1", grp=str(m_dir))
                print_point(Point_A1, msg=str(Point_A1_User_Name) + ", (internal Point_A1) : ")
                Point_B1_User_Name = plot_point(Point_B1, part, "Point_B1", grp=str(m_dir))                 
                print_point(Point_B1, msg=str(Point_B1_User_Name) + ", (internal Point_B1) : ")
            
        # Line onto Ref Plane
        Edge_Vector = Point_B1 - Point_A1
        Edge_Length = m_length_max * 1.5 * 2
        # Mid point
        Point_MidPoint = Point_B1 + Point_A1
        Point_MidPoint = Point_MidPoint.multiply(0.5)
        # Attachement Point
        Attach_Point = Point_MidPoint        
        # Normal
        Vector_Normal = Edge_Vector.cross(Plane_Normal)
        
        # Build a cutting Plane
        if msg == 1:
            print_msg( "\nBuild a cutting Plane")        
                        
        Plane_Point = Attach_Point
        Plane_Normal = Edge_Vector.cross(Plane_Normal)
        # Get projection of Plane_Point1 to cutting Plane
        C1 = Plane_Point1
        B1 = C1 + Plane_Normal
        T1 = intersecLinePlane(C1, B1, Plane_Normal, Plane_Point, info=0)       
        # Get projection of Plane_Point2 to cutting Plane
        C2 = Plane_Point2
        B2 = C2 + Plane_Normal
        T2 = intersecLinePlane(C2, B2, Plane_Normal, Plane_Point, info=0)
        # New Attachement Point        
        Attach_Point = T2 - T1
        Attach_Point = Attach_Point.multiply(0.5)
        Attach_Point = Point_MidPoint + Attach_Point
        # Build a cutting Plane
        cutting_plane = None
        Plane_cutting_User_Name, cutting_plane = plot_plane(Edge_Length, Edge_Length, Attach_Point, Vector_Normal, part, "Cutting_plane", grp=str(m_dir)) 
        if cutting_plane == None:
            printError_msg("Unable to create Cutting plane !")
            return
                 
        # Rotate the cutting Plane if needed
        if m_angleCutObject != 0.0:
            rot_angle = m_angleCutObject
            rot_axis = Edge_Vector
            m_center = Point_MidPoint
            m_rot = App.Rotation(rot_axis,rot_angle)
            if msg == 1:
                print_msg("rotation  =       " + str(m_rot))
                print_msg("rotation axis   = " + str(rot_axis))
            m_place = App.Placement(cutting_plane.Placement)
            m_base1 = m_place.Base                
            if msg == 1:
                print_msg("base1   = " + str(m_base1))
            m_rot1 = m_place.Rotation
            if msg == 1:
                print_msg("rot1   = " + str(m_rot1))
            m_rot = m_rot.multiply(m_rot1)
            m_newplace = App.Placement(m_base1,m_rot,m_center-m_base1)
            cutting_plane.Placement = m_newplace
            
        Attach_Point = cutting_plane.Shape.CenterOfMass
        Vector_Normal = cutting_plane.Shape.normalAt(0,0)
        # Duplicate the cutting Plane and move if thickness not null
        if m_thicknessCutObject != 0.0:
            Attach_Point2 = Vector_Normal - Attach_Point
            Attach_Point2 =  Attach_Point + Attach_Point2.normalize().multiply(0.5 * m_thicknessCutObject)
            # Build a cutting Plane
            cutting_plane2 = None
            Plane_cutting2_User_Name, cutting_plane2 = plot_plane(Edge_Length, Edge_Length, Attach_Point2, Vector_Normal, part, "Cutting_plane", grp=str(m_dir)) 
            if cutting_plane2 == None:
                printError_msg("Unable to create Cutting plane 2 !")
                return
                       
            Attach_Point3 = Vector_Normal - Attach_Point
            Attach_Point3 =  Attach_Point + Attach_Point3.normalize().multiply(-0.5 * m_thicknessCutObject)
            # Build a cutting Plane
            cutting_plane3 = None
            Plane_cutting3_User_Name, cutting_plane3 = plot_plane(Edge_Length, Edge_Length, Attach_Point3, Vector_Normal, part, "Cutting_plane", grp=str(m_dir)) 
            if cutting_plane3 == None:
                printError_msg("Unable to create Cutting plane 3 !")
                return

            


                
#==============================================================================
            
        # Just need to find the intersection line between cutting Plane and
        # the object (nearest bounding Plane)
        cut_plane = cutting_plane.Shape
        near_plane = Selected_Plane1
        if msg == 1:
            print_msg(str(cut_plane))
            print_msg(str(near_plane))
                        
        cut_plane_Normal  = cut_plane.normalAt(0,0)
        near_plane_Normal = near_plane.normalAt(0,0)
        if msg == 1:
            print_msg( "\nFind the intersection line between cutting Plane and the object (nearest plane of bounding box)")
            print_point(cut_plane_Normal, msg="Normal1 : ")
            print_point(near_plane_Normal, msg="Normal2 : ")

        cut_plane_Point   = cut_plane.CenterOfMass
        near_plane_Point  = near_plane.CenterOfMass
        if msg == 1:
            print_point(cut_plane_Point , msg="cut_plane_Point : ")
            print_point(near_plane_Point , msg="near_plane_Point : ")
            
        Axis_dir = intersecPlanePlane(cut_plane_Normal, cut_plane_Point, near_plane_Normal, near_plane_Point, info=msg)
                
        if Axis_dir == None:
            printError_msg("Not able to find an intersection between the cutting Plane and the Object !")
            return
            
        # Intersection Line found
        Intersecline = None       
        Vertx = []
        Distx = []
        Vertx_names = []
        
        min_val, max_val = init_min_max()
        dist_to_center_min = max_val
        # For the first plane look after all edges and look at 
        # intersections of the edges with the second plane
        Number_of_Edges = len(cut_plane.Edges)
        for j in range(Number_of_Edges):
            A = cut_plane.Edges[j].valueAt( 0.0 )
            B = cut_plane.Edges[j].valueAt(cut_plane.Edges[j].Length )
            T = intersecLinePlane(A, B, near_plane_Normal, near_plane_Point, info=0)                    
            if T != None:              
                D = T - cut_plane_Point                       
                dist_to_center = math.sqrt(D.dot(D))                
                if dist_to_center < dist_to_center_min:
                    dist_to_center_min = dist_to_center
                    Vertx.append(T)
                    Distx.append(dist_to_center)                        
                          
#==============================================================================
#         Number_of_Edges = len(near_plane.Edges)
#         dist_to_center_min = max_val
#         for jj in range(Number_of_Edges):
#             A = near_plane.Edges[jj].valueAt( 0.0 )
#             B = near_plane.Edges[jj].valueAt(near_plane.Edges[jj].Length )
#             T = intersecLinePlane(A, B, cut_plane_Normal, cut_plane_Point, info=0)
#             if T != None:                 
#                 D = T - near_plane_Point
#                 dist_to_center = math.sqrt(D.dot(D))                 
#                 if dist_to_center < dist_to_center_min:
#                     dist_to_center_min = dist_to_center
#                     Vertx.append(T)
#                     Distx.append(dist_to_center)
#==============================================================================

        if msg == 1:
            for k in range(len(Vertx)):
                Point_User_Name = plot_point(Vertx[k], part, "Edge_point", grp=str(m_dir))
                Vertx_names.append(str(Point_User_Name))
                print_point(Vertx[k], msg=str(Point_User_Name) + ", (internal Edge_point) : ")

        C = meanVectorsPoint(Vertx,info=0)

        if msg == 1:            
            Edge_point_C_User_Name = plot_point(C, part, "Edge_point_C", grp=str(m_dir))
            print_point(C, msg=str(Edge_point_C_User_Name) + ", (internal Edge_point_C) : ")

        if C != None:
            extension = max(Distx)
            A = C -  Axis_dir.normalize().multiply(extension*1.5)
            B = C +  Axis_dir
            IntersecLine_User_Name, Intersecline = plot_axis(A, B, part, "IntersecLine", grp=str(m_dir))
#==============================================================================

#==============================================================================
        # Look for A2 and B2 intersection of Intersecline and edges of the object
        # (nearest plane of bounding box : Selected_Plane1)
        Point_A2 = Point_A1
        Point_B2 = Point_B1
        # Get intersections of this line with the Edges of the Face
        # To update  Point_A1 and Point_B1 into Point_A2 and Point_B2
        Number_of_Intersec, Intersec_Points = intersecPoints(Intersecline.Shape, Selected_Plane1, info=0)
        if msg == 1:
            print_msg( "\nLook for A2 and B2 intersection of Intersecline and edges of the object (nearest plane of bounding box)")
            print_msg("Number_of_Intersec = " + str(Number_of_Intersec))
            
        if Number_of_Intersec == 0:
            printError_msg("No intersection point between Intersecline and Object !")
            return
        if Number_of_Intersec == 1:
            printError_msg("Only one intersection point between Intersecline and Object ! No cut possible !")
            return            
        if Number_of_Intersec == 2:
            Point_A2 = Intersec_Points[0]
            Point_B2 = Intersec_Points[1]
            if msg == 1:
                print_msg( "Intersections of Intersecline with the Edges of the Face :")
                Point_A2_User_Name = plot_point(Intersec_Points[0], part, "Point_A2", grp=str(m_dir))
                print_point(Point_A2, msg=str(Point_A2_User_Name) + ", (internal Point_A2) : ")
                Point_B2_User_Name = plot_point(Intersec_Points[1], part, "Point_B2", grp=str(m_dir))                 
                print_point(Point_B2, msg=str(Point_B2_User_Name) + ", (internal Point_B2) : ")

#==============================================================================

#==============================================================================        
        # Now we need to extrude the cutting Plane
        BB_edges_names = []    
        # First get 2 Vectors in which direction to extrude from Point_A2
        Vector_extrude1 = App.Vector(0.0,0.0,0.0)
        Vector_extrude2 = App.Vector(0.0,0.0,0.0)
        for m_i in range(len(BB_Edges)):                                 
            #( 2, 6, (Points[2], Points[6]), edge, mid_point, length )
            if msg == 1:
                Axis_User_Name, Axis = plot_axis(BB_Edges[m_i][2][0], BB_Edges[m_i][2][1], part, "bb_edge", grp=str(m_dir))
                BB_edges_names.append(str(Axis_User_Name))
            if colinearVectors(BB_Edges[m_i][2][0], Point_A2, BB_Edges[m_i][2][1], info=0, precision=1e-10):                
                # Plot them
                if msg == 1:
                    Point_A2_prime_User_Name = plot_point(BB_Edges[m_i][2][0], part, "Point_A2_prime", grp=str(m_dir))
                    print_point(BB_Edges[m_i][2][0], msg=str(Point_A2_prime_User_Name) + ", (internal Point_A2_prime) : ")
                    Point_A2_second_User_Name = plot_point(BB_Edges[m_i][2][1], part, "Point_A2_second", grp=str(m_dir))
                    print_point(BB_Edges[m_i][2][1], msg=str(Point_A2_second_User_Name) + ", (internal Point_A2_second) : ")
                
                Vector_extrude1 = BB_Edges[m_i][2][0] - Point_A2 
                Vector_extrude2 = Point_A2 - BB_Edges[m_i][2][1]
        
        if Vector_extrude1 == App.Vector(0.0,0.0,0.0):
            for m_i in range(len(BB_Edges)):                        
                #( 2, 6, (Points[2], Points[6]), edge, mid_point, length )
                if msg == 1:
                    Axis_User_Name, Axis = plot_axis(BB_Edges[m_i][2][0], BB_Edges[m_i][2][1], part, "bb_edge", grp=str(m_dir))
                    BB_edges_names.append(str(Axis_User_Name))
                if colinearVectors(BB_Edges[m_i][2][0], Point_B2, BB_Edges[m_i][2][1], info=0, precision=1e-10):                
                    # Plot them
                    if msg == 1:
                        Point_A2_prime_User_Name = plot_point(BB_Edges[m_i][2][0], part, "Point_B2_prime", grp=str(m_dir))
                        print_point(BB_Edges[m_i][2][0], msg=str(Point_A2_prime_User_Name) + ", (internal Point_B2_prime) : ")
                        Point_A2_second_User_Name = plot_point(BB_Edges[m_i][2][1], part, "Point_B2_second", grp=str(m_dir))
                        print_point(BB_Edges[m_i][2][1], msg=str(Point_A2_second_User_Name) + ", (internal Point_B2_second) : ")
                    
                    Vector_extrude1 = BB_Edges[m_i][2][0] - Point_B2 
                    Vector_extrude2 = Point_B2 - BB_Edges[m_i][2][1]

            if Vector_extrude1 == App.Vector(0.0,0.0,0.0):
                printError_msg("Vector_extrude1 is Null!")
                return
                
        if Vector_extrude2 == App.Vector(0.0,0.0,0.0):
            printError_msg("Vector_extrude2 is Null!")
            return
        
        # Get the max length of the bounding box
        Vector_extrude1 = Vector_extrude1.normalize().multiply(m_length_max)
        Vector_extrude2 = Vector_extrude2.normalize().multiply(m_length_max)  
        # Extrude a bit after the extreme edges with a 45 deg angle (diagonal)
        Vector_extrude1 = Vector_extrude1.multiply(1.5).multiply(2)
        Vector_extrude2 = Vector_extrude2.multiply(-1.5).multiply(2)
        if msg == 1:
            print_msg("Vector_extrude1  =       " + str(Vector_extrude1))
            print_msg("Vector_extrude2  =       " + str(Vector_extrude2))    
                            
        # Get the shape of the cutting Plane
        plane_shape = cutting_plane.Shape
        if msg == 1:
            print_msg("plane       =       " + str(cutting_plane))
            print_msg("plane_shape =       " + str( plane_shape))
            
        # We extrude in the first direction
        extrude1 = plane_shape.extrude(Vector_extrude1)
        if msg == 1:
            print_msg("extrude1   =       " + str(extrude1))
        m_extrude1_name = str(m_Obj_name) + "_" + str(name) + "extrude01"
        Extrude1 = App.ActiveDocument.addObject(part,m_extrude1_name)
        App.ActiveDocument.getObject(str(m_dir)).addObject(Extrude1)
        m_extrude1_name = Extrude1.Name
        Extrude1.Shape = extrude1
        
        # We extrude in the second direction
        extrude2 = plane_shape.extrude(Vector_extrude2)
        if msg == 1:
            print_msg("extrude2   =       " + str(extrude2))
        m_extrude2_name = str(m_Obj_name) + "_" + str(name) + "extrude02"
        Extrude2 = App.ActiveDocument.addObject(part,m_extrude2_name)
        App.ActiveDocument.getObject(str(m_dir)).addObject(Extrude2)
        m_extrude2_name = Extrude2.Name
        Extrude2.Shape = extrude2

        # if thickness not null
        if m_thicknessCutObject != 0.0:
            plane_shape2 = cutting_plane2.Shape
            plane_shape3 = cutting_plane3.Shape
            Vector_extrude3 = Attach_Point3 - Attach_Point2
            Vector_extrude4 = Attach_Point2 - Attach_Point3
            
            extrude1b = plane_shape2.extrude(Vector_extrude3)
            if msg == 1:
                print_msg("extrude1b   =       " + str(extrude1b))
            m_extrude1b_name = str(m_Obj_name) + "_" + str(name) + "extrude01b"
            Extrude1b = App.ActiveDocument.addObject(part,m_extrude1b_name)
            App.ActiveDocument.getObject(str(m_dir)).addObject(Extrude1b)
            m_extrude1b_name = Extrude1b.Name
            Extrude1b.Shape = extrude1b

            extrude2b = plane_shape3.extrude(Vector_extrude4)
            if msg == 1:
                print_msg("extrude2b   =       " + str(extrude2b))
            m_extrude2b_name = str(m_Obj_name) + "_" + str(name) + "extrude02b"
            Extrude2b = App.ActiveDocument.addObject(part,m_extrude2b_name)
            App.ActiveDocument.getObject(str(m_dir)).addObject(Extrude2b)
            m_extrude2b_name = Extrude2b.Name
            Extrude2b.Shape = extrude2b
#==============================================================================

#==============================================================================
        # Let's duplicate the Object
        m_obj2 = m_actDoc.copyObject(m_Obj)
        m_obj3 = m_actDoc.copyObject(m_Obj)
        App.ActiveDocument.getObject(str(m_dir)).addObject(m_obj2)
        App.ActiveDocument.getObject(str(m_dir)).addObject(m_obj3) 
        Obj2_User_Name = m_obj2.Name            
        Obj3_User_Name = m_obj3.Name
        
        # and Split in two parts
        m_diff1_name = str(m_Obj_name) + "_01_" + str(name)
        Diff1 = App.ActiveDocument.addObject( part, m_diff1_name )        
        Diff1.Shape = m_obj2.Shape.cut(extrude1)
        if m_thicknessCutObject != 0.0:
            Diff1.Shape = Diff1.Shape.cut(extrude1b)
        App.ActiveDocument.getObject(str(m_dir)).addObject(Diff1)
        
        m_diff2_name = str(m_Obj_name) + "_02_" + str(name)
        Diff2 = App.ActiveDocument.addObject( part, m_diff2_name )       
        Diff2.Shape = m_obj3.Shape.cut(extrude2)
        if m_thicknessCutObject != 0.0:
            Diff2.Shape = Diff2.Shape.cut(extrude2b)
        App.ActiveDocument.getObject(str(m_dir)).addObject(Diff2)
#==============================================================================        

#==============================================================================
        # Hide intermediate objects
        if msg == 1:
            Gui.ActiveDocument.getObject(str(Point_A_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_B_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_C_User_Name)).Visibility=False
            
            Gui.ActiveDocument.getObject(str(Point_Face01_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_Face02_User_Name)).Visibility=False

            Gui.ActiveDocument.getObject(str(Point_A0_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_B0_User_Name)).Visibility=False
            
            Gui.ActiveDocument.getObject(str(Point_A1_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_B1_User_Name)).Visibility=False
                           
            for k in range(len(Vertx)):
                Gui.ActiveDocument.getObject(str(Vertx_names[k])).Visibility=False
            Gui.ActiveDocument.getObject(str(Edge_point_C_User_Name)).Visibility=False
            
            Gui.ActiveDocument.getObject(str(Point_A2_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_B2_User_Name)).Visibility=False
            for k in range(len(BB_edges_names)):
               Gui.ActiveDocument.getObject(str(BB_edges_names[k])).Visibility=False 

            Gui.ActiveDocument.getObject(str(Point_A2_prime_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Point_A2_second_User_Name)).Visibility=False
            
            Gui.ActiveDocument.getObject(str(m_extrude1_name)).Visibility=False
            Gui.ActiveDocument.getObject(str(m_extrude2_name)).Visibility=False
            if m_thicknessCutObject != 0.0:
                Gui.ActiveDocument.getObject(str(m_extrude1b_name)).Visibility=False
                Gui.ActiveDocument.getObject(str(m_extrude2b_name)).Visibility=False
            
            Gui.ActiveDocument.getObject(str(Obj2_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Obj3_User_Name)).Visibility=False
        
        # hide lines
        Gui.ActiveDocument.getObject(str(AxisA0B0_User_Name)).Visibility=False
        Gui.ActiveDocument.getObject(str(IntersecLine_User_Name)).Visibility=False
        
        # hide the cutting planes            
        Gui.ActiveDocument.getObject(str(Plane_cutting_User_Name)).Visibility=False
        if m_thicknessCutObject != 0.0:
            Gui.ActiveDocument.getObject(str(Plane_cutting2_User_Name)).Visibility=False
            Gui.ActiveDocument.getObject(str(Plane_cutting3_User_Name)).Visibility=False    
        
        # hide the Original
        Gui.ActiveDocument.getObject(str(m_Obj_name)).Visibility=False        
#==============================================================================       
#==============================================================================
        # Remove intermediate objects
        if msg == 0:
            App.getDocument(str(m_actDoc.Name)).removeObject(m_extrude1_name)
            App.getDocument(str(m_actDoc.Name)).removeObject(m_extrude2_name)
            if m_thicknessCutObject != 0.0:
                App.getDocument(str(m_actDoc.Name)).removeObject(m_extrude1b_name)
                App.getDocument(str(m_actDoc.Name)).removeObject(m_extrude2b_name)
            App.getDocument(str(m_actDoc.Name)).removeObject(Obj2_User_Name)
            App.getDocument(str(m_actDoc.Name)).removeObject(Obj3_User_Name)
#==============================================================================
        print_msg( str(m_diff1_name) + result_msg + str(m_dir) )
        print_msg( str(m_diff2_name) + result_msg + str(m_dir) )
        
        del BB_edges_names[:]
        del Distx[:]
        del Vertx[:]
        del Vertx_names[:]
    else:
        printError_msg(error_msg)

    cut_reset()

            
def object_align2view():
    """ Place your object selected to the position ActiveView (camera)
    __author__ = "Mario52"
    """
    # revoir le point de rotation
    msg=0
    error_msg  = "Select one object !"
    
    m_actDoc = get_ActiveDocument(info=msg)
    if m_actDoc == None:
        return None
        
    m_num, m_selEx, m_objs, m_objNames = get_InfoObjects(info=msg)
    Center = centerObjectsPoint(m_objs)
    if Center != None:
        pl = FreeCAD.Placement()
        pl.Rotation = Gui.ActiveDocument.ActiveView.getCameraOrientation()
        pl.Base = App.Vector(0,0,0)
        for m_objName in m_objNames:           
            App.ActiveDocument.getObject(m_objName).Placement=pl
        
    else:
        printError_msg(error_msg)  
        
    #sel = Gui.Selection.getSelection()
    #Nameelement = sel[0].Name
    #pl = FreeCAD.Placement()
    #pl.Rotation = Gui.ActiveDocument.ActiveView.getCameraOrientation()
    #pl.Base = FreeCAD.Vector(0.0,0.0,0.0)
    #App.ActiveDocument.getObject(Nameelement).Placement=pl
   
        
def view_align():
    """ Set the current view perpendicular to the selected Face, Edge
    or 2 points selected
    """
    # TODO
    # se mettre tangent a un objet...
    error_msg = "Unable to align camera : \nSelect one Face, one Edge or 2 points !"
    m_actDoc=App.activeDocument()
    if m_actDoc.Name:
        # Return a list of Objects for a given document name.
        m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
        m_num = len(m_selEx)
        if m_num >= 1:
            Selected_Points = []
            m_cam = Gui.ActiveDocument.ActiveView.getCameraNode()
            m_camValues = m_cam.position.getValue()
            m_pos = App.Vector( (m_camValues[0], m_camValues[1], m_camValues[2],) )
            
            for m_i in range(m_num):
                Sel_i_Object = m_selEx[m_i]
                SubObjects_Inside = Sel_i_Object.SubObjects
                SubObject = SubObjects_Inside[0]            
                
                if SubObject.ShapeType == "Vertex":
                    Selected_Points.append(SubObject)
                    Number_of_Points = len(Selected_Points)
                    if Number_of_Points == 2:
                        m_Vertex1 = Selected_Points[0]
                        m_dist1 = m_pos.sub(Selected_Points[0].Point) 
                        m_Vertex2 = Selected_Points[1]                   
                        m_dist2 = m_pos.sub(Selected_Points[1].Point)
                    
                        #print_msg("dist1=" + str(m_dist1.Length) + "\ndist2=" + str(m_dist2.Length))
                        if m_dist1.Length < m_dist2.Length:
                            alignCamera(m_Vertex1.Point,m_Vertex2.Point,False)
                        else:
                            alignCamera(m_Vertex1.Point,m_Vertex2.Point,True)

                            
                elif SubObject.ShapeType == "Edge":
                    m_Vertex1 = SubObject.Vertexes[0]
                    m_dist1 = m_pos.sub(SubObject.valueAt( 0.0 )) 
                    m_Vertex2 = SubObject.Vertexes[1]                    
                    m_dist2 = m_pos.sub(SubObject.valueAt( SubObject.Length ))
                    
                    #print_msg("dist1=" + str(m_dist1.Length) + "\ndist2=" + str(m_dist2.Length))
                    if m_dist1.Length < m_dist2.Length:
                        alignCamera(m_Vertex1.Point,m_Vertex2.Point,False)
                    else:
                        alignCamera(m_Vertex1.Point,m_Vertex2.Point,True)
                        
                elif SubObject.ShapeType == "Face":
                    m_faceSel = Sel_i_Object.SubObjects[0]
                    m_dir = m_faceSel.normalAt(0,0)
                    m_dir = m_faceSel.Surface.Axis
                    m_edge = Part.makeLine(m_faceSel.CenterOfMass, m_faceSel.CenterOfMass.add(m_dir))
    
                    m_Vertex1 = m_edge.Vertexes[0]
                    m_dist1 = m_pos.sub(m_faceSel.CenterOfMass)                    
                    m_Vertex2 = m_edge.Vertexes[1]
                    m_dist2 = m_pos.sub(m_faceSel.CenterOfMass.add(m_dir))
                    
                    #print_msg("dist1=" + str(m_dist1.Length) + "\ndist2=" + str(m_dist2.Length))
                    if m_dist1.Length < m_dist2.Length:
                        alignCamera(m_Vertex1.Point,m_Vertex2.Point,False)
                    else:
                        alignCamera(m_Vertex1.Point,m_Vertex2.Point,True)
                else:
                    printError_msg(error_msg)                       
        else:
            printError_msg(error_msg)
    
####################################################################################   
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

####################################################################################  
class WorkFeatureTab():
    def __init__(self):
        # Get main window
        self.m_main = self.getMainWindow()
        
        # Get Tab panel
        self.m_tab = self.getComboView(self.m_main)
        
        if self.m_tab.count() == 2:
            # Create a new fake dialog
            self.m_fake_dialog = QtGui.QDialog()
            self.m_tab.addTab(self.m_fake_dialog,"")
            
        # Create a new dialog for WorkFeatureTab
        self.m_dialog = QtGui.QDialog()
        # Add the dialog in a new tab or focus on it if already exists
        if self.m_tab.count() >= 2:
            for i in range(2,self.m_tab.count()):
                #print_msg (str(isinstance(self.m_tab.tabText(i), unicode)))
                #print_msg (str(unicode(self.m_tab.tabText(i), 'utf-8')))
                #if "Work Features" == str(unicode(self.m_tab.tabText(i), 'utf-8')):
                if "Work Features" == str(_fromUtf8(self.m_tab.tabText(i))):
                    self.m_tab.removeTab(int(i))
                    break
        
        self.m_tab.addTab(self.m_dialog,"Work Features")
              
        self.ui = WFGui.Ui_Form()
        self.ui.setupUi(self.m_dialog)
        self.m_tab.setCurrentIndex(3)
                
        # Connect to functions
        self.connections_for_checkbox_toggled = {
                             "checkBox_object_center"       : "bBox_toggled", 
                            }
        self.connections_for_button_clicked = {
                             "button_WF_quit"               : "quit_clicked", 
                            }                
                #self.PB_Quit.clicked.connect(self.on_PB_Quit_clicked) # quit
                
        self.connections_for_button_pressed = { 
                             "button_origin"               : "plot_originObject",
                             
                             "button_object_center"        : "plot_centerObjectPoint",
                             "button_Npoints_center"       : "plot_NpointsPoint",
                             "button_line_center"          : "plot_centerLinePoint",
                             "button_line_extrema"         : "plot_extremaLinePoint",
                             "button_point_on_line"        : "plot_alongLinePoint",
                             "button_circle_center"        : "plot_centerCirclePoint",
                             "button_face_center"          : "plot_centerFacePoint",
                             "button_line_face_point"      : "plot_lineFacePoint",
                             "button_point_line_point"     : "plot_pointLinePoint",
                             "button_point_face_point"     : "plot_pointFacePoint",
                             "button_twolines_point"       : "plot_2LinesPoint",
                             "button_click_for_point"      : "plot_clickForPoint",
                             "button_object_base_point"    : "plot_baseObjectPoint",
                             
                             "button_object_axis"          : "plot_centerObjectAxes",
                             "button_twopoints_axis"       : "plot_2PointsAxis",
                             "button_cylinder_axis"        : "plot_cylinderAxis",                            
                             "button_twolines_axis"        : "plot_2LinesAxis",
                             "button_plane_axis"           : "plot_planeAxis",
                             "button_face_normal"          : "plot_faceNormal",
                             "button_point_line_axis"      : "plot_pointLineAxis",
                             "button_line_point_axis"      : "plot_linePointAxis",
                             "button_line_plane_axis"      : "plot_linePlaneAxis",
                             "button_twoplanes_axis"       : "plot_2PlanesAxis",                             
                             "button_object_base_axes"     : "plot_baseObjectAxes",
                             
                             "button_linecenter_circle"    : "plot_linecenterCircle",
                             "button_linepoint_circle"     : "plot_linepointCircle",
                             "button_3points_circle"       : "plot_3pointsCircle",
                             "button_3points_ellipse"      : "plot_3pointsEllipse",                          
                                                          
                             "button_threepoints_plane"    : "plot_3PointsPlane",
                             "button_axisandpoint_plane"   : "plot_axisPointPlane",
                             "button_axis_point_plane"     : "plot_perpendicularAxisPointPlane",
                             "button_planeandpoint_plane"  : "plot_planePointPlane",                             
                             "button_planeandaxis_plane"   : "plot_planeAxisPlane",
                             "button_face_tangent"         : "plot_faceTangentPlane",
                             "button_click_for_plane"      : "plot_clickForPlane",
                             "button_object_center_planes" : "plot_centerObjectPlanes",
                             
                             "button_boundingboxes"        : "plot_boundingBoxes",
                             "button_boundingbox"          : "plot_boundingBox",
                             "button_cylinder_create"      : "plot_axisPointCylinder",
                             "button_cube_create"          : "plot_axisPointCube",
                             
                             "button_alignview"            : "view_align",                            
                             
                             "button_cut_select_object"    : "cut_selectObject",
                             "button_cut_select_line"      : "cut_selectLine",
                             "button_cut_select_plane"     : "cut_selectPlane",
                             
                             "button_cut_reset"            : "cut_reset", 
                             "button_cut_apply"            : "plot_cutObject", 
                                                          
                            } 
        self.connections_for_text_changed = { 
                             "distance_point_on_line"    : "distanceLinePoint",
                             
                             "extension_twopoints_axis"  : "extensionTwoPointsAxis",
                             "extension_face_normal"     : "extensionFaceNormal",
                             "extension_line_point_axis" : "extensionLinePointAxis",
                             
                             "radius_circle"             : "radiusCircle",
                             
                             "extension_planePointPlane" : "extensionPlanePointPlane",
                             "angle_planeandaxis_plane"  : "anglePlaneAxisPlane",
                             
                             "diameter_cylinder"         : "diameterCylinder",
                             "length_cylinder"           : "lengthCylinder",
                             "section_cube"              : "sectionCube",
                             "height_cube"               : "heightCube",
                             
                             "angle_cut_object"          : "angleCutObject",
                             "thickness_cut_object"      : "thicknessCutObject",

                             "length_plane"              : "lengthPlane",
                             "width_plane"               : "widthPlane",
                             "length_plane_2"            : "lengthPlane",
                             "width_plane_2"             : "widthPlane",
                            }
                            
        self.connections_for_spin_changed = {
                             "spin_line_center"          : "numberLinePart",
                            }
                            
        self.connections_for_radiobutton_clicked = {                     
                             "radioButton_verbose"       : "verbose_toggled",
                            }
                
        for m_key, m_val in self.connections_for_button_clicked.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL("clicked()"),getattr(self,str(m_val)))
                                   
                                   
        for m_key, m_val in self.connections_for_button_pressed.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL("pressed()"),globals()[str(m_val)])
            
        
        for m_key, m_val in self.connections_for_text_changed.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL(_fromUtf8("textChanged(QString)")),globals()[str(m_val)])   
                                   #QtCore.SIGNAL(QtCore.QString.fromUtf8("textChanged(QString)")),globals()[str(m_val)])   

        
        for m_key, m_val in self.connections_for_spin_changed.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL("valueChanged(int)"),globals()[str(m_val)])   

        
        for m_key, m_val in self.connections_for_checkbox_toggled.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL(_fromUtf8("toggled(bool)")),globals()[str(m_val)])                           
        

        for m_key, m_val in self.connections_for_radiobutton_clicked.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL(_fromUtf8("clicked(bool)")),globals()[str(m_val)]) 
                                   
        self.m_dialog.show()
        m_text=str(myRelease)
        self.ui.label_release.setText(QtGui.QApplication.translate("Form", m_text, None, QtGui.QApplication.UnicodeUTF8))
        
       
    def quit_clicked(self): # quit
        #self.m_dialog.hide()
        self.m_dialog.close()
        if self.m_tab.count() >= 2:
            for i in range(2,self.m_tab.count()):
                if "Work Features" == str(_fromUtf8(self.m_tab.tabText(i))):
                    self.m_tab.removeTab(int(i))
                    break     
                
    def getMainWindow(self):
       """ Returns the main window
       """
       # using QtGui.qApp.activeWindow() isn't very reliable because if another
       # widget than the mainwindow is active (e.g. a dialog) the wrong widget
       # is returned
       toplevel = QtGui.qApp.topLevelWidgets()
       for i in toplevel:
           if i.metaObject().className() == "Gui::MainWindow":
               return i
       raise Exception("No main window found")

       
    def getComboView(self,window):
        """ Returns the main Tab.
        """
        dw=window.findChildren(QtGui.QDockWidget)
        for i in dw:
            if str(i.objectName()) == "Combo View":
                return i.findChild(QtGui.QTabWidget)
        raise Exception("No tab widget found")
 
 
if __name__ == '__main__':
    myDialog = WorkFeatureTab()
    
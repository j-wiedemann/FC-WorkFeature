# -*- coding: utf-8 -*-

"""
***************************************************************************
*   Thanks to original ideas and codes from :                             *
*   Javier Martinez Garcia 2014                                           *
*   Gui ideas from by Jonathan Wiedemann 2014                             *
*   Jonathan Wiedemann for view codes                                     *
*   Special thanks to Mario52                                             *
*      for bounding box codes, advices, diverse pieces of codes           *
*      and all discussions                                                *
***************************************************************************
***************************************************************************
*   FreeCAD Work Features / version 2015-01                               *
*   Copyright (c) 2014, 2015 <rentlau_64>                                 *
*   Code rewrite by <rentlau_64>                                          *
*   Copyright (c) 2014 Javier Martinez Garcia                             *
*   Copyright (c) 2014 Jonathan Wiedemann                                 *
*   Copyright (c) 2014, 2015 Mario52                                      *
*   Copyright (c) 2013 Jonathan Wiedemann                                 *
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

import WFGui_2015_01_25 as WFGui

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
m_distanceLinePoint = 0.0
m_extensionTwoPointsAxis = 0.0
m_extensionLinePointAxis = 0.0
m_extensionPlanePointPlane = 0.0
m_anglePlaneAxisPlane = 0.0
m_lengthPlane = 10.0
m_diameterCylinder = 2.0
m_lengthCylinder = 20.0
m_lengthCube = 2.0
m_widthCube = 2.0
m_heightCube = 20.0
m_widthPlane = 10.0
m_angleCutObject = 0.0
m_thicknessCutObject = 1.0

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
    m_list_dirs = ['Origin','WorkPoints','WorkAxis','WorkPlanes','WorkBoxes','WorkObjects']
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


def get_InfoObjects(info=0):
    """ Return info on objects selected:
    num, selEx, objs, objNames
    num     : number of objects
    selEx   : a list of Selected Objects
    objs    : a list of the .Object
    objNames: a list of the .ObjectName
    """
    m_actDoc=get_ActiveDocument()
    if m_actDoc == None:
        printError_msg("No active document !")
        return 0, 0, 0, 0
    # Return a list of Selected Objects for a given document name.
    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_objs = [selobj.Object for selobj in m_selEx]
    m_objNames = [selobj.ObjectName for selobj in m_selEx]
    m_num = len(m_objs)
    if m_num < 1:
        printError_msg("Select at least one object !")
        return 0, 0, 0, 0
    if info != 0:
        print_msg("m_num=" + str(m_num) +
                  ", m_selEx=" + str(m_selEx) +
                  ", m_objs=" + str(m_objs) +
                  ", m_objNames=" + str(m_objNames))
    return m_num, m_selEx, m_objs, m_objNames


def get_SelectedObjects(info=0):
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
    """ Return the min and max limits along the 3 Axis for all selected objects
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
        print_msg("Limits of all objects selected are :")
        print_msg("xmax =" + str(xmax) + ", "
                  "xmin =" + str(xmin) + ", "
                  "ymax =" + str(ymax) + ", "
                  "ymin =" + str(ymin) + ", "
                  "zmax =" + str(zmax) + ", "
                  "zmin =" + str(zmin))
    return xmax, xmin, ymax, ymin, zmax, zmin


def minMaxObjectsLimits(objs,info=0):
    """ Return the min and max limits along the 3 Axis for all selected objects
    """
    xmax = xmin = ymax = ymin = zmax = zmin = 0
    if objs == None:
        print_msg("ERROR : objs=None, leaving minMaxObjectsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin

    m_objs = objs
    m_num = len(m_objs)
    if m_num < 1:
        print_msg("ERROR : len(m_vertx) <1 , leaving minMaxObjectsLimits()")
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


def centerVectorsPoint(vertx,info=0):
    """ Return the center point of all selected Vectors.
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


def colinearVectors(A, B, C, info=0):
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

    if abs(Vector_3.x) <= 1e-12 and abs(Vector_3.y) <= 1e-12 and abs(Vector_3.z) <= 1e-12:
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
            view.removeEventCallback("SoMouseButtonEvent",m_callback)
            del m_stack[:]


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


def plot_centerObjectPoint():
    """ Plot the center point of all selected Objects together.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Point of Object(s) : \nSelect at least one Object !"
    result_msg = " : Center Point of Object(s) created !"
    m_actDoc = get_ActiveDocument(info=0)
    name = "CenterObjects"
    part = "Part::Feature"
    if m_actDoc.Name:
        # Return a list of SelectionObjects for a given document name.
        m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
        m_objs = [selobj.Object for selobj in m_selEx]
        Vector_Objects_Center = centerObjectsPoint(m_objs,info=0)
        if Vector_Objects_Center != None:
            Center_User_Name = plot_point(Vector_Objects_Center, part, name)
            print_msg(str(Center_User_Name) + result_msg )
        else:
            printError_msg(error_msg)


def plot_extremaLinePoint():
    """ Plot the first and last point of all selected Lines.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create First and Last Line Point(s) : \nSelect at least one Line !"
    result_msg = " : First and Last Line Point(s) created !"
    name = "extremumPoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
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
                print_msg(str(Center_User_Name) + result_msg )
                Center_User_Name = plot_point(Vector_B, part, name)
                print_msg(str(Center_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_centerLinePoint():
    """ Plot the mid point of all selected Lines.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create Mid Line Point(s) : \nSelect at least one Line !"
    result_msg = " : Mid Line Point(s) created !"
    name = "MidPoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
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
                print_msg(str(Center_User_Name) + result_msg )
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
    error_msg = "Unable to create a point along a Line : \nSelect one Edge AND one point only!"
    result_msg = " : Point along a Line created !"
    name = "PointLine"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
                print_msg(str(Center_User_Name) + result_msg )
            else:
                printError_msg("The Point and the line MUST be aligned !")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_centerCirclePoint():
    """ Plot the center point of all selected Circles.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Circle Point(s) : \nSelect at least one Edge of Circle !"
    result_msg = " : Center Circle Point(s) created !"
    name = "CenterCircle"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
    try:
        SelectedObjects = Selection
        Number_of_Edges = SelectedObjects[1]
        if Number_of_Edges >= 1:
            Edge_List = SelectedObjects[4]
            for i in range( Number_of_Edges ):
                try:
                    Edge_List[i].Curve.Radius
                    #Center = Edge_List[i].centerOfCurvatureAt( 0.0 )
                    Vector_Circle_Center = centerCirclePoint(Edge_List[i],info=1)

                    Center_User_Name = plot_point(Vector_Circle_Center, part, name)
                    print_msg(str(Center_User_Name) + result_msg )
                except:
                    printError_msg("Found One or More Non-Circular Edges")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_centerFacePoint():
    """ Plot the center point of all selected Planes.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create Center Face Point(s) : \nSelect at least one Plane surface !"
    result_msg = " : Center Face Point(s) created !"
    name = "CenterFace"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
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
                    print_msg(str(Center_User_Name) + result_msg )
                except:
                    printError_msg("Non Planar Surface !")
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_lineFacePoint():
    """ Plot the intersection point between one Line and one plane.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create (Line,Face) Intersection : \nSelect one Line and one Plane surface !"
    result_msg = " : (Line,Face) Intersection created !"
    name = "LineFacePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
            print_msg(str(Center_User_Name) + result_msg )
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_pointLinePoint():
    """ Plot the intersection point T on a Line given one Line and One Point C.
    The Vector TC is perpendicular to the line.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create (Point,Line) Intersection : \nSelect one Line and one Point not on the Line !"
    result_msg = " : (Point,Line) Intersection and symetric are created !"
    name = "PointLinePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=1)
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
            plot_point(Vector_Tprime, part, name)
            print_msg(str(Center_User_Name) + result_msg + " at a distance from the line of " + str(Distance))
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_pointFacePoint():
    """ Plot the intersection point T on a Plane given one Plane and One Point C.
    The Vector TC is perpendicular to the plane.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create (Point,Face) Intersection : \nSelect one Face and one Point not on the Face !"
    result_msg = " : (Point,Face) Intersection and symetric are created !"
    name = "PointFacePoint"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=1)
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
            print_msg(str(Center_User_Name) + result_msg )

        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_clickForPoint():
    """ Plot a Point at location of a mouse click.
    """
    global m_callback
    #print_msg("plot_clickForPoint" )
    #view = Gui.ActiveDocument.ActiveView
    view = get_ActiveView()
    #m_callback = view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),getClickedPoint)
    m_callback = view.addEventCallback("SoMouseButtonEvent",getClickedPoint2)


def plot_baseObjectPoint():
    """ Plot base point of all selected objects.
    """
    createFolders('WorkPoints')
    error_msg = "Unable to create Base point of Object(s): \nSelect at least one Object !"
    result_msg = " : Base point of Object(s) created !"
    m_actDoc = get_ActiveDocument(info=0)
    name = "BasePoint"
    part = "Part::Feature"
    if m_actDoc.Name:
        # Return a list of SelectionObjects for a given document name.
        m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
        m_objs = [selobj.Object for selobj in m_selEx]
        m_num = len(m_objs)
        if m_num >= 1:
            for m_i in range(0,m_num):
                m_base = m_objs[m_i].Placement.Base
                if m_base != None:
                    Center_User_Name = plot_point(m_base, part, name)
                    print_msg(str(Center_User_Name) + result_msg )
        else:
            printError_msg(error_msg)


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


def plot_centerObjectAxes():
    """ Create 3 Axes XY, and Z at center point of all selected objects.
    """
    createFolders('WorkAxis')
    error_msg = "Unable to create Axes : \nSelect at least one object !"
    result_msg = " : Axes created !"
    m_actDoc=App.activeDocument()
    message = "Active Document is : " + str(m_actDoc.Name)
    print_msg(message)
    if m_actDoc.Name == None:
        printError_msg("No Active document selected !")
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


def plot_twoPointsAxis():
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis : \nSelect two points only !"
    result_msg = " : Axis created !"
    name = "Line from 2 Points"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=1)
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
    createFolders('WorkAxis')
    error_msg = "Unable to create Cylinder Axis : \nSelect one cylindrical face only !"
    result_msg = " : Cylinder Axis created !"
    name = "Cylinder Axis"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
    try:
        SelectedObjects = Selection
        Number_of_Faces = SelectedObjects[2]
        #print_msg(" Number_of_Faces=" + str(Number_of_Faces))
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
        else:
            printError_msg(error_msg)
    except:
        printError_msg(error_msg)


def plot_twoLinesAxis():
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis between 2 Lines : \nSelect two lines only !"
    result_msg = " : Axis between 2 Lines created !"
    name = "MidLine"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
    createFolders('WorkAxis')
    error_msg = "Unable to create Plane Axis : \nSelect at least one plane face !"
    result_msg = " : Plane Axis created !"
    name = "Axis"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
    createFolders('WorkAxis')
    error_msg = "Unable to create Perpendicular Axis : \nSelect one Point and one Line only !"
    result_msg = " : Perpendicular Axis created !"
    name = "Perpendicular Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
            Vector_C      = Point_List[0].Point
            Vector_A      = Edge_List[0].valueAt( 0.0 )
            Vector_B      = Edge_List[0].valueAt( Edge_List[0].Length )

            Vector_T, Distance, Vector_Tprime = intersecPerpendicularLine(Vector_A, Vector_B, Vector_C, info=0)

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
    createFolders('WorkAxis')
    error_msg = "Unable to create Parallel Axis : \nSelect one Point and one Line only !"
    result_msg = " : Paralell Axis created !"
    name = "Parallel Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
    createFolders('WorkAxis')
    error_msg = "Unable to create projection Axis onto a Plane : \nSelect one Plane and one Line !"
    result_msg = " : Projection Axis onto a Plane created !"
    name = "Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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


def plot_twoPlanesAxis():
    """ Plot the intersection Axis between two planes.
    """
    createFolders('WorkAxis')
    error_msg = "Unable to create Axis between 2 Planes : \nSelect two Planes not parallel !"
    result_msg = " : Axis between 2 Planes created !"
    name = "Line"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
                C = centerVectorsPoint(Vertx,info=0)
                #print_point(C , msg="C : ")

                if C != None:
                    extension = m_xmax - m_xmin
                    if extension < m_ymax - m_ymin:
                        extension = m_ymax - m_ymin
                    if extension < m_zmax - m_zmin:
                        extension = m_zmax - m_zmin
                    extension = extension/2
                    A = C -  Axis_dir.normalize().multiply(extension*1.3)
                    B = C +  Axis_dir.normalize().multiply(extension*1.3)
                    Axis_User_Name, axis = plot_axis(A, B, part, name)
                    print_msg(str(Axis_User_Name) + result_msg )
        else:
            printError_msg(error_msg)

    except:
        printError_msg(error_msg)


def plot_baseObjectAxes():
    createFolders('Origin')
    error_msg = "Unable to create Axes : \nSelect at least one object !"
    result_msg = " : Axes created !"
    m_actDoc = get_ActiveDocument(info=0)
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


def plot_threePointsPlane():
    """ Create a Plane from 3 Points.
    """
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect three points only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
    try:
        SelectedObjects = Selection
        Number_of_Points = SelectedObjects[0]
        #print_msg("Number_of_Points=" + str(Number_of_Points))
        points = []
        if Number_of_Points == 3 :
            Point_List = SelectedObjects[3]
            #print_msg(str(Points_List))
            Point_A = Point_List[0].Point
            points.append(Point_A)
            Point_B = Point_List[1].Point
            points.append(Point_B)
            Point_C = Point_List[2].Point
            points.append(Point_C)
            #print_point(Point_A, msg="Point_A : ")
            #print_point(Point_B, msg="Point_B : ")
            #print_point(Point_C, msg="Point_C : ")

            Vector_Center = centerVectorsPoint(points, info=0)
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
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Line and one Point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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

            Vector_Center = centerVectorsPoint(points, info=0)
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
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Line and one point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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
    createFolders('WorkPlanes')
    error_msg = "Unable to create Plane : \nSelect one Plane and one Point only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects()
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
    createFolders('WorkPlanes')
    error_msg = "Unable to create Planes : \nSelect one Line and one Plane only !"
    result_msg = " : Plane created !"
    name = "WorkPlane"
    part = "Part::Feature"
    Selection = get_SelectedObjects(info=0)
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


def plot_clickForPlane():
    """ Create a Plane at location of one mouse click in the view or
    onto a clicked object or
    at a pre-selected point location.
    """
    createFolders('WorkPlanes')

    m_actDoc=get_ActiveDocument(info=1)
    if m_actDoc == None:
        printError_msg("No Active document selected !")
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
    createFolders('WorkPlanes')
    error_msg = "Unable to create Planes : \nSelect at least one objec !"
    result_msg = " : Planes created !"
    m_actDoc=App.activeDocument()
    message = "Active Document is : " + str(m_actDoc.Name)
    print_msg(message)
    if m_actDoc.Name == None:
        printError_msg("No Active document selected !")
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

def get_all_from_bounding_box(ori_X,ori_Y,ori_Z,length_X,length_Y,length_Z,info=0):
    """ returns 8 points ,12 edges and 6 planes from the bounding box
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

#    Part.Point()
#    myVertex = myShape.Vertexes[0]
#    print myVertex.Point
#    > Vector (3, 2, 0)
#    vec1 = Base.Vector(0,0,0)
#    vec2 = Base.Vector(10,0,0)
#    line = Part.Line(vec1,vec2)
#    edge = line.toShape()
#
#    edge1 = Part.makeLine((0,0,0), (10,0,0))
#    edge2 = Part.makeLine((10,0,0), (10,10,0))
#    wire1 = Part.Wire([edge1,edge2])
#    wire3.Length
#    > 40.0
#    wire3.CenterOfMass
#    > Vector (5, 5, 0)
#    wire3.isClosed()
#    > True
#    wire2.isClosed()
#    > False
#    face = Part.Face(wire3)
#    face.Area
#    > 99.999999999999972
#    face.CenterOfMass
#    > Vector (5, 5, 0)
#    face.Length
#    > 40.0
#    face.isValid()
#    > True
#    sface = Part.Face(wire2)
#    face.isValid()
#    > False

    m_list_of_edges = [ ( 0, 1), ( 1, 3), ( 3, 2), ( 2, 0),
                ( 4, 5), ( 5, 7), ( 7, 6), ( 6, 4),
                ( 0, 4), ( 1, 5), ( 3, 7), ( 2, 6) ]

    for i in m_list_of_edges:
        print_msg( str(i) )
        line = Part.Line(Points[i[0]], Points[i[1]])
        edge = line.toShape()
        wire = Part.Wire([edge])
        if info != 0:
            Part.show(wire)
        mid_point = wire.CenterOfMass
        length = wire.Length
        Edges.append( ( i[0], i[1], (Points[i[0]], Points[i[1]]), edge, mid_point, length ) )
#
#        Edges.append( ( 0, 1, (Points[0], Points[1]) ) )
#        Edges.append( ( 1, 3, (Points[1], Points[3]) ) )
#        Edges.append( ( 3, 2, (Points[3], Points[2]) ) )
#        Edges.append( ( 2, 0, (Points[2], Points[0]) ) )
#
#        Edges.append( ( 4, 5, (Points[4], Points[5]) ) )
#        Edges.append( ( 5, 7, (Points[5], Points[7]) ) )
#        Edges.append( ( 7, 6, (Points[7], Points[6]) ) )
#        Edges.append( ( 6, 4, (Points[6], Points[4]) ) )
#
#        Edges.append( ( 0, 4, (Points[0], Points[4]) ) )
#        Edges.append( ( 1, 5, (Points[1], Points[5]) ) )
#        Edges.append( ( 3, 7, (Points[3], Points[7]) ) )
#        Edges.append( ( 2, 6, (Points[2], Points[6]) ) )
    m_list_of_faces = [ (2, 11, 6, 10),
                        (0,  8, 4,  9),
                        (3,  8, 7, 11),
                        (1,  9, 5, 10),
                        (7,  4, 5,  6),
                        (3,  0,  1, 2) ]

    for i in m_list_of_faces:
        print_msg( str(i) )
        wire = Part.Wire([Edges[i[0]][3], Edges[i[1]][3], Edges[i[2]][3], Edges[i[3]][3] ])
        if wire.isClosed():
            face = Part.Face(wire)
            mid_point = face.CenterOfMass
            length = face.Length
            if info != 0:
                Part.show(face)
            Faces.append( ( i[0], i[1], i[2], i[3], (Edges[i[0]][3],Edges[i[1]][3],Edges[i[2]][3],Edges[i[3]][3]), face, mid_point, length ) )

    if info != 0:
        for m_i in range(len(Points)):
            print_point(Points[m_i], msg="Point_" + str(m_i) + " : ")
        for m_i in range(len(Edges)):
            print_msg("segment : " + str(Edges[m_i]))
        for m_i in range(len(Faces)):
            print_msg("face : " + str(Faces[m_i]))

    return Points, Edges, Faces


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


def plot_boundingBoxes():
    """Create bounding boxes around each of selected object(s).
    """
    msg=0
    createFolders('WorkBoxes')
    error_msg  = "Select at least one object !"
    result_msg = "Bounding box created !"

    m_actDoc=get_ActiveDocument(info=msg)
    if m_actDoc.Name == None:
        printError_msg("No Active document selected !")
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
    error_msg = "Unable to create a Cylinder : \nSelect one Axis AND one point only!"
    result_msg = " : Cylinder created !"
    name = "Cylinder"
    part = "Part::Feature"
    m_actDoc=get_ActiveDocument(info=msg)
    global m_diameterCylinder
    global m_lengthCylinder

    if m_actDoc.Name == None:
        printError_msg("No Active document selected !")
        return None

    Selection = get_SelectedObjects(info=msg)
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
    error_msg = "Unable to create a Cube : \nSelect one Axis AND one point only!"
    result_msg = " : Cube created !"
    name = "Cuboid"
    part = "Part::Feature"
    m_actDoc=get_ActiveDocument(info=msg)
    global m_lengthCube
    global m_widthCube
    global m_heightCube

    if m_actDoc.Name == None:
        printError_msg("No Active document selected !")
        return None

    Selection = get_SelectedObjects(info=msg)
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
        self.connections_for_button_pressed = {
                             "button_origin"               : "plot_originObject",

                             "button_object_center"        : "plot_centerObjectPoint",
                             "button_line_center"          : "plot_centerLinePoint",
                             "button_line_extrema"         : "plot_extremaLinePoint",
                             "button_point_on_line"        : "plot_alongLinePoint",
                             "button_circle_center"        : "plot_centerCirclePoint",
                             "button_face_center"          : "plot_centerFacePoint",
                             "button_line_face_point"      : "plot_lineFacePoint",
                             "button_point_line_point"     : "plot_pointLinePoint",
                             "button_point_face_point"     : "plot_pointFacePoint",
                             "button_click_for_point"      : "plot_clickForPoint",
                             "button_object_base_point"    : "plot_baseObjectPoint",

                             "button_object_axis"          : "plot_centerObjectAxes",
                             "button_twopoints_axis"       : "plot_twoPointsAxis",
                             "button_cylinder_axis"        : "plot_cylinderAxis",
                             "button_twolines_axis"        : "plot_twoLinesAxis",
                             "button_plane_axis"           : "plot_planeAxis",
                             "button_point_line_axis"      : "plot_pointLineAxis",
                             "button_line_point_axis"      : "plot_linePointAxis",
                             "button_line_plane_axis"      : "plot_linePlaneAxis",
                             "button_2Planes_axis"         : "plot_twoPlanesAxis",

                             "button_object_base_axes"     : "plot_baseObjectAxes",

                             "button_threepoints_plane"    : "plot_threePointsPlane",
                             "button_axisandpoint_plane"   : "plot_axisPointPlane",
                             "button_axis_point_plane"     : "plot_perpendicularAxisPointPlane",
                             "button_planeandpoint_plane"  : "plot_planePointPlane",
                             "button_planeandaxis_plane"   : "plot_planeAxisPlane",
                             "button_click_for_plane"      : "plot_clickForPlane",
                             "button_object_center_planes" : "plot_centerObjectPlanes",

                             "button_boundingboxes"        : "plot_boundingBoxes",
                             "button_boundingbox"          : "plot_boundingBox",
                             "button_cylinder_create"      : "plot_axisPointCylinder",
                             "button_cube_create"          : "plot_axisPointCube",

                             "button_alignview"            : "view_align",

                            }
        self.connections_for_text_changed = {
                             "distance_point_on_line"    : "distanceLinePoint",

                             "extension_twopoints_axis"  : "extensionTwoPointsAxis",
                             "extension_line_point_axis" : "extensionLinePointAxis",

                             "extension_planePointPlane" : "extensionPlanePointPlane",
                             "angle_planeandaxis_plane"  : "anglePlaneAxisPlane",

                             "diameter_cylinder"         : "diameterCylinder",
                             "length_cylinder"           : "lengthCylinder",
                             "section_cube"              : "sectionCube",
                             "height_cube"               : "heightCube",

                             "length_plane"              : "lengthPlane",
                             "width_plane"               : "widthPlane",
                            }

        for m_key, m_val in self.connections_for_button_pressed.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL("pressed()"),globals()[str(m_val)])


        for m_key, m_val in self.connections_for_text_changed.items():
            #print_msg( "Connecting : " + str(m_key) + " and " + str(m_val) )
            QtCore.QObject.connect(getattr(self.ui, str(m_key)),
                                   QtCore.SIGNAL(_fromUtf8("textChanged(QString)")),globals()[str(m_val)])
                                   #QtCore.SIGNAL(QtCore.QString.fromUtf8("textChanged(QString)")),globals()[str(m_val)])


        self.m_dialog.show()


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

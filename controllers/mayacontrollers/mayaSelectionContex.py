# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

"""
mayaSelectionContex.py
Created by Simon Breslav on 2011-09-27
Maya Selection Context, genarates callbacks when things are selected
in Maya 3D view
"""

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx
from controllers.mayacontrollers.mayaObjectManager import Mom

contextCmdName = "spMayaCtxCmd"


def selectionCallback(clientData):
        #print "mayaSelcectionContex: selectionCallback called"
        selectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(selectionList)
        selectionIter = OpenMaya.MItSelectionList(selectionList,
                                                  OpenMaya.MFn.kInvalid)
        decoratorList = []
        m = Mom()
        while not selectionIter.isDone():
                dependNode = OpenMaya.MObject()
                dagNode = OpenMaya.MFnDagNode()
                try:
                        selectionIter.getDependNode(dependNode)
                        if dependNode.isNull() or not dependNode.hasFn( \
                                                OpenMaya.MFn.kDependencyNode):
                            selectionIter.next()
                            continue
                        dagNode = OpenMaya.MFnDagNode(dependNode)
                except:
                        selectionIter.next()
                        continue
                if dagNode.name().startswith(m.decoratorTransformName):
                    if dagNode.name() not in decoratorList:
                        decoratorList.append(dagNode.name())
                selectionIter.next()
        m.staplePreDecoratorSelected(decoratorList)


class mayaSelctionContext(OpenMayaMPx.MPxSelectionContext):
    def __init__(self):
        OpenMayaMPx.MPxSelectionContext.__init__(self)

    def toolOnSetup(self, event):
        OpenMaya.MModelMessage.addCallback( \
                        OpenMaya.MModelMessage.kActiveListModified,
                                            selectionCallback, self)


class mayaSelctionCtxCmd(OpenMayaMPx.MPxContextCommand):
    def __init__(self):
        OpenMayaMPx.MPxContextCommand.__init__(self)

    def makeObj(self):
        return OpenMayaMPx.asMPxPtr(mayaSelctionContext())


def contextCmdCreator():
    return OpenMayaMPx.asMPxPtr(mayaSelctionCtxCmd())


# initialize the script plug-in
def initializePlugin(mobject):
    #print "mayaSelctionContext: initializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerContextCommand(contextCmdName, contextCmdCreator)
    except:
        print "Failed to register context command: %s" % contextCmdName
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    #print "mayaSelctionContext uninitializePlugin for helixManip called"
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterContextCommand(contextCmdName)
    except:
        print "Failed to deregister context command: %s" % contextCmdName
        raise
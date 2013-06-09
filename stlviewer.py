#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
from PySide import QtCore, QtGui, QtOpenGL
from numpy import *
import re, cmath

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "STL Viewer",
                            "PyOpenGL must be installed to run this application.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.glWidget = GLWidget()
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr('STL Viewer'))

class GLWidget(QtOpenGL.QGLWidget,QtGui.QWidget):
    triangles = []
    timerId= 0
    fieldSize = 20
    step = 2
    delay = 500
    cellsCount = 0
    pos = 1.0

    def __init__(self,parent=None):
        QtOpenGL.QGLWidget.__init__(self,parent)
        self.object = 0
        self.xRot = 2440
        self.yRot = 2160
        self.zRot = 0
        self.lastPos = QtCore.QPoint()
        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.open()

    def sizeRotation(self):
        return self.xRot

    def sizeRotation(self):
        return self.yRot

    def sizeRotation(self):
        return self.zRot

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.updateGL()

    def initializeGL(self):
        self.qglClearColor(self.trolltechPurple.darker())
        self.object = self.makeObject()
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glScalef(self.pos, self.pos, self.pos)
        glTranslated(0.0, 0.0, -20.0)
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        glCallList(self.object)

    def resizeGL(self, width, height):
        side = max(width, height)
        glViewport((width - side) / 2, (height - side) / 2, side, side)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-50, +50, +50, -50, -100.0, 500.0)
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())
        if event.buttons() & QtCore.Qt.RightButton:
            pass

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.pos += 0.1
        else:
            self.pos -= 0.1
        self.updateGL()

    def mouseMoveEvent(self,event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)
        self.lastPos = QtCore.QPoint(event.pos())

    def makeObject(self):
        genList = glGenLists(1)
        glNewList(genList, GL_COMPILE)
        self.axis()
        glEndList()
        return genList

    def timerEvent(self, event):
        self.updateGL()

    def axis(self):

        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glLineWidth(0.5)
        glColor3f(0.0,0.0,0.0)
        glBegin(GL_LINES)
        for i in range(self.fieldSize+1):
            glVertex3f(-100, 0, (float(i)*10)-100)
            glVertex3f(100, 0, (float(i)*10)-100)

        for i in range(self.fieldSize+1):
            glVertex3f((float(i)*10)-100, 0, -100)
            glVertex3f((float(i)*10)-100, 0, 100)
        glEnd()
        glDisable(GL_BLEND)
        glDisable(GL_LINE_SMOOTH)
        glLineWidth(1)
        glColor3f(1,0,0)
        glBegin(GL_LINES)
        glVertex3f(0,0,0.0)
        glVertex3f(0,100,0.0)
        glEnd()

        glColor3f(0,0,1)
        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3f(100,0,0)
        glEnd()

        glColor3f(0,1,0)
        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3f(0,0,100)
        glEnd()

        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.8, 0.1, 0.0, 1.0))
        glShadeModel(GL_FLAT)
        self.qglColor(self.trolltechGreen)
        glNormal3d(0, 0, 1)
        glBegin(GL_TRIANGLES)
        for triangel in self.triangles:
            glVertex3f(float(triangel[0]), float(triangel[1]), float(triangel[2]))
        glEnd()

    def open(self):
        fileName, filtr = QtGui.QFileDialog.getOpenFileName(self)
        if fileName:
            file = QtCore.QFile(fileName)
            if not file.open( QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                return False
            instr = QtCore.QTextStream(file)
            start = False
            width = 0
            lines = []
            while not instr.atEnd():
                line = instr.readLine()
                pattern = re.compile("vertex")
                if pattern.search(line):
                    triangel = re.findall('(-?\d+\.\d+e\+?-?\d+)', line)
                    if len(triangel):
                        self.triangles.append(triangel)
        return True

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

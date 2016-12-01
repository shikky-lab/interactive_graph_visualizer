#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import Qt
from PyQt4 import QtGui

class VerboseWidget(QtGui.QDockWidget):
	def __init__(self,*args,**kwargs):
		parent=kwargs.get("parent")
		QtGui.QWidget.__init__(self ,parent=parent)

		self.table=QtGui.QTableWidget()
		self.table.horizontalHeader().setVisible(False)
		self.table.verticalHeader().setVisible(False)
		self.table.horizontalHeader().setStretchLastSection(True)
		vbox = QtGui.QVBoxLayout(self)
		vbox.addWidget(self.table)    #add canvs to the layout
		self.table.setRowCount(2)
		self.table.setColumnCount(2)

def main():

    app = QtGui.QApplication(sys.argv)
    w = QtGui.QMainWindow()

    top_dock = QtGui.QDockWidget('Top',w)
    top_dock.setWidget(QtGui.QWidget())
    w.addDockWidget(Qt.Qt.TopDockWidgetArea, top_dock)

    left_dock = QtGui.QDockWidget('Left',w)
    left_dock.setWidget(QtGui.QWidget())
    w.addDockWidget(Qt.Qt.LeftDockWidgetArea, left_dock)

    right_dock = QtGui.QDockWidget('Right',w)
    right_dock.setWidget(QtGui.QWidget())
    w.addDockWidget(Qt.Qt.RightDockWidgetArea, right_dock)

    bottom_dock = QtGui.QDockWidget('Bottom',right_dock)
    bottom_dock.setWidget(QtGui.QWidget())
    #right_dock.addDockWidget(Qt.Qt.BottomDockWidgetArea, bottom_dock)

    center_widget = QtGui.QWidget()
    label = QtGui.QLabel('Center',center_widget)
    w.setCentralWidget(center_widget)

    w.resize(320,240)
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
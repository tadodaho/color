#!/usr/bin/python3
import sys
sys.path.append("icon/")
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QAction, QWidget, QSizePolicy, 
qApp, QDesktopWidget, QMainWindow, QMessageBox, QToolTip, 
QPushButton, QTextEdit, QVBoxLayout, QFileDialog, QGridLayout, QComboBox, QListWidget, QListWidgetItem, QLabel)
from PyQt5.QtCore import QCoreApplication, QUrl, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap, QDesktopServices 
from utils import openillum, openobs, calculation

ILLUMINANT = openillum('D65.data')
OBSERVER = openobs('1931.data')

class ListColors(QListWidget):
	def __init__(self):
		QListWidget.__init__(self)

class Color(QMainWindow):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.current_path = os.getcwd()

	def initUI(self):
		self.setWindowIcon(QIcon(sys.path[-1] + 'color_wheel.png'))
		self.figure = plt.figure()
		self.main_menu()
		self.control()
		self.resize(740, 480)
		self.setWindowTitle('Color')
		self.center()
		self.show()

	def center(self):
		frame_geometry = self.frameGeometry()
		center = QDesktopWidget().availableGeometry().center()
		frame_geometry.moveCenter(center)
		self.move(frame_geometry.topLeft())

	def btn_add_item(self, rgb, xyz, xyt):
		numpy_array = np.full((32, 32, 3), [np.uint8(int(rgb[0])), np.uint8(int(rgb[1])), np.uint8(int(rgb[2]))])
		h, w, _ = numpy_array.shape
		img = QImage(numpy_array, w, h, w * 3, QImage.Format_RGB888)
		item = QListWidgetItem()
		item.setText('RGB (%s, %s, %s)\n' % rgb + 'XYZ (%s, %s, %s)\n' % xyz + 'xyY (%s, %s, %s)' % xyt)
		item.setIcon(QIcon(QPixmap.fromImage(img)))
		self._list.insertItem(self._list.count()+1, item)

	def plot(self, fname, rgb, x=None, y=None):
		fname = fname[0].split('/')[-1].split('.')[0]
		ax = self.figure.add_subplot(111)
		ax.set_xlim(380, 780)
		ax.set_ylim(0, 1.0)
		ax.set_xlabel('Wavelength, nm')
		ax.set_ylabel('Transmittance')
		ax.grid(True)
		lines = ax.plot(x, y, '-', color=(rgb[0]/255, rgb[1]/255, rgb[2]/255), label=fname)
		ax.legend()
		self.canvas.draw()

	def remove_item(self):
		list_items=self._list.selectedItems()
		if not list_items: return        
		for item in list_items:
			self._list.takeItem(self._list.row(item))
		for i in self.figure.axes:
			i.lines[0].remove()
		self.canvas.draw()

	def clear_all(self):
		self._list.clear()
		self.figure.clear()
		self.canvas.draw()

	def getfile(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', self.current_path, "Text files (*.txt *.lr *.data)")
		try:
			with open(fname[0], 'r') as f:
				result = f.read().rsplit()
		except FileNotFoundError:
			pass
		else:
			nm = []
			coeff = []
			for i in range(len(result)):
				if i % 2 == 0:
					nm.append(int(result[i]))
					continue
				coeff.append(float(result[i]))
			rgb, xyt, xyz = calculation(coeff, OBSERVER, ILLUMINANT)
			self.btn_add_item(rgb, xyz, xyt)
			self.plot(fname, rgb, nm, coeff)
	
	def open_url(self):
		url = QUrl('https://github.com/tadodaho/color')
		if not QDesktopServices.openUrl(url):
			QMessageBox.warning(self, 'Warning', 'Could not open url')

	def main_menu(self):
		exit_action = QAction(QIcon(sys.path[-1] + 'exit.png'), '&Exit', self)
		exit_action.setShortcut('Ctrl+Q')
		exit_action.setStatusTip('Quit this program')
		exit_action.triggered.connect(qApp.quit)

		visit_git = QAction(QIcon(sys.path[-1] + 'github.png'), '&Github', self)
		visit_git.setStatusTip('Visit page projects on GitHub')
		visit_git.triggered.connect(self.open_url)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exit_action)
		helpMenu = menubar.addMenu('&Help')
		helpMenu.addAction(visit_git)
		self.statusBar()

	def control(self):
		self.canvas = FigureCanvas(self.figure)
		self._list = ListColors()
		button_clear_all = QPushButton('Clear all')
		button_clear_all.clicked.connect(self.clear_all)

		label_observ = QLabel('Standard colorimetric observer')
		cmbox_observ = QComboBox()
		cmbox_observ.addItems(['CIE 1931', 'CIE 1964'])

		label_ill = QLabel('Standard Illuminant')
		cmbox_ill = QComboBox()
		cmbox_ill.addItems(['D65', 'A'])

		button_add = QPushButton()
		button_add.setIcon(QIcon(sys.path[-1] + 'add.png'))
		button_add.clicked.connect(self.getfile)

		layout = QGridLayout()
		layout.setHorizontalSpacing(45)
		layout.setSpacing(17)
		layout.addWidget(self.canvas,  0, 0, 18, 40)
		layout.addWidget(label_observ,      0, 40, 1, 1)
		layout.addWidget(cmbox_observ,   0, 41, 1, 3)

		layout.addWidget(label_ill,  1, 40, 1, 1)
		layout.addWidget(cmbox_ill, 1, 41, 1, 3)

		layout.addWidget(self._list,   2, 40, 15, 3)
		layout.addWidget(button_add,   2, 43, 1, 1)
		layout.addWidget(button_clear_all, 17, 41, 1, 1)
		central_widget = QWidget(self)
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Color()
	sys.exit(app.exec_())
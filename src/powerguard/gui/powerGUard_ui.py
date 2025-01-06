# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'powerGUard.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1118, 859)
        self.actionNew_Project = QAction(MainWindow)
        self.actionNew_Project.setObjectName(u"actionNew_Project")
        self.actionOpen_Project = QAction(MainWindow)
        self.actionOpen_Project.setObjectName(u"actionOpen_Project")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(MainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionExport_muav = QAction(MainWindow)
        self.actionExport_muav.setObjectName(u"actionExport_muav")
        self.actionImport_muav = QAction(MainWindow)
        self.actionImport_muav.setObjectName(u"actionImport_muav")
        self.actionNew_Requirement = QAction(MainWindow)
        self.actionNew_Requirement.setObjectName(u"actionNew_Requirement")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 1101, 831))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(330, 50, 391, 161))
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btnServer = QPushButton(self.frame)
        self.btnServer.setObjectName(u"btnServer")
        self.btnServer.setGeometry(QRect(140, 250, 281, 121))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1118, 33))
        self.menuProject = QMenu(self.menubar)
        self.menuProject.setObjectName(u"menuProject")
        self.menuRequirement = QMenu(self.menubar)
        self.menuRequirement.setObjectName(u"menuRequirement")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuRequirement.menuAction())
        self.menuProject.addAction(self.actionNew_Project)
        self.menuProject.addAction(self.actionOpen_Project)
        self.menuProject.addAction(self.actionSave)
        self.menuProject.addAction(self.actionSave_as)
        self.menuProject.addAction(self.actionExport_muav)
        self.menuProject.addAction(self.actionImport_muav)
        self.menuProject.addAction(self.actionPreferences)
        self.menuRequirement.addAction(self.actionNew_Requirement)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"UAV Designer", None))
        self.actionNew_Project.setText(QCoreApplication.translate("MainWindow", u"New Project", None))
        self.actionOpen_Project.setText(QCoreApplication.translate("MainWindow", u"Open Project", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_as.setText(QCoreApplication.translate("MainWindow", u"Save as", None))
        self.actionExport_muav.setText(QCoreApplication.translate("MainWindow", u"Export .uav", None))
        self.actionImport_muav.setText(QCoreApplication.translate("MainWindow", u"Import .uav", None))
        self.actionNew_Requirement.setText(QCoreApplication.translate("MainWindow", u"New Requirement", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Power Guard", None))
        self.btnServer.setText(QCoreApplication.translate("MainWindow", u"Start Server", None))
        self.menuProject.setTitle(QCoreApplication.translate("MainWindow", u"Project", None))
        self.menuRequirement.setTitle(QCoreApplication.translate("MainWindow", u"Requirement", None))
    # retranslateUi


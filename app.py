import sys
import typing
import uuid
from PyQt5 import QtCore

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPicture, QPainter, QPen, QBrush, QPolygonF, QColor, QPainterPath
from PyQt5.QtWidgets import QApplication, QToolBar, QCheckBox, QStyle, QToolButton, QMessageBox, QFrame, QWidget, QLabel, QSlider, QGraphicsScene, QDockWidget, QMainWindow, QMenu, QPushButton, QAction, QHBoxLayout, QInputDialog, QVBoxLayout, QGraphicsView
import pyqtgraph as pg
from enum import Enum
from functools import *
import qdarktheme
from math import sqrt, pow, sin, cos, acos, degrees, radians, asin, pi

class GeometryType(Enum):
    SIDE = 1
    ANGLE = 2

class ActionType(Enum):
    ADD_ANGLE = GeometryType.ANGLE
    ADD_SIDE = GeometryType.SIDE
    RESOLVE_TRIANGLE = 3
    REMOVE_TRIANGLE = 4

class Geometry():
    def __init__(self, type: GeometryType , value: float):
        self.type = type
        self.uid = str(uuid.uuid4())
        self.value = value
        self.between = False
    
class Triangle(pg.GraphicsObject):
    def __init__(self, x1, y1, x2, y2, x3, y3, color):
        super().__init__()
        self.pen = QPen()
        self.pen.setWidthF(x2/200)
        self.pen.setJoinStyle(Qt.MiterJoin)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.picture = QPicture()
        self.painter = QPainter(self.picture)
        self.triangle = QPolygonF([QPointF(x1, y1,),QPointF(x2, y2,), QPointF(x3, y3,) ])
        self._generate_picture(color)


    def _generate_picture(self, color):
        self.brush = QBrush(color)
        self.painter.setPen(self.pen)
        
        self.painter.setBrush(self.brush)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.painter.drawPolygon(self.triangle)
        self.painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

class Helper():
    def __init__(self, *args, **kwargs):
        self.lightblue = QColor(173, 216, 230, 120)
        self.lightcoral = QColor(240, 128, 128, 120)

    def errorBox(self, text):
        errorBox = QMessageBox()
        errorBox.setWindowTitle("Errore")
        errorBox.setText(text)
        errorBox.exec_()

class Resolver():
    def __init__(self, helper):
        self.helper = helper

    def LLL(self, a, b, c):
        a,b,c = a, b, c
        if a<b+c or b<a+c or c<a+b:    
            try:
                print(f"{a=}")
                print(f"{b=}")
                print(f"{c=}")
                alpha = degrees(acos((pow(c,2) - pow(a,2) - pow(b,2))/(-2*a*b)))
                beta = degrees(acos((pow(b,2) - pow(a,2) - pow(c,2))/(-2*a*c)))
                gamma = degrees(acos((pow(a,2) - pow(b,2) - pow(c,2))/(-2*b*c)))
                return alpha, beta, gamma
            except:
                return
        return
    
    def LAL(self, side1, angle1, side2):
        # calcolo lato mancante
        side3 = sqrt(pow(side1, 2)+pow(side2,2) - 2*side1*side2*cos(radians(angle1)))
        # calcolo dei 2 angoli mancanti
        angle2 = degrees(asin((side2*sin(radians(angle1)))/side3)) # beta
        angle3 = degrees(asin((side1*sin(radians(angle1)))/side3)) # gamma 
        return angle2, angle3, side3

    # l'angolo specificato è adiacente al secondo lato
    def LLA(self, a, b, alpha):
        sin_beta = (b/a)*sin(radians(alpha))
        alpha = radians(alpha)
        if sin_beta > 1:
            self.helper.errorBox("Triangolo impossibile")
        if sin_beta == 1:
            if radians(alpha) >= pi/2:        
                self.helper.errorBox("Triangolo impossibile")
            # 1 soluzione
            else:
                beta = asin(sin_beta)
                gamma = pi - beta - radians(alpha)
                c = a * sin(gamma)/sin(alpha)
                return [(degrees(beta), degrees(gamma), c)] 
        # fino a 2 possibili soluzioni
        elif sin_beta < 1 and sin_beta > 0:
            beta = asin(sin_beta)
            gamma = pi - beta - alpha            
            # 1 soluzione (angolo acuto) 
            if alpha >= pi/2 or (alpha < pi/2 and b < a) or b == a:
                gamma = pi - beta - alpha
                c = a * sin(gamma)/sin(alpha)
                return [(degrees(beta), degrees(gamma), c)]
            # 2 soluzioni
            elif alpha < pi/2 and b > a:
                beta2 = pi - beta
                gamma2 = pi - beta2 - alpha
                c1 = a * sin(gamma)/sin(alpha)
                c2 = a * sin(gamma2)/sin(alpha)
                return [(degrees(beta), degrees(gamma),c1), (degrees(beta2), degrees(gamma2), c2)]

    def ALA(self, angle1, side1, angle2):
        angle1 = radians(angle1)
        angle2 = radians(angle2)
        angle3 = pi - angle1 - angle2
        side2 = (sin(angle1) * side1)/sin(angle3)
        side3 = (sin(angle2) * side1)/sin(angle3)
        return degrees(angle3), side2, side3
    
    def AAL(self, angle1, angle2, side1):
        angle1 = radians(angle1)
        angle2 = radians(angle2)
        angle3 = pi - angle1 - angle2
        side2 = (side1/sin(angle1))*sin(angle2)
        side3 = (side1/sin(angle1))*sin(angle3)
        return degrees(angle3), side2, side3


class DockElement(QFrame):

    def __init__(self, text, geometry: Geometry, **kwargs):
        super().__init__()
        self.geometry = geometry
        self.checkbox = QCheckBox()
        self.checkbox.setText("compreso tra gli altri 2")
        self.setFrameShape(QFrame.StyledPanel)
        if "kwargs" in kwargs["kwargs"]:
            self.setStyleSheet(f"background-color: {kwargs['kwargs']['kwargs']};")
        self.label = QLabel(text)
        self.hbox = QHBoxLayout()
        self.button = QToolButton()
        self.icon = self.style().standardIcon(QStyle.SP_BrowserStop)
        self.button.setIcon(self.icon)
        self.hbox.addWidget(self.button)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.label)
        self.setLayout(self.hbox)
        self.hbox.addLayout(self.vbox)

    def update_geometry(self, x):
        if x==2:
            self.geometry.between = True
        elif x==0:
            self.geometry.between = False

    def updateUI(self):
        if self.checkbox != None:
            self.vbox.removeWidget(self.checkbox)
            self.checkbox.deleteLater()
            self.checkbox = None

        if self.geometry.between:
            self.checkbox = QCheckBox()
            self.checkbox.setText("compreso tra gli altri 2")
            self.vbox.addWidget(self.checkbox)
            self.checkbox.stateChanged.connect(self.update_geometry)
            self.checkbox.setChecked(self.geometry.between)
            
        
class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.triangle = []
        self.is_check = False
        self.helper = Helper()
        self.resolver = Resolver(self.helper)
        self.setWindowTitle("Risolutore di triangoli")
        self.setGeometry(0,0,720, 480)
        self.setupLayout()
        self.createActions()
        self.createToolBar()
        self.connectActions()


    def order_dock(self):
        angle_elements = []
        side_elements = []
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            if myWidget.geometry.type == GeometryType.ANGLE:
                angle_elements.append(myWidget)
            elif myWidget.geometry.type == GeometryType.SIDE:
                side_elements.append(myWidget)
        new_elements = side_elements + angle_elements
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            new_geometry = new_elements[i].geometry
            new_text = new_elements[i].label.text()
            myWidget.text = new_text
            myWidget.new_geometry = new_geometry
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.label.setText(myWidget.text)
            myWidget.geometry = myWidget.new_geometry
    
    def update_toolbar(self):
        if len(self.triangle)==3:
            for action in self.toolBar.actions():
                #print(type(action.data()))
                if type(action.data()) == GeometryType:
                   action.setDisabled(True)
                else:
                    action.setEnabled(True)
            self.toolBar.actions()[3].setDisabled(True)
        elif len(self.triangle) < 3:
            for action in self.toolBar.actions():
                if type(action.data()) == GeometryType:
                    action.setEnabled(True)
                elif type(action.data()) == ActionType:
                    action.setDisabled(True)

            self.toolBar.actions()[3].setDisabled(True)
        elif len(self.triangle) == 6 or len(self.triangle) == 9:
            for action in self.toolBar.actions():
                action.setDisabled(True)
            
            self.toolBar.actions()[3].setEnabled(True)
        else:
            for action in self.toolBar.actions():
                action.setDisabled(True)
            self.toolBar.actions()[3].setDisabled(True)

    def draw_triangle(self, is_between):
        side_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.SIDE]
        angle_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.ANGLE]   
        #print(f"{side_list=}")
        #print(f"{angle_list=}")
        if is_between == False:
            self.graph_triangle = Triangle(0, 0, side_list[0], 0, side_list[1]*cos(radians(angle_list[2])), side_list[1]*sin(radians(angle_list[2])), self.helper.lightblue)
            self.graphWidget.addItem(self.graph_triangle)
            if len(angle_list) > 3:
                self.graph_triangle2 = Triangle(0, 0, side_list[0], 0, side_list[1]*cos(radians(angle_list[4])), side_list[1]*sin(radians(angle_list[4])), self.helper.lightcoral)
                self.graphWidget.addItem(self.graph_triangle2)
        else:
            self.graph_triangle = Triangle(0, 0, side_list[0], 0, side_list[1]*cos(radians(angle_list[0])), side_list[1]*sin(radians(angle_list[0])), self.helper.lightblue)
            self.graphWidget.addItem(self.graph_triangle)
            

    def calculate_triangle(self):
        self.is_between = False
        side_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.SIDE]
        angle_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.ANGLE]
        if len(self.triangle) < 3 or len(self.triangle) > 3:
            self.helper.errorBox("Sono richiesti esattamente 3 parametri")
            return -1
        # caso AAA
        if len(angle_list) == 3:         
            self.helper.errorBox("Esiste un numero infinito di triangolo dati 3 angoli")
            return -1
        # caso LLL
        if len(side_list) == 3:
            result = self.resolver.LLL(side_list[0], side_list[1], side_list[2])
            if result:
                for angle in result:
                    self.add_parameter(GeometryType.ANGLE, angle)
                return result
            else:
                self.helper.errorBox("I lati non rispettano la disuguaglianza triangolare")
                return 
        # caso LAL e LLA
        # se sono dati 2 lati e un angolo
        if len(angle_list) == 1 and len(side_list) == 2:
            self.is_between = False
            # controlla se l'angolo è compreso
            for geometry in self.triangle:
                if geometry.between:
                    self.is_between = True
            if self.is_between:
                result = self.resolver.LAL(side_list[0], angle_list[0], side_list[1]) 
                #print(result)
                if result:
                    for x in result[0:2]:
                        self.add_parameter(GeometryType.ANGLE, x)
                self.add_parameter(GeometryType.SIDE, result[2])
                return result
            #print("between")
            result = self.resolver.LLA(side_list[0], side_list[1], angle_list[0])
            #print(result)
            if result:
                for n in range(len(result)):
                    #print(n)
                    color = "lightgreen"
                    if len(result) == 2:
                        if n == 0:
                            color = "lightblue"
                        elif n == 1:
                            color = "lightcoral"
                    for x in result[n][0:2]:
                        self.add_parameter(GeometryType.ANGLE, x, kwargs=color)
                    self.add_parameter(GeometryType.SIDE, result[n][2], kwargs=color)
            #if result == -1:
            #self.helper.errorBox("Il triangolo è ambiguo")                        
            return result 
    
        if len(angle_list) == 2 and len(side_list) == 1:
            if radians(angle_list[0]) + radians(angle_list[1]) >= pi:
                self.helper.errorBox("La somma dei 2 angoli deve essere minore di 180°")
                return
            self.is_between = False
            for geometry in self.triangle:
                if geometry.between:
                    self.is_between = True
            if self.is_between:
                result = self.resolver.ALA(angle_list[0], side_list[0], angle_list[1])
                if result:
                    self.add_parameter(GeometryType.ANGLE, result[0])
                    for x in result[1:3]:
                        self.add_parameter(GeometryType.SIDE, x)
                    return result
            result = self.resolver.AAL(angle_list[0], angle_list[1], side_list[0])
            if result:
                self.add_parameter(GeometryType.ANGLE, result[0])
                for x in result[1:3]:
                    self.add_parameter(GeometryType.SIDE, x)
                return result
            
    def resolve_triangle(self):
        result = self.calculate_triangle()
        if result:
            #if len(angle_list) <= 3:
            #    self.order_dock()
            self.draw_triangle(self.is_between)
            for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                myWidget.geometry.between = False
                myWidget.updateUI()
            self.update_toolbar()
            

    def clearLayout(self):
        self.triangle = []
        for action in self.toolBar.actions():
            #print(type(action.data()))
            if type(action.data()) == GeometryType:
                action.setEnabled(True)
            else:
                action.setDisabled(True)
        self.toolBar.actions()[3].setDisabled(True)
        self.graphWidget.removeItem(self.graph_triangle)
        try:
            self.graphWidget.removeItem(self.graph_triangle2)
        except:
            pass       
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.deleteLater()    

    def remove_parameter(self, e: DockElement):
        # 1 disabilita l'opzione compreso
        # 2 aggiorna la ui di ogni dockelement
        uids = [geometry.uid for geometry in self.triangle]
        for geometry in self.triangle:
            if geometry.uid == e.geometry.uid:
                self.triangle.remove(geometry)
        e.setParent(None)
        if len(self.triangle) == 3:
            angles_count=0
            sides_count=0
            for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                if myWidget.geometry.type == GeometryType.ANGLE:
                    angles_count += 1
                elif myWidget.geometry.type == GeometryType.SIDE:
                    sides_count += 1
            if angles_count == 1:
                for i in range(self.vLayout.count()-1):
                    myWidget = self.vLayout.itemAt(i).widget()
                    if myWidget.geometry.type == GeometryType.ANGLE:
                        myWidget.geometry.between = True
                    else:
                        myWidget.geometry.between = False
            elif sides_count == 1:
                for i in range(self.vLayout.count()-1):
                    myWidget = self.vLayout.itemAt(i).widget()
                    if myWidget.geometry.type == GeometryType.SIDE:
                        myWidget.geometry.between = True
                    else:
                        myWidget.geometry.between = False
            
        if len(self.triangle) == 5:
            self.graphWidget.removeItem(self.graph_triangle)
        if len(self.triangle) == 8:
            self.graphWidget.removeItem(self.graph_triangle)
            self.graphWidget.removeItem(self.graph_triangle2)
            
        if len(self.triangle) == 2:
            for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                myWidget.geometry.between = False
        for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                myWidget.setStyleSheet("")
                myWidget.updateUI()
        self.update_toolbar()

    def add_parameter(self, data: GeometryType, value, **kwargs):
        # 1 sceglie a quale geometria aggiungere l'opzione compreso (solo se ci sono 3 geometrie)
        # 2 aggiunge il nuovo dockelement al dock
        # 3 aggiorna la ui di ogni dockelement
        new_geometry = Geometry(data, value)
        self.triangle.append(new_geometry)
        self.update_toolbar()
        # controlla se aggiungere l'opzione compreso a uno dei parametri
        if len(self.triangle) == 3:
            # se tutti i parametri sono dello stesso tipo non c'è bisogno di specificare se l'angolo/il lato è compreso
            if all(geometry.type==GeometryType.ANGLE for geometry in self.triangle) != True or all(geometry.type==GeometryType.SIDE for geometry in self.triangle) != True:
                unique_angle = [x for x in self.triangle if x.type == GeometryType.ANGLE]
                unique_side = [y for y in self.triangle if y.type == GeometryType.SIDE]
                # non possono essere entrambe vere
                if len(unique_angle) == 1:
                    for x in self.triangle:
                        if x.type == GeometryType.ANGLE :
                            x.between = True
                elif len(unique_side) == 1:
                    for y in self.triangle:
                        if y.type == GeometryType.SIDE :
                            y.between = True
        # add the dockelement to the dock                    
        if new_geometry.type==GeometryType.ANGLE:
            e = DockElement("Angolo: {v:.1f}°".format(v=new_geometry.value), new_geometry, kwargs=kwargs)
        elif new_geometry.type==GeometryType.SIDE:
            e =  DockElement("Lato: {v:.1f}".format(v=new_geometry.value), new_geometry, kwargs=kwargs)
        e.button.clicked.connect(partial(self.remove_parameter, e))
        self.vLayout.insertWidget(self.vLayout.count()-1, e)
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.updateUI()
            
    def select_parameter(self, data: GeometryType):
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.IntInput)
        dlg.setWindowTitle("Aggiungi Parametro")
        dlg.setLabelText("Inserisci un valore:")
        if data == GeometryType.SIDE:
            dlg.setIntRange(1, 1000)
        elif data == GeometryType.ANGLE:
            dlg.setIntRange(1, 179)
        dlg.intValueSelected.connect(partial(self.add_parameter, data))
        dlg.exec()
    
    def setupLayout(self):        
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked(ratio=1)
        self.setCentralWidget(self.graphWidget)

        pen = pg.mkPen(color=(255, 0, 0),width=5)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')
        self.vLayout = QVBoxLayout()
        self.vLayout.addStretch()
        self.vWidget = QWidget()
        self.vWidget.setLayout(self.vLayout)
        self.dockWidget = QDockWidget("Parametri", self)
        self.dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                                       Qt.RightDockWidgetArea)
        self.dockWidget.setMinimumWidth(120)
        self.dockWidget.sizeHint()
        self.dockWidget.setWidget(self.vWidget)
        self.dockWidget.setFeatures(QDockWidget.DockWidgetFloatable | 
                 QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        
    def connectActions(self):
        for action in self.toolBar.actions():
            if action.data() == ActionType.RESOLVE_TRIANGLE:
                action.triggered.connect(self.resolve_triangle)
            if action.data() == ActionType.REMOVE_TRIANGLE:
                action.triggered.connect(self.clearLayout)
            elif action.data() == GeometryType.ANGLE or action.data() == GeometryType.SIDE:
                action.triggered.connect(partial(self.select_parameter, action.data()))
                
    def createActions(self):
        # menu opzioni
        self.resolveAction = QAction(self)
        self.resolveAction.setText("&Risolvi triangolo")
        self.resolveAction.setData(ActionType.RESOLVE_TRIANGLE)
        self.resolveAction.setDisabled(True)
        self.deleteAction = QAction(self)
        self.deleteAction.setText("&Cancella triangolo")
        self.deleteAction.setData(ActionType.REMOVE_TRIANGLE)
        self.deleteAction.setDisabled(True)

        # menu angoli e lati
        self.addAngleAction = QAction("Aggiungi Angolo", self)
        self.addAngleAction.setData(GeometryType.ANGLE) # uguale a ActionType.ADD_ANGLE
        self.addSideAction = QAction("Aggiungi Lato", self)
        self.addSideAction.setData(GeometryType.SIDE) # uguale a ActionType.ADD_SIDE

    def createToolBar(self):
        # create tool bar
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        # add actions to tool bar
        self.toolBar.addActions([ self.resolveAction, self.addAngleAction, self.addSideAction, self.deleteAction])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme(theme="light")
    win = Window()
    win.show()
    sys.exit(app.exec_())

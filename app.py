import sys
import typing
import uuid
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QPointF, QRectF, QLineF, QRegExp
from PyQt5.QtGui import QPicture, QPainter,QFont, QPen, QBrush, QPolygonF, QColor, QPainterPath, QIntValidator, QDoubleValidator, QKeySequence, QTextOption, QLinearGradient
from PyQt5.QtWidgets import *
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

class ErrorCode:
    INSUFFICIENT_PARAMETERS = 1
    INVALID_PARAMETERS = 2
    TRIANGLE_INEQUALITY = 3
    INVALID_ANGLES = 4
    DUPLICATE_ARGUMENTS = 5
    INFINITE_TRIANGLES = 6
    IMPOSSIBLE_CONSTRUCTION = 7

class Geometry():
    def __init__(self, type: GeometryType , name, value):
        self.type = type
        self.uid = str(uuid.uuid4())
        self.value = value
        self.name = name
        self.static = False
        self.between = False
    
class Triangle(pg.GraphicsObject):
    def __init__(self, x1, y1, x2, y2, x3, y3, alfa, beta, gamma, color, *args):
        super().__init__()
        self.pen = QPen()
        self.pen.setWidthF(0.1)
        self.pen.setJoinStyle(Qt.MiterJoin)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.picture = QPicture()
        self.painter = QPainter(self.picture)
        if len(args) > 0:
            self.triangle = QPolygonF([QPointF(x1, y1,),QPointF(x2, y2,), QPointF(x3, y3,) ])
            self.brush = QBrush(color)
            self.painter.setPen(self.pen)
            self.painter.setBrush(self.brush)
            self.painter.drawPolygon(self.triangle, Qt.WindingFill)
            self.painter.end()
        else:   
            self.painter.scale(1,-1)

            # draw angles        
            self.drawAngle(0,0, 3, 0, alfa, QColor(0,100,0,100))
            self.drawAngle(x2, y2, 3, 180, -beta, QColor(0,0,255,100))
            new_gamma = gamma
            #if gamma > 90:
            #    new_gamma = 90 + gamma
            self.drawAngle(x3, y3, 3, -beta, -new_gamma, QColor(255,0,0,100))

            
            #self.drawText(x2, y2-1.5, "β")
            #self.drawText(x3, y3+0.75, "γ")
            
            self.painter.setPen(Qt.black)
            self.painter.setFont(QFont('Arial', 1))
            
            # draw text
            self.drawText(x1, y1-1.5, "α")
            self.drawText(x2, y2-1.5, "β")
            self.drawText(x3, y3+0.75, "γ")

            
            ax = x3+(x2-x3)/2
            ay = abs((y2-y3)/2)
            self.drawText(ax+1, ay+1, "a")

            bx = (x3-x1)/2
            by = abs((y3-y1)/2)
            self.drawText(bx-1, by+1, "b")
        
            cx = x2/2
            cy = -1.5
            self.drawText(cx-1, cy, "c")
            
            # setup paint options
            self.brush = QBrush(color)
            self.painter.scale(1,-1)
            self.painter.setRenderHint(QPainter.Antialiasing)
            self.painter.setBrush(self.brush)

            # draw lines
            # lato a
            self.pen.setColor(Qt.red)
            self.painter.setPen(self.pen)
            self.painter.drawLine(QLineF(x1, y1, x2, y2))
            # lato c
            self.pen.setColor(Qt.darkGreen)
            self.painter.setPen(self.pen)
            self.painter.drawLine(QLineF(x2, y2, x3, y3))
            # lato b
            self.pen.setColor(Qt.blue)
            self.painter.setPen(self.pen)
            self.painter.drawLine(QLineF(x1, y1, x3, y3))
            
            # draw points
            self.dotpen = QPen(Qt.black, 0.2 , Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin)
            # punto A
            self.dotpen.setColor(Qt.darkGreen)
            self.painter.setPen(self.dotpen)         
            self.painter.drawPoint(QPointF(x1, y1))
            # punto B
            self.dotpen.setColor(Qt.blue)
            self.painter.setPen(self.dotpen)         
            self.painter.drawPoint(QPointF(x2, y2))
            # punto C
            self.dotpen.setColor(Qt.red)
            self.painter.setPen(self.dotpen)         
            self.painter.drawPoint(QPointF(x3, y3))

            self.painter.end()

    def drawAngle(self, x, y, radius, startAngle, angle, color):
        myBrush = QBrush()
        myBrush.setColor(color)
        myBrush.setStyle(Qt.SolidPattern)
        myPen = QPen()
        myPen.setColor(QColor(255,255,255,255))
        startPoint = QPointF()
        center = QPointF(0, 0)
        myPath = QPainterPath()
        myPath.moveTo(center)
        myPath.arcTo(QRectF(-radius,-radius,radius*2, radius*2), startAngle,
                    angle)
        myPath.translate(x,-y)
        myPen.setWidthF(0.01)
        self.painter.setBrush(myBrush)
        self.painter.setPen(myPen)
        self.painter.drawPath(myPath)

    def drawText(self, x, y, text):
        self.painter.drawText(QRectF(x-25, -y-25, 50, 50), text, QTextOption(Qt.AlignCenter))
         
    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        bounds = self.picture.boundingRect()
        return QRectF(bounds.x()-19, bounds.y()-19, bounds.width()+40, bounds.height()+40)

class Helper():
    def __init__(self, *args, **kwargs):
        self.lightblue = QColor(173, 216, 230, 120)
        self.lightcoral = QColor(240, 128, 128, 120)
        self.lightyellow = QColor(255,255,153)

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
                alpha = degrees(acos((pow(a,2) - pow(b,2) - pow(c,2))/(-2*b*c)))
                beta = degrees(acos((pow(b,2) - pow(a,2) - pow(c,2))/(-2*a*c)))
                gamma = degrees(acos((pow(c,2) - pow(a,2) - pow(b,2))/(-2*a*b)))
                return [alpha, beta, gamma]
            except Exception as error:
                raise Exception(int(ErrorCode.INVALID_PARAMETERS)) from error
        raise Exception(int(ErrorCode.TRIANGLE_INEQUALITY))
    
    def LAL(self, above, alfa, below):
        # calcolo lato mancante
        opposite = sqrt(pow(above, 2)+pow(below,2) - 2*above*below*cos(radians(alfa)))
        # calcolo dei 2 angoli mancanti
        beta = degrees(acos((pow(opposite, 2) + pow(below,2) - pow(above, 2))/(2*opposite*below)))
        gamma = 180 - alfa - beta        
        return [opposite, beta, gamma]

    # l'angolo specificato è adiacente al secondo lato
    def LLA(self, a, b, alpha):
        sin_beta = (b/a)*sin(radians(alpha))
        alpha = radians(alpha)
        if sin_beta > 1:
            raise Exception(ErrorCode.IMPOSSIBLE_CONSTRUCTION)
            
        if sin_beta == 1:
            if radians(alpha) >= pi/2:        
                raise Exception(ErrorCode.IMPOSSIBLE_CONSTRUCTION)
            # 1 soluzione
            else:
                beta = asin(sin_beta)
                gamma = pi - beta - radians(alpha)
                c = a * sin(gamma)/sin(alpha)
                return [c, degrees(gamma), degrees(beta)]
        # fino a 2 possibili soluzioni
        elif sin_beta < 1 and sin_beta > 0:
            beta = asin(sin_beta)
            gamma = pi - beta - alpha            
            # 1 soluzione (angolo acuto) 
            if alpha >= pi/2 or (alpha < pi/2 and b < a) or b == a:
                gamma = pi - beta - alpha
                c = a * sin(gamma)/sin(alpha)
                return [degrees(beta), degrees(gamma), c]
            # 2 soluzioni
            elif alpha < pi/2 and b > a:
                beta2 = pi - beta
                gamma2 = pi - beta2 - alpha
                c1 = a * sin(gamma)/sin(alpha)
                c2 = a * sin(gamma2)/sin(alpha)
                return [(degrees(beta), degrees(gamma),c1), (degrees(beta2), degrees(gamma2), c2)]

    def ALA(self, alfa, c, beta):
        alfa = radians(alfa)
        beta = radians(beta)
        gamma = pi - alfa - beta
        a = (sin(alfa) * c)/sin(gamma)
        b = (sin(beta) * c)/sin(gamma)
        return [degrees(gamma), a, b]
    
    def AAL(self, alfa, gamma, c):
        alfa = radians(alfa)
        gamma = radians(gamma)
        beta = pi - alfa - gamma
        b = (c/sin(gamma))*sin(beta)
        a = (c/sin(gamma))*sin(alfa)
        return [degrees(beta), a, b]

class DockElement(QFrame):

    def __init__(self, geometry, static):
        super().__init__()
        self.isStatic = static
        self.geometry = geometry
        self.checkbox = QCheckBox()
        self.checkbox.setText("compreso tra gli altri 2")
        self.setFrameShape(QFrame.StyledPanel)
        self.hbox = QHBoxLayout()
        self.button = QToolButton()
        self.icon = self.style().standardIcon(QStyle.SP_BrowserStop)
        self.button.setIcon(self.icon)
        self.hbox.addWidget(self.button)
        self.vbox = QVBoxLayout()
        
        self.setLayout(self.hbox)

        self.textLabel = QLabel()
        self.valueLabel = QLabel()
        self.labelBox = QHBoxLayout()
        self.labelBox.addWidget(self.textLabel)
        self.labelBox.addWidget(self.valueLabel)
        self.vbox.addLayout(self.labelBox)
        self.hbox.addLayout(self.vbox)
        if geometry.type == GeometryType.ANGLE:
            if geometry.name == "alfa":
                name = "α"
            elif geometry.name == "alfa2":
                name = "α2"
            elif geometry.name == "beta":
                name = "β"
            elif geometry.name == "beta2":
                name = "β2"    
            elif geometry.name == "gamma":
                name = "γ"
            elif geometry.name == "gamma2":
                name = "γ2"
            self.textLabel.setText(f"Angolo {name}:")  
            self.valueLabel.setText("{:.1f}°".format(geometry.value))
        elif geometry.type == GeometryType.SIDE:
            self.textLabel.setText(f"Lato {geometry.name}:")
            self.valueLabel.setText("{:.1f}".format(geometry.value))
        if self.isStatic != True:
            self.slider = QSlider(Qt.Orientation.Horizontal)
            self.slider.setSingleStep(1)
            if geometry.type == GeometryType.SIDE:
                self.slider.setRange(1, 1000)
            elif geometry.type == GeometryType.ANGLE:
                self.slider.setRange(0, 1799)
            self.slider.setValue(int(geometry.value*10))
            self.slider.valueChanged.connect(self.sliderValueChanged)
            self.vbox.addWidget(self.slider)

    def sliderValueChanged(self, new):
        self.geometry.value = float(new/10)
        if self.geometry.type == GeometryType.ANGLE:
            self.valueLabel.setText("{:.1f}°".format(float(new/10)))
        else:
            self.valueLabel.setText("{:.1f}".format(float(new/10)))
        win.graphWidget.removeItem(win.graph_triangle)
        if win.second_triangle:
            win.graphWidget.removeItem(win.second_triangle) 
        try:
            params = win.calculate_triangle()
            self.setStyleSheet(f"background-color: rgb(255, 255, 255);")
            win.draw_triangle(*params) 
            win.errorLabel.setText("")
        except Exception as error:
            code = int(error.args[0])
            if code == int(ErrorCode.INSUFFICIENT_PARAMETERS):
                return
            self.setStyleSheet(f"background-color: lightcoral;")
            win.handle_error(code)

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
            
class AddParameterDialog(QDialog):
    def __init__(self, type):
        super().__init__()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        
        # bottone a tendina
        self.comboBox = QComboBox()
        self.comboBox.setEditable(True)
        lineedit = self.comboBox.lineEdit()
        lineedit.setAlignment(Qt.AlignCenter)
        lineedit.setReadOnly(True)
        # casella di testo
        onlyInt = QDoubleValidator()
        if type == GeometryType.SIDE:
            self.comboBox.addItems(["a", "b", "c"])
            self.setWindowTitle("Inserisci un lato")
            #onlyInt.setRange(1, 100)
        elif type == GeometryType.ANGLE:
            self.comboBox.addItems(["alfa", "beta", "gamma"])
            self.setWindowTitle("Inserisci un angolo")
            #
            #onlyInt.setRange(0, 179)
        self.textInput = QLineEdit()
        self.textInput.setValidator(onlyInt)
        # messaggio
        self.uselessMessage = QLabel("Angolo")
        # layout secondario orizzontale
        self.hLayout = QHBoxLayout()
        #self.hLayout.addWidget(self.uselessMessage)
        self.hLayout.addWidget(self.comboBox)
        self.hLayout.addWidget(self.textInput)
        self.hLayout.addWidget(self.buttonBox)
        self.hLayout.setStretchFactor(self.comboBox, 2)
        self.hLayout.setStretchFactor(self.textInput, 2)
        self.hLayout.setStretchFactor(self.buttonBox, 1)
        # checkbox
        #self.checkbox = QCheckBox("Compreso tra gli altri due")
        #self.checkbox.setChecked(False)
        # layout principale
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.hLayout)
        #self.mainLayout.addWidget(self.checkbox)
        self.setLayout(self.mainLayout)

class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.triangle = []
        self.is_check = False
        self.helper = Helper()
        self.can_update = False
        self.second_triangle = None
        self.resolver = Resolver(self.helper)
        self.setWindowTitle("Risolutore di triangoli")
        self.setGeometry(0,0,720, 480)
        self.setupLayout()
        self.createActions()
        self.createToolBar()
        self.connectActions()
        self.draw_triangle(10, 10, 10, 60, 60, 60)


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
    
    def draw_triangle(self, a, b, c, alfa, beta, gamma, *args):
        side_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.SIDE]
        angle_list = [geometry.value for geometry in self.triangle if geometry.type ==GeometryType.ANGLE]   
        if len(args) > 0:      
            self.second_triangle = Triangle(0, 0, c, 0, cos(radians(alfa))*b, sin(radians(alfa))*b, alfa, beta, gamma, self.helper.lightyellow, 1)
            self.graphWidget.addItem(self.second_triangle)
            return
        self.graph_triangle = Triangle(0, 0, c, 0, cos(radians(alfa))*b, sin(radians(alfa))*b, alfa, beta, gamma, self.helper.lightblue)
        self.graphWidget.addItem(self.graph_triangle)

    def get_by_name(self, *args):
        output = []
        for param in args:
            found = False
            for geometry in self.triangle:
                if param == geometry.name:
                    found = True
                    output.append(int(geometry.value)) 
            if not found:
                output.append(None)
        if len(output) > len(args):
            raise Exception(ErrorCode.DUPLICATE_ARGUMENTS)
        return output    
    
    def update_nonstatic_params(self, *args):
        nsplit = int(len(args)/2)
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            found = False
            for param, value in zip(args[:nsplit], args[nsplit:]):
                if found:
                    continue
                if myWidget.geometry.name == param:
                    found = True
                    myWidget.slider.setValue(value) 
            
    def get_geoms_by_type(self, type):
        output = [geometry for geometry in self.triangle if geometry.type == type and geometry.static != True]
        return output
    
    def calculate_triangle(self):
        angles = self.get_geoms_by_type(GeometryType.ANGLE)
        sides = self.get_geoms_by_type(GeometryType.SIDE)
        if len(angles) == 1 and len(sides) == 2:
            unique_angle = angles[0]
            if unique_angle.between:
                if unique_angle.name == "alfa":       
                    alfa = unique_angle.value 
                    b, c = self.get_by_name("b", "c")
                    if all([b,c]) != True:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))
                    a, beta, gamma = self.resolver.LAL(int(b), int(alfa), int(c))
                    self.add_or_update_parameter(GeometryType.SIDE, "a", a, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "gamma", gamma, True)
                elif unique_angle.name == "beta":   
                    beta = unique_angle.value 
                    a, c = self.get_by_name("a", "c")   
                    if all([a,c]) != True:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))
                        #self.helper.errorBox("Parametri non validi")
                          
                    b, gamma, alfa = self.resolver.LAL(int(c), int(beta), int(a))
                    self.add_or_update_parameter(GeometryType.SIDE, "b", b, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "gamma", gamma, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                elif unique_angle.name == "gamma":
                    gamma = unique_angle.value  
                    b, a = self.get_by_name("b", "a")
                    if all([b,a]) != True:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))
                    c, beta, alfa = self.resolver.LAL(int(b), int(gamma), int(a))
                    self.add_or_update_parameter(GeometryType.SIDE, "c", c, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                    self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
            else:
                if unique_angle.name == "alfa":
                    alfa = unique_angle.value
                    if all(self.get_by_name("a", "b")):
                        a,b = self.get_by_name("a", "b")
                        output = self.resolver.LLA(a, b, alfa)
                        if len(output) == 2:
                            beta, gamma, c = output[0]
                            beta2, gamma2, c2 = output[1]
                            self.add_or_update_parameter(GeometryType.SIDE, "c2", c2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "beta2", beta2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "gamma2", gamma2, True, 1)
                            self.draw_triangle(a, b, c2, alfa, beta2, gamma2, 1)
                        else:
                            beta, gamma, c = output
                        self.add_or_update_parameter(GeometryType.SIDE, "c", c, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "gamma", gamma, True)
                    elif all(self.get_by_name("a","c")):
                        a,c = self.get_by_name("a", "c")
                        output = self.resolver.LLA(a, c, alfa)
                        if len(output) == 2:
                            gamma, beta, b = output[0]
                            gamma2, beta2, b2 = output[1]
                            self.add_or_update_parameter(GeometryType.SIDE, "b2", b2, True)
                            self.add_or_update_parameter(GeometryType.ANGLE, "beta2", beta2, True)
                            self.add_or_update_parameter(GeometryType.ANGLE, "gammma2", gamma2, True)
                            self.draw_triangle(a, b2, c, alfa, beta2, gamma2, 1)
                        else:
                            gamma, beta, b = output
                        self.add_or_update_parameter(GeometryType.SIDE, "b", b, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "gammma", gamma, True)                   
                    else:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))
                elif unique_angle.name == "beta":
                    beta = unique_angle.value
                    if all(self.get_by_name("b", "c")):
                        b,c = self.get_by_name("b", "c")
                        output = self.resolver.LLA(b, c, beta)
                        if len(output) == 2:
                            gamma, alfa, a = output[0]
                            gamma2, alfa2, a2 = output[1]    
                            self.add_or_update_parameter(GeometryType.SIDE, "a2", a2, True,1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "alfa2", alfa2, True,1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "gamma2", gamma2, True,1)
                            self.draw_triangle(a2, b, c, alfa2, beta, gamma2, 1)
                        else:
                            gamma, alfa, a = output
                        self.add_or_update_parameter(GeometryType.SIDE, "a", a, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "gamma", gamma, True)
                    elif all(self.get_by_name("a","b")):
                        a,b = self.get_by_name("a", "b")
                        output = self.resolver.LLA(b, a, beta)
                        if len(output) == 2:
                            alfa, gamma, c = output[0]
                            alfa2, gamma2, c2 = output[1]
                            self.add_or_update_parameter(GeometryType.SIDE, "c2", c2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "alfa2", alfa2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "gammma2", gamma2, True, 1)    
                            self.draw_triangle(a, b, c2, alfa2, beta, gamma2, 1)
                        else:
                            alfa, gamma, c = output
                        self.add_or_update_parameter(GeometryType.SIDE, "c", c, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "gammma", gamma, True)                   
                    else:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))

                elif unique_angle.name == "gamma":
                    gamma = unique_angle.value
                    if all(self.get_by_name("a", "c")):
                        a, c = self.get_by_name("a", "c")
                        output = self.resolver.LLA(c, a, gamma)
                        if len(output) == 2:
                            alfa, beta, b = output[0]
                            alfa2, beta2, b2 = output[1]
                            self.add_or_update_parameter(GeometryType.SIDE, "b2", b, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "alfa2", alfa, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "beta2", beta, True, 1)
                            self.draw_triangle(a, b2, c, alfa2, beta2, gamma, 1)
                        else:
                            alfa, beta, b = output
                        self.add_or_update_parameter(GeometryType.SIDE, "b", b, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
                    elif all(self.get_by_name("c","b")):
                        c, b = self.get_by_name("c", "b")
                        output = self.resolver.LLA(c, b, gamma)
                        if len(output) == 2:
                            beta, alfa, a = output[0]
                            beta2, alfa2, a2 = output[1]
                            self.add_or_update_parameter(GeometryType.SIDE, "a2", a2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "alfa2", alfa2, True, 1)
                            self.add_or_update_parameter(GeometryType.ANGLE, "beta2", beta2, True, 1)                   
                            self.draw_triangle(a2, b, c, alfa2, beta2, gamma, 1)
                        else:
                            beta, alfa, a = output
                        self.add_or_update_parameter(GeometryType.SIDE, "a", a, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
                        self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)                   
                    else:
                        raise Exception(int(ErrorCode.INVALID_PARAMETERS))
        elif len(sides) == 3:
            a, b, c = self.get_by_name("a", "b", "c")
            try:
                alfa, beta, gamma = self.resolver.LLL(a, b, c)
            except Exception as error:
                raise error
            self.add_or_update_parameter(GeometryType.ANGLE, "alfa", alfa, True)
            self.add_or_update_parameter(GeometryType.ANGLE, "beta", beta, True)
            self.add_or_update_parameter(GeometryType.ANGLE, "gamma", gamma, True)
        elif len(angles) == 3:         
            raise Exception(ErrorCode.INFINITE_TRIANGLES)
        elif len(angles) == 2 and len(sides) == 1:
            unique_side = sides[0]
            if angles[0].value + angles[1].value > 180:
                raise Exception(int(ErrorCode.INVALID_ANGLES))
            if unique_side.between:
                if unique_side.name == "c":
                    c = unique_side.value
                    alfa, beta = self.get_by_name("alfa", "beta")
                    if all([alfa, beta]) != True:
                        self.helper.errorBox("Parametri non validi")
                        return -1
                    gamma, a, b = self.resolver.ALA(alfa, c, beta)
                elif unique_side.name == "a":
                    a = unique_side.value
                    beta, gamma = self.get_by_name("beta", "gamma")
                    if all([beta, gamma]) != True:
                        self.helper.errorBox("Parametri non validi")
                        return -1
                    alfa, b, c = self.resolver.ALA(beta, a, gamma)
                elif unique_side.name == "b":
                    b = unique_side.value
                    gamma, alfa = self.get_by_name("gamma", "alfa")
                    if all([gamma, alfa]) != True:
                        self.helper.errorBox("Parametri non validi")
                        return -1
                    beta, c, a = self.resolver.ALA(gamma, b, alfa)
            else:    
                if unique_side.name == "c":
                    c = unique_side.value
                    if all(self.get_by_name("alfa", "gamma")):
                        alfa, gamma = self.get_by_name("alfa", "gamma")
                        beta, a, b = self.resolver.AAL(alfa, gamma, c)
                    elif all(self.get_by_name("beta", "gamma")):
                        beta, gamma = self.get_by_name("beta", "gamma")
                        alfa, b, a = self.resolver.AAL(angle_list[0], angle_list[1], side_list[0])
                    else:
                        return
                elif unique_side.name == "a":
                    a = unique_side.value
                    if all(self.get_by_name("beta", "alfa")):
                        beta, alfa = self.get_by_name("beta", "alfa")
                        gamma, b, c = self.resolver.AAL(beta, alfa, a)
                    elif all(self.get_by_name("gamma", "alfa")):
                        gamma, alfa = self.get_by_name("gamma", "alfa")
                        beta, c, b = self.resolver.AAL(gamma, alfa, a)
                    else:
                        return
                elif unique_side.name == "b":
                    b = unique_side.value
                    if all(self.get_by_name("gamma", "beta")):
                        gamma, beta = self.get_by_name("gamma", "beta")
                        alfa, c, a = self.resolver.AAL(gamma, beta, b)
                    elif all(self.get_by_name("alfa", "beta")):
                        beta, gamma = self.get_by_name("beta", "gamma")
                        gamma, a, c = self.resolver.AAL(alfa, beta, b)
                    else:
                        return 
        else:
            raise Exception(ErrorCode.INSUFFICIENT_PARAMETERS)
        return [a, b, c, alfa, beta, gamma]       
    
    def handle_error(self, code):
        if code == ErrorCode.INVALID_PARAMETERS:
            self.errorLabel.setText("Parametri invalidi")
        elif code == ErrorCode.TRIANGLE_INEQUALITY:
            self.errorLabel.setText("I parametri non rispettano la disuguaglianza triangolare")
        elif code == ErrorCode.INVALID_ANGLES:
            self.errorLabel.setText("La somma dei 2 angoli deve essere minore di 180°")
        elif code == ErrorCode.INFINITE_TRIANGLES:
            self.errorLabel.setText("Esiste un numero infinito di triangoli dati tre lati")
        elif code == ErrorCode.IMPOSSIBLE_CONSTRUCTION:
            self.errorLabel.setText("Triangolo impossibile")
        elif code == ErrorCode.DUPLICATE_ARGUMENTS:
            self.errorLabel.setText("Parametri duplicati")

    def resolve_triangle(self):
        self.errorLabel.setText("")
        if self.graph_triangle != None:
            self.graphWidget.removeItem(self.graph_triangle)
        try:
            a, b, c, alfa, beta, gamma = self.calculate_triangle()
        except Exception as error:
            code = error.args[0]
            self.handle_error(code)
            return
        self.draw_triangle(int(a), int(b), int(c), int(alfa), int(beta), int(gamma))
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.updateUI()
        self.update_toolbar()
        
    def clearLayout(self):
        self.errorLabel.setText("")
        self.triangle = []
        for action in self.toolBar.actions():
            if type(action.data()) == GeometryType:
                action.setEnabled(True)
            else:
                action.setDisabled(True)
        self.toolBar.actions()[3].setDisabled(True)
        self.graphWidget.removeItem(self.graph_triangle)
        try:
            self.graphWidget.removeItem(self.second_triangle)
        except:
            pass       
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.deleteLater()    

    def remove_parameter(self, e: DockElement):
        self.errorLabel.setText("")
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
            self.graphWidget.removeItem(self.second_triangle)
            
        if len(self.triangle) == 2:
            for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                myWidget.geometry.between = False
        for i in range(self.vLayout.count()-1):
                myWidget = self.vLayout.itemAt(i).widget()
                myWidget.setStyleSheet("")
                myWidget.updateUI()
        self.update_toolbar()        
     
    def add_or_update_parameter(self, type, name, value, static, *args):
        new_geometry = Geometry(type, name, value)
        if static:
            new_geometry.static = True
            foo = self.get_by_name(name)
            # check if param already exists
            if self.get_by_name(name)[0] != None:
                # replace existing param
                for i in range(self.vLayout.count()-1):
                    myWidget = self.vLayout.itemAt(i).widget()
                    if myWidget.geometry.name == name:
                        if type == GeometryType.ANGLE:
                            myWidget.valueLabel.setText("{:.1f}°".format(value))
                            return
                        myWidget.valueLabel.setText("{:.1f}".format(value))
                        return 
                return
            self.triangle.append(new_geometry)
        else:
            self.triangle.append(new_geometry)
            self.update_toolbar()
            # 1 sceglie a quale geometria aggiungere l'opzione compreso (solo se ci sono 3 geometrie)
            # 2 aggiunge il nuovo dockelement al dock
            # 3 aggiorna la ui di ogni dockelement
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
        e = DockElement(new_geometry, static)
        if len(args) > 0:
           e.setStyleSheet("background-color: lightyellow;")
        e.button.clicked.connect(partial(self.remove_parameter, e))
        self.vLayout.insertWidget(self.vLayout.count()-1, e)
        for i in range(self.vLayout.count()-1):
            myWidget = self.vLayout.itemAt(i).widget()
            myWidget.updateUI()
        
    def on_add_parameter(self, dialog, type):
        name = dialog.comboBox.currentText()
        value = float(dialog.textInput.text())
        
        self.add_or_update_parameter(type, name, value, False)

        dialog.close()

    def select_parameter(self, type):
        dialog = AddParameterDialog(type)
        dialog.buttonBox.accepted.connect(partial(self.on_add_parameter, dialog, type))
        dialog.exec()
    
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
        
        self.addAngleShortcut= QShortcut(QKeySequence("Ctrl+A"), self)
        self.addAngleShortcut.activated.connect(partial(self.select_parameter, GeometryType.ANGLE))
        self.addSideShortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.addSideShortcut.activated.connect(partial(self.select_parameter, GeometryType.SIDE))

    def createToolBar(self):
        # create tool bar
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        # add actions to tool bar
        self.toolBar.addActions([ self.resolveAction, self.addAngleAction, self.addSideAction, self.deleteAction])
        self.errorLabel = QLabel("")
        self.errorLabel.setStyleSheet('color: red')
        self.toolBar.addWidget(self.errorLabel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme(theme="light")
    win = Window()
    win.show()
    sys.exit(app.exec_())

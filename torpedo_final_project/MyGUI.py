from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QLabel, QHBoxLayout, QMainWindow, QAction, QTextEdit, QPushButton
from PyQt5.Qt import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer,QThread, pyqtSignal
import sys
from PyQt5 import uic
import cv2
from shapes_detector import shape_detector 
from Line_task import process_frame


circle_count = 0
square_count = 0
triangle_count = 0
Red_count = 0
Green_count = 0
Blue_count = 0
Yellow_count = 0
White_count = 0
Black_count = 0
StationShape=""
CurrentShape=""


class MainWindow(QMainWindow)  : 
    def __init__(self) : 
        super(MainWindow,self).__init__() 
        uic.loadUi("MyGUI.ui",self)
        self.show()
        self.publisher_=rover_control_node()
        self.LiveCamera=self.findChild(QLabel,"label_1")
        self.ProcessingCamera=self.findChild(QLabel,"label_2")

        self.LogsTask_1=self.findChild(QTextEdit,"textEdit_1")
        self.LogsTask_2=self.findChild(QTextEdit,"textEdit_2")

        self.DetectionShapeButton=self.findChild(QPushButton,"pushButton_3")
        self.DetectionShapeButton.clicked.connect(self.detectShapes)

        self.SetShape=self.findChild(QPushButton,"pushButton_1")
        self.SetShape.clicked.connect(self.SetStationShape)

        self.CheckMatchShape=self.findChild(QPushButton,"pushButton_2")
        self.CheckMatchShape.clicked.connect(self.CheckStationShape)

        self.StartStreaming() 

    def StartStreaming(self)  :
        ip_camera_url="http://192.168.121.239:8080/video"
        self.capture=cv2.VideoCapture(ip_camera_url)
        self.timer=QTimer(self) 
        self.timer.timeout.connect(self.UpdateFrame)
        self.timer.start(15)

    def UpdateFrame(self) : 
        ret , Frame=self.capture.read()
        if ret :
            RGB_frame=cv2.cvtColor(Frame,cv2.COLOR_BGR2RGB)
            processed_frame,control_signal=process_frame(Frame)
            self.appendLog(f"Control Signal: {control_signal}", self.LogsTask_1)
            self.publihser_.publish(control_signal)
            self.displayFrameInLabel(processed_frame, self.ProcessingCamera)
            self.displayFrameInLabel(RGB_frame, self.LiveCamera) 
        else : 
            print("No Frame captured !") 
    
    def displayFrameInLabel(self, frame, label):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        qImg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)
    
    def SetStationShape(self) : 
        global StationShape,CurrentShape 
        StationShape=CurrentShape 



    def CheckStationShape(self) : 
        global StationShape,CurrentShape 
        if StationShape==CurrentShape : 
            self.appendLog("Find Home! -- The current shape is the station shape", self.LogsTask_2)
        else : 
            self.appendLog("Not Home! -- The current shape is not the station shape",self.LogsTask_2)

    def detectShapes(self):
        global circle_count, square_count, triangle_count ,Cuurent_Shape  
        global Red_count, Green_count, Blue_count, Yellow_count, White_count, Black_count
        ret, frame = self.capture.read()
        if ret:
            processed_frame, shape_count, shape_names ,shapes_color = shape_detector(frame)
            # Display the processed frame
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            self.displayFrameInLabel(frame_rgb, self.ProcessingCamera)
            self.publisher_.publish(shape_names)
            shapes_with_colors = [f"{color} {shape}" for shape, color in zip(shape_names, shapes_color)]
        
            print(f"Detected {shape_count} shapes: {', '.join(shapes_with_colors)}")
            self.appendLog(f"Detected {shape_count} shapes: {', '.join(shapes_with_colors)}", self.LogsTask_2)

        if shape_count == 1:
            CurrentShape= shape_names[0]
            for shape, color in zip(shape_names, shapes_color):
                if shape == "circle":
                    circle_count += 1
                elif shape == "square":
                    square_count += 1
                elif shape == "triangle":
                    triangle_count += 1
########################################################
                if color == "Red":
                    Red_count += 1
                elif color == "Green":
                    Green_count += 1
                elif color == "Blue":
                    Blue_count += 1
                elif color == "Yellow":
                    Yellow_count += 1
                elif color == "White":
                    White_count += 1
                elif color == "Black":
                    Black_count += 1
            print(f"Number of Circles: {circle_count}, "
                  f"Number of Squares: {square_count}, "
                  f"Number of Triangles: {triangle_count}")
            print(f"Number of Red: {Red_count}, "
                  f"Number of Green: {Green_count}, "
                  f"Number of Blue: {Blue_count}, "
                  f"Number of Yellow: {Yellow_count}, "
                  f"Number of White: {White_count}, "
                  f"Number of Black: {Black_count}")
            
    
    def appendLog(self, log_text, log_frame):
        if log_frame:  # Check if the widget is found
            log_frame.append(log_text)  # Append log to QTextEdit
        else:
            print("Log frame not found")


            
    def closeEvent(self, event):
        self.capture.release()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
#!/usr/bin/env python3

import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import Qt

from skimage import io
from skimage.filters import threshold_mean
from skimage.filters import threshold_otsu
from skimage.filters import threshold_minimum
from skimage.filters import threshold_local

from skimage.color import rgb2gray
from skimage.exposure import equalize_hist 

from skimage import img_as_uint
        
import os, shutil

#constants
scalemax = 15000

bricolab = True

iconsize = 300
if bricolab:
    iconsize = 250


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)

        # some modifications implemented on CoSin2018 by Werner "Wene" Meier (wene83@gmx.ch)
        self.setWindowTitle("SuperCut [CoSin 2018 edition]")	
        
        boxes = ['Foto','Vektor','Test','Schnitt']
        handles = {'Foto':self.handleBFOTO,
                   'Vektor':self.handleBVEKTOR,
                   'Test':self.handleBTEST,
                   'Schnitt':self.handleBSCHNITT,}
        
        self.views = []
        self.buttons = []
        
        self.btn_import = QtWidgets.QPushButton("Import SVG")
        layout.addWidget(self.btn_import)
        self.btn_import.clicked.connect(self.handleImport)

        for name in boxes[:-1]:
            view = QtWidgets.QListWidget(self)
            view.setViewMode(QtWidgets.QListView.IconMode)
            view.setIconSize(QtCore.QSize(iconsize, iconsize))
            view.setResizeMode(QtWidgets.QListView.Adjust)
            view.setSpacing(10)
        
            
            # record handles
            self.views.append(view)
            
            # button
            button = QtWidgets.QPushButton(name, self)
            button.clicked.connect(handles[name])
            button.setStyleSheet("QPushButton { background-color: lightblue }"
                      "QPushButton:pressed { background-color: red }" )
                      
            vbox = QtWidgets.QVBoxLayout(self)
            
            vbox.addWidget(view)
            #vbox.addStretch(1)         
            vbox.addWidget(button)
            
            layout.addLayout(vbox)
        
        lay_slider = QtWidgets.QVBoxLayout()
        layout.addLayout(lay_slider)
        self.sld = QtWidgets.QSlider(Qt.Vertical,self)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setGeometry(30, 40, 100, 30)
        self.sld.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.sld.setValue(50)
        self.sld.setRange(0, 150)
        #self.sld.setMinimum(0)
        #self.sld.setMaximum(100)
        self.sld.setTickInterval(10)
        self.sld.setSingleStep(1)
        self.sld.valueChanged[int].connect(self.changeValue)
        
        lay_slider.addWidget(self.sld)

        self.edt_number = QtWidgets.QSpinBox()
        self.edt_number.setValue(self.sld.value())
        self.edt_number.setMinimum(self.sld.minimum())
        self.edt_number.setMaximum(self.sld.maximum())
        self.edt_number.valueChanged.connect(self.sld.setValue)
        self.sld.valueChanged.connect(self.edt_number.setValue)
        lay_slider.addWidget(self.edt_number)
        
        # schnitt button
        name = boxes[len(boxes)-1]
        button = QtWidgets.QPushButton(name, self)
        button.clicked.connect(handles[name])
        button.setStyleSheet("QPushButton { background-color: orange }"
                      "QPushButton:pressed { background-color: red }" )
            
        layout.addWidget(button)
        
        self.scalefactor = 1.0
        self.bboxscale = [0,0,10000,10000]

    # slider
    def changeValue(self,value):
        factorabs = 2*abs(value-50)/50.0 +1
        self.scalefactor = factorabs if value-50 >= 0 else 1/factorabs
        #print(self.scalefactor)
        
    def loadIMG(self,path,view):
        pixmap = QtGui.QPixmap()
        print('load (%s) %r' % (pixmap.load(path), path))
        item = QtWidgets.QListWidgetItem(os.path.basename(path))
        item.setIcon(QtGui.QIcon(path))
        self.views[view].addItem(item)

    def openIMG(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return(fileName)


        
    def addtext(self,txt,view):    
        item = QtWidgets.QListWidgetItem(txt)
        self.views[view].addItem(item)
    
    
    def scaleHPGL(self,lines,factor):
        print(factor)
        
        newlines = []
        for line in lines:
                #print(line[0:80])
                
                # for testing
                #newline = line.replace('PD','')
                newline = line
                
                if line[0:2] == 'PA':
                    newline = 'PA'
                    #parse plotting line
                    coords = line[2:].replace(";", "").split(',')
                    
                    prevX = -1
                    prevY = -1
                    
                    for i in range(0,len(coords),2):
                        #print(i)
                        #print(coords[i])
                        #print(coords[i+1])
                        prescaleX = int(coords[i])
                        prescaleY = int(coords[i+1])
                        x = round(prescaleX*factor)
                        y = round(prescaleY*factor)
                        if prevX != x or prevY != y:
                            newline = newline + str(x) +','
                            newline = newline + str(y) +','
                            prevX = x
                            prevY = y
                            
                    # replace last , with ;
                    newline = newline[0:-1]
                    newline += ';\n'
                
                newlines.append(newline)
         
        return newlines

    def reboundHPGL(self,lines,x0,y0):
        print(x0)
        print(y0)
        
        newlines = []
        for line in lines:
                #print(line[0:80])
                
                # for testing
                #newline = line.replace('PD','')
                newline = line
                
                if line[0:2] == 'PA':
                    newline = 'PA'
                    #parse plotting line
                    coords = line[2:].replace(";", "").split(',')
                        
                    for i in range(0,len(coords),2):
                        #print(i)
                        #print(coords[i])
                        #print(coords[i+1])
                        prereboundX = int(coords[i])
                        prereboundY = int(coords[i+1])
                        if prereboundX >= x0 and prereboundY >= y0:
                            newline += str(prereboundX-x0) +','
                            newline += str(prereboundY-y0) +','
                        else:
                            newline += '0,0,'
                        
                            
                    # replace last , with ;
                    newline = newline[0:-1]
                    newline += ';\n'
                
                newlines.append(newline)
         
        return newlines



    def closeHPGLpath(self,path):
        
        newpath = path
        
        if len(path)>2:
            newpath.append(path[0])
            newpath.append(path[1])
        
        return newpath


        
    def removeFILL(self,path):
        lines = []
        with open(path, 'r') as f:
            for l in f.readlines():
                l = l.replace("stroke:none","stroke:#000000;stroke-width:2")    
                l = l.replace("fill:#000000","fill:none")    
                #l = l.replace("stroke=\"none\"","stroke=\"#000000\" stroke-width=\"20\"")    
                #l = l.replace("fill=\"#000000\"","fill=\"none\"")    
                lines.append(l)
            f.close()
        with open(path, 'w') as f:
            f.writelines(lines)


    # returns bounidng box of path [xmin,ymin,xmax,ymax] 
    # where path = [[p1x,p1y],[p2x,p2y],...] 
    def boundingBoxPath(self,path):
        xmax = -1
        ymax = -1 
        xmin = 10000000
        ymin = 10000000
        
        for p in path:
            x = p[0]
            y = p[1]
            if (xmin > x):
                xmin = x
            if (ymin > y):
                ymin = y
            if (xmax < x):
                xmax = x
            if (ymax < y):
                ymax = y
        
        print('boundingbox ['+str(xmin)+','+str(ymin)+','+str(xmax)+','+str(ymax)+']')
        return [xmin,ymin,xmax,ymax]
    
    
    
    
    # generates HPGL code from paths in the form of a list of [path1, path2, ...]
    # where path1 = [[p1x,p1y],[p2x,p2y],...]
    def writeHPGLfromPaths(self,paths):
        header = "IN;PU;\nIN;\n"
        footer = "PA0,0;\nPG0;\n"
        
        lines = [header]
        for path in paths:
            lines.append('PA'+str(path[0][0])+','+str(path[0][1])+';\n')
            lines.append('PD;\n')
            
            line = 'PA'
            for i in range(1,len(path)):
                line += str(path[i][0])+','+str(path[i][1])+','
            # replace last ',' with ';'
            line = line[0:-1]
            line += ';\n'    
            
            lines.append(line)
            lines.append('PU;\n')
            
        lines.append(footer)
        
        return lines
        
        
    # generates HPGL code from bounding box in the form of [xmin,ymin,xmax,ymax] 
    # note that pen stays up
    def writeHPGLfromBBox(self,bbox):
        header = "IN;PU;\nIN;\n"
        footer = "PA0,0;\nPG0;\n"
         
        lines = [header]

        lines.append('PA'+str(bbox[0])+','+str(bbox[1])+';\n')
        lines.append('PA'+str(bbox[2])+','+str(bbox[1])+';\n')
        lines.append('PA'+str(bbox[2])+','+str(bbox[3])+';\n')
        lines.append('PA'+str(bbox[0])+','+str(bbox[3])+';\n')
        lines.append('PA'+str(bbox[0])+','+str(bbox[1])+';\n')
            
        lines.append(footer)
        
        return lines
                   

        
    # parses HPGL code after distiller to a list of [path1, path2, ...]
    # where path1 = [[p1x,p1y],[p2x,p2y],...]  
    def parse_paths(self,lines):
        pendown = False

        allpaths = []        
        path = []
        
        for line in lines:
            #print(line[0:80])
            if line.find('PU') >= 0:
                pendown = False
                if len(path)>0 : allpaths.append(path)
                path = []
            if line.find('PD') >= 0:
                pendown = True
            
            if line[0:2] == 'PA': 
                coords = line[2:].replace(";", "").split(',')
                if pendown:
                    #parse plotting line
                    coords = line[2:].replace(";", "").split(',')
                    for i in range(0,len(coords),2):
                        #print(i)
                        #print(coords[i])
                        #print(coords[i+1])
                        x = int(coords[i])
                        y = int(coords[i+1])
                        path.append([x,y])
                else: 
                    # starting point of path
                    x = int(coords[0])
                    y = int(coords[1])
                    path.append([x,y])
        return allpaths


    # returns bounding box [xmin,ymin,xmax,ymax]    
    def boundingBoxHPGL(self,lines):
        path_allbboxes = []
        for p in self.parse_paths(lines):
            bbox = self.boundingBoxPath(p)
            path_allbboxes.append([bbox[0],bbox[1]])    
            path_allbboxes.append([bbox[2],bbox[3]])    

        return self.boundingBoxPath(path_allbboxes)
        



    # checks if bounding box is inside another
    def isinsideBBox(self,isin,bbox):
        if isin[0]>bbox[0] and isin[1]>bbox[1] and isin[2]<bbox[2] and isin[3]<bbox[3]:
            return True
        else: 
            return False


            
    # returns  reordered lines starting with innermost path and progressing to outermost    
    # computed according to bounding box of each path   
    def reorderBBoxHPGL(self,lines):
        
        # parse HPGL to paths
        paths = self.parse_paths(lines)
        
        # compute bbox of each path
        bboxes = []
        for p in paths:
            bboxes.append(self.boundingBoxPath(p))

        
        # find innermost path by computing score of being inside other paths    
        linescore = []
        maxscore = -1
        
        for i,p in enumerate(paths):
            if bboxes[i][3] > 0:
                score = 0;
                for j,box in enumerate(bboxes):
                    if (i==j): continue
                    if self.isinsideBBox(bboxes[i],box): score+=1
            else: score = -1
            
            linescore.append(score)
            if score > maxscore: maxscore = score 
        
        print(linescore)
        print(maxscore)
        
        # reorder paths according to score and reverse order to begin with innermost
        orderedpaths = []
        
        for s in range(maxscore+1):
            for i,p in enumerate(paths):
                if linescore[i] == s:
                    #orderedpaths.append(self.closeHPGLpath(p))
                    orderedpaths.append(p)
        
        orderedpaths.reverse()
                    
        return self.writeHPGLfromPaths(orderedpaths)
        
                

        
            

    def handleBFOTO(self):
        #view = 0
        v = 0
        self.views[v].clear()
        
        #TODO take picture with webcam (openCV)
        os.system("streamer -c /dev/video1 -s 1280x960 -o ./img/foto.ppm")
        #os.system("streamer -c /dev/video0 -s 1920x1080 -o ./img/foto.ppm")
        os.system("convert ./img/foto.ppm ./img/test.png")
        
        
        path = './img/test.png' 

        img = rgb2gray(io.imread(path))
        #img = equalize_hist(rgb2gray(io.imread(path)))
        io.imsave('./img/testGRAY.png', img)
        
        
        # thresholding
        #thresh = threshold_mean(img)
        #thresh = threshold_otsu(img)
        thresh = threshold_minimum(img)
        print(thresh)
        binary = img > thresh
        io.imsave('./img/testTH.png', img_as_uint(binary))
        
        # adaptive thresholding
        #block_size = 35
        #adaptive_thresh = threshold_local(img, block_size, offset=10)
        #binary_adaptive = img > adaptive_thresh        
        #io.imsave('./testTHadapt.png', img_as_uint(binary))

        # load iamge
        path = './img/testTH.png' 
        self.loadIMG(path,v)

    def handleBVEKTOR(self):
        #view = 1
        v = 1
        self.views[v].clear()
        
        # mirror the image        
        os.system("convert -flop ./img/testTH.png ./img/testTH.ppm")
        # -W width
        # -H height
        # -A rotate
        # -t
        # -u
        if bricolab:
            os.system("potrace -t 10 -W 8in -H 6in -u 10 -s ./img/testTH.ppm -o ./vector/test.svg")
            os.system("potrace -t 10 -W 8in -H 6in -u 10 -A 90 -s ./img/testTH.ppm -o ./vector/test90.svg")
        else:
            os.system("potrace -t 10 -W 11in -H 6in -u 10 -s ./img/testTH.ppm -o ./vector/test.svg")
            os.system("potrace -t 10 -W 11in -H 6in -u 10 -A 90 -s ./img/testTH.ppm -o ./vector/test90.svg")

        
        #https://jenda.hrach.eu/f2/plotter/Linux%20inkscape%20save%20as%20HPGL%20file%20for%20pen%20cutting%20plotter%20extension.html
        
        # possiblz use rsvg/convert instead of inkscape but no tightness....
        
        # for display (rotated 90)
        os.system("inkscape --without-gui --file=./vector/test.svg --export-pdf=./vector/test.pdf --export-area-drawing")
        os.system("inkscape --without-gui --file=./vector/test.pdf --export-plain-svg=./vector/testDISPLAY.svg")
        path = './vector/testDISPLAY.svg' 
        self.removeFILL(path)
        self.loadIMG(path,v)
        
        # for print
        os.system("inkscape --without-gui --file=./vector/test90.svg --export-pdf=./vector/test.pdf --export-area-drawing")
        
        os.system("pstoedit -f plot-hpgl ./vector/test.pdf hpgl/fulloutput.plt")
        #os.system("pstoedit -f hpgl \"-hpgl2\" ./vector/test.pdf hpgl/fulloutput.plt")
        os.system("./hpgl-distiller -i hpgl/fulloutput.plt -o hpgl/distilled.plt")
        
        with open('hpgl/distilled.plt', 'r') as f:
            lines = f.readlines()
            bbox = self.boundingBoxHPGL(lines)
            with open('hpgl/rebounded.plt', 'w') as g:
                for line in self.reboundHPGL(lines,bbox[0],bbox[1]):
                    g.write(line)
                g.close()
            f.close()
  
        
        with open('hpgl/rebounded.plt', 'r') as f:
            lines = f.readlines()
            #bbox = self.boundingBoxHPGL(lines)
            with open('hpgl/defaultscaled.plt', 'w') as g:
                for line in self.scaleHPGL(lines,1):
                    g.write(line)
                g.close()
            f.close()


    def handleImport(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open', '', '*.svg')
        if file_path != "":

            v = 1
            self.views[v].clear()
        

        
        #https://jenda.hrach.eu/f2/plotter/Linux%20inkscape%20save%20as%20HPGL%20file%20for%20pen%20cutting%20plotter%20extension.html
        
            # possiblz use rsvg/convert instead of inkscape but no tightness....
        
            # for display (rotated 90)
            os.system("inkscape --without-gui --file=" + file_path + " --export-pdf=./vector/test.pdf --export-area-drawing")
            os.system("inkscape --without-gui --file=./vector/test.pdf --export-plain-svg=./vector/testDISPLAY.svg")
            path = './vector/testDISPLAY.svg' 
            self.removeFILL(path)
            self.loadIMG(path,v)
        
            # for print
            os.system("inkscape --without-gui --file=" + file_path + " --export-pdf=./vector/test.pdf --export-area-drawing")
        
            os.system("pstoedit -f plot-hpgl -rotate 90 ./vector/test.pdf hpgl/fulloutput.plt")
            #os.system("pstoedit -f hpgl \"-hpgl2\" ./vector/test.pdf hpgl/fulloutput.plt")
            os.system("./hpgl-distiller -i hpgl/fulloutput.plt -o hpgl/distilled.plt")
        
            with open('hpgl/distilled.plt', 'r') as f:
                lines = f.readlines()
                bbox = self.boundingBoxHPGL(lines)
                with open('hpgl/rebounded.plt', 'w') as g:
                    for line in self.reboundHPGL(lines,bbox[0],bbox[1]):
                        g.write(line)
  
        
            with open('hpgl/rebounded.plt', 'r') as f:
                lines = f.readlines()
                #bbox = self.boundingBoxHPGL(lines)
                with open('hpgl/defaultscaled.plt', 'w') as g:
                    for line in self.scaleHPGL(lines,1):
                        g.write(line)


    def handleBTEST(self):
        #view = 2
        v = 2
        self.views[v].clear()
                
        with open('hpgl/defaultscaled.plt', 'r') as f:
            bbox = self.boundingBoxHPGL(f.readlines())
            #self.scalefactor = bbox[3]/float(scalemax)
            self.bboxscale = [round(x * self.scalefactor) for x in bbox]
            print(self.bboxscale)
            f.close()
            
        with open('./hpgl/boundingbox.plt','w') as f:
            for line in self.writeHPGLfromBBox(self.bboxscale): 
                f.write(line)
            f.close()
        
        
        path = './vector/testDISPLAY.svg' 
        self.loadIMG(path,v)
        
        # display
        xsize = (bbox[2]-bbox[0])*0.025/10.0 
        ysize = (bbox[3]-bbox[1])*0.025/10.0 
        xsizescale = (self.bboxscale[2]-self.bboxscale[0])*0.025/10.0 
        ysizescale = (self.bboxscale[3]-self.bboxscale[1])*0.025/10.0 
        
        # "{:10.4f}".format(x)
        self.addtext('\n\noriginal: '+"{:4.2f}".format(xsize)+' x '+"{:4.2f}".format(ysize)+' cm\n\nscaled  : '+"{:4.2f}".format(xsizescale)+' x '+"{:4.2f}".format(ysizescale)+' cm',v)    
        
        os.system("cat ./hpgl/boundingbox.plt > /dev/ttyUSB0")


    def handleBSCHNITT(self):
        #view = 3
        v = 3
        #self.views[v].clear()
        
        #TODO scale hpgl
        with open('hpgl/defaultscaled.plt', 'r') as f:
            lines = f.readlines()
            with open('hpgl/final.plt', 'w') as g:
                for line in self.reorderBBoxHPGL(self.scaleHPGL(lines,self.scalefactor)):
                    g.write(line)
                    #g.write(line)
                g.close()
            f.close()

        #with open('hpgl/final.plt', 'r') as f:
        #    bbox = self.boundingBoxHPGL(f.readlines())
        #    f.close()


        #path = './vektor/testAREA.svg' 
        #self.loadIMG(path,v)
        
        os.system("cat ./hpgl/final.plt > /dev/ttyUSB0")



if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(200, 150, 1398, 400)
    window.show()
    sys.exit(app.exec_())
    
    
    
    

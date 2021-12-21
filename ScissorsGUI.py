import sys
from sys import argv
from os.path import join, dirname, abspath
from os import chdir, getcwd, mkdir, listdir

# Main Dialog
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon

# Image Control
from cv2 import imread, imwrite
from scissorsPKG import extractor as ext

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', dirname(abspath(__file__)))
    return join(base_path, relative_path)
form = resource_path("scissors.ui")
mainDlg_class = uic.loadUiType(form)[0]
poppler_path = resource_path("./poppler-21.11.0/Library/bin")

class PlanExtractor(QMainWindow, mainDlg_class):
    def __init__(self):
        super(PlanExtractor, self).__init__()
        self.setupUi(self)

        icon = resource_path("scissors.png")
        self.setWindowIcon(QIcon(icon))

        self.default_path = getcwd()
        self.rotateAngle = 0

        self.loadState = 'loading..\n'
        self.loadList = []

        self.loadBtn.clicked.connect(self.loadBtnFunction)
        self.startBtn.clicked.connect(self.startBtnFunction)
        self.resetBtn.clicked.connect(self.resetBtnFunction)

    def loadBtnFunction(self):
        self.progressBar.setValue(0)

        filenames = QFileDialog.getOpenFileNames(self, 'Load jpg files', "",
                                            "All Files(*);; pdf Files(*.pdf);; "
                                            "jpg Files(*.jpg);; png Files(*.png);;" , '/home')
        if filenames[0]:
            filenames = list(filenames)
            filenames.pop()
            filenames = filenames[0]

            self.progressBar.setMaximum(len(filenames))

            filecnt = 0

            for i, filename in enumerate(filenames):
                filecnt += 1
                self.loadList.append(filename)
                self.progressBar.setValue(filecnt)

                temp = filename.split('/')
                self.loadState = self.loadState + str(i) + '... ' + temp[-1] + '\n'
                self.textEdit_jpgList.setText(self.loadState)

            self.loadState = self.loadState + 'Load Complete!'
            self.textEdit_jpgList.setText(self.loadState)
            self.startBtn.setEnabled(True)

        else:
            pass

    def startBtnFunction(self):
        try:
            chdir(self.default_path)

            self.progressBar.setValue(0)
            self.progressBar.setMaximum(len(self.loadList))
            filecnt = 0

            currentState = 'converting..\n'

            for i, name in enumerate(self.loadList):
                oldName = name.split('/')[-1]
                newName = oldName[:-4] + '_fig.jpg'
                currentState = currentState + str(i) + ' : ' + oldName + ' => ' + newName + '\n'

                file_format = name.split(".")[-1]
                if file_format!="jpg":
                    img = ext.convert_jpg(format=file_format, path=name, poppler_path=poppler_path)
                else:
                    img = imread(name)

                img_ori, mask2 = ext.preprocessing(img)
                result = ext.find_plan(img_ori, mask2)

                # Make directory to save result files
                try:
                    chdir("../")
                    imwrite('./result/'+newName, result)
                except Exception as e:
                    if "[WinError 2] 지정된 파일을 찾을 수 없습니다: './result/'" in str(e) or\
                            "No such file or directory" in str(e):
                        mkdir('./result')
                    imwrite('./result/' + newName, result)

                self.textEdit_jpgList.setText(currentState)

                filecnt += 1
                self.progressBar.setValue(filecnt)

            currentState = currentState + 'Finish!'
            self.textEdit_jpgList.setText(currentState)
            self.loadState = 'loading..\n'

            reply = QMessageBox.question(self, 'Message', 'Do you want to convert more files?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                pass
            else:
                sys.exit()
        except Exception as e:
            if "poppler" in str(e):
                QMessageBox.critical(self, "ERROR!!",
                                     "Expected Path: \n"+self.default_path+"\\"+poppler_path)
            else:
                QMessageBox.critical(self, "ERROR!!", str(e))

    def resetBtnFunction(self):
        self.startBtn.setEnabled(False)
        self.loadList = []
        self.progressBar.setValue(0)

if __name__ == "__main__":
    app = QApplication(argv)
    win = PlanExtractor()
    win.show()
    app.exec_()

from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QFrame, QLabel, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import cv2
import numpy as np


class DocScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Document Scanner'
        self.left = 50
        self.top = 50
        self.width = 500
        self.coords = []
        self.filename = ""
        self.check_empty = True
        self.height = 550
        self.setFixedSize(self.width, self.height)
        self.setObjectName("main_window")
        with open("design.qss", "r") as fopen:
            stylesheet = fopen.read()
        self.setStyleSheet(stylesheet)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #---------------------------------------first window-----------------------------------------------------

        self.win1 = QFrame(self)
        self.win1.setObjectName("windows")

        self.upload_btn = QPushButton(self.win1)
        self.upload_btn.setObjectName("btns")
        self.upload_btn.move(200, 12)
        self.upload_btn.setText("Upload Image")
        self.upload_btn.clicked.connect(self.upload_img)

        self.pic_label = QLabel(self.win1)
        self.pic_label.setObjectName("picLabel")
        pixmap = QPixmap("empt.jpg")
        self.pic_label.setPixmap(pixmap)
        self.pic_label.move(100, 70)
        self.pic_label.setScaledContents(True)

        self.select_roi = QPushButton(self.win1)
        self.select_roi.setObjectName("btns")
        self.select_roi.move(140, 450)
        self.select_roi.setText("Select ROI")
        self.select_roi.clicked.connect(self.select_doc)

        self.or_label = QLabel(self.win1)
        self.or_label.move(237, 460)
        self.or_label.setText("OR")
        self.or_label.setObjectName("orLabel")

        self.auto_detect = QPushButton(self.win1)
        self.auto_detect.setObjectName("btns")
        self.auto_detect.move(260, 450)
        self.auto_detect.setText("Auto Detect")
        self.auto_detect.clicked.connect(self.auto_detect_func)

        self.del_pic = QLabel(self.pic_label)
        self.del_pic.move(278, 5)
        self.del_pic.setVisible(False)
        self.del_pic.setObjectName("crossBtn")
        self.del_pic.setTextFormat(Qt.RichText)
        self.del_pic.mousePressEvent = self.remove_pic




        #---------------------------------------Second window-----------------------------------------------------

        self.win2 = QFrame(self)
        self.win2.setObjectName("windows")
        self.win2.setVisible(False)

        self.back_arrow = QLabel(self.win2)
        self.back_arrow.move(15, 0)
        self.back_arrow.setObjectName("back_arrow")
        self.back_arrow.setTextFormat(Qt.RichText)
        self.back_arrow.setText("&#8592;")
        self.back_arrow.mousePressEvent = self.back_arrow_clicked

        self.pic_label_ouput = QLabel(self.win2)
        self.pic_label_ouput.setObjectName("picLabel")
        self.pic_label_ouput.move(100, 70)
        self.pic_label_ouput.setScaledContents(True)

        self.output_label = QLabel(self.win2)
        self.output_label.setText("Extracted document")
        self.output_label.move(148, 430)
        self.output_label.setObjectName("labels")



        self.show()


    # -----------------------------------------------Functions-----------------------------------------------

    def upload_img(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);; JPG (*.jpg);; PNG (*.png)")
        pixmap = QPixmap(self.filename)
        self.filename1 = self.filename
        self.pic_label.setPixmap(pixmap)
        self.del_pic.setVisible(True)
        self.del_pic.setText("&#10005;")
        self.del_pic.adjustSize()
        self.check_empty = False

    def select_doc(self):
        if self.check_empty == False:
            self.img = cv2.imread(self.filename, 1)

            cv2.imshow('image', self.img)
            cv2.setMouseCallback('image', self.click_event)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            self.no_any_image()



    def auto_detect_func(self):
        if self.check_empty == False:
            img = cv2.imread(self.filename1)
            img_threshold = self.preprocess(img)
            contours, hierarchy = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            biggest, maxArea = self.biggest_contour(contours)
            if biggest.size != 0:
                biggest = self.reorder(biggest)
                img_width = biggest[3, 0, 0]
                img_height = biggest[3, 0, 1]
                pts1 = np.float32(biggest)
                pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                img_warp_colored = cv2.warpPerspective(img, matrix, (img_width, img_height))
                cv2.imwrite("Output.jpg", img_warp_colored)
                pixmap = QPixmap("Output.jpg")
                self.pic_label_ouput.setPixmap(pixmap)
                self.win2.setVisible(True)
                self.win1.setVisible(False)
            else:
                self.show_pop_up()
        else:
            self.no_any_image()


    def biggest_contour(self, contours):
        biggest = np.array([])
        max_area = 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > 50:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                if area > max_area and len(approx) == 4:
                    biggest = approx
                    max_area = area
        return biggest, max_area

    def preprocess(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
        img_thres = cv2.adaptiveThreshold(img_blur, 255, 1, 1, 11, 2)
        return img_thres



    def click_event(self, event, x, y, flags, ig):
        # img = cv2.imread(self.filename, 1)
        if event == cv2.EVENT_LBUTTONDOWN:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(self.img, ".", (x, y), font,
                        1, (0, 0, 255), 5)
            self.coords.append([x, y])
            cv2.imshow('image', self.img)
            if len(self.coords) == 4:
                cv2.destroyAllWindows()
                points = self.reorder(self.coords)
                self.coords = []
                img_width = points[3, 0, 0]
                img_height = points[3, 0, 1]
                pts1 = np.float32(points)
                pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                img_warp_colored = cv2.warpPerspective(self.img, matrix, (img_width, img_height))
                cv2.imwrite("Output.jpg", img_warp_colored)
                pixmap = QPixmap("Output.jpg")
                self.pic_label_ouput.setPixmap(pixmap)
                self.win2.setVisible(True)
                self.win1.setVisible(False)


    def reorder(self, points):
        points = np.array(points)
        points = points.reshape((4, 2))
        points_new = np.zeros((4, 1, 2), np.int32)
        add = points.sum(1)
        points_new[0] = points[np.argmin(add)]
        points_new[3] = points[np.argmax(add)]
        diff = np.diff(points, axis=1)
        points_new[1] = points[np.argmin(diff)]
        points_new[2] = points[np.argmax(diff)]
        return points_new

    def back_arrow_clicked(self, event):
        self.win1.setVisible(True)
        self.win2.setVisible(False)

    def show_pop_up(self):
        msg = QMessageBox()
        msg.setWindowTitle("Opps!")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Could not find any document. Please select the roi manually.")
        x = msg.exec_()

    def no_any_image(self):
        msg = QMessageBox()
        msg.setWindowTitle("No Image!")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Please upload an image first.")
        msg.exec_()




    def remove_pic(self, event):
        pixamp = QPixmap("empt.jpg")
        self.pic_label.setPixmap(pixamp)
        self.del_pic.setVisible(False)
        self.check_empty = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    docScan = DocScanner()
    sys.exit(app.exec_())


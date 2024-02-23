import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QLabel, QScrollBar
from PyQt5 import QtCore

class UncertaintyApp(QMainWindow):
    def __init__(self, uncertainties=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]):
        super().__init__()
        self.setWindowTitle("Uncertainty Map Generator")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.generate_button = QPushButton("Generate Uncertainty Map")
        self.layout.addWidget(self.generate_button, 0, 0, 1, 4)

        self.threshold1_label = QLabel("Threshold 1:")
        self.threshold1_scrollbar = QScrollBar(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.threshold1_label, 1, 0)
        self.layout.addWidget(self.threshold1_scrollbar, 1, 1, 1, 3)

        self.threshold2_label = QLabel("Threshold 2:")
        self.threshold2_scrollbar = QScrollBar(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.threshold2_label, 2, 0)
        self.layout.addWidget(self.threshold2_scrollbar, 2, 1, 1, 3)

        self.uncertainties = uncertainties
        self.added_uncertainties = []
        self.removed_uncertainties = []
        self.create_uncertainty_rows()

    def create_uncertainty_rows(self):
        for i, uncertainty in enumerate(self.uncertainties):
            label = QLabel(str(uncertainty))
            label.setAlignment(QtCore.Qt.AlignCenter)  # Center-align the label text
            view_button = QPushButton("View")
            add_button = QPushButton("Add")
            delete_button = QPushButton("Delete")

            row = 3 + i  # Adjust the row index based on the previous rows
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(view_button, row, 1)
            self.layout.addWidget(add_button, row, 2)
            self.layout.addWidget(delete_button, row, 3)

            add_button.clicked.connect(lambda _, unc=uncertainty, r=row: self.add_uncertainty(unc, r))
            delete_button.clicked.connect(lambda _, unc=uncertainty, r=row: self.remove_uncertainty(unc, r))

    def add_uncertainty(self, uncertainty, row):
        self.added_uncertainties.append(uncertainty)
        self.layout.itemAtPosition(row, 0).widget().deleteLater()
        self.layout.itemAtPosition(row, 1).widget().deleteLater()
        self.layout.itemAtPosition(row, 2).widget().deleteLater()
        self.layout.itemAtPosition(row, 3).widget().deleteLater()
        print("added_uncertainties", self.added_uncertainties)
        print("removed_uncertainties", self.removed_uncertainties)

    def remove_uncertainty(self, uncertainty, row):
        self.removed_uncertainties.append(uncertainty)
        self.layout.itemAtPosition(row, 0).widget().deleteLater()
        self.layout.itemAtPosition(row, 1).widget().deleteLater()
        self.layout.itemAtPosition(row, 2).widget().deleteLater()
        self.layout.itemAtPosition(row, 3).widget().deleteLater()
        print("added_uncertainties", self.added_uncertainties)
        print("removed_uncertainties", self.removed_uncertainties)

if __name__ == '__main__':
    uncertainties = [0.9994117, 0.9847864, 0.9663298, 0.94203204, 0.92357075, 0.9172335, 0.9004218, 0.88948745, 0.872781, 0.86585414, 0.8408712, 0.80161023, 0.79769474, 0.76535803, 0.7608035, 0.66329485, 0.6441232, 0.6295662, 0.6058438, 0.57135785, 0.56632525, 0.53965604, 0.48446727, 0.36129376, 0.35598627, 0.34595203, 0.29225653, 0.23944478, 0.23062223, 0.19967544, 0.16696183, 0.14770436, 0.07876308, 0.0741945, 0.0309859, 0.0]  # Replace with your array of uncertainties
    app = QApplication(sys.argv)
    window = UncertaintyApp(uncertainties)
    window.show()
    sys.exit(app.exec_())

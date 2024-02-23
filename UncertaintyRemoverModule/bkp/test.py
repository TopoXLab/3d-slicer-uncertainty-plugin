import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QWidget, QLabel
from PyQt5 import QtCore

class UncertaintyApp(QMainWindow):
    def __init__(self, uncertainties = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]):
        super().__init__()
        self.setWindowTitle("Uncertainty Map Generator")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.generate_button = QPushButton("Generate Uncertainty Map")
        self.layout.addWidget(self.generate_button, 0, 0, 1, 4)

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

            row = 2 + i  # Adjust the row index based on the previous rows
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
    uncertainties = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]  # Replace with your array of uncertainties
    app = QApplication(sys.argv)
    window = UncertaintyApp(uncertainties)
    window.show()
    sys.exit(app.exec_())

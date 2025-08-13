from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

text_edit = QTextEdit()

def lst_to_str(lst):
    result_string = ""
    for pressure in lst:
        result_string += str(pressure) + "\n"
    result_string = result_string[:-1]
    return result_string

lst = []
for i in range(10):
    lst.append(i)
text_edit.setPlainText(lst_to_str(lst))


layout.addWidget(text_edit)
window.setLayout(layout)
window.show()
app.exec_()

class Recorder(QThread):

    def __init__(self):
        super().__init__()
        

    def run(self):
        for i in range(100):
            

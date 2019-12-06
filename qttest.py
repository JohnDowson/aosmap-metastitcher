from os import path
import lzma
DEBUG = False
#from PyQt5.QtWidgets import QFileDialog, QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QPlainTextEdit
from PyQt5.QtWidgets import *
def debug(msg, *variables):
    with open("./metastitcher_debug.log", mode='wt') as logfile:
        logfile.write("#### " + msg)
        for var in variables:
            logfile.write(var)
class Button:
    def __init__(self, text, callback):
        self.callback = callback
        self._button = QPushButton(text)
        self._button.clicked.connect(self.callback)

    def __call__(self):
        return self._button
HEADER      = b'\x02\x01\x00AOSMAP\x00\x01\x02'
END_OF_META = b'\x00METADATAEND\x00'

class AosMap:
    def __init__(self, binary, metadata=""):
        self.vxl = binary
        self.metadata = metadata

    def to_file(self, filename):
        with open(filename, mode='wb') as map_file:
            map_file.write(HEADER)
            map_file.write(bytes(self.metadata, encoding='ascii'))
            map_file.write(END_OF_META)
            vxl_lzma = lzma.compress(self.vxl, format=lzma.FORMAT_ALONE)
            map_file.write(vxl_lzma)

    def to_vxl(self, filename):
        with open(filename, mode='wb') as vxl_file:
            vxl_file.write(self.vxl)
    
    def __str__(self):
        return f"VXL bytes: {str(self.vxl)}\nMetadata: {self.metadata}"

    @classmethod
    def from_aosmap(self, aosmap: bytes):
        if aosmap[0:len(HEADER)] != HEADER:
            raise TypeError
        else:
            current_byte = len(HEADER)
            metadata = ""
            while aosmap[current_byte:current_byte+len(END_OF_META)] != END_OF_META:
                metadata += chr(aosmap[current_byte])
                current_byte += 1
            current_byte += len(END_OF_META)
            vxl_lzma = aosmap[current_byte:]
            vxl_data = lzma.decompress(vxl_lzma, format = lzma.FORMAT_ALONE)
            return self(vxl_data, metadata)

app = QApplication([])
def fileDialogCallbackFactory(file_path_global, file_name_label):
    def callback():
        file, _ = QFileDialog.getOpenFileName(window, "Pick VXL", "", "All Files (*);;Map Files (*.vxl, *.aosmap)")
        if DEBUG:
            debug(f"File {path.dirname(file)}, {path.basename(file)}")
        
        globals()[file_path_global] = file
        globals()[file_name_label].setText(file)
    return callback


open_path = "./map.aosmap"
save_path = "./map.aosmap"
vxl_map = None
def loadMap():
    with open(open_path, mode='rb') as vxl_file:
        vxl_data = vxl_file.read()

        if path.basename(open_path).split('.')[-1] == 'aosmap':
            vxl_map = AosMap.from_aosmap(vxl_data)
            metadata_field.clear()
            metadata_field.insertPlainText(vxl_map.metadata)
        else:
            vxl_map = AosMap(vxl_data, metadata=metadata_field.toPlainText())

        if DEBUG:
            vxl_file_repr = str(vxl_map)
            map_display.clear()
            map_display.insertPlainText(vxl_file_repr)
            vxl_map.to_vxl("./test_vxl_out")
        globals()['vxl_map'] = vxl_map

def saveMap():
    if vxl_map:
        print(f"saving map to {save_path}")
        vxl_map.metadata = metadata_field.toPlainText()
        vxl_map.to_file(save_path)

loadVXL = Button('Load map', loadMap)
selectVXL = Button('Select map', fileDialogCallbackFactory('open_path', 'loadpathShower'))
selectSave = Button('Select output file', fileDialogCallbackFactory('save_path', 'savepathShower'))
saveAosmap = Button('Save as aosmap', saveMap)

window = QWidget()
load_row = QHBoxLayout()
load_row.addWidget(selectVXL())
loadpathShower = QLabel(open_path)
load_row.addWidget(loadpathShower)
load_row.addWidget(loadVXL())

savepathShower = QLabel(save_path)
save_row = QHBoxLayout()
save_row.addWidget(selectSave())
save_row.addWidget(savepathShower)
save_row.addWidget(saveAosmap())

if DEBUG:
    map_display = QPlainTextEdit()
    map_display.setPlaceholderText("AOSMAP REPRESENTATION")
    layout.addWidget(map_display)

metadata_field = QPlainTextEdit()
metadata_field.setPlaceholderText("AOSMAP REPRESENTATION")

layout = QVBoxLayout()
layout.addWidget(metadata_field)
layout.addLayout(load_row)
layout.addLayout(save_row)
window.setLayout(layout)
window.show()
app.exec_()

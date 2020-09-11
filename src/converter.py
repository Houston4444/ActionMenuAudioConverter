#!/usr/bin/python3

import os
import shlex
import subprocess
import sys
import threading

#from pymediainfo import MediaInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import QProcess, QTimer

import ui_ogg
import ui_progress

EXTENSIONS = {'wav': 'audio-x-wav',
              'flac': 'audio-x-flac',
              'mp3': 'audio-mp3',
              'ogg': 'audio-x-generic'}

MODE_ONE_FILE = 0 # there is only one file given as argument
MODE_MANY_FILES = 1 # many files are given as arguments
MODE_FOLDERS = 2 # arguments are folders

def home_clean(path:str)->str:
    if path.startswith(os.getenv('HOME') + '/'):
        return path.replace(os.getenv('HOME') + '/', '~/', 1)
    return path

def file_path_convert(ext:str, file_path:str, black_list:list)->str:
        file_no_ext = file_path
        if '.' in os.path.basename(file_path):
            file_no_ext = file_path.rpartition('.')[0]

        output_file = file_no_ext + '.' + ext
        
        i=1
        while os.path.exists(output_file) or output_file in black_list:
            output_file = file_no_ext + ' (%i).' % i + ext
            i+=1
        
        return output_file


class MainObject:
    extension = 'wav'
    mode = MODE_MANY_FILES
    input_common_path = ''
    output_common_path = ''
    _walk_finished = False
    
    def __init__(self, extension, arg_files):
        self.extension = extension
        self.arg_files = arg_files
        self.true_files = []
        self.process_args = []
        
        if not arg_files:
            sys.stderr.write("error, missing arguments\n")
            sys.exit(1)
            return
        
        if os.path.isdir(arg_files[0]):
            self.mode = MODE_FOLDERS
        elif len(arg_files) == 1:
            self.mode = MODE_ONE_FILE
        
        self.input_common_path = arg_files[0]
        if len(arg_files) > 1:
            self.input_common_path = os.path.commonpath(arg_files)
        
        if self.mode == MODE_ONE_FILE:
            self.output_common_path = file_path_convert(self.extension, self.input_common_path, [])
        elif self.mode == MODE_MANY_FILES:
            self.output_common_path = self.input_common_path
        elif self.mode == MODE_FOLDERS:
            self.output_common_path = "%s (%s)" % (self.input_common_path, self.extension)
    
    def arg_files_len(self):
        return len(self.arg_files)
    
    def walk(self):
        self.true_files.clear()
        
        if self.mode != MODE_FOLDERS:
            for arg_file in self.arg_files:
                self.true_files.append(
                    arg_file.replace(self.input_common_path + '/', '', 1))
            self._walk_finished = True
            return
        
        for arg_dir in self.arg_files:
            for root, dirs, files in os.walk(arg_dir):
                base_root = root.replace(self.input_common_path + '/', '', 1)
                for file in files:
                    self.true_files.append("%s/%s" % (base_root, file))
                    
        self._walk_finished = True
    
    def walk_finished(self):
        return self._walk_finished
    
    def get_full_true_file_path(self, index:int)->str:
        if self.mode == MODE_ONE_FILE:
            return self.input_common_path
        return "%s/%s" % (self.input_common_path, self.true_files[index])
    
    def get_converted_file(self, index:int)->str:
        if index >= len(self.true_files):
            sys.stderr.write("index out of range %i for %i\n" % (index, (len(self.true_files))))
            return ""
        
        if self.mode == MODE_ONE_FILE:
            return self.output_common_path
        
        return self.file_path_convert(self.true_files[index])
        
    def file_path_convert(self, file_path:str):
        file_no_ext = file_path
        if '.' in os.path.basename(file_path):
            file_no_ext = file_path.rpartition('.')[0]

        output_file = "%s.%s" % (file_no_ext, self.extension)
        
        output_dir = self.output_common_path
        if self.mode == MODE_ONE_FILE:
            output_dir = ''
        
        i=1
        while os.path.exists("%s/%s" % (output_dir, output_file)):
            output_file = "%s (%i).%s" % (file_no_ext, i, self.extension)
            i+=1
        
        return "%s/%s" % (output_dir, output_file)
    
    
class ProgressDialog(QDialog):
    def __init__(self, main_object):
        QDialog.__init__(self)
        self.ui = ui_progress.Ui_Dialog()
        self.ui.setupUi(self)
        
        self.mo = main_object
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.check_n_files)
        
        self.check_n_files()
        self.timer.start()
            
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ForwardedChannels)
        self.process.finished.connect(self.process_finished)
        
        self.file_error_indexes = []
        self.running_index = 0
        
        self.start_process()
    
    def check_n_files(self):
        number_of_files = len(self.mo.true_files)
        self.ui.progressBar.setMaximum(number_of_files)
        if self.mo.walk_finished():
            self.timer.stop()
    
    def process_finished(self, exit_code, exit_status):
        if exit_code:
            self.files_error_indexes.append(self.running_index)
        self.running_index += 1
        self.ui.progressBar.setValue(self.running_index)
        
        if self.running_index == len(self.mo.true_files):
            self.accept()
            return
        
        self.start_process()
        
    def start_process(self):
        process_args = ['-hide_banner', '-i',
                        self.mo.get_full_true_file_path(self.running_index)]
        process_args += self.mo.process_args
        process_args.append(self.mo.get_converted_file(self.running_index))
        
        cli_args = []
        for string in process_args:
            if shlex.quote(string).startswith("'"):
                cli_args.append('"%s"' % string.replace('"', '\"'))
            else:
                cli_args.append(string)
        
        sys.stdout.write("\033[92m$\033[0m ffmpeg " + ' '.join(cli_args) + '\n')
        self.process.start('ffmpeg', process_args)
        
        self.ui.labelSource.setText(home_clean(self.mo.get_full_true_file_path(self.running_index)))
        self.ui.labelStep.setText("Treating file %i/%i" % (self.running_index + 1, len(self.mo.true_files)))

class ogg_dialog(QDialog):
    def __init__(self, main_object):
        QDialog.__init__(self)
        self.ui = ui_ogg.Ui_Dialog()
        self.ui.setupUi(self)
        
        self.mo = main_object
        
        self.ui.comboBoxSamplerate.addItem('44.100 kHz', 44100)
        self.ui.comboBoxSamplerate.addItem('48.000 kHz', 48000)
        if self.mo.extension != 'mp3':
            self.ui.comboBoxSamplerate.addItem('88.000 kHz', 88000)
            self.ui.comboBoxSamplerate.addItem('96.000 kHz', 96000)
            self.ui.comboBoxSamplerate.addItem('192.000 kHz', 192000)
        self.ui.comboBoxSamplerate.setCurrentIndex(0)
        
        for bitrate in (64, 80, 96, 112, 128, 160, 192, 224, 256, 320):
            self.ui.comboBoxMp3Quality.addItem(str(bitrate) + ' Kbits', bitrate)
        self.ui.comboBoxMp3Quality.setCurrentIndex(8) # 256 KBits by default
        
        self.ui.comboBoxBitDepth.addItem('16 Bits', 16)
        self.ui.comboBoxBitDepth.addItem('24 Bits', 24)
        if self.mo.extension != 'flac':
            self.ui.comboBoxBitDepth.addItem('32 Bits (float)', 32)
            self.ui.comboBoxBitDepth.addItem('64 Bits (float)', 64)

        self.ui.checkBoxSamplerate.stateChanged.connect(
            self.ui.comboBoxSamplerate.setEnabled)
        self.ui.checkBoxOggQuality.stateChanged.connect(
            self.ui.spinBoxOggQuality.setEnabled)
        self.ui.checkBoxMp3Quality.stateChanged.connect(
            self.ui.comboBoxMp3Quality.setEnabled)
        self.ui.checkBoxBitDepth.stateChanged.connect(
            self.ui.comboBoxBitDepth.setEnabled)
        self.ui.checkBoxVideo.stateChanged.connect(self.video_box_changed)
        self.ui.checkBoxAudio.stateChanged.connect(self.audio_box_changed)
        self.ui.toolButtonOutputPath.clicked.connect(
            self.tool_button_output_path_clicked)
        
        label = ""
        
        if self.mo.mode == MODE_FOLDERS:
            if len(self.mo.arg_files) == 1:
                label = "<p>Convert audio files in folder "
                label += "<strong>%s</strong> to %s.</p>" \
                    % (home_clean(self.mo.arg_files[0]), self.mo.extension.upper())
            else:
                label = "<p>Convert %i folders to %s.</p>" % (len(self.mo.arg_files),
                                                     self.mo.extension.upper())
        elif self.mo.mode == MODE_ONE_FILE:
            label = "<p>Convert <strong>%s</strong> to %s.</p>" \
                    % (home_clean(self.mo.input_common_path), self.mo.extension.upper())
            self.ui.groupBoxFolder.setVisible(False)
            
        elif self.mo.mode == MODE_MANY_FILES:
            label = "<p>Convert %i files to %s.</p>" % (len(self.mo.arg_files),
                                                        self.mo.extension.upper())
            self.ui.groupBoxFolder.setVisible(False)
            
        self.ui.labelPresentation.setText(label)
            
        self.set_output_path(self.mo.output_common_path)
        
        if self.mo.extension != 'ogg':
            self.ui.checkBoxOggQuality.setVisible(False)
            self.ui.labelColonOggQuality.setVisible(False)
            self.ui.spinBoxOggQuality.setVisible(False)
        if self.mo.extension != 'mp3':
            self.ui.checkBoxMp3Quality.setVisible(False)
            self.ui.labelColonMp3Quality.setVisible(False)
            self.ui.comboBoxMp3Quality.setVisible(False)
        if self.mo.extension not in ('wav', 'flac'):
            self.ui.checkBoxBitDepth.setVisible(False)
            self.ui.labelColonBitDepth.setVisible(False)
            self.ui.comboBoxBitDepth.setVisible(False)
        
        self.resize(0, 0)
        #self.resize(self.width(), self.height() + 100)
        
    def video_box_changed(self, state):
        if not state:
            self.ui.checkBoxAudio.setChecked(True)
    
    def audio_box_changed(self, state):
        if not state:
            self.ui.checkBoxVideo.setChecked(True)
    
    def tool_button_output_path_clicked(self):
        if self.mo.mode == MODE_ONE_FILE:
            path = QFileDialog.getSaveFileName(
                self, "convert to…", self.mo.output_common_path,
                "Audio Files (*.%s)" % self.mo.extension)
            if not path:
                return
        else:
            path = QFileDialog.getExistingDirectory(
                self, "Choose directory where files will be converted…", self.mo.output_common_path)
            if not path:
                return

        self.set_output_path(path)
    
    def set_output_path(self, path):        
        path_label = "<html><head/><body><p>Output folder:<br/>"
        if self.mo.mode == MODE_ONE_FILE:
            path_label = "<html><head/><body><p>Output file:<br/>"
        path_label += "<span style=\" font-style:italic;\">"
        path_label += home_clean(path)
        if not self.mo.mode == MODE_ONE_FILE:
            path_label += '/'
        path_label += "</span></p></body></html>"
        
        self.output_path = path
        self.ui.labelOutputPath.setText(path_label)
    
    def get_output_path(self):
        return self.output_path
    
    def get_process_args(self):
        args = ['-vn', '-c:a']
        
        if self.mo.extension == 'ogg':
            args.append('libvorbis')
            if self.ui.checkBoxOggQuality.isChecked():
                args += ['-q', str(self.ui.spinBoxOggQuality.value())]

        elif self.mo.extension == 'mp3':
            args.append('libmp3lame')
            if self.ui.checkBoxMp3Quality.isChecked():
                args += ['-ab', str(self.ui.comboBoxMp3Quality.currentData()) + 'k']

        elif self.mo.extension == 'flac':
            args.append('flac')
            if (self.ui.checkBoxBitDepth.isChecked()
                    and self.ui.comboBoxBitDepth.currentData() == 16):
                args += ['-sample_fmt', 's16']

        elif self.mo.extension == 'wav':
            encoder = 'pcm_s16le'
            if self.ui.checkBoxBitDepth.isChecked():
                bits = self.ui.comboBoxBitDepth.currentData()
                if bits <= 24:
                    encoder = 'pcm_s%ile' % bits
                else:
                    encoder = 'pcm_f%ile' % bits
            args.append(encoder)

        if self.ui.checkBoxSamplerate.isChecked():
            args += ['-ar', str(self.ui.comboBoxSamplerate.currentData())]

        return args
    
def extension_and_files(args):
    if len(args) < 3:
        sys.stderr.write('Not enought arguments.\n')
        sys.exit(1)
    
    extension = args[1]
    if not extension.lower() in EXTENSIONS:
        sys.stderr.write('extension can only be %s.\n' % ' '.join(EXTENSIONS))
        sys.exit(1)
    
    files = []
    for input_file in args[2:]:
        if not input_file.startswith('/'):
            input_file = os.getcwd() + '/' + input_file
        files.append(input_file)
        
    return (extension, files)

def main_script():
    if len(sys.argv) < 3:
        sys.stderr.write('Not enought arguments.\n')
        sys.exit(1)
    
    extension = sys.argv[1]
    if not extension.lower() in EXTENSIONS:
        sys.stderr.write('extension can only be %s.\n' % ' '.join(EXTENSIONS))
        sys.exit(1)
    
    arg_files = []
    for arg in sys.argv[2:]:
        arg_files.append(os.path.realpath(arg))
    
    main_object = MainObject(extension, arg_files)
    
    walk_thread = threading.Thread(target=main_object.walk)
    walk_thread.start()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme(EXTENSIONS[extension]))
    
    dialog = ogg_dialog(main_object)
    dialog.exec()
    if not dialog.result():
        sys.exit(0)
        
    main_object.output_common_path = dialog.get_output_path()
    main_object.process_args = dialog.get_process_args()
    
    progress_dialog = ProgressDialog(main_object)
    progress_dialog.exec()
    
    walk_thread.join()
    app.quit()

if __name__ == '__main__':
    main_script()
    

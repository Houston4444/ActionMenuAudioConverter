

import os
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from pymediainfo import MediaInfo

import main_object as Mo
import ui_first_dialog

_translate = QApplication.translate

class FirstDialog(QDialog):
    def __init__(self, main_object, settings):
        QDialog.__init__(self)
        self.ui = ui_first_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.mo = main_object
        ext = self.mo.extension
        upper_ext = ext.upper()

        self.ui.comboBoxSamplerate.addItem('44.100 kHz', 44100)
        self.ui.comboBoxSamplerate.addItem('48.000 kHz', 48000)
        if self.mo.extension != 'mp3':
            self.ui.comboBoxSamplerate.addItem('88.000 kHz', 88000)
            self.ui.comboBoxSamplerate.addItem('96.000 kHz', 96000)
            self.ui.comboBoxSamplerate.addItem('192.000 kHz', 192000)

        for i in range(self.ui.comboBoxSamplerate.count()):
            if (self.ui.comboBoxSamplerate.itemData(i)
                    == settings.value("%s_samplerate" % ext,
                                      44100, type=int)):
                self.ui.comboBoxSamplerate.setCurrentIndex(i)
                break

        if ext == 'mp3':
            for bitrate in (64, 80, 96, 112, 128, 160, 192, 224, 256, 320):
                self.ui.comboBoxMp3Quality.addItem(
                    "%i Kbits" % bitrate, bitrate)
            for i in range(self.ui.comboBoxMp3Quality.count()):
                if (self.ui.comboBoxMp3Quality.itemData(i)
                        == settings.value("%s_quality" % ext,
                                        256, type=int)):
                    self.ui.comboBoxMp3Quality.setCurrentIndex(i)
                    break

        elif ext in ('wav', 'flac'):
            self.ui.comboBoxBitDepth.addItem('16 Bits', 16)
            self.ui.comboBoxBitDepth.addItem('24 Bits', 24)
            if ext != 'flac':
                self.ui.comboBoxBitDepth.addItem('32 Bits (float)', 32)
                self.ui.comboBoxBitDepth.addItem('64 Bits (float)', 64)

            for i in range(self.ui.comboBoxBitDepth.count()):
                if (self.ui.comboBoxBitDepth.itemData(i)
                        == settings.value("%s_bitdepth" % ext, 16, type=int)):
                    self.ui.comboBoxBitDepth.setCurrentIndex(i)
                    break

        elif ext == 'ogg':
            self.ui.spinBoxOggQuality.setValue(
                settings.value("%s_quality" % ext, 7, type=int))

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

        if self.mo.mode == Mo.MODE_FOLDERS:
            if len(self.mo.arg_files) <= 5:
                label = "<p>"
                if len(self.mo.arg_files) == 1:
                    label += _translate('first_dialog', "Convert to %s audio files in folder") \
                        % upper_ext
                else:
                    label += _translate('first_dialog', "Convert to %s audio files in folders") \
                        % upper_ext
                label += "<br><span style=\" font-style:italic;\">"
                label += '<br>'.join(
                    ["%s" % self.mo.shorter_path(a) for a in self.mo.arg_files])
                label += "</span></p>"
            else:
                label = _translate('first_dialog', "Convert to %s audio files in %i folders" % (
                    len(self.mo.arg_files), len(self.mo.arg_files)))

        else:
            is_video = False
            media_info = MediaInfo.parse(self.mo.arg_files[0])
            for track in media_info.tracks:
                if track.track_type == "Video":
                    is_video = True
                    break

            if len(self.mo.arg_files) <= 5:
                label = "<p>"
                if self.mo.mode == Mo.MODE_ONE_FILE:
                    if is_video:
                        label += _translate('first_dialog', "Extract to %s audio tracks from video file") \
                            % upper_ext
                    else:
                        label += _translate('first_dialog', "Convert to %s audio file") % upper_ext
                    label += "<br><span style=\" font-style:italic;\">%s</span></p>" \
                        % self.mo.shorter_path(self.mo.input_common_path)
                else:
                    if is_video:
                        label += _translate('first_dialog', "Extract to %s audio tracks from video files") \
                            % upper_ext
                    else:
                        label += _translate('first_dialog', "Convert to %s audio files") % upper_ext
                    label += "<br><span style=\" font-style:italic;\">"
                    label += '<br>'.join(
                        ["%s" % self.mo.shorter_path(a) for a in self.mo.arg_files])
                    label += "</span></p>"
            else:
                label = _translate('first_dialog', "Convert %i audio files to %s") % (
                    len(self.mo.arg_files), upper_ext)

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

        self.setWindowTitle(_translate('first_dialog', "%s Conversion") % upper_ext)
        self.resize(0, 0)

    def video_box_changed(self, state):
        if not state:
            self.ui.checkBoxAudio.setChecked(True)

    def audio_box_changed(self, state):
        if not state:
            self.ui.checkBoxVideo.setChecked(True)

    def tool_button_output_path_clicked(self):
        path = ""
        check_path = ""

        while True:
            if self.mo.mode == Mo.MODE_ONE_FILE:
                path, ok = QFileDialog.getSaveFileName(
                    self,
                    _translate('first_dialog', "Convert to %s to...") % self.mo.extension.upper(),
                    self.mo.output_common_path,
                    "%s(*.%s)" % (
                        _translate('first_dialog', "%s Audio files") % self.mo.extension.upper(),
                        self.mo.extension))

                if not ok:
                    return

                check_path = os.path.dirname(path)
            else:
                path = QFileDialog.getExistingDirectory(
                    self,
                    _translate('first_dialog', "Folder where files will be converted to %s")
                        % self.mo.extension.upper(),
                    self.mo.output_common_path)

                if not path:
                    return

                check_path = path

            if not os.access(check_path, os.W_OK):
                QMessageBox.critical(self, _translate('first_dialog', "Unwritable Path"),
                    _translate('first_dialog', "%s is not writable, please choose a writable path.") % (path))
                continue

            if self.mo.mode == Mo.MODE_FOLDERS:
                for folder in self.mo.arg_files:
                    if folder == path or path.startswith(folder + '/'):
                        QMessageBox.critical(self, _translate('first_dialog', "Wrong folder"),
                            _translate('first_dialog', "Impossible. Folder %s is in %s which is part of the selection")
                                % (path, folder))
                        continue
            break

        self.set_output_path(path)

    def set_output_path(self, path):
        path_label = "<p><strong>%s</strong><br/>" % _translate('first_dialog', "Output folder:")
        if self.mo.mode == Mo.MODE_ONE_FILE:
            path_label = "<p><strong>%s</strong><br/>" % _translate('first_dialog', "Output file:")
        path_label += "<span style=\" font-style:italic;\">"
        path_label += self.mo.shorter_path(path)
        if not self.mo.mode == Mo.MODE_ONE_FILE:
            path_label += '/'
        path_label += "</span></p>"

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

    def get_video_mode(self)->int:
        if self.mo.mode != Mo.MODE_FOLDERS:
            return Mo.MODE_VIDEO_EXTRACT

        if self.ui.checkBoxAudio.isChecked():
            if self.ui.checkBoxVideo.isChecked():
                return Mo.MODE_VIDEO_EXTRACT
            return Mo.MODE_VIDEO_COPY
        return Mo.MODE_VIDEO_ONLY

    def get_max_copy_size(self)->int:
        size = self.ui.spinBoxCopySize.value()
        if size < 1:
            # set max_size to -1 to avoid copy of empty files
            return -1

        return size * 1024 * 1024

    def get_parameters(self)->tuple:
        return (self.get_output_path(),
                self.get_video_mode(),
                self.get_max_copy_size(),
                self.get_process_args())

    def remember_settings(self, settings):
        ext = self.mo.extension

        settings.setValue("%s_samplerate" % ext,
                          self.ui.comboBoxSamplerate.currentData())

        if ext in ('wav', 'flac'):
            settings.setValue("%s_bitdepth" % ext,
                              self.ui.comboBoxBitDepth.currentData())
        elif ext == 'ogg':
            settings.setValue("%s_quality" % ext,
                              self.ui.spinBoxOggQuality.value())
        elif ext == 'mp3':
            settings.setValue("%s_quality" % ext,
                              self.ui.comboBoxMp3Quality.currentData())

        if self.mo.mode == Mo.MODE_FOLDERS:
            settings.setValue("video_mode", self.get_video_mode())
            settings.setValue("max_copy_size", self.ui.spinBoxCopySize.value())

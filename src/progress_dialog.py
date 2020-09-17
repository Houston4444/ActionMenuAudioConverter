
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTimer

import main_object as Mo
import ui_progress

_translate = QApplication.translate

class ProgressDialog(QDialog):
    def __init__(self, main_object, settings):
        QDialog.__init__(self)
        self.ui = ui_progress.Ui_Dialog()
        self.ui.setupUi(self)

        self.mo = main_object
        self.settings = settings
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.check_n_files)

        if self.mo.mode == Mo.MODE_ONE_FILE:
            self.ui.line_2.setVisible(False)
            self.ui.labelStep.setVisible(False)
            self.ui.progressBar.setVisible(False)

        self.ui.labelExtension.setText(_translate('progress',
            "Conversion to %s...") % self.mo.extension.upper())

        self.ui.checkBox.setChecked(
            settings.value('close_terminal', True, type=bool))

        self.check_n_files()
        self.timer.start()

    def check_n_files(self):
        number_of_files = len(self.mo.true_files)
        self.ui.progressBar.setMaximum(number_of_files)
        if self.mo.walk_finished():
            self.timer.stop()

    def display_running_file(self, input_file: str, output_file: str,
                             running_index: int, total: int):
        self.ui.labelSource.setText(self.mo.shorter_path(input_file))
        self.ui.labelDestination.setText(self.mo.shorter_path(output_file))
        self.ui.labelStep.setText(_translate('progress',
            "Treating file %i/%i") % (running_index + 1, total))
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(running_index)

    def close_terminal_at_end(self)->bool:
        return self.ui.checkBox.isChecked()

    def get_terminal_end_translated(self)->tuple:
        # should not be there, but app.tr() doesn't works
        return (self.tr("Some errors appears, "),
                self.tr("Press Enter to close this terminal:"))


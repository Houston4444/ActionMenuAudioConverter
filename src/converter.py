#!/usr/bin/python3

import os
import sys
import threading

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale, QTranslator, QSettings

import main_object as Mo
import first_dialog
import progress_dialog


def main_script():
    if len(sys.argv) < 3:
        sys.stderr.write('Not enought arguments.\n')
        sys.exit(1)
    
    extension = sys.argv[1]
    if not extension.lower() in Mo.EXTENSIONS:
        sys.stderr.write('extension can only be %s.\n' % ' '.join(Mo.EXTENSIONS))
        sys.exit(1)
    
    arg_files = []
    for arg in sys.argv[2:]:
        arg_files.append(os.path.realpath(arg))
    
    main_obj = Mo.MainObject(extension, arg_files)
    
    # start to list files before displaying the first dialog
    walk_thread = threading.Thread(target=main_obj.walk)
    walk_thread.start()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme(Mo.EXTENSIONS[extension]))
    
    settings = QSettings()
    
    ### Translation process
    locale = QLocale.system().name()
    app_translator = QTranslator()
    code_root = os.path.dirname(os.path.dirname(sys.argv[0]))
    
    if app_translator.load("%s/locale/converter_%s" % (code_root, locale)):
        app.installTranslator(app_translator)
    
    dialog = first_dialog.FirstDialog(main_obj, settings)
    dialog.exec()
    if not dialog.result():
        sys.exit(0)
    
    dialog.remember_settings(settings)
    
    progress_dlg = progress_dialog.ProgressDialog(main_obj, settings)
    main_obj.progress_dialog = progress_dlg
    main_obj.read_parameters(dialog.get_parameters())
    main_obj.start_next_process()
    progress_dlg.exec()
    
    close_terminal = progress_dlg.close_terminal_at_end()
    terminal_end_translated = progress_dlg.get_terminal_end_translated()
    settings.setValue('close_terminal', close_terminal)
    
    walk_thread.join()
    app.quit()
    
    if main_obj.files_error_indexes:
        sys.stderr.write(terminal_end_translated[0])
    if main_obj.files_error_indexes or not close_terminal:
        sys.stderr.write(terminal_end_translated[1])
        input()

if __name__ == '__main__':
    main_script()
    


import os
import dbus
import random

from PyQt5.QtCore import QCoreApplication

import main_object as Mo


class Notifier:
    item              = "org.freedesktop.Notifications"
    path              = "/org/freedesktop/Notifications"
    interface         = "org.freedesktop.Notifications"
    #random is used to don't group notifications
    #app_name          = "ActionMenuAudioConverter" + str(random.random())
    id_num_to_replace = 0
    icon              = ""
    title             = ""
    text              = ""
    actions_list      = ''
    hint              = ''
    time              = 0   # Use seconds x 1000

    def __init__(self, main_object):
        self.mo = main_object
        self.icon = Mo.EXTENSIONS[self.mo.extension]
        self.text = self.mo.output_common_path
        self.app_name = "ActionMenuAudioConverter_" + self.mo.extension

    def notify(self):
        # no notification if no new audio file
        if not self.mo.audio_converted_count:
            return

        _translate = QCoreApplication.translate

        title = _translate('notifications', "Conversion to %s") \
            % self.mo.extension.upper()

        text = ""

        if self.mo.mode == Mo.MODE_ONE_FILE:
            text = _translate('notifications', "New %s audio file:") \
                % self.mo.extension
        else:
            text = _translate('notifications', "%i new %s audio files in") \
                % (self.mo.audio_converted_count, self.mo.extension)

        text += '\n'
        text += self.mo.shorter_path(self.mo.output_common_path)

        bus = dbus.SessionBus()
        notif = bus.get_object(self.item, self.path)
        notify = dbus.Interface(notif, self.interface)
        notify.Notify(self.app_name, self.id_num_to_replace, self.icon, title, text, '', '', 2000)

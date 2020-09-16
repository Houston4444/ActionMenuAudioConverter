
import os
import shlex
import sys

from PyQt5.QtCore import QProcess
from pymediainfo import MediaInfo

EXTENSIONS = {'wav': 'audio-x-wav',
              'flac': 'audio-x-flac',
              'mp3': 'audio-mp3',
              'ogg': 'audio-x-generic'}

MODE_ONE_FILE = 0 # there is only one file given as argument
MODE_MANY_FILES = 1 # many files are given as arguments
MODE_FOLDERS = 2 # arguments are folders

MODE_VIDEO_EXTRACT = 0
MODE_VIDEO_COPY = 1
MODE_VIDEO_ONLY = 2

class MainObject:
    extension = 'wav'
    mode = MODE_MANY_FILES
    video_mode = MODE_VIDEO_EXTRACT
    input_common_path = ''
    output_common_path = ''
    max_copy_size = 1024 * 1024 * 10
    _walk_finished = False
    _running_index = -1
    output_is_writable = False
    
    @staticmethod
    def shorter_path(path: str)->str:
        home_slash = os.getenv('HOME') + '/'
        
        if path.startswith(home_slash):
            path = path.replace(home_slash, '~/', 1)
        
        if len(path) > 140:
            return "%s[…]%s" % (path[:68], path[-68:])
        return path
    
    def __init__(self, extension, arg_files):
        self.extension = extension
        self.arg_files = arg_files
        self.true_files = []
        self.files_error_indexes = []
        self.process_args = []
        self.progress_dialog = None
        
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ForwardedChannels)
        self.process.finished.connect(self.process_finished)
        
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
        
        # set the output common path
        if self.mode == MODE_ONE_FILE:
            dirname, slash, file_no_ext = self.input_common_path.rpartition('/')
            
            if '.' in os.path.basename(file_no_ext):
                file_no_ext = file_no_ext.rpartition('.')[0]
            
            if not os.access(dirname, os.W_OK):
                dirname = self.get_music_dir()
            
            output_file = "%s/%s.%s" % (dirname, file_no_ext, self.extension)
            
            i = 1
            while os.path.exists(output_file):
                output_file = '%s/%s (%i).%s' % (dirname, file_no_ext, i, self.extension)
                i += 1
            
            self.output_common_path = output_file
            
        elif self.mode == MODE_MANY_FILES:
            self.output_common_path = self.input_common_path
            if not os.access(self.output_common_path, os.W_OK):
                self.output_common_path = self.get_music_dir()
                
        elif self.mode == MODE_FOLDERS:
            dirname ,slash, basedir = self.input_common_path.rpartition('/')
            if not os.access(dirname, os.W_OK):
                dirname = self.get_music_dir()
            
            self.output_common_path = "%s/%s (%s)" % (
                dirname, basedir, self.extension)
            
            n = 1
            while os.path.exists(self.output_common_path):
                self.output_common_path = "%s/%s (%s) (%i)" % (
                    dirname, self.input_common_path, self.extension, n)
                n += 1
    
    def get_music_dir(self):
        user_dirs_file = "%s/.config/user-dirs.dirs" % os.getenv('HOME')
        if (os.path.exists(user_dirs_file)
                and os.access(user_dirs_file, os.R_OK)):
            file = open(user_dirs_file, 'r')
            data = file.read()
            for line in data.split('\n'):
                if line.startswith("XDG_MUSIC_DIR="):
                    music_dirs = line.partition('=')[2]
                    music_dir_list = shlex.split(music_dirs)
                    if music_dir_list:
                        music_dir = os.path.expandvars(music_dir_list[0])
                        if (os.path.exists(music_dir)
                                and os.access(music_dir, os.W_OK)):
                            return music_dir
                    break

        return os.getenv('HOME')
    
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
                if root == self.input_common_path:
                    for file in files:
                        self.true_files.append(file)
                else:
                    base_root = root.replace(self.input_common_path + '/', '', 1)
                    for file in files:
                        self.true_files.append("%s/%s" % (base_root, file))
                        
        self._walk_finished = True
    
    def walk_finished(self):
        return self._walk_finished
    
    def read_parameters(self, parameters: tuple):
        self.output_common_path, self.video_mode, self.max_copy_size, self.process_args = parameters
    
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
    
    def process_finished(self, exit_code, exit_status):
        if exit_code:
            self.files_error_indexes.append(self._running_index)
        
        if self._running_index + 1 == len(self.true_files):
            if self.progress_dialog:
                self.progress_dialog.accept()
            return
        
        self.start_next_process()
    
    def start_next_process(self):
        while True:
            self._running_index += 1
            input_file = self.get_full_true_file_path(self._running_index)
            
            is_video = False
            is_audio = False
            must_copy = False
            
            media = MediaInfo.parse(input_file)
            for track in media.tracks:
                if track.track_type == "Video":
                    is_video = True
                elif track.track_type == "Audio":
                    is_audio = True
            
            if (not is_audio
                    or (is_video and self.video_mode == MODE_VIDEO_COPY)
                    or (not is_video and self.video_mode == MODE_VIDEO_ONLY)):
                if os.path.getsize(input_file) > self.max_copy_size:
                    if self._running_index + 1 == len(self.true_files):
                        self.process_finished(0, 0)
                        return
                    continue
                must_copy = True

            break
        
        output_file = self.get_converted_file(self._running_index)
        if must_copy:
            output_file = input_file.replace(self.input_common_path,
                                             self.output_common_path, 1)
            
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        command = 'ffmpeg'
        process_args = []
        
        if must_copy:
            command = 'cp'
            process_args += [input_file, output_file]
        else:
            process_args += ['-hide_banner', '-i', input_file]
            process_args += self.process_args
            process_args.append(output_file)
        
        # write the command in the terminal to say how it works
        cli_args = []
        for string in process_args:
            if shlex.quote(string).startswith("'"):
                cli_args.append('"%s"' % string.replace('"', '\"'))
            else:
                cli_args.append(string)
        
        sys.stdout.write(
            "\033[92m$\033[0m %s %s\n" % (command, ' '.join(cli_args)))
        
        self.process.start(command, process_args)
        if self.progress_dialog:
            self.progress_dialog.display_running_file(
                input_file, output_file,
                self._running_index, len(self.true_files)) 

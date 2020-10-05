# ---  INSTALL for ActionMenuAudioConverter  ---

Before installing, please uninstall any existing ActionMenuAudioConverter installation: <br/>
`$ [sudo] make uninstall`

To install ActionMenuAudioConverter, simply run as usual: <br/>
`$ make` <br/>
`$ [sudo] make install`

depending of the distribution you'll need to use LRELEASE variable to install.
If you don't have 'lrelease' executable but 'lrelease-qt5' use:
`$ make LRELEASE=lrelease-qt5` <br/>
`$ [sudo] make install`


Packagers can make use of the 'PREFIX' and 'DESTDIR' variable during install, like this: <br/>
`$ make install PREFIX=/usr DESTDIR=./test-dir`

Note that you could install it locally to $HOME/.local , it will works if $HOME/.local/bin is in your $PATH env variable.<br/>


To uninstall ActionMenuAudioConverter, run: <br/>
`$ [sudo] make uninstall`
<br/>

===== BUILD DEPENDENCIES =====
--------------------------------
The required build dependencies are: <i>(devel packages of these)</i>

 - PyQt5
 - Qt5 dev tools 
 - qtchooser

On Debian and Ubuntu, use these commands to install all build dependencies: <br/>
`$ sudo apt-get install python3-pyqt5 pyqt5-dev-tools qtchooser`

To run it, you'll additionally need:
 - python3-pyqt5
 - python3-pymediainfo
 - ffmpeg

 
To make menus appears in Caja (MATE file manager), you also need:

 - caja-actions

#!/bin/bash

INSTALL_PREFIX="X-PREFIX-X"

main_command="$INSTALL_PREFIX/share/ActionMenuAudioConverter/src/converter.py"
extension="$1"
terminal_title="Audio Conversion to ${extension^^}"

case $LANG in
    fr_*)
        terminal_title="Conversion audio en ${extension^^}"
        ;;
esac

terminals=""

# get the terminal to launch with the desktop environment
case $XDG_CURRENT_DESKTOP in
    GNOME )
        terminals=gnome-terminal
    ;;
    KDE )
        terminals=konsole
    ;;
    MATE )
        terminals=mate-terminal
    ;;
    XFCE )
        terminals="xfce-terminal xfce4-terminal"
    ;;
    LXDE )
        terminals=lxterminal
    ;;
esac

terminals="${terminals} gnome-terminal mate-terminal xfce4-terminal xterm konsole lxterminal rxvt"
terminal=""

for term in $terminals; do
    if which $term > /dev/null;then
        terminal="$term"
        break
    fi
done

if [ -z "$terminal" ];then
    echo "No terminal found, abort." >2
    exit 1
fi

# execute the good terminal with good arguments
case $terminal in
    gnome-terminal )
        exec gnome-terminal --hide-menubar -e "$main_command" "$@"
    ;;
    konsole )
        exec konsole --hide-tabbar --hide-menubar -p tabtitle="$terminal_title" -e "$main_command" "$@"
    ;;
    mate-terminal )
        exec mate-terminal --hide-menubar --title "$terminal_title" -e "$main_command" "$@"
    ;;
    xfce4-terminal )
        exec xfce4-terminal --hide-menubar --hide-toolbar -T "$terminal_title" -e "$main_command" "$@"
    ;;
    * )
        exec $terminal -e "$main_command" "$@"
    ;;
esac

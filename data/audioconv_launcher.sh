#!/bin/bash

PREFIX=XXX_PREFIX_XXX

main_command=audioconvv
terminal_title="Audio Conversion to $1"

case $LANG in
    fr_*)
        terminal_title="Conversion audio en $1"
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
        terminals="lxterminal"
    ;;
esac

terminals="${terminals} xterm rxvt"
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
echo terminal: $terminal

# execute the good terminal with good arguments
case $terminal in
    gnome-terminal )
        exec gnome-terminal --hide-menubar -e "$main_command" "$@"
    ;;
    konsole )
        echo konsole --hide-tabbar --hide-menubar -p tabtitle="$terminal_title" -e "$main_command" "$@"
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

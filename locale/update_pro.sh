#!/bin/bash

# This is a little script for refresh converter.pro and update .ts files.
# TRANSLATOR: You don't need to run it !

contents=""

this_script=`realpath "$0"`
locale_root=`dirname "$this_script"`
code_root=`dirname "$locale_root"`
cd "$code_root/resources/ui/"

for file in *.ui;do
    contents+="FORMS += ../resources/ui/$file
"
done


cd "$code_root/src/"

for file in *.py;do
    [[ "$file" =~ ^ui_ ]] && continue
    
    if cat "$file"|grep -q "_translate\|self.tr(";then
        contents+="SOURCES += ../src/${file}
"
    fi
done

contents+="
TRANSLATIONS += converter_en_US.ts
TRANSLATIONS += converter_fr_FR.ts
"

echo "$contents" > "$locale_root/converter.pro"

pylupdate5 "$locale_root/converter.pro"


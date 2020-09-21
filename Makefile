#!/usr/bin/make -f
# Makefile for Action Menu Audio Converter #
# ---------------------- #
# Created by houston4444
#
PREFIX  = /usr/local
DESTDIR =
DEST_SOURCE := $(DESTDIR)$(PREFIX)/share/ActionMenuAudioConverter

LINK = ln -s
PYUIC := pyuic5
PYRCC := pyrcc5

LRELEASE := lrelease
ifeq (, $(shell which $(LRELEASE)))
 LRELEASE := lrelease-qt5
endif

ifeq (, $(shell which $(LRELEASE)))
 LRELEASE := lrelease-qt4
endif

# -----------------------------------------------------------------------------------------------------------------------------------------

# all: RES UI LOCALE
all: UI LOCALE

# -----------------------------------------------------------------------------------------------------------------------------------------
# Resources

# RES: src/gui/resources_rc.py
# 
# src/gui/resources_rc.py: resources/resources.qrc
# 	$(PYRCC) $< -o $@

# -----------------------------------------------------------------------------------------------------------------------------------------
# UI code

UI: converter

converter: src/ui_first_dialog.py \
	   src/ui_progress.py

src/ui_%.py: resources/ui/%.ui
	$(PYUIC) $< -o $@
	
# -----------------------------------------------------------------------------------------------------------------------------------------
# Translations Files

LOCALE: locale

locale: locale/converter_fr_FR.qm locale/converter_en_US.qm

locale/%.qm: locale/%.ts
	$(LRELEASE) $< -qm $@
# -----------------------------------------------------------------------------------------------------------------------------------------

clean:
	rm -f *~ src/*~ src/*.pyc src/ui_*.py src/resources_rc.py locale/*.qm
	rm -f -R src/__pycache__ src/*/__pycache__ src/*/*/__pycache__
# -----------------------------------------------------------------------------------------------------------------------------------------

debug:
	$(MAKE) DEBUG=true

# -----------------------------------------------------------------------------------------------------------------------------------------

install:
	#clean unwanted __pycache__ folders
	rm -f -R src/__pycache__ src/*/__pycache__ src/*/*/__pycache__
	
	# Create directories
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -d $(DESTDIR)$(PREFIX)/share/
	install -d $(DESTDIR)$(PREFIX)/share/kservices5/
	install -d $(DESTDIR)$(PREFIX)/share/kservices5/ServiceMenus/
	install -d $(DESTDIR)$(PREFIX)/share/file-manager/
	install -d $(DESTDIR)$(PREFIX)/share/file-manager/actions/
	install -d $(DEST_SOURCE)/
	install -d $(DEST_SOURCE)/locale/
	
	# Install KDE ServiceMenus
	cp -r data/share/kservices5/ServiceMenus/ActionMenuAudioConverter \
		$(DESTDIR)$(PREFIX)/share/kservices5/ServiceMenus/
	
	install -m 644 data/share/file-manager/actions/*.desktop \
		$(DESTDIR)$(PREFIX)/share/file-manager/actions/
	
	# Install main code
	cp -r src $(DEST_SOURCE)/
	
	# install main bash script to bin
	install -m 755 data/bin/action_menu_audio_converter.sh $(DESTDIR)$(PREFIX)/bin/         
	
	# modify PREFIX in main bash script
	sed -i "s?X-PREFIX-X?$(PREFIX)?" $(DESTDIR)$(PREFIX)/bin/action_menu_audio_converter.sh
	
	# Install Translations
	install -m 644 locale/*.qm $(DEST_SOURCE)/locale/
	-----------------------------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f  $(DESTDIR)$(PREFIX)/bin/action_menu_audio_converter.sh
	rm -rf $(DEST_SOURCE)
	rm -rf $(DESTDIR)$(PREFIX)/share/kservices5/ServiceMenus/ActionMenuAudioConverter
	rm -f  $(DESTDIR)$(PREFIX)/share/file-manager/actions/ActionMenuAudioConverter_*.desktop


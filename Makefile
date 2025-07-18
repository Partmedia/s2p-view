.PHONY: build desktop package

VERSION = 0.1.3

SRCS = s2p_view/about.py s2p_view/layout.py s2p_view/main.py s2p_view/__init__.py __main__.py

s2p-view: s2p-view.zip
	echo "#!/usr/bin/env python3" | cat - s2p-view.zip > s2p-view
	chmod +x s2p-view

s2p-view.zip: ${SRCS}
	tar -caf $@ ${SRCS}

build: s2p_view/about.py s2p_view/layout.py

s2p_view/about.py: about.imm Makefile
	sed -e 's/@VERSION@/${VERSION}/' about.imm > $@

about.imm: about.ui
	pyuic5 about.ui -o $@

s2p_view/layout.py: layout.imm
	sed -e 's/FigureCanvas(.*)/FigureCanvas(self.fig)/' layout.imm > $@

layout.imm: layout.ui
	pyuic5 layout.ui -o $@

desktop:
	xdg-mime install mime-x-snp.xml
	xdg-desktop-menu install s2p-view.desktop && xdg-desktop-menu forceupdate

package:
	pyinstaller --windowed --onefile -n s2p-view -p . --collect-submodules s2p_view __main__.py --hiddenimport scipy._cyutility

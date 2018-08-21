.PHONY: build

VERSION = 0.1.0

SRCS = about.py layout.py __main__.py

s2p-view: s2p-view.zip
	echo "#!/usr/bin/env python3" | cat - s2p-view.zip > s2p-view
	chmod +x s2p-view

s2p-view.zip: ${SRCS}
	tar -caf $@ ${SRCS}

build: about.py layout.py

about.py: about.imm
	sed -e 's/@VERSION@/${VERSION}/' about.imm > about.py

about.imm: about.ui
	pyuic5 about.ui -o $@

layout.py: layout.imm
	sed -e 's/FigureCanvas(.*)/FigureCanvas(self.fig)/' layout.imm > layout.py

layout.imm: layout.ui
	pyuic5 layout.ui -o $@

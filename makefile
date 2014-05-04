i2pdf:
	echo ":)"

install:
	cp ./i2pdf.py /usr/bin
	cp ./i2pdf.png /usr/share/icons/
	cp ./i2pdf.desktop /usr/share/applications/

deb:
	./make-deb.sh
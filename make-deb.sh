#!/bin/bash
mkdir -p ./debian/usr/bin ./debian/usr/share/icons/ ./debian/usr/share/applications/
cp ./i2pdf.py ./debian/usr/bin
cp ./i2pdf.png ./debian/usr/share/icons/
cp ./i2pdf.desktop ./debian/usr/share/applications/

mkdir -p ./debian/DEBIAN
find ./debian -type d | xargs chmod 755   # this is necessary on Debian Woody, don't ask me why
cp control debian/DEBIAN
dpkg-deb --build debian
mv debian.deb i2pdf.deb
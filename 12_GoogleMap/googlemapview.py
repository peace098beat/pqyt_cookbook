#! coding:utf-8
"""
googlemapview.py

Created by 0160929 on 2017/01/13 15:59
"""
from PyQt5 import QtNetwork

from PyQt5.QtCore import *
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import *

Signal = pyqtSignal
Slot = pyqtSlot


def localizacion(lat, lon):
    latitud = str(lat)
    longitud = str(lon)
    html = \
        """
        <!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Simple markers</title>
            <style>
              html, body {
                height: 100%;
                margin: 0;
                padding: 0;
              }
              #map {
                height: 100%;
              }
            </style>
          </head>
          <body>
            <div id="map"></div>
            <script>

        function initMap() {
          var myLatLng = {lat: """ + latitud + """ , lng: """ + longitud + """};
          var map = new google.maps.Map(document.getElementById('map'), {
            zoom: 15,
            center: myLatLng
          });

          var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            title: 'Mapa Prueba!'
          });
        }

        </script>
        <script async defer
            src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCeTwE_pb_KaSTBD1vmOvQehCCp0izdPUI&signed_in=true&callback=initMap"></script>
      </body>
    </html>
    """
    return html


class GoogleMapView(QWidget):
    def __init__(self):
        super().__init__()
        self.webView = QWebView(self)
        self.webView.setUrl(QUrl("about:blank"))

        self.lat, self.lon = 35.922379, 139.391464

        self.tedit_lon = QDoubleSpinBox(self)
        self.tedit_lat = QDoubleSpinBox(self)
        self.tedit_lon.setValue(self.lon)
        self.tedit_lat.setValue(self.lat)
        self.tedit_lon.setSingleStep(0.00000001)
        self.tedit_lat.setSingleStep(0.00000001)
        self.tedit_lon.setRange(0.00000001, 10000)
        self.tedit_lat.setRange(0.00000001, 10000)
        self.tedit_lon.setDecimals(9)
        self.tedit_lat.setDecimals(9)
        self.tedit_lat.valueChanged.connect(self._update_googlemap)
        self.tedit_lon.valueChanged.connect(self._update_googlemap)

        self.set_location(self.lat, self.lon)

        self.comboBox = QComboBox(self)
        self.comboBox.addItem("160.196.170.48")
        self.comboBox.addItem("160.196.170.26")
        self.comboBox.activated[str].connect(self.set_proxy)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.webView, 0, 0, 2, 3)
        self.layout.addWidget(self.tedit_lat, 2, 0)
        self.layout.addWidget(self.tedit_lon, 2, 1)
        self.layout.addWidget(self.comboBox, 2, 2)

        self.set_proxy(ip='160.196.170.48')

    @Slot(str)
    def set_proxy(self, ip='160.196.170.48'):
        proxy = QtNetwork.QNetworkProxy()
        proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(ip)
        proxy.setPort(8080)
        QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
        self._update_googlemap()

    def _update_googlemap(self):
        lat = self.tedit_lat.value()
        lon = self.tedit_lon.value()
        html = localizacion(lat, lon)
        self.webView.setHtml(html)

    def set_location(self, lat, lon):
        if self.lat == lat:
            return
        if self.lon == lon:
            return

        self.tedit_lon.setValue(lon)
        self.tedit_lat.setValue(lat)

        self.lat, self.lon = lat, lon

        html = localizacion(lat, lon)
        self.webView.setHtml(html)


def main():
    import sys

    app = QApplication(sys.argv)
    window = GoogleMapView()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import requests
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QButtonGroup, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap
from PIL import Image
from io import BytesIO
import sys
from PyQt5.QtCore import Qt


class MapView(QWidget):
    COORDS_X, COORDS_y = 37.588392, 55.734036
    pt_x, pt_y = 0, 0
    MASHTAB = 0.05
    step = 1
    flag = False

    def __init__(self):
        super(MapView, self).__init__()

        self.setFixedSize(700, 700)
        self.l1 = 'map'
        self.map_label = QLabel(self)

        self.map_label.resize(700, 600)
        self.maprequest()
        self.pixmap = QPixmap('map.png').scaled(700, 600)
        self.map_label.setPixmap(self.pixmap)

        self.buttton_group = QButtonGroup(self)
        self.sputnik_button = QPushButton("Спутник", self)
        self.sputnik_button.move(50, 650)
        self.sputnik_button.resize(100, 20)
        self.shema_button = QPushButton("Схема", self)
        self.shema_button.move(300, 650)
        self.shema_button.resize(100, 20)
        self.gibrid_button = QPushButton("Гибрид", self)
        self.gibrid_button.move(500, 650)

        self.buttton_group.addButton(self.sputnik_button)
        self.buttton_group.addButton(self.shema_button)
        self.buttton_group.addButton(self.gibrid_button)
        self.buttton_group.buttonClicked.connect(self.change_l_param)

        self.address_request = QLineEdit("Введите адрес", self)
        self.address_request.move(10, 610)
        self.address_request.resize(100, 20)
        self.search_button = QPushButton("Поиск", self)
        self.search_button.move(115, 610)
        self.search_button.resize(60, 20)
        self.search_button.clicked.connect(self.search_address)

        self.clean_pt = QPushButton("Сброс метки", self)
        self.clean_pt.move(570, 610)
        self.clean_pt.resize(100, 20)
        self.clean_pt.clicked.connect(self.clean)

        self.full_address = QLabel(self)
        self.full_address.move(200, 610)
        self.full_address.resize(400, 20)

    def clean(self):
        self.flag = False
        self.full_address.setText("")
        self.maprequest()

    def search_address(self):
        address = self.address_request.text()
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": address,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            # обработка ошибочной ситуации
            pass
        else:
            # Преобразуем ответ в json-объект
            json_response = response.json()
            # Получаем первый топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            self.flag = True
            self.COORDS_X, self.COORDS_y = map(float, toponym_coodrinates.split())
            self.pt_x, self.pt_y = self.COORDS_X, self.COORDS_y
            self.full_address.setText(toponym_address)
            self.maprequest()

    def change_l_param(self, button):

        if button.text() == "Спутник":
            self.l1 = "sat"
        elif button.text() == "Схема":
            self.l1 = "map"
        elif button.text() == "Гибрид":
            self.l1 = "sat,skl"
        self.maprequest()

    def maprequest(self):
        url = "http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": f"{self.COORDS_X},{self.COORDS_y}",
            "spn": ",".join([str(self.MASHTAB), str(self.MASHTAB)]),
            "l": self.l1

        }
        if self.flag:
            params["pt"] = f"{self.pt_x},{self.pt_y}"

        response = requests.get(url, params=params)
        yandex_map = Image.open(BytesIO(response.content))
        yandex_map.save("map.png")
        self.pixmap = QPixmap('map.png').scaled(700, 600)
        self.map_label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.MASHTAB > 0.0005:
                self.MASHTAB *= 0.1
                self.step /= 10

                self.maprequest()
        if event.key() == Qt.Key_Down:
            if self.MASHTAB < 50.0:
                self.step *= 10
                self.MASHTAB /= 0.1
                self.maprequest()
            else:
                pass
        if event.key() == Qt.Key_W:
            self.COORDS_y += (0.01 * self.step)
            self.maprequest()
        if event.key() == Qt.Key_S:
            self.COORDS_y -= (0.01 * self.step)
            self.maprequest()
        if event.key() == Qt.Key_D:
            self.COORDS_X += (0.01 * self.step)
            self.maprequest()
        if event.key() == Qt.Key_A:
            self.COORDS_X -= (0.01 * self.step)
            self.maprequest()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapView()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

import time

import hid
from PyQt5 import QtWidgets
import sys
import main_window


class App(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.LEDs = []
        self.setupUi(self)
        self.pb_apply.clicked.connect(self.check_options)

        self.opacity = None
        self.red = None
        self.green = None
        self.blue = None
        self.mode = None
        self.buffer = []
        self.cycling_period = 0.5

    def set_opacity(self, value):
        self.label_4.setText(str(value))

    def check_color(self):
        self.red = int(int(self.le_color_red.text()) * self.opacity)
        self.green = int(int(self.le_color_green.text()) * self.opacity)
        self.blue = int(int(self.le_color_blue.text()) * self.opacity)

    def check_opacity(self):
        self.opacity = int(self.slider_opacity.value()) / 100
        self.set_opacity(int(self.opacity * 100))

    def check_mode(self):
        if self.cb_mode_simple.isChecked():
            self.mode = "simple"
        elif self.cb_mode_cycling.isChecked():
            self.mode = "cycling"
        elif self.cb_mode_flashing.isChecked():
            self.mode = "flashing"

    def fill_buffer_0(self, count):
        for i in range(count):
            self.buffer.append(0x00)

    def set_LEDs(self):
        self.LEDs = []
        if self.cb_LEDs_advanced.isChecked():
            self.LEDs.append(self.rb_LED_0.isChecked())
            self.LEDs.append(self.rb_LED_1.isChecked())
            self.LEDs.append(self.rb_LED_2.isChecked())
            self.LEDs.append(self.rb_LED_3.isChecked())
            self.LEDs.append(self.rb_LED_4.isChecked())
            self.LEDs.append(self.rb_LED_5.isChecked())
            self.LEDs.append(self.rb_LED_6.isChecked())
            self.LEDs.append(self.rb_LED_7.isChecked())
            self.LEDs.append(self.rb_LED_8.isChecked())
            self.LEDs.append(self.rb_LED_9.isChecked())
            self.LEDs.append(self.rb_LED_10.isChecked())
            self.LEDs.append(self.rb_LED_11.isChecked())
            self.LEDs.append(self.rb_LED_12.isChecked())
            self.LEDs.append(self.rb_LED_13.isChecked())
            self.LEDs.append(self.rb_LED_14.isChecked())
            self.LEDs.append(self.rb_LED_15.isChecked())
            self.LEDs.append(self.rb_LED_16.isChecked())
            self.LEDs.append(self.rb_LED_17.isChecked())
            self.LEDs.append(self.rb_LED_18.isChecked())
            self.LEDs.append(self.rb_LED_19.isChecked())
            self.LEDs.append(self.rb_LED_20.isChecked())
            self.LEDs.append(self.rb_LED_21.isChecked())
            self.LEDs.append(self.rb_LED_22.isChecked())
            self.LEDs.append(self.rb_LED_23.isChecked())
            self.LEDs.append(self.rb_LED_24.isChecked())
            self.LEDs.append(self.rb_LED_25.isChecked())
            self.LEDs.append(self.rb_LED_26.isChecked())
            self.LEDs.append(self.rb_LED_27.isChecked())
            self.LEDs.append(self.rb_LED_28.isChecked())
            self.LEDs.append(self.rb_LED_29.isChecked())
            self.LEDs.append(self.rb_LED_30.isChecked())
            self.LEDs.append(self.rb_LED_31.isChecked())
            self.LEDs.append(self.rb_LED_32.isChecked())
            return

        if self.cb_LEDs_all.isChecked():
            for i in range(33):
                self.LEDs.append(True)
            return

        if self.cb_LEDs_even.isChecked():
            for i in range(16):
                self.LEDs.append(True)
                self.LEDs.append(False)
            self.LEDs[32] = self.cb_LEDs_logo.isChecked()
            return

        if self.cb_LEDs_even.isChecked():
            for i in range(16):
                self.LEDs.append(False)
                self.LEDs.append(True)
            self.LEDs[32] = self.cb_LEDs_logo.isChecked()
            return

    def check_options(self):
        self.check_mode()
        self.check_opacity()
        self.check_color()
        self.set_LEDs()

        self.configure_packet()

    def fill_buffer_one_color(self, color):
        for i in range(32):
            if self.LEDs[i]:
                self.buffer.append(color)
            else:
                self.buffer.append(0x00)

    def configure_packet(self):
        self.buffer.clear()

        self.fill_buffer_one_color(self.red)
        self.fill_buffer_one_color(self.green)
        self.fill_buffer_one_color(self.blue)

        self.fill_buffer_0(4)

        if self.LEDs[32]:
            self.buffer.append(self.red)
            self.buffer.append(self.green)
            self.buffer.append(self.blue)
        else:
            for i in range(3):
                self.buffer.append(0x00)

        send_cycle(self.device, self.buffer, self.mode, 0.5)

    def configure_led_logo(self):
        self.buffer.append(self.red)
        self.buffer.append(self.green)
        self.buffer.append(self.blue)


MOU_VENDOR_ID = 0x0951
MOU_PRODUCT_ID = 0x16d3


# MOU_VENDOR_ID = 2385
# MOU_PRODUCT_ID = 5843

def fill_packet_info(buffer):
    buff_packet = [0x21, 0x09, 0x07, 0x03, 0x01, 0x00, 0x08, 0x01, 0x07, 0x14, 0x00, 0xa0, 0x00, 0x00, 0x00, 0x00]

    for i in buffer:
        buff_packet.append(i)
    for i in range(272 - len(buff_packet)):
        buff_packet.append(0x00)

    return buff_packet


def shift(arr):
    arr.insert(0, arr.pop())


def is_null(arr):
    return arr.count(0) == len(arr)


def reconfigure_packet(buffer, previous, mode):
    if mode == "simple":
        return buffer
    elif mode == "cycling":
        buff_red = buffer[0:32]
        buff_green = buffer[32:64]
        buff_blue = buffer[64:96]
        buff_logo = buffer[len(buffer) - 3:]

        shift(buff_red)
        shift(buff_green)
        shift(buff_blue)

        new_buffer = []
        for i in buff_red:
            new_buffer.append(i)

        for i in buff_green:
            new_buffer.append(i)

        for i in buff_blue:
            new_buffer.append(i)

        new_buffer.append(0x00)
        new_buffer.append(0x00)
        new_buffer.append(0x00)
        new_buffer.append(0x00)

        for i in buff_logo:
            new_buffer.append(i)

        return new_buffer

    elif mode == "flashing":
        if not is_null(buffer[:len(buffer) - 3]):
            new_buffer = []
            for i in range(len(buffer) - 3):
                new_buffer.append(0x00)

            new_buffer.append(buffer[len(buffer) - 3])
            new_buffer.append(buffer[len(buffer) - 2])
            new_buffer.append(buffer[len(buffer) - 1])
            return new_buffer
        else:
            return previous


def send_cycle(device, buffer, mode, period):
    prev = buffer
    start = time.time()
    while True:
        if time.time() - start > period:
            start = time.time()
            tmp = reconfigure_packet(buffer, prev, mode)
            prev = buffer
            buffer = tmp
            print(fill_packet_info(buffer))
            device.write(fill_packet_info(buffer))


def connect_to_mouse():
    device_mou = hid.device()
    device_mou.open(MOU_VENDOR_ID, MOU_PRODUCT_ID)
    device_mou.set_nonblocking(True)
    print('Connected to {} {}\n'.format(device_mou.get_manufacturer_string(), device_mou.get_product_string()))
    return device_mou


def disconnect(device):
    device.close()


def main():
    application = QtWidgets.QApplication(sys.argv)
    device_mou = connect_to_mouse()
    window = App(device_mou)
    window.show()

    application.exec_()
    disconnect(device_mou)


if __name__ == "__main__":
    main()

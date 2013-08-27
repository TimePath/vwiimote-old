Resources:
http://www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
https://code.google.com/p/androhid/wiki/AndroHid
http://www.btessentials.com/examples/examples.html
http://bluetooth-pentest.narod.ru/software/bluetooth_class_of_device-service_generator.html
https://github.com/chipturner/bluetooth
https://code.google.com/p/remoko/
http://radekp.github.io/qtmoko/api/bluetooth-bluetoothservice.html
http://lxr.free-electrons.com/source/drivers/hid/
http://developer.nokia.com/Community/Wiki/Bluetooth_HID_profile_(client_device)
http://www.instructables.com/id/USB-Wii-Classic-Controller/step13/Bonus-Keyboard-and-Mouse/
http://hidedit.org/hidedit.html
http://gerald.webhop.org/wiki/wii/wii-remote_on_linux

Disable plugins:
# nano /etc/bluetooth/main.conf:
DisablePlugins = network,input,audio,pnat,sap,serial

Restart:
# systemctl restart bluetooth

Must return nothing:
# sdptool browse local

Adapter settings:
# hciconfig hci0 -a

Scan:
# hcitool scan
My phone: 7C:61:93:BD:6C:0A

Dump:
# sdptool records --xml <MAC>

Connect:
# bluez-simple-agent hci0 <MAC>

Disconnect:
# bluez-test-device remove <MAC>
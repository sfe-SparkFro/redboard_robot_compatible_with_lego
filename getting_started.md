# Getting Started

This is not a full guide or tutorial. This is just documenting info and resources that are helpful for users that can tinker and figure things out on their own. No support will be provided at this time.

## 3D Print Files

This project uses some 3D printed pieces to interface the electronics with the LEGO Technic building system. Printable files are available on [Printables](https://www.printables.com/model/1704496-sparkfun-redboard-robot-compatible-with-legor), with the original designs available in [Onshape](https://cad.onshape.com/documents/c39684ab5c062d6b8bf12cd7/w/a39fa9d7be89937e84273478/e/af4bfda3b816f3b4d85f6beb?renderMode=0&uiState=69f14dbcfb334e8d03b3172d)

## Materials

### Required

These are the bare minimum parts needed to build a minimally functioning robot:

* 1x [SparkFun IoT RedBoard RP2350](https://www.sparkfun.com/catalog/product/view/id/17811/s/sparkfun-iot-redboard-rp2350/)
* 1x [SparkFun Ardumoto Motor Driver Shield](https://www.sparkfun.com/sparkfun-ardumoto-motor-driver-shield.html)
    * 1x [Stackable Header Kit](https://www.sparkfun.com/arduino-stackable-header-kit-r3.html)
    * 3x [Screw Terminals (2-Pin, 3.5mm Pitch)](https://www.sparkfun.com/screw-terminals-3-5mm-pitch-2-pin.html)
* 1x [4xAA Battery Holder (Barrel Jack Connector)](https://www.sparkfun.com/battery-holder-4xaa-to-barrel-jack-connector.html)
* 1x [3D Printed Battery and RedBoard Mount](https://www.printables.com/model/1704496-sparkfun-redboard-robot-compatible-with-legor)
    * Double-sided tape to secure RedBoard
* 2x [Ribbon Cable Connector (6-Pin)](https://www.sparkfun.com/ribbon-crimp-connector-6-pin-2x3-female.html)
    * 4x-12x [Jumper Wires (M/M)](https://www.sparkfun.com/jumper-wires-connected-6-m-m-20-pack.html)
* 2x LEGO motors
* LEGO Technic pieces

### Display Add-On

These are extra parts if you want to add a display to the robot:

* 1x [SparkFun Red Vision Touch Display for RedBoard](https://www.sparkfun.com/sparkfun-red-vision-touch-display-for-redboard.html)

### Breadboard Add-On

These are extra parts if you want to add a breadboard to the robot:

* 1x [Breadboard (Half-Size, Adhesive)](https://www.sparkfun.com/breadboard-self-adhesive-white.html)
* 1x [3D Printed Breadboard Plate](https://www.printables.com/model/1704496-sparkfun-redboard-robot-compatible-with-legor)
* [Jumper Wires (M/M)](https://www.sparkfun.com/jumper-wires-connected-6-m-m-20-pack.html)
* Other components as needed

### Optical Odometry Sensor Add-On

These are extra parts if you want to add an optical odometry sensor to the robot:

* 1x [SparkFun Optical Tracking Odometry Sensor](https://www.sparkfun.com/sparkfun-optical-tracking-odometry-sensor-paa5160e1-qwiic.html)
* 1x [Qwiic Cable (100mm)](https://www.sparkfun.com/flexible-qwiic-cable-100mm.html)
* 1x [3D Printed Qwiic 1x1 Mount](https://www.printables.com/model/1704496-sparkfun-redboard-robot-compatible-with-legor)

### LEGO Color Sensor Add-On

These are extra parts if you want to add a LEGO color sensor to the robot:

* 1x [Ribbon Cable Connector (6-Pin)](https://www.sparkfun.com/ribbon-crimp-connector-6-pin-2x3-female.html)
    * 6x [Jumper Wires (M/M)](https://www.sparkfun.com/jumper-wires-connected-6-m-m-20-pack.html)
* 1x LEGO Color Sensor

## Software

This project uses MicroPython; you can download the latest MicroPython for your board from [here](https://micropython.org/download/). If the Red Vision display is used, you'll most likely want to instead use the Red Vision firmware, available from [here](https://github.com/sparkfun/micropython/releases).

Once MicroPython is installed, upload all the files in the [code directory](code) to the root directory of your MicroPython device. You can either use your favorite MicroPython IDE, or use [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html):

```
cd code
mpremote cp -r . :
```

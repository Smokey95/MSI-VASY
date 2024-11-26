# Multi Hop Communication

## Include-Path
To include common classes in other project directory`s and to have full PyCharm support the Python Include Path has to changed as follow:

In the PyCharm project select: 
```
File -> Settings -> Project: -> Python Interpreter -> Show All -> Show Interpreter Path (dir icon) -> +
```
and select the `utility` dir

## Hardware-Settings
To communicate in a network all devices need the same following network settings (value in [] are the AT-Commands):

* Network PAN ID [ID]
* Channel [CH]

The device identification could be done using a unique Node Identifier ([NI]) or the 16-bit Source Address ([MY])
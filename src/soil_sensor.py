from farmware_tools import device
from farmware_tools import app

class SoilSensor:

    def __init__(self, farmwarename):
        self.farmwarename = farmwarename


    def read_sensor(self):
        read = device.read_pin(59, "Soil sensor", 1)
        #device.log(message=str(read), message_type="info")
        values = app.get("sensor_readings")
        
        tabValues = []

        for input in values :
            tabValues.append(input.get("value"))
            #device.log(message=str(input.get("value")), message_type="info")
        
        lastVal = tabValues[len(tabValues)-1]/1023

        return lastVal


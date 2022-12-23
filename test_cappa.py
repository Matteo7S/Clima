import max6675

cs = 24
sck = 23
so = 21
max6675.set_pin(cs, sck, so, 1)

def get_measure_value_MAXX6675(sensor_cod):
        # temp = await W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_cod).get_temperature()
        try:
            # read temperature connected at CS 22
            temp = max6675.read_temp(cs)
            return temp
        except Exception as err:
                print("errore")
                print(err)

if __name__ == "__main__":
    print(get_measure_value_MAXX6675(1))

    
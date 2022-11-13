
import os
import signal
import time
import threading
import traceback
import json
from contextlib import closing
from database import DB

#import database

from tools import MeasureTools, Camino, Pumps
from config import Config
from log import Log

db = DB()
log = Log()
camino = Camino()
pump_tools = Pumps()
# sensori = Sensors()
misurazioni = MeasureTools()

class SensorManager:
    def __init__(self):
        self.sensors = SensorReader()
        self.camino = Camino()
        self.pumps = PumpManager()
        self._running = False
        self.COMMANDS = {
            "start": self.start_sensors,
            "stop": self.stop_sensors,
            "restart": self.restart_sensors}
    # Sensor reader manager
    def start_sensors(self, reason):
        self.sensors.start()
        log.log("Sensors thread start command sent: " + reason)

    def stop_sensors(self, reason):
        self.sensors.stop()
        log.log("Sensors thread stop command sent: " + reason)

    def restart_sensors(self, reason):
        self.sensors.restart()
        log.log("Sensors thread restart command sent: " + reason)

    # Camino manager
    def start_camino(self, reason):
        self.camino.start()
        log.log("Sensors thread start command sent: " + reason)

    def stop_camino(self, reason):
        self.camino.stop()
        log.log("Camino thread stop command sent: " + reason)

    def restart_camino(self, reason):
        self.camino.restart()
        log.log("Camino thread restart command sent: " + reason)
    
     # Pumps manager
    def start_pumps(self, reason):
        self.pumps.start()
        log.log("Pumps thread start command sent: " + reason)

    def stop_pumps(self, reason):
        self.pumps.stop()
        log.log("Pumps thread stop command sent: " + reason)

    def restart_pumps(self, reason):
        self.pumps.restart()
        log.log("Pumps thread restart command sent: " + reason)

    def catch_sigexit(self, sig, frame):
        log.log("Recivecd Exit signal: exiting ")
        self.stop_all("Recived Exit signal")
        self._running = False

    def catch_sigreload(self, sig, frame):
        log.log("Recivecd Reload signal: restarting ")
        self.restart_sensors("Recived Reload signal")

    def bind_sig(self):
        signal.signal(signal.SIGINT, self.catch_sigexit)
        signal.signal(signal.SIGTERM, self.catch_sigexit)
        signal.signal(signal.SIGHUP, self.catch_sigreload)
    
    def start_all(self, reason):
        self.start_sensors(reason)
        self.start_camino(reason)
        self.start_pumps(reason)
    
    def stop_all(self, reason):
        self.stop_sensors(reason)
        self.stop_camino(reason)
        self.stop_pumps(reason)

    def arm_all(self, reason):
        self.sensors.arm(reason)
        self.camino.arm(reason)
        self.pumps.arm(reason)

    def main(self):
        self._running = True
        self.bind_sig()
        if Config["auto_start"]:
            self.start_all("Auto Start")
            if Config["auto_arm"]:
                self.arm_all("Auto Arm")
        while self._running:
            try:
                # print("fai o di qualcosa")
                # log.log_state()
                time.sleep(Config["manager_sleep"])
            except Exception as err:
                log.log("Error in manager Main loop", err)
            except KeyboardInterrupt:
                log.log("Recivecd Ctl-C: exiting ")
                self.stop_sensors("Recivecd Ctl-C")
                self._running = False
        # log.log_state()

class SensorReader:

    DISARMED = 0
    ARMED = 1
    ARMDELAY = 2
    TRIPPED = 3
    PUMPON = 4
    FAULT = 5

    SENSOR_READER_STATES = {
        DISARMED: "Disarmed",
        ARMED: "Armed",
        TRIPPED: "Tripped",
        PUMPON: "Pump-on",
        FAULT: "Fault"}

    NOOP_STATES = [FAULT]

    ACTIONS = {
        "arm": None,
        "disarm": None,
        "trip": None,
        "pumpon": None}

    def __init__(self):
        self.thread = None
        self._running = False
        self._configured = False
        self.ios = None
        self.interfaces = None
        # self.MESSAGES = {
            # "input": self.process_input,
            # "switch": self.process_switch}

        self.ACTIONS["arm"] = self.arm
        self.ACTIONS["disarm"] = self.disarm
        self.ACTIONS["trip"] = self.trip

        self.state = 0
        self.last = time.time()
        self.armtime = 0

        self.buses = {}
        self.ios = {}
        self.interfaces = {}
        self.indicators = {}
        self.actions = {}

    def is_running(self):
        if self.thread is not None:
            return self.thread.is_alive()
        return False

    def arm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == self.DISARMED:
            self.state = self.ARMED
            self.armtime = time.time()
        log.log("ARM " + reason)

    def disarm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        self.state = self.DISARMED
        log.log("DISARM " + reason)

    def trip(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == SensorReader.ARMED:
            self.state = SensorReader.TRIPPED
            self.last = time.time()
            log.log("TRIPPED " + reason)
        elif self.state == SensorReader.DISARMED:
            self.state = SensorReader.FAULT
            log.log("FAULTED " + reason)
            self.last = time.time()

    # def camino(self, reason):
    #     self.state = Camino.PUMPON
    #     log.log("Pump on " + reason, camino=True)

    def update_state(self):
        for key in self.indicators:
            indicator = self.indicators[key]
            self.interfaces[indicator["interface"]].update_state(
                indicator["state"] == self.state)

    def update_tripped(self):
        now = time.time()
        if now - self.last > Config["tripped_timeout"]:
            print("Tripped timeout spent")
            # self.camino("Tripped timeout")

    def update_faulted(self):
        now = time.time()
        if now - self.last > Config["faulted_timeout"]:
            self.state = SensorReader.DISARMED

    def update_armdelay(self):
        now = time.time()
        if now - self.armtime > Config["arm_delay"]:
            self.state = SensorReader.ARMED

    def configure(self):
    #     with closing(database.get_db()) as db:
    #         c = db.cursor()
    #         self._configure_ios(c)
    #         self._configure_interfaces(c)
    #         self._configure_actions(c)
    #         self._configure_indicators(c)
        self.ios = 1
        self.interfaces = 1
        self._configured = True

    def _configure_ios(self, c):
        # self.I2C_BUS = 1
        # self.I2C_ADDR = 0x20
        print("configura il collegamento ai sensori")

    def _configure_interfaces(self, c):
            # c.execute(
            #     "select interface_id, type, io_id, slot, data "
            #     "from interface-camino;")
            # interfaces = c.fetchall()
            # if interfaces:
            #     self.interfaces = {}
            #     for interface in interfaces:
            #         interface_id, t, io_id, slot, data_s = interface
            #         if t not in smbio.INTERFACETYPES:
            #             raise ValueError(
            #                 "invalid interface type for interface %s"
            #                 % (interface_id,))
            #         data = json.loads(data_s)
            #         klass = smbio.INTERFACEMAP[
            #             smbio.INTERFACETYPES[t]]
            #         self.interfaces[interface_id] = klass(
            #             interface_id, self.ios[io_id][slot], data)
            print("configura i sensori di temperatura")

    def log(self, message, error=None, sensor_reader=False):
        timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        if error:
            trace = traceback.format_exc()
            message += "\n" + trace
        message = timestamp + " " + message
        # database.write_log_camino(message, error=(error is not None), camino=camino)

    # def log_state(self, states):
    #     with closing(database.get_db()) as db:
    #         c = db.cursor()
    #         time_now = time.time()
    #         states["camino"] = self.state
    #         for state, data in states.items():
    #             c.execute(
    #                 "INSERT OR IGNORE INTO stateCamino (key) VALUES (:key);",
    #                 {"key":  state})
    #             c.execute(
    #                 "UPDATE state SET "
    #                 "data = :data, "
    #                 "state_time = :time "
    #                 "WHERE key = :key;",
    #                 {
    #                     "key":  state,
    #                     "data": json.dumps(data),
    #                     "time": time_now})
    #         db.commit()

    def stop(self):
        if self._running:
            if self.thread is not None:
                self._running = False
                self.thread.join()
            if self.ios is not None:
                for io in self.ios.values():
                    io.reset()
            del self.thread
            del self.ios
            del self.interfaces
            self.thread = None
            self._configured = False
            self.ios = None
            self.interfaces = None

    def start(self):
        if not self._running:
            if self.thread is None:
                self.thread = threading.Thread(target=self.run)
                self._running = True
                self.configure()
                self.thread.start()

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        try:
            if not self._configured:
                raise RuntimeError("SensorReader system has no configuration")
            if self.ios is None:
                raise RuntimeError("No ios configured")
            if self.interfaces is None:
                raise RuntimeError("No interfaces configured")
            self.main()
            
        except Exception as err:
            log.log("Error running SensorReader main thread", error=err)
        self._running = False

    def update(self):
        # if self.state == SensorReader.ARMDELAY:
        #     self.update_armdelay()
        # elif self.state == SensorReader.TRIPPED:
        #     self.update_tripped()
        # elif self.state == SensorReader.FAULT:
        #     self.update_faulted()
        self.update_state()
        states = {}
        try:
            # campiona le temperature
            # scrivo nel DB le temperature campionate

            temp = misurazioni.measurator()
            # print('sensor funziona')
            
        except Exception as err:
            log.log("Error running Sensor update", error=err)

    def main(self):
        log.log("SensorReader main loop starting")
        while self._running:
            self.update()
            time.sleep(Config["sensor_reader_sampling_time"])
        log.log("SensorReader main loop stoped")

    # diventerà process_temp
    # def process_switch(self, state, interface):
    #     if state:
    #         self.trip("Switch on interface {}: {} tripped".format(
    #             interface.pid, interface.desc))

class Camino:

    DISARMED = 0
    ARMED = 1
    ARMDELAY = 2
    TRIPPED = 3
    PUMPON = 4
    FAULT = 5

    SENSOR_READER_STATES = {
        DISARMED: "Disarmed",
        ARMED: "Armed",
        TRIPPED: "Tripped",
        PUMPON: "Pump-on",
        FAULT: "Fault"}

    NOOP_STATES = [FAULT]

    ACTIONS = {
        "arm": None,
        "disarm": None,
        "trip": None,
        "pumpon": None}

    def __init__(self):
        self.thread = None
        self._running = False
        self._configured = False
        self.ios = None
        self.interfaces = None
        # self.MESSAGES = {
            # "input": self.process_input,
            # "switch": self.process_switch}

        self.ACTIONS["arm"] = self.arm
        self.ACTIONS["disarm"] = self.disarm
        self.ACTIONS["trip"] = self.trip

        self.state = 0
        self.last = time.time()
        self.armtime = 0

        self.buses = {}
        self.ios = {}
        self.interfaces = {}
        self.indicators = {}
        self.actions = {}

    def is_running(self):
        if self.thread is not None:
            return self.thread.is_alive()
        return False

    def arm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == self.DISARMED:
            self.state = self.ARMED
            self.armtime = time.time()
        log.log("ARM " + reason)

    def disarm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        self.state = self.DISARMED
        log.log("DISARM " + reason)

    def trip(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == SensorReader.ARMED:
            self.state = SensorReader.TRIPPED
            self.last = time.time()
            log.log("TRIPPED " + reason)
        elif self.state == SensorReader.DISARMED:
            self.state = SensorReader.FAULT
            log.log("FAULTED " + reason)
            self.last = time.time()

    # def camino(self, reason):
    #     self.state = Camino.PUMPON
    #     log.log("Pump on " + reason, camino=True)

    def update_state(self):
        for key in self.indicators:
            indicator = self.indicators[key]
            self.interfaces[indicator["interface"]].update_state(
                indicator["state"] == self.state)

    def update_tripped(self):
        now = time.time()
        if now - self.last > Config["tripped_timeout"]:
            print("Tripped timeout spent")
            # self.camino("Tripped timeout")

    def update_faulted(self):
        now = time.time()
        if now - self.last > Config["faulted_timeout"]:
            self.state = SensorReader.DISARMED

    def update_armdelay(self):
        now = time.time()
        if now - self.armtime > Config["arm_delay"]:
            self.state = SensorReader.ARMED

    def configure(self):
    #     with closing(database.get_db()) as db:
    #         c = db.cursor()
    #         self._configure_ios(c)
    #         self._configure_interfaces(c)
    #         self._configure_actions(c)
    #         self._configure_indicators(c)
        self.ios = 1
        self.interfaces = 1
        self._configured = True

    def _configure_ios(self, c):
        # self.I2C_BUS = 1
        # self.I2C_ADDR = 0x20
        print("configura il collegamento ai sensori")

    def _configure_interfaces(self, c):
            # c.execute(
            #     "select interface_id, type, io_id, slot, data "
            #     "from interface-camino;")
            # interfaces = c.fetchall()
            # if interfaces:
            #     self.interfaces = {}
            #     for interface in interfaces:
            #         interface_id, t, io_id, slot, data_s = interface
            #         if t not in smbio.INTERFACETYPES:
            #             raise ValueError(
            #                 "invalid interface type for interface %s"
            #                 % (interface_id,))
            #         data = json.loads(data_s)
            #         klass = smbio.INTERFACEMAP[
            #             smbio.INTERFACETYPES[t]]
            #         self.interfaces[interface_id] = klass(
            #             interface_id, self.ios[io_id][slot], data)
            print("configura i sensori di temperatura")

    def stop(self):
        if self._running:
            if self.thread is not None:
                self._running = False
                self.thread.join()
            if self.ios is not None:
                for io in self.ios.values():
                    io.reset()
            del self.thread
            del self.ios
            del self.interfaces
            self.thread = None
            self._configured = False
            self.ios = None
            self.interfaces = None

    def start(self):
        if not self._running:
            if self.thread is None:
                self.thread = threading.Thread(target=self.run)
                self._running = True
                self.configure()
                self.thread.start()

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        try:
            if not self._configured:
                raise RuntimeError("Camino system has no configuration")
            if self.ios is None:
                raise RuntimeError("No Camino ios configured")
            if self.interfaces is None:
                raise RuntimeError("No Camino interfaces configured")
            self.main()
            
        except Exception as err:
            log.log("Error running Camino main thread", error=err)
        self._running = False

    def update(self):
        # if self.state == SensorReader.ARMDELAY:
        #     self.update_armdelay()
        # elif self.state == SensorReader.TRIPPED:
        #     self.update_tripped()
        # elif self.state == SensorReader.FAULT:
        #     self.update_faulted()
        self.update_state()
        states = {}
        
        try:
            camino.check_state()
        
        except Exception as err:
            log.log("Error running Camino update", error=err)

        # log.log_state(states)

    def main(self):
        log.log("Camino main loop starting")
        while self._running:
            self.update()
            # print('camino funziona')
            time.sleep(Config["camino_check_time"])
        log.log("Camino main loop stoped")

    # diventerà process_temp
    # def process_switch(self, state, interface):
    #     if state:
    #         self.trip("Switch on interface {}: {} tripped".format(
    #             interface.pid, interface.desc))


class PumpManager:

    DISARMED = 0
    ARMED = 1
    ARMDELAY = 2
    TRIPPED = 3
    PUMPON = 4
    FAULT = 5

    SENSOR_READER_STATES = {
        DISARMED: "Disarmed",
        ARMED: "Armed",
        TRIPPED: "Tripped",
        PUMPON: "Pump-on",
        FAULT: "Fault"}

    NOOP_STATES = [FAULT]

    ACTIONS = {
        "arm": None,
        "disarm": None,
        "trip": None,
        "pumpon": None}

    def __init__(self):
        self.thread = None
        self._running = False
        self._configured = False
        self.ios = None
        self.interfaces = None
        # self.MESSAGES = {
            # "input": self.process_input,
            # "switch": self.process_switch}

        self.ACTIONS["arm"] = self.arm
        self.ACTIONS["disarm"] = self.disarm
        self.ACTIONS["trip"] = self.trip

        self.state = 0
        self.last = time.time()
        self.armtime = 0

        self.buses = {}
        self.ios = {}
        self.interfaces = {}
        self.indicators = {}
        self.actions = {}

    def is_running(self):
        if self.thread is not None:
            return self.thread.is_alive()
        return False

    def arm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == self.DISARMED:
            self.state = self.ARMED
            self.armtime = time.time()
        log.log("ARM " + reason)

    def disarm(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        self.state = self.DISARMED
        log.log("DISARM " + reason)

    def trip(self, reason):
        if self.state in SensorReader.NOOP_STATES:
            return
        if self.state == SensorReader.ARMED:
            self.state = SensorReader.TRIPPED
            self.last = time.time()
            log.log("TRIPPED " + reason)
        elif self.state == SensorReader.DISARMED:
            self.state = SensorReader.FAULT
            log.log("FAULTED " + reason)
            self.last = time.time()

    # def camino(self, reason):
    #     self.state = Camino.PUMPON
    #     log.log("Pump on " + reason, camino=True)

    def update_state(self):
        for key in self.indicators:
            indicator = self.indicators[key]
            self.interfaces[indicator["interface"]].update_state(
                indicator["state"] == self.state)

    def update_tripped(self):
        now = time.time()
        if now - self.last > Config["tripped_timeout"]:
            print("Tripped timeout spent")
            # self.camino("Tripped timeout")

    def update_faulted(self):
        now = time.time()
        if now - self.last > Config["faulted_timeout"]:
            self.state = SensorReader.DISARMED

    def update_armdelay(self):
        now = time.time()
        if now - self.armtime > Config["arm_delay"]:
            self.state = SensorReader.ARMED

    def configure(self):
    #     with closing(database.get_db()) as db:
    #         c = db.cursor()
    #         self._configure_ios(c)
    #         self._configure_interfaces(c)
    #         self._configure_actions(c)
    #         self._configure_indicators(c)
        self.ios = 1
        self.interfaces = 1
        self._configured = True

    def _configure_ios(self, c):
        # self.I2C_BUS = 1
        # self.I2C_ADDR = 0x20
        print("configura il collegamento alle pompe")

    def _configure_interfaces(self, c):
            # c.execute(
            #     "select interface_id, type, io_id, slot, data "
            #     "from interface-camino;")
            # interfaces = c.fetchall()
            # if interfaces:
            #     self.interfaces = {}
            #     for interface in interfaces:
            #         interface_id, t, io_id, slot, data_s = interface
            #         if t not in smbio.INTERFACETYPES:
            #             raise ValueError(
            #                 "invalid interface type for interface %s"
            #                 % (interface_id,))
            #         data = json.loads(data_s)
            #         klass = smbio.INTERFACEMAP[
            #             smbio.INTERFACETYPES[t]]
            #         self.interfaces[interface_id] = klass(
            #             interface_id, self.ios[io_id][slot], data)
            print("configura le pompe temperatura")

    def stop(self):
        if self._running:
            if self.thread is not None:
                self._running = False
                self.thread.join()
            if self.ios is not None:
                for io in self.ios.values():
                    io.reset()
            del self.thread
            del self.ios
            del self.interfaces
            self.thread = None
            self._configured = False
            self.ios = None
            self.interfaces = None

    def start(self):
        if not self._running:
            if self.thread is None:
                self.thread = threading.Thread(target=self.run)
                self._running = True
                self.configure()
                self.thread.start()

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        try:
            if not self._configured:
                raise RuntimeError("Pumps system has no configuration")
            if self.ios is None:
                raise RuntimeError("No Pumps ios configured")
            if self.interfaces is None:
                raise RuntimeError("No Pumps interfaces configured")
            self.main()
            
        except Exception as err:
            log.log("Error running Pumps main thread", error=err)
        self._running = False

    def update(self):
        # if self.state == SensorReader.ARMDELAY:
        #     self.update_armdelay()
        # elif self.state == SensorReader.TRIPPED:
        #     self.update_tripped()
        # elif self.state == SensorReader.FAULT:
        #     self.update_faulted()
        self.update_state()
        states = {}
        
        try:
            # print("pompee")
            pump_tools.pump_manager()
        
        except Exception as err:
            log.log("erroe in Pumps update")

        # log.log_state(states)

    def main(self):
        log.log("Pumps main loop starting")
        while self._running:
            self.update()
            time.sleep(Config["pumps_check_time"])
        log.log("Pumps main loop stoped")

    # diventerà process_temp
    # def process_switch(self, state, interface):
    #     if state:
    #         self.trip("Switch on interface {}: {} tripped".format(
    #             interface.pid, interface.desc))


def write_pid():
    with open(Config["pidfile"], "w") as f:
        f.write(str(os.getpid()))

def del_pid():
    os.remove(Config["pidfile"])

if __name__ == "__main__":
    # database.init_db()
    a = SensorManager()
    write_pid()
    a.main()
    del_pid()
import carla
from pynput import keyboard

class KeyboardControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.throttle = 0.0
        self.brake = 0.0
        self.steering = 0.0
        self.reverse = False

        # Create a listener that will call on_press and on_release when a key is pressed or released
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            if key.char == 'w':
                self.throttle = 1.0
            elif key.char == 's':
                self.brake = 1.0
            elif key.char == 'a':
                self.steering = -1.0
            elif key.char == 'd':
                self.steering = 1.0
            elif key.char == 'q':
                self.reverse = not self.reverse
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key.char == 'w':
                self.throttle = 0.0
            elif key.char == 's':
                self.brake = 0.0
            elif key.char in ('a', 'd'):
                self.steering = 0.0
        except AttributeError:
            pass

    def apply_controls(self):
        # Apply controls to the vehicle
        control = carla.VehicleControl()
        if self.reverse:
            control.reverse = True
        control.throttle = self.throttle
        control.brake = self.brake
        control.steer = self.steering
        self.vehicle.apply_control(control)

    def tick(self):
        # Apply controls to the vehicle
        self.apply_controls()
    
    def clean(self):
        self.listener.stop()
        self.listener.join()

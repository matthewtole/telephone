import time
from gpiozero import InputDevice, OutputDevice

output_pins = [12, 16, 20, 21]
input_pins = [18, 23, 24, 25]

inputs = list(map(lambda pin: InputDevice(pin, pull_up=True), input_pins))
outputs = list(map(lambda pin: InputDevice(pin, pull_up=True), output_pins))

mapping = [
    ['7', '9', '8', None],
    ['*', '#', '0', None],
    ['4', '6', '5', None],
    ['1', '3', '2', None],
]

print("Start")

pressed = set([])

while True:
    for o in range(4):
        outputs[o].close()
        tmp = OutputDevice(output_pins[o], active_high=False)
        tmp.on()
        for i in range(4):
            key = mapping[i][o]
            if inputs[i].is_active:
                if key == '':
                    continue
                if key not in pressed:
                    print(key)
                    pressed.add(key)
            else:
                if key in pressed:
                    pressed.remove(key)

        tmp.close()
        outputs[o] = InputDevice(output_pins[o], pull_up=True)
    time.sleep(0.02)

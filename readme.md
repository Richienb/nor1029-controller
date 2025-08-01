# nor1029-controller

> Programmatically control the [Norsonic Nor265 microphone boom / turntable](https://www.norsonic.com/products/noise-sources/nor265a-microphone-boom/)

# Install

```sh
pip install nor1029-controller
```

# Usage

```py
from nor1029_controller import Nor265

with Nor265('/dev/serial.0') as nor:
    nor.rotate(180, speed=10, acceleration=2)
```

# API

## Nor265(port)

### port

The serial port to connect to.

## nor

`Nor265` instance.

### .angle

*readonly*

Optional parameters will default to whatever was previously set.

### .rotate(angle, speed?, acceleration?)

### .rotate_relative(angle, speed?, acceleration?)

### .start_sweep(start_angle, stop_angle, period, acceleration?)

Oscillate between two angles.

### .start_continuous_rotation(direction, speed?, acceleration?)

```py
from nor1029_controller import Nor265, RotationDirection
import time

with Nor265() as nor:
    nor.start_continuous_rotation(
        direction=RotationDirection.CLOCKWISE,
        speed=10,
        acceleration=2
    )

    # Rotate for 5 seconds
    time.sleep(5)

    nor.stop()
```

### .start_rotate(angle, speed?, acceleration?)

### .start_rotate_relative(angle, speed?, acceleration?)

The `start_*` methods will return when the movement starts, while the regular methods will also wait for the movement to finish.

### .stop()

Stop any ongoing movement.

### .go_home()

Rotate back to the home position.

### .is_moving

*readonly*

### .close()

If you're not using a context manager, you should instead call this method when you are done.

```py
from nor1029_controller import Nor265

nor = Nor265('/dev/serial.0')

nor.rotate(180, speed=10, acceleration=2)

nor.close()
```

### .wait_stopped(timeout?, poll_interval?)

Wait until it is not moving.

`.rotate()` and `.rotate_relative()` do this automatically.

#### timeout

The maximum time to wait in seconds.

Default: `None` (no timeout)

#### poll_interval

The interval between each check in seconds.

Default: `0.01` (10 milliseconds)

```py
from nor1029_controller import Nor265

with Nor265('/dev/serial.0') as nor:
    nor.start_rotate(180, speed=10, acceleration=2)
    
    # ...
    
    nor.wait_stopped(timeout=10)
```

## list_ports()

Scan for available serial ports (according to their description).

```py
from nor1029_controller import Nor265, list_ports

# Pick first serial port
port = list_ports()[0].device

with Nor265(port) as nor:
    nor.rotate(180, speed=10, acceleration=2)
```

## RotationDirection

*Enum*

- `CLOCKWISE`
- `COUNTER_CLOCKWISE`

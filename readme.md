# nor1029-controller

> Programmatically control Norsonic Nor1029

The [Nor265(A) microphone boom / turntable](https://www.norsonic.com/products/noise-sources/nor265a-microphone-boom/) is controlled by its proprietary Nor1029 software (see downloads section of product page). After installing and configuring it, you can control the hardware programmatically using this library, which launches and interacts with the GUI.

# Install

```sh
pip install nor1029-controller
```

# Usage

```py
from nor1029_controller import Nor1029Controller

with Nor1029Controller() as nor:
    nor.rotate(180, speed=10, acceleration=2)
```

# API

## Nor1029Controller(filename?, timeout?)

### filename

Path to `nor1029.exe`.

Default: `"C:\Program Files (x86)\Norsonic\Nor1029\nor1029.exe"`

### timeout

Timeout for operations in seconds.

Default: `300` (5 minutes)

## nor

`Nor1029Controller` instance.

### .angle

*readonly*

### .rotations

*readonly*

Optional parameters will default to whatever was previously set.

### .rotate(angle, speed?, acceleration?)

### .rotate_relative(angle, speed?, acceleration?)

### .sweep(start_angle, stop_angle, duration, acceleration?)

Oscillate between two angles.

### .start_continuous_rotation(direction, speed?, acceleration?)

```py
from nor1029_controller import Nor1029Controller, RotationDirection
import time

with Nor1029Controller() as nor:
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

### .start_sweep(start_angle, stop_angle, duration, acceleration?)

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
from nor1029_controller import Nor1029Controller

nor = Nor1029Controller()

nor.rotate(180, speed=10, acceleration=2)

nor.close()
```

## RotationDirection

*Enum*

- `CLOCKWISE`
- `COUNTER_CLOCKWISE`

import pytest
from time import sleep
from nor1029_controller import Nor265, RotationDirection


@pytest.fixture(scope="session")
def nor(pytestconfig):
	port = pytestconfig.getoption("port")

	with Nor265(port) as nor:
		yield nor


def assert_stopped_at_angle(nor: Nor265, angle: float | int):
	assert not nor.is_moving
	assert nor.angle == angle


@pytest.fixture(autouse=True)
def between_test(nor: Nor265):
	nor.stop()
	assert not nor.is_moving

	nor.rotate(0)
	assert_stopped_at_angle(nor, 0)


def test_rotate(nor: Nor265):
	nor.rotate(90)
	assert_stopped_at_angle(nor, 90)

	nor.rotate(-90)
	assert_stopped_at_angle(nor, -90)

	nor.rotate(0, speed=10, acceleration=2)
	assert_stopped_at_angle(nor, 0)


def test_start_rotate(nor: Nor265):
	nor.start_rotate(90)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 90)

	nor.start_rotate(-90)
	assert nor.is_moving

	# Hopefully this is enough time
	sleep(10)

	assert_stopped_at_angle(nor, -90)

	nor.start_rotate(0, speed=10, acceleration=2)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 0)


def test_rotate_relative(nor: Nor265):
	nor.rotate_relative(90)
	assert_stopped_at_angle(nor, 90)

	nor.rotate_relative(90)
	assert_stopped_at_angle(nor, 180)

	nor.rotate_relative(-90)
	assert_stopped_at_angle(nor, 90)

	nor.rotate_relative(0, speed=10, acceleration=2)
	assert_stopped_at_angle(nor, 90)


def test_start_rotate_relative(nor: Nor265):
	nor.start_rotate_relative(90)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 90)

	nor.start_rotate_relative(90)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 180)

	nor.start_rotate_relative(-90)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 90)

	nor.start_rotate_relative(-90, speed=10, acceleration=2)
	assert nor.is_moving

	sleep(5)

	assert_stopped_at_angle(nor, 0)


def test_start_continuous_rotation(nor: Nor265):
	nor.start_continuous_rotation(RotationDirection.CLOCKWISE)
	assert nor.is_moving

	sleep(5)

	assert nor.is_moving

	nor.stop()

	nor.start_continuous_rotation(RotationDirection.COUNTER_CLOCKWISE)
	assert nor.is_moving

	sleep(5)

	assert nor.is_moving

	nor.stop()

	nor.start_continuous_rotation(RotationDirection.CLOCKWISE, speed=10, acceleration=2)

	sleep(5)

	assert nor.is_moving


def test_start_sweep(nor: Nor265):
	nor.start_sweep(0, 180, 10)

	sleep(5)

	assert nor.is_moving

	sleep(10)

	assert nor.is_moving

	nor.stop()
	assert not nor.is_moving

	with pytest.raises(RuntimeError):
		nor.start_sweep(0, 180, 5)


def test_wait_stopped(nor: Nor265):
	nor.start_rotate(90)
	assert nor.is_moving

	nor.wait_stopped()

	assert_stopped_at_angle(nor, 90)

	nor.start_rotate_relative(90)
	assert nor.is_moving

	with pytest.raises(TimeoutError):
		nor.wait_stopped(timeout=1)

	nor.wait_stopped(timeout=10)
	assert_stopped_at_angle(nor, 180)

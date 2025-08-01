import pytest
from nor1029_controller import Nor265, list_ports


@pytest.fixture(scope="session")
def nor():
	# Setup
	port = list_ports()[0].device
	nor = Nor265(port)

	yield nor

	# Teardown
	nor.close()


@pytest.fixture(autouse=True)
def between_test(nor: Nor265):
	nor.stop()
	nor.rotate(0)


def test_rotate(nor: Nor265):
	assert nor.angle == 0
	nor.rotate(90)
	assert nor.angle == 90

def test_rotate_negative(nor: Nor265):
	assert nor.angle == 0
	nor.rotate(-90)
	assert nor.angle == -90

def test_start_rotate(nor: Nor265):
	nor.start_rotate(180)
	assert nor.is_moving

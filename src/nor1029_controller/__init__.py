from typing import Optional

from pywinauto.application import Application
from enum import Enum


class RotationDirection(Enum):
	CLOCKWISE = "Clockwise"
	COUNTER_CLOCKWISE = "Counterclockwise"


class Nor1029Sys:
	def __init__(self, filename, timeout):
		self.filename = filename
		self.timeout = timeout

	def open(self):
		self.app = Application(backend="uia").start(self.filename)
		self.window = self.app.window(title="Nor1029")
		self.window.wait("visible", timeout=self.timeout)

		self.clear_button = self.window.child_window(
			title="Clear", control_type="Button"
		)
		self.error_edit = self.window.child_window(control_type="Edit", found_index=0)

		self.angle_edit = self.window.child_window(control_type="Edit", found_index=2)
		self.rotation_edit = self.window.child_window(
			control_type="Edit", found_index=1
		)

		self.stop_button = self.window.child_window(title="Stop", control_type="Button")
		self.go_home_button = self.window.child_window(
			title="Go Home", control_type="Button"
		)

		go_to_group = self.window.child_window(title="Go To", control_type="Group")
		self.go_to_button = go_to_group.child_window(
			title="Go To", control_type="Button"
		)
		self.go_to_angle_edit = go_to_group.child_window(
			control_type="Edit", found_index=0
		)
		self.go_to_speed_edit = go_to_group.child_window(
			control_type="Edit", found_index=2
		)
		self.go_to_acceleration_edit = go_to_group.child_window(
			control_type="Edit", found_index=1
		)

		go_relative_group = self.window.child_window(
			title="Go Relative", control_type="Group"
		)
		self.go_relative_button = go_relative_group.child_window(
			title="Go Relative", control_type="Button"
		)
		self.go_relative_angle_edit = go_relative_group.child_window(
			control_type="Edit", found_index=0
		)
		self.go_relative_speed_edit = go_relative_group.child_window(
			control_type="Edit", found_index=2
		)
		self.go_relative_acceleration_edit = go_relative_group.child_window(
			control_type="Edit", found_index=1
		)

		sweep_group = self.window.child_window(title="Sweep", control_type="Group")
		self.sweep_button = sweep_group.child_window(
			title="Start Sweep", control_type="Button"
		)
		self.sweep_start_angle_edit = sweep_group.child_window(
			control_type="Edit", found_index=1
		)
		self.sweep_stop_angle_edit = sweep_group.child_window(
			control_type="Edit", found_index=0
		)
		self.sweep_time_edit = sweep_group.child_window(
			control_type="Edit", found_index=3
		)
		self.sweep_acceleration_edit = sweep_group.child_window(
			control_type="Edit", found_index=2
		)

		rotation_group = self.window.child_window(
			title="Rotation", control_type="Group"
		)
		self.rotation_button = rotation_group.child_window(
			title="Continuous Rotation", control_type="Button"
		)
		self.rotation_counterclockwise_radio_button = rotation_group.child_window(
			title="Counterclockwise", control_type="RadioButton"
		)
		self.rotation_clockwise_radio_button = rotation_group.child_window(
			title="Clockwise", control_type="RadioButton"
		)
		self.rotation_speed_edit = rotation_group.child_window(
			control_type="Edit", found_index=0
		)
		self.rotation_acceleration_edit = rotation_group.child_window(
			control_type="Edit", found_index=1
		)

	def close(self):
		self.app.kill(soft=True)

	@staticmethod
	def _parse_angle(angle_str: str) -> float:
		# "100°" -> 100
		return float(angle_str[:-1])

	@staticmethod
	def _compose_angle(angle: int | float) -> str:
		# 100 -> "100°"
		return f"{angle}°"

	@staticmethod
	def _parse_speed(speed_str: str) -> int:
		# "100 s/r" -> 100
		return int(speed_str[:-3])

	@staticmethod
	def _compose_speed(speed: int) -> str:
		# 100 -> "100 s/r"
		return f"{speed} s/r"

	@staticmethod
	def _parse_secs(acceleration_str: str) -> int:
		# "100 s" -> 100
		return int(acceleration_str[:-1])

	@staticmethod
	def _compose_secs(acceleration: int) -> str:
		# 100 -> "100 s"
		return f"{acceleration} s"

	@property
	def angle(self) -> float:
		return self._parse_angle(self.angle_edit.get_value())

	@property
	def rotation(self) -> float:
		return int(
			# "100 turns" -> 100
			self.rotation_edit.get_value()[:-6]
		)

	def stop(self):
		self.stop_button.click()

	def go_home(self):
		self.go_home_button.click()

	@property
	def error(self) -> Optional[str]:
		value = self.error_edit.get_value()

		if value == "":
			return None

		return value

	def clear_error(self):
		self.clear_button.click()

	@property
	def go_to_angle(self) -> float:
		return self._parse_angle(self.go_to_angle_edit.get_value())

	@go_to_angle.setter
	def go_to_angle(self, new_angle: int | float):
		new_angle = float(new_angle)

		if new_angle == self.go_to_angle:
			return

		self.go_to_angle_edit.set_edit_text(self._compose_angle(new_angle))

	@property
	def go_to_speed(self) -> int:
		return self._parse_speed(self.go_to_speed_edit.get_value())

	@go_to_speed.setter
	def go_to_speed(self, new_speed: int):
		if self.go_to_speed == new_speed:
			return

		self.go_to_speed_edit.set_edit_text(self._compose_speed(new_speed))

	@property
	def go_to_acceleration(self) -> int:
		return self._parse_secs(self.go_to_acceleration_edit.get_value())

	@go_to_acceleration.setter
	def go_to_acceleration(self, new_acceleration: int):
		if self.go_to_acceleration == new_acceleration:
			return

		self.go_to_acceleration_edit.set_edit_text(self._compose_secs(new_acceleration))

	def go_to(self):
		self.go_to_button.click()

	@property
	def go_relative_angle(self) -> float:
		return self._parse_angle(self.go_relative_angle_edit.get_value())

	@go_relative_angle.setter
	def go_relative_angle(self, new_angle: int | float):
		new_angle = float(new_angle)

		if new_angle == self.go_relative_angle:
			return

		self.go_relative_angle_edit.set_edit_text(self._compose_angle(new_angle))

	@property
	def go_relative_speed(self) -> int:
		return self._parse_speed(self.go_relative_speed_edit.get_value())

	@go_relative_speed.setter
	def go_relative_speed(self, new_speed: int):
		if self.go_relative_speed == new_speed:
			return

		self.go_relative_speed_edit.set_edit_text(self._compose_speed(new_speed))

	@property
	def go_relative_acceleration(self) -> int:
		return self._parse_secs(self.go_relative_acceleration_edit.get_value())

	@go_relative_acceleration.setter
	def go_relative_acceleration(self, new_acceleration: int):
		if self.go_relative_acceleration == new_acceleration:
			return

		self.go_relative_acceleration_edit.set_edit_text(
			self._compose_secs(new_acceleration)
		)

	def go_relative(self):
		self.go_relative_button.click()

	@property
	def sweep_start_angle(self) -> float:
		return self._parse_angle(self.sweep_start_angle_edit.get_value())

	@sweep_start_angle.setter
	def sweep_start_angle(self, new_angle: int | float):
		new_angle = float(new_angle)

		if self.sweep_start_angle == new_angle:
			return

		self.sweep_start_angle_edit.set_edit_text(self._compose_angle(new_angle))

	@property
	def sweep_stop_angle(self) -> float:
		return self._parse_angle(self.sweep_stop_angle_edit.get_value())

	@sweep_stop_angle.setter
	def sweep_stop_angle(self, new_angle: int | float):
		new_angle = float(new_angle)

		if self.sweep_stop_angle == new_angle:
			return

		self.sweep_stop_angle_edit.set_edit_text(self._compose_angle(new_angle))

	@property
	def sweep_time(self) -> int:
		return self._parse_secs(self.sweep_time_edit.get_value())

	@sweep_time.setter
	def sweep_time(self, new_time: int):
		if self.sweep_time == new_time:
			return

		self.sweep_time_edit.set_edit_text(self._compose_secs(new_time))

	@property
	def sweep_acceleration(self) -> int:
		return self._parse_secs(self.sweep_acceleration_edit.get_value())

	@sweep_acceleration.setter
	def sweep_acceleration(self, new_acceleration: int):
		if self.sweep_acceleration == new_acceleration:
			return

		self.sweep_acceleration_edit.set_edit_text(self._compose_secs(new_acceleration))

	def sweep(self):
		self.sweep_button.click()

	@property
	def rotation_direction(self) -> RotationDirection:
		if self.rotation_clockwise_radio_button.is_selected():
			return RotationDirection.CLOCKWISE

		if self.rotation_counterclockwise_radio_button.is_selected():
			return RotationDirection.COUNTER_CLOCKWISE

		# Unreachable!
		raise RuntimeError("No rotation direction selected")

	@rotation_direction.setter
	def rotation_direction(self, direction: RotationDirection):
		if self.rotation_direction == direction:
			return

		if direction == RotationDirection.CLOCKWISE:
			self.rotation_clockwise_radio_button.select()

		elif direction == RotationDirection.COUNTER_CLOCKWISE:
			self.rotation_counterclockwise_radio_button.select()

		else:
			raise ValueError(f"Invalid rotation direction: {direction}")

	@property
	def rotation_speed(self) -> int:
		return self._parse_speed(self.rotation_speed_edit.get_value())

	@rotation_speed.setter
	def rotation_speed(self, new_speed: int):
		if self.rotation_speed == new_speed:
			return

		self.rotation_speed_edit.set_edit_text(self._compose_speed(new_speed))

	@property
	def rotation_acceleration(self) -> int:
		return self._parse_secs(self.rotation_acceleration_edit.get_value())

	@rotation_acceleration.setter
	def rotation_acceleration(self, new_acceleration: int):
		if self.rotation_acceleration == new_acceleration:
			return

		self.rotation_acceleration_edit.set_edit_text(
			self._compose_secs(new_acceleration)
		)

	def rotate(self):
		self.rotation_button.click()


class Nor1029Controller:
	def __init__(
		self,
		filename: str = r"C:\Program Files (x86)\Norsonic\Nor1029\nor1029.exe",
		timeout: int = 300,
	):
		self.sys = Nor1029Sys(filename, timeout)
		self.sys.open()
		self.timeout = timeout

		# TODO: Catch KeyboardInterrupt, and call .stop()

	@property
	def angle(self) -> float:
		return self.sys.angle

	@property
	def rotations(self) -> float:
		return self.sys.rotation

	@property
	def is_moving(self) -> bool:
		return not self.sys.go_to_button.is_enabled()

	def _wait_start(self):
		if self.is_moving:
			return

		self.sys.go_to_button.wait_not("enabled", timeout=self.timeout)

	def _wait_ready(self):
		self._wait_start()

		self.sys.go_to_button.wait("enabled", timeout=self.timeout)

	def start_rotate(
		self, angle: int | float, speed: int = None, acceleration: int = None
	):
		self.sys.go_to_angle = angle

		if speed is not None:
			self.sys.go_to_speed = speed

		if acceleration is not None:
			self.sys.go_to_acceleration = acceleration

		self.sys.go_to()

		self._wait_start()

	def rotate(self, angle: int | float, speed: int = None, acceleration: int = None):
		self.start_rotate(angle, speed, acceleration)

		self._wait_ready()

	def start_rotate_relative(
		self, angle: int | float, speed: int = None, acceleration: int = None
	):
		self.sys.go_relative_angle = angle

		if speed is not None:
			self.sys.go_relative_speed = speed

		if acceleration is not None:
			self.sys.go_relative_acceleration = acceleration

		self.sys.go_relative()

		self._wait_start()

	def rotate_relative(
		self, angle: int | float, speed: int = None, acceleration: int = None
	):
		self.start_rotate_relative(angle, speed, acceleration)

		self._wait_ready()

	def start_sweep(
		self,
		start_angle: int | float,
		stop_angle: int | float,
		duration: int,
		acceleration: int = None,
	):
		self.sys.sweep_start_angle = start_angle
		self.sys.sweep_stop_angle = stop_angle

		self.sys.sweep_time = duration

		if acceleration is not None:
			self.sys.sweep_acceleration = acceleration

		self.sys.sweep()

		self._wait_start()

	def sweep(
		self,
		start_angle: int | float,
		stop_angle: int | float,
		duration: int,
		acceleration: int = None,
	):
		self.start_sweep(start_angle, stop_angle, duration, acceleration)

		self._wait_ready()

	def start_continuous_rotation(
		self, direction: RotationDirection, speed: int = None, acceleration: int = None
	):
		self.sys.rotation_direction = direction

		if speed is not None:
			self.sys.rotation_speed = speed

		if acceleration is not None:
			self.sys.rotation_acceleration = acceleration

		self.sys.rotate()

		self._wait_start()

	def stop(self):
		self.sys.stop()
		self._wait_ready()

	def go_home(self):
		self.sys.go_home()
		self._wait_ready()

	def close(self):
		self.sys.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

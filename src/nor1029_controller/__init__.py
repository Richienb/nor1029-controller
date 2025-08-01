from time import sleep, time
from typing import Optional

import serial
from serial.tools.list_ports import grep as grep_ports
from enum import Enum
import logging


class RotationDirection(Enum):
	CLOCKWISE = "Clockwise"
	COUNTER_CLOCKWISE = "Counterclockwise"


class OperationMode(Enum):
	LOCAL = "Local operation"
	REMOTE = "Remote operation"


operationModeMap = {
	"L": OperationMode.LOCAL,
	"R": OperationMode.REMOTE,
}


class MotorStatus(Enum):
	BUSY = "Busy"
	READY = "Finished/Ready"


motorStatusMap = {
	"B": MotorStatus.BUSY,
	"@": MotorStatus.READY,
}


class HomeStatus(Enum):
	DETECTED = "Home detected"
	UNCALIBRATED = "Uncalibrated angle reference"


homeStatusMap = {
	"H": HomeStatus.DETECTED,
	"U": HomeStatus.UNCALIBRATED,
}


class Errors(Enum):
	ANGLE = "Angle parameter out of range"
	SPEED = "Speed parameter out of range"
	SWEEP_TIME = "Sweep time parameter out of range"
	ACCELERATION = "Acceleration parameter out of range"
	SPEED_LIMIT = "Sweep limit parameter out of range"
	RELATIVE_ANGLE = "Relative angle parameter out of range"
	UNKNOWN = "Unknown command"
	SPACE = "Missing space before parameter"
	SWEEP_TIME_SHORT = "Sweep time too short"
	ILLEGAL_WHILE_LOCAL = "Command is not legal while in local operation"
	HOME_DETECTOR = "Home detector not found"
	ILLEGAL = "llegal command during home process"
	ILLEGAL_POSITION = "Illegal position for PP command"
	BAUD = "Baud rate out of range"
	# NONE = "OK – no error detected"


errorMap = {
	"A": Errors.ANGLE,
	"S": Errors.SPEED,
	"T": Errors.SWEEP_TIME,
	"C": Errors.ACCELERATION,
	"L": Errors.SPEED_LIMIT,
	"R": Errors.RELATIVE_ANGLE,
	"E": Errors.UNKNOWN,
	"P": Errors.SPACE,
	"W": Errors.SWEEP_TIME_SHORT,
	"X": Errors.ILLEGAL_WHILE_LOCAL,
	"N": Errors.HOME_DETECTOR,
	"I": Errors.ILLEGAL,
	"O": Errors.ILLEGAL_POSITION,
	"B": Errors.BAUD,
	# "@": None,  # OK – no error detected
}

logger = logging.getLogger(__package__)


class Nor265Sys:
	def __init__(self, port, baudrate=9600):
		self._port = port
		self._baudrate = baudrate
		self.serial = None

	def open(self):
		if self.serial is None:
			self.serial = serial.Serial(
				port=self._port,
				baudrate=self._baudrate,
				bytesize=serial.EIGHTBITS,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				dsrdtr=True,
				rtscts=True,
			)
		else:
			self.serial.open()

		logging.debug(f"Serial port opened on {self._port}")

	def _send_command(
		self, command: str, parameter: Optional[str | int | float] = None
	):
		if parameter is None:
			message = f"{command};"
		else:
			message = f"{command} {parameter};"

		logging.debug(f"Sending command: {message}")

		self.serial.write(message.encode())

		self.serial.flush()

	def _read_line(self):
		line = self.serial.readline().decode().strip()

		logging.debug(f"Received line: {line}")

		return line

	def _send_request(self, command: str, parameter: Optional[str] = None) -> str:
		self._send_command(command, parameter)

		response = self._read_line()

		return response

	def close(self):
		self.serial.close()

		logging.debug(f"Serial port closed on {self._port}")

	def reset(self):
		self._send_command("IR")

	@property
	def errors(self):
		return self.status["errors"]

	@property
	def status(self):
		response = self._send_request("FS")

		errors = []

		for error_code in response[4:8]:
			error = errorMap.get(error_code, None)

			if error is not None:
				errors.append(error)

		return {
			"operation_type": operationModeMap[response[0]],
			"motor_status": motorStatusMap[response[1]],
			"home_status": homeStatusMap[response[2]],
			"errors": errors,
		}

	@property
	def instrument_identification(self):
		return self._send_request("ID")

	@property
	def software_version(self):
		return self._send_request("SW")

	def go_home(self):
		self._send_command("GH")

	def go_to(self, angle: int | float):
		self._send_command("GT", angle)

	@property
	def speed(self):
		return self.current_parameters["speed"]

	@speed.setter
	def speed(self, value: int):
		self._send_command("TR", value)

	@property
	def acceleration(self):
		return self.current_parameters["acceleration"]

	@acceleration.setter
	def acceleration(self, value: int):
		self._send_command("TA", value)

	@property
	def sweep_time(self):
		return self.current_parameters["sweep_time"]

	@sweep_time.setter
	def sweep_time(self, value: int):
		self._send_command("TT", value)

	def start_sweep(self):
		self._send_command("ST")

	def stop(self):
		self._send_command("SP")

	@property
	def sweep_limit_a(self) -> float:
		return self.current_parameters["sweep_limit_a"]

	@sweep_limit_a.setter
	def sweep_limit_a(self, value: int | float):
		self._send_command("SA", value)

	@property
	def sweep_limit_b(self) -> float:
		return self.current_parameters["sweep_limit_b"]

	@sweep_limit_b.setter
	def sweep_limit_b(self, value: int | float):
		self._send_command("SB", value)

	def go_relative(self, angle: int | float):
		self._send_command("GR", angle)

	def go_continuous_positive_direction(self):
		self._send_command("CP")

	def go_continuous_negative_direction(self):
		self._send_command("CN")

	def set_default_setup(self):
		self._send_command("MR")

	@property
	def angle(self):
		return float(self._send_request("AN"))

	@property
	def switch_positions(self):
		return self._send_request("LP")

	@switch_positions.setter
	def switch_positions(self, x):
		self._send_command("PP", x)

	@property
	def current_parameters(self):
		self._send_command("LR")

		acceleration = float(self._read_line())

		line = self._read_line().split(", ")
		sweep_limit_a = float(line[0][1:])
		sweep_limit_b = float(line[1][1:])

		sweep_time = float(self._read_line())

		speed = float(self._read_line())

		return {
			"acceleration": acceleration,
			"sweep_limit_a": sweep_limit_a,
			"sweep_limit_b": sweep_limit_b,
			"sweep_time": sweep_time,
			"speed": speed,
		}

	@property
	def baudrate(self):
		return self.serial.baudrate

	@baudrate.setter
	def baudrate(self, value: int):
		self._send_command("BR", value)
		self._baudrate = value
		self.serial.baudrate = value


class Nor265:
	def __init__(
		self,
		port: str,
	):
		self.sys = Nor265Sys(port)
		self.sys.open()

		# Flush errors by reading them
		_ = self.sys.errors

	def _throw_if_new_errors(self):
		# Errors are cleared after receiving them
		new_errors = self.sys.errors

		if len(new_errors) == 0:
			return

		if len(new_errors) == 1:
			raise RuntimeError(new_errors[0].value)

		# Newest errors are at the front
		new_errors = reversed(new_errors)

		raise ExceptionGroup(
			"Upstream error", [RuntimeError(error.value) for error in new_errors]
		)

	@property
	def angle(self) -> float:
		return self.sys.angle

	@property
	def is_moving(self) -> bool:
		return self.sys.status["motor_status"] == MotorStatus.BUSY

	def wait_stopped(self, timeout: Optional[int] = None, poll_interval: float = 0.01):
		if timeout is not None:
			start_time = time()

			while self.is_moving:
				elapsed_time = time() - start_time

				if elapsed_time > timeout:
					raise TimeoutError(
						"Rotation did not stop within the timeout period"
					)

				sleep(poll_interval)

			return

		while self.is_moving:
			sleep(poll_interval)

		self._throw_if_new_errors()

	def start_rotate(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed
			self._throw_if_new_errors()

		if acceleration is not None:
			self.sys.acceleration = acceleration
			self._throw_if_new_errors()

		self.sys.go_to(angle)

		self._throw_if_new_errors()

	def rotate(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		self.start_rotate(angle, speed, acceleration)

		self.wait_stopped()

	def start_rotate_relative(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed
			self._throw_if_new_errors()

		if acceleration is not None:
			self.sys.acceleration = acceleration
			self._throw_if_new_errors()

		self.sys.go_relative(angle)

		self._throw_if_new_errors()

	def rotate_relative(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		self.start_rotate_relative(angle, speed, acceleration)

		self.wait_stopped()

	def start_sweep(
		self,
		start_angle: int | float,
		stop_angle: int | float,
		period: int,
		acceleration: Optional[int] = None,
	):
		if acceleration is not None:
			self.sys.acceleration = acceleration
			self._throw_if_new_errors()

		self.sys.sweep_limit_a = start_angle
		self._throw_if_new_errors()

		self.sys.sweep_limit_b = stop_angle
		self._throw_if_new_errors()

		self.sys.sweep_time = period
		self._throw_if_new_errors()

		self.sys.start_sweep()

		self._throw_if_new_errors()

	def start_continuous_rotation(
		self,
		direction: RotationDirection,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed
			self._throw_if_new_errors()

		if acceleration is not None:
			self.sys.acceleration = acceleration
			self._throw_if_new_errors()

		match direction:
			case RotationDirection.CLOCKWISE:
				self.sys.go_continuous_positive_direction()
			case RotationDirection.COUNTER_CLOCKWISE:
				self.sys.go_continuous_negative_direction()
			case _:
				raise ValueError("Invalid rotation direction")

		self._throw_if_new_errors()

	def stop(self):
		self.sys.stop()
		self.wait_stopped()

	def go_home(self):
		self.sys.go_home()
		self.wait_stopped()

	def close(self):
		self.sys.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


def list_ports():
	return list(grep_ports("serial"))

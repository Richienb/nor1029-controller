from time import sleep
from typing import Optional

import serial
from enum import Enum


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


class Nor265Sys:
	def __init__(self, port, timeout, baudrate=9600):
		self.port = port
		self.timeout = timeout
		self.ser = serial.Serial(
			baudrate=baudrate,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=self.timeout,
		)

	def open(self):
		self.ser.open(self.port)

	def _send_command(self, command: str, parameter: Optional[str] = None):
		if parameter is None:
			message = f"${command};"
		else:
			message = f"${command} {parameter};"

		self.ser.write(message.encode())

		self.ser.flush()

	def _read_line(self):
		return self.ser.readline().decode().strip()

	def _send_request(self, command: str, parameter: Optional[str] = None) -> str:
		self._send_command(command, parameter)

		response = self._read_line()

		return response

	def close(self):
		self.ser.close()

	def reset(self):
		self._send_command("IR")

	@property
	def errors(self):
		return self.status["errors"]

	@property
	def status(self):
		response = self._send_request("FS")

		errors = []

		for error_code in response[4:7]:
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
		self._send_command("GT", f"{angle:+.2f}")

	@property
	def speed(self):
		return self.current_parameters["speed"]

	@speed.setter
	def speed(self, value: int):
		self._send_command("TR", f"{value:+.2f}")

	@property
	def acceleration(self):
		return self.current_parameters["acceleration"]

	@acceleration.setter
	def acceleration(self, value: int):
		self._send_command("TA", f"{value:+.2f}")

	@property
	def sweep_time(self):
		return self.current_parameters["sweep_time"]

	@sweep_time.setter
	def sweep_time(self, value: int):
		self._send_command("TT", f"{value:+.2f}")

	def start_sweep(self):
		self._send_command("ST")

	def stop(self):
		self._send_command("SP")

	@property
	def sweep_limit_a(self) -> float:
		return self.current_parameters["sweep_limit_a"]

	@sweep_limit_a.setter
	def sweep_limit_a(self, value: int | float):
		self._send_command("SA", f"{value:+.2f}")

	@property
	def sweep_limit_b(self) -> float:
		return self.current_parameters["sweep_limit_b"]

	@sweep_limit_b.setter
	def sweep_limit_b(self, value: int | float):
		self._send_command("SB", f"{value:+.2f}")

	def go_relative(self, angle: int | float):
		self._send_command("GR", f"{angle:+.2f}")

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
		self._send_command("PP", str(x))

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
		return self.ser.baudrate

	@baudrate.setter
	def baudrate(self, value: int):
		self._send_command("BR", str(value))
		self.ser.baudrate = value


class Nor265:
	def __init__(
		self,
		port: str,
		timeout: int = 300,
	):
		self.timeout = timeout

		self.sys = Nor265Sys(port, self.timeout)
		self.sys.open()

		self._previous_errors = self.sys.errors

		# TODO: Catch KeyboardInterrupt, and call .stop()

	def _throw_if_new_errors(self):
		current_errors = self.sys.errors
		reversed_current_errors = reversed(current_errors)

		new_errors = []

		for previous_error, current_error in zip(reversed(self._previous_errors), reversed_current_errors):
			if previous_error != current_error:
				new_errors.append(current_error)

		# Remaining errors
		new_errors.extend(reversed_current_errors)

		if len(new_errors) == 0:
			return

		raise ExceptionGroup("Upstream error", [
			RuntimeError(error.value) for error in new_errors
		])

	@property
	def angle(self) -> float:
		return self.sys.angle

	@property
	def is_moving(self) -> bool:
		return self.sys.status["motor_status"] == MotorStatus.BUSY

	def _wait_ready(self):
		while self.is_moving:
			sleep(0.01)

		self._throw_if_new_errors()

	def start_rotate(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed

		if acceleration is not None:
			self.sys.acceleration = acceleration

		self.sys.go_to(angle)

		self._throw_if_new_errors()

	def rotate(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		self.start_rotate(angle, speed, acceleration)

		self._wait_ready()

	def start_rotate_relative(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed

		if acceleration is not None:
			self.sys.acceleration = acceleration

		self.sys.go_relative(angle)

		self._throw_if_new_errors()

	def rotate_relative(
		self,
		angle: int | float,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		self.start_rotate_relative(angle, speed, acceleration)

		self._wait_ready()

	def start_sweep(
		self,
		start_angle: int | float,
		stop_angle: int | float,
		duration: int,
		acceleration: Optional[int] = None,
	):
		if acceleration is not None:
			self.sys.acceleration = acceleration

		self.sys.sweep_limit_a = start_angle
		self.sys.sweep_limit_b = stop_angle

		self.sys.sweep_time = duration

		self.sys.start_sweep()

		self._throw_if_new_errors()

	def sweep(
		self,
		start_angle: int | float,
		stop_angle: int | float,
		duration: int,
		acceleration: Optional[int] = None,
	):
		self.start_sweep(start_angle, stop_angle, duration, acceleration)

		self._wait_ready()

	def start_continuous_rotation(
		self,
		direction: RotationDirection,
		speed: Optional[int] = None,
		acceleration: Optional[int] = None,
	):
		if speed is not None:
			self.sys.speed = speed

		if acceleration is not None:
			self.sys.acceleration = acceleration

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

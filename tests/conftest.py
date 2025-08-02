from nor1029_controller import list_ports


def pytest_addoption(parser):
	# Doesn't include ports that don't include "serial" in their name
	ports = [port.device for port in list_ports()]
	parser.addoption("--port", action="store", default=ports[0], choices=ports)

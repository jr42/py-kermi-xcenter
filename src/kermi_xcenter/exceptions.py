"""Custom exceptions for kermi_xcenter."""


class KermiModbusError(Exception):
    """Base exception for all kermi_xcenter errors."""


class ConnectionError(KermiModbusError):
    """Failed to connect to or communicate with the Modbus device."""


class RegisterReadError(KermiModbusError):
    """Failed to read from a Modbus register."""

    def __init__(self, address: int, message: str = "") -> None:
        """Initialize RegisterReadError.

        Args:
            address: Register address that failed to read
            message: Optional error message
        """
        self.address = address
        super().__init__(
            f"Failed to read register {address}: {message}"
            if message
            else f"Failed to read register {address}"
        )


class RegisterWriteError(KermiModbusError):
    """Failed to write to a Modbus register."""

    def __init__(self, address: int, value: int, message: str = "") -> None:
        """Initialize RegisterWriteError.

        Args:
            address: Register address that failed to write
            value: Value that was attempted to write
            message: Optional error message
        """
        self.address = address
        self.value = value
        super().__init__(
            f"Failed to write {value} to register {address}: {message}"
            if message
            else f"Failed to write {value} to register {address}"
        )


class ValidationError(KermiModbusError):
    """Value validation failed (out of range, invalid type, etc.)."""

    def __init__(self, field: str, value: float | int, message: str = "") -> None:
        """Initialize ValidationError.

        Args:
            field: Field name that failed validation
            value: Invalid value
            message: Optional error message
        """
        self.field = field
        self.value = value
        super().__init__(
            f"Validation failed for {field}={value}: {message}"
            if message
            else f"Validation failed for {field}={value}"
        )


class ReadOnlyRegisterError(KermiModbusError):
    """Attempted to write to a read-only register."""

    def __init__(self, register_name: str) -> None:
        """Initialize ReadOnlyRegisterError.

        Args:
            register_name: Name of the read-only register
        """
        self.register_name = register_name
        super().__init__(f"Register '{register_name}' is read-only")


class RegisterUnsupportedError(KermiModbusError):
    """Data point not available on this device or firmware version.

    This typically indicates a feature that exists in the specification
    but is not implemented on this particular device model or firmware.
    Similar to HTTP 501 Not Implemented.
    """

    def __init__(self, register_name: str, message: str = "") -> None:
        """Initialize RegisterUnsupportedError.

        Args:
            register_name: Name of the unsupported data point
            message: Optional error message
        """
        self.register_name = register_name
        super().__init__(
            f"Data point '{register_name}' not available on this device: {message}"
            if message
            else f"Data point '{register_name}' not available on this device"
        )


class DataConversionError(KermiModbusError):
    """Failed to convert data to expected format.

    Raised when data is successfully read from the device but the conversion
    to the expected format fails (e.g., unexpected value format, type mismatch).
    """

    def __init__(self, register_name: str, raw_value: int, message: str = "") -> None:
        """Initialize DataConversionError.

        Args:
            register_name: Name of the data point
            raw_value: Raw value that failed to convert
            message: Optional error message
        """
        self.register_name = register_name
        self.raw_value = raw_value
        super().__init__(
            f"Failed to convert '{register_name}' value {raw_value}: {message}"
            if message
            else f"Failed to convert '{register_name}' value {raw_value}"
        )


# Protocol-agnostic alias for future compatibility
KermiError = KermiModbusError


# HTTP API Exceptions


class HttpError(KermiError):
    """Base exception for HTTP API errors."""


class AuthenticationError(HttpError):
    """Authentication failed (wrong password or missing when required)."""


class SessionExpiredError(HttpError):
    """HTTP session expired.

    The session will be automatically re-established on the next request.
    """


class DatapointNotWritableError(KermiError):
    """Attempted to write to a read-only or restricted datapoint.

    This is raised when trying to write to:
    - Read-only sensor values
    - Dangerous/non-user-facing settings (pressure, calibration, etc.)
    """

    def __init__(self, datapoint_name: str) -> None:
        """Initialize DatapointNotWritableError.

        Args:
            datapoint_name: Name of the datapoint that cannot be written
        """
        self.datapoint_name = datapoint_name
        super().__init__(f"Datapoint '{datapoint_name}' is not writable")

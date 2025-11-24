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

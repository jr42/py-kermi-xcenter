"""Data type conversion utilities for Modbus register values.

All Kermi Modbus values are transmitted as 16-bit integers with specific
scaling factors. These utilities handle bidirectional conversions between
raw register values and engineering units.
"""


def raw_to_temperature(value: int) -> float:
    """Convert raw INT16 register value to temperature in °C.

    Kermi transmits temperatures as signed 16-bit integers in units of 0.1°C.

    Args:
        value: Raw register value (INT16)

    Returns:
        Temperature in degrees Celsius

    Examples:
        >>> raw_to_temperature(235)
        23.5
        >>> raw_to_temperature(-50)
        -5.0
    """
    return value / 10.0


def temperature_to_raw(temp: float) -> int:
    """Convert temperature in °C to raw INT16 register value.

    Args:
        temp: Temperature in degrees Celsius

    Returns:
        Raw register value (INT16)

    Examples:
        >>> temperature_to_raw(23.5)
        235
        >>> temperature_to_raw(-5.0)
        -50
    """
    return int(round(temp * 10))


def raw_to_power(value: int) -> float:
    """Convert raw UINT16 register value to power in kW.

    Kermi transmits power values as unsigned 16-bit integers in units of 0.1 kW.

    Note: The official specification states 0.01 kW units, but actual device
    behavior uses 0.1 kW units, matching the temperature scaling convention.

    Args:
        value: Raw register value (UINT16)

    Returns:
        Power in kilowatts

    Examples:
        >>> raw_to_power(71)
        7.1
        >>> raw_to_power(125)
        12.5
    """
    return value / 10.0


def raw_to_cop(value: int) -> float:
    """Convert raw UINT16 register value to COP (Coefficient of Performance).

    Kermi transmits COP values as unsigned 16-bit integers in units of 0.1.

    Note: The official specification states 0.01 units, but actual device
    behavior uses 0.1 units, matching the temperature scaling convention.

    Args:
        value: Raw register value (UINT16)

    Returns:
        COP value

    Examples:
        >>> raw_to_cop(39)
        3.9
        >>> raw_to_cop(45)
        4.5
    """
    return value / 10.0


def raw_to_flow_rate(value: int) -> float:
    """Convert raw UINT16 register value to flow rate in l/min.

    Kermi transmits flow rates as unsigned 16-bit integers in units of 0.1 l/min.

    Args:
        value: Raw register value (UINT16)

    Returns:
        Flow rate in liters per minute

    Examples:
        >>> raw_to_flow_rate(125)
        12.5
        >>> raw_to_flow_rate(50)
        5.0
    """
    return value / 10.0

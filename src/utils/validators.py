"""Input validation utilities"""

import re
from typing import Union


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError(f"Invalid symbol: {symbol}")
    
    if not re.match(r'^[A-Z0-9]+$', symbol):
        raise ValueError(f"Symbol must contain only uppercase letters and numbers: {symbol}")
    
    if len(symbol) < 4 or len(symbol) > 20:
        raise ValueError(f"Symbol length must be between 4 and 20 characters: {symbol}")
    
    return True


def validate_quantity(quantity: Union[int, float]) -> bool:
    """Validate order quantity
    
    Args:
        quantity: Order quantity
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not isinstance(quantity, (int, float)):
        raise ValueError(f"Quantity must be a number: {quantity}")
    
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive: {quantity}")
    
    if quantity > 1_000_000_000:  # Reasonable upper limit
        raise ValueError(f"Quantity exceeds maximum: {quantity}")
    
    return True


def validate_price(price: Union[int, float]) -> bool:
    """Validate price
    
    Args:
        price: Price value
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not isinstance(price, (int, float)):
        raise ValueError(f"Price must be a number: {price}")
    
    if price <= 0:
        raise ValueError(f"Price must be positive: {price}")
    
    if price > 1_000_000_000:
        raise ValueError(f"Price exceeds maximum: {price}")
    
    return True

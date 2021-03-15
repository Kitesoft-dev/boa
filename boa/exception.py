class BoaException(Exception):
    """Base exception for Boa application"""


class InvalidSourceException(BoaException):
    """Invalid source provided"""


class InvalidDestinationException(BoaException):
    """Invalid destination provided"""

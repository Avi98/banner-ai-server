class InvalidProductInfoError(Exception):
    """Exception raised for errors in the product information."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"InvalidProductInfoError: {self.message}"

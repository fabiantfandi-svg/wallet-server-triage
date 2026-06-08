class BusinessRuleException(Exception):
    """Clase base para todos los errores de lógica del banco."""
    pass

class InvalidAmountException(BusinessRuleException):
    """Monto inválido: letras, negativos, nulos o intentos de inyección."""
    pass

class AccountNotFoundException(BusinessRuleException):
    """La cuenta de origen o destino no existe en el sistema."""
    pass

class AccountStatusException(BusinessRuleException):
    """Alguna de las cuentas involucradas está BLOQUEADA o inactiva."""
    pass

class InsufficientFundsException(BusinessRuleException):
    """La cuenta de origen no tiene la plata suficiente."""
    pass
from abc import ABC, abstractmethod

class AccountRepositoryInterface(ABC):
    """
    CONTRATO (Interfaz): Define qué operaciones se pueden hacer con los datos,
    sin importar si están en un JSON, PostgreSQL o Firebase.
    """
    
    @abstractmethod
    def find_by_id(self, account_id: str) -> dict:
        """Busca una cuenta por su ID. Retorna un diccionario o None."""
        pass

    @abstractmethod
    def update_balances(self, origin_id: str, destiny_id: str, amount: float, transfer_data: dict) -> bool:
        """Guarda de forma segura los nuevos saldos e historiales."""
        pass
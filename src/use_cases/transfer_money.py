import math
from infrastructure.repositories.repo_interface import AccountRepositoryInterface
from domain.exceptions import (
    InvalidAmountException,
    AccountNotFoundException,
    AccountStatusException,
    InsufficientFundsException
)

class TransferMoneyUseCase:
    def __init__(self, repository: AccountRepositoryInterface):
        self.repository = repository

    def execute(self, origin_id: str, destiny_id: str, raw_amount) -> dict:
        """
        Ejecuta el flujo completo de transferencia con blindaje total.
        """
        try:
            amount = float(raw_amount)
        except (ValueError, TypeError):
            raise InvalidAmountException("El monto de la transferencia debe ser un número válido.")

        if math.isnan(amount) or math.isinf(amount) or amount <= 0:
            raise InvalidAmountException("El monto debe ser un número positivo real mayor a cero.")

        origin_account = self.repository.find_by_id(origin_id)
        destiny_account = self.repository.find_by_id(destiny_id)

        if not origin_account or not destiny_account:
            raise AccountNotFoundException("Una o ambas cuentas no existen en el sistema.")

        if origin_account.get("estado") != "ACTIVA":
            raise AccountStatusException(f"La cuenta de origen [{origin_id}] está bloqueada o inactiva.")
            
        if destiny_account.get("estado") != "ACTIVA":
            raise AccountStatusException(f"La cuenta de destino [{destiny_id}] no puede recibir transferencias en su estado actual.")

        if origin_account["saldo"] < amount:
            raise InsufficientFundsException("La cuenta de origen no tiene fondos suficientes para esta transacción.")

        transfer_data = {
            "monto": amount,
            "origin_history": {"tipo": "DEBITO", "monto": amount, "target": destiny_id},
            "destiny_history": {"tipo": "CREDITO", "monto": amount, "target": origin_id}
        }

        success = self.repository.update_balances(origin_id, destiny_id, amount, transfer_data)
        
        if not success:
            raise Exception("Error crítico: No se pudo escribir la transacción en el almacenamiento.")

        return {
            "status": "SUCCESS",
            "message": "Transferencia validada, blindada y procesada con éxito."
        }
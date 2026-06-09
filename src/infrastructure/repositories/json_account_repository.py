import json
import os
import threading
from infrastructure.repositories.repo_interface import AccountRepositoryInterface

class JsonAccountRepository(AccountRepositoryInterface):
    def __init__(self, file_path: str = "accounts.json"):
        self.file_path = file_path
        self._lock = threading.Lock()  

    def _read_file_raw(self) -> dict:
        if not os.path.exists(self.file_path): 
            return {}
        with open(self.file_path, "r") as f: 
            return json.load(f)

    def find_by_id(self, account_id: str) -> dict:
        with self._lock:
            return self._read_file_raw().get(account_id)

    def update_balances(self, origin_id: str, destiny_id: str, amount: float, transfer_data: dict) -> bool:
        with self._lock:   
            try:
                db = self._read_file_raw()
                db[origin_id]["saldo"] -= amount
                db[destiny_id]["saldo"] += amount
                db[origin_id]["historial"].append(transfer_data["origin_history"])
                db[destiny_id]["historial"].append(transfer_data["destiny_history"])
                with open(self.file_path, "w") as f:
                    json.dump(db, f, indent=4)
                return True
            except Exception:
                return False

    def admin_update_status(self, account_id: str, new_status: str) -> bool:
        with self._lock:
            try:
                db = self._read_file_raw()
                if account_id in db:
                    db[account_id]["estado"] = new_status
                    with open(self.file_path, "w") as f: 
                        json.dump(db, f, indent=4)
                    return True
                return False
            except Exception: 
                return False
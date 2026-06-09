import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from domain.exceptions import BusinessRuleException

ADMIN_SECRET_TOKEN = "SENA-ADSO-2026-SECRET"

class CleanPaymentGatewayAPI(BaseHTTPRequestHandler):
    transfer_use_case = None
    account_repository = None

    def _response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _is_authenticated_admin(self) -> bool: 
        return self.headers.get("X-SecureWallet-AdminToken") == ADMIN_SECRET_TOKEN

    def do_POST(self):
        url_parsed = urlparse(self.path)
        path = url_parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8")) if content_length > 0 else {}
        except Exception:
            return self._response({"error": "JSON Malformado"}, 400)
 
        if path == "/api/v1/transactions/transfer":
            try:
                result = self.transfer_use_case.execute(payload.get("desde"), payload.get("hacia"), payload.get("monto"))
                return self._response(result, 200)
            except BusinessRuleException as e:
                error_map = {"InvalidAmountException": 422, "InsufficientFundsException": 400, "AccountStatusException": 403, "AccountNotFoundException": 404}
                return self._response({"error": str(e)}, error_map.get(e.__class__.__name__, 400))
 
        elif path == "/api/v1/accounts/admin/bypass-status":
            if not self._is_authenticated_admin():
                return self._response({"error": "No autorizado. Token inválido."}, 401)

            success = self.account_repository.admin_update_status(payload.get("id"), payload.get("status"))
            if success: return self._response({"status": "CHANGED", "message": "Estado modificado por administrador"})
            return self._response({"error": "Cuenta no encontrada"}, 404)

        self._response({"error": "No encontrado"}, 404)

def start_server(port=8500):
    from use_cases.transfer_money import TransferMoneyUseCase
    from infrastructure.repositories.json_account_repository import JsonAccountRepository
    repo = JsonAccountRepository()
    use_case = TransferMoneyUseCase(repo)
    CleanPaymentGatewayAPI.account_repository = repo
    CleanPaymentGatewayAPI.transfer_use_case = use_case
    httpd = HTTPServer(('', port), CleanPaymentGatewayAPI)
    print(f" Core bancario corriendo en puerto {port}...")
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    httpd.server_close()

if __name__ == "__main__":
    start_server()
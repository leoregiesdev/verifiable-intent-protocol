import hashlib
import json
import time
from typing import Dict, Any, List, Optional

class VerifiableIntentProtocol:
    """
    Implementação de referência do Protocolo de Intenção Verificável (VIP).
    Este protótipo demonstra os conceitos de DIF, PC e RII.
    """

    def __init__(self):
        self.rii: List[Dict[str, Any]] = [] # Registro Imutável de Intenções (Simulado)

    def generate_dif(self, intent_description: str, constraints: List[str]) -> Dict[str, Any]:
        """
        Gera uma Declaração de Intenção Formal (DIF) simplificada.
        """
        dif = {
            "intent": intent_description,
            "constraints": constraints,
            "version": "1.0",
            "timestamp": time.time()
        }
        return dif

    def generate_pc(self, code: str, dif: Dict[str, Any]) -> str:
        """
        Gera uma Prova de Conformidade (PC) simplificada.
        Em uma implementação real, isso envolveria Verificação Formal e ZKP.
        Aqui, usamos um hash criptográfico do código e da DIF como um 'compromisso'.
        """
        payload = {
            "code_hash": hashlib.sha256(code.encode()).hexdigest(),
            "dif_hash": hashlib.sha256(json.dumps(dif, sort_keys=True).encode()).hexdigest()
        }
        pc = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return pc

    def register_intent(self, dif: Dict[str, Any], pc: str) -> int:
        """
        Registra a DIF e a PC no Registro Imutável de Intenções (RII).
        """
        entry = {
            "id": len(self.rii),
            "dif": dif,
            "pc": pc,
            "registered_at": time.time()
        }
        self.rii.append(entry)
        return entry["id"]

    def verify_conformity(self, code: str, dif_id: int) -> bool:
        """
        Verifica se um determinado código está em conformidade com a intenção registrada.
        """
        if dif_id < 0 or dif_id >= len(self.rii):
            return False

        entry = self.rii[dif_id]
        expected_pc = entry["pc"]
        actual_pc = self.generate_pc(code, entry["dif"])

        return actual_pc == expected_pc

# Exemplo de Uso
if __name__ == "__main__":
    vip = VerifiableIntentProtocol()

    # 1. Definir Intenção
    intent = "Um algoritmo de ordenação que não altera os dados originais."
    constraints = ["O array de entrada deve permanecer inalterado", "O array de saída deve estar ordenado de forma crescente"]
    dif = vip.generate_dif(intent, constraints)

    # 2. Desenvolver Código
    code = """
def sort_data(data):
    return sorted(data)
    """

    # 3. Gerar Prova de Conformidade
    pc = vip.generate_pc(code, dif)

    # 4. Registrar Intenção
    reg_id = vip.register_intent(dif, pc)
    print(f"Intenção registrada com ID: {reg_id}")

    # 5. Verificar Conformidade
    is_valid = vip.verify_conformity(code, reg_id)
    print(f"Conformidade do código verificada: {is_valid}")

    # Teste com código malicioso/incorreto
    malicious_code = """
def sort_data(data):
    data.sort() # Altera os dados originais!
    return data
    """
    is_valid_malicious = vip.verify_conformity(malicious_code, reg_id)
    print(f"Conformidade do código malicioso verificada: {is_valid_malicious}")
  

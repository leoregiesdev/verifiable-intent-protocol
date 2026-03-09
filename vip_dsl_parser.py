import re
import json

class VIPDSLParser:
    def __init__(self):
        self.parsed_intent = {}
        self.errors = []

    def parse(self, dsl_content: str) -> dict:
        self.parsed_intent = {}
        self.errors = []
        lines = dsl_content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('INTENT'):
                match = re.match(r'INTENT\s+([a-zA-Z0-9_]+)', line)
                if match:
                    self.parsed_intent['name'] = match.group(1)
                    current_section = 'HEADER'
                else:
                    self.errors.append(f"Erro na linha {i+1}: Sintaxe inválida para INTENT.")
            elif line.startswith('VERSION'):
                match = re.match(r'VERSION\s+([0-9.]+)', line)
                if match:
                    self.parsed_intent['version'] = match.group(1)
                else:
                    self.errors.append(f"Erro na linha {i+1}: Sintaxe inválida para VERSION.")
            elif line.startswith('DESCRIPTION'):
                match = re.match(r'DESCRIPTION\s+"(.*)"', line)
                if match:
                    self.parsed_intent['description'] = match.group(1)
                else:
                    self.errors.append(f"Erro na linha {i+1}: Sintaxe inválida para DESCRIPTION.")
            elif line == 'PERMISSIONS':
                current_section = 'PERMISSIONS'
                self.parsed_intent['permissions'] = []
            elif line == 'CONSTRAINTS':
                current_section = 'CONSTRAINTS'
                self.parsed_intent['constraints'] = []
            elif line == 'ASSERTIONS':
                current_section = 'ASSERTIONS'
                self.parsed_intent['assertions'] = []
            elif line == 'END INTENT':
                current_section = None
            elif current_section == 'PERMISSIONS':
                match = re.match(r'ALLOW\s+([a-zA-Z0-9_]+(?:\([a-zA-Z0-9_\s,\"\.\-]+?\))?);', line)
                if match:
                    self.parsed_intent['permissions'].append(match.group(1))
                else:
                    self.errors.append(f"Erro na linha {i+1} (PERMISSIONS): Sintaxe inválida para permissão.")
            elif current_section == 'CONSTRAINTS':
                match = re.match(r'(DENY|ENSURE)\s+([a-zA-Z0-9_]+(?:\([a-zA-Z0-9_\s,\"\.\-]+?\))?);', line)
                if match:
                    self.parsed_intent['constraints'].append(f"{match.group(1)} {match.group(2)}")
                else:
                    self.errors.append(f"Erro na linha {i+1} (CONSTRAINTS): Sintaxe inválida para restrição.")
            elif current_section == 'ASSERTIONS':
                match = re.match(r'ON\s+([a-zA-Z0-9_]+)\s+ASSERT\s+([a-zA-Z0-9_]+);', line)
                if match:
                    self.parsed_intent['assertions'].append(f"ON {match.group(1)} ASSERT {match.group(2)}")
                else:
                    self.errors.append(f"Erro na linha {i+1} (ASSERTIONS): Sintaxe inválida para asserção.")
            elif current_section is None and line:
                self.errors.append(f"Erro na linha {i+1}: Conteúdo fora de uma seção válida.")

        if not self.errors and 'name' not in self.parsed_intent:
            self.errors.append("Erro: Declaração INTENT não encontrada.")

        return self.parsed_intent

    def validate(self, dsl_content: str) -> bool:
        self.parse(dsl_content)
        if self.errors:
            print("Erros de validação da VIP-DSL:")
            for error in self.errors:
                print(f"- {error}")
            return False
        print("VIP-DSL validada com sucesso!")
        return True

# Exemplo de uso:
if __name__ == "__main__":
    example_dsl = """
INTENT UserAuthenticationService
  VERSION 1.0.0
  DESCRIPTION "Serviço responsável por autenticar usuários e gerenciar sessões de forma segura."

  PERMISSIONS
    ALLOW NETWORK_OUTBOUND_HTTPS_PORT(443);
    ALLOW DATABASE_READ_WRITE("users_table", "sessions_table");
    ALLOW CRYPTO_HASH(SHA256, PBKDF2);
    ALLOW MEMORY_ALLOCATION(256MB);

  CONSTRAINTS
    DENY NETWORK_INBOUND;
    DENY FILESYSTEM_WRITE;
    DENY DATA_EXFILTRATION_TO_EXTERNAL_IP;
    ENSURE NO_HARDCODED_CREDENTIALS;
    ENSURE NO_WEAK_CRYPTO_ALGORITHMS;

  ASSERTIONS
    ON authenticate_user ASSERT user_session_created_securely;
    ON change_password ASSERT old_password_cannot_be_reused;
END INTENT
"""

    parser = VIPDSLParser()
    if parser.validate(example_dsl):
        print("\nConteúdo VIP-DSL parseado:")
        print(json.dumps(parser.parsed_intent, indent=2))

    print("\n--- Testando DSL com erro ---")
    error_dsl = """
INTENT InvalidService
  VERSION 1.0.0
  DESCRIPTION "Serviço com erro."

  PERMISSIONS
    ALLOW INVALID_PERMISSION;

  CONSTRAINTS
    DENY INVALID_CONSTRAINT;

  ASSERTIONS
    ON invalid_event ASSERT invalid_assertion;
END INTENT
"""
    if not parser.validate(error_dsl):
        print("Teste de erro bem-sucedido: Erros detectados.")

    print("\n--- Testando DSL com erro de sintaxe ---")
    syntax_error_dsl = """
INTENT AnotherService
  VERSION 1.0.0
  DESCRIPTION "Serviço com erro de sintaxe."

  PERMISSIONS
    ALLOW NETWORK_OUTBOUND_HTTPS_PORT(443)

  CONSTRAINTS
    DENY FILESYSTEM_WRITE;
END INTENT
"""
    if not parser.validate(syntax_error_dsl):
        print("Teste de erro de sintaxe bem-sucedido: Erros detectados.")

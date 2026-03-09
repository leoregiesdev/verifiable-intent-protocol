import sys
import argparse
import json
import os
from vip_engine import VIPEngine

class VIPCLI:
    """
    Interface de Linha de Comando (CLI) para o Protocolo de Intenção Verificável (VIP).
    """

    def __init__(self):
        self.engine = VIPEngine()
        self.parser = argparse.ArgumentParser(
            description="VIP-CLI: Ferramenta oficial do Protocolo de Intenção Verificável (VIP)",
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.setup_commands()

    def setup_commands(self):
        subparsers = self.parser.add_subparsers(dest="command", help="Comandos disponíveis")

        # Comando: init
        init_parser = subparsers.add_parser("init", help="Inicializa um novo contrato de intenção (VIP-DSL)")
        init_parser.add_argument("name", help="Nome do módulo de software")

        # Comando: verify
        verify_parser = subparsers.add_parser("verify", help="Verifica um código em relação a um contrato de intenção")
        verify_parser.add_argument("--code", required=True, help="Caminho para o arquivo de código-fonte (.py)")
        verify_parser.add_argument("--intent", required=True, help="Caminho para o arquivo de intenção (.vip)")
        verify_parser.add_argument("--output", help="Caminho para salvar o resultado da verificação (JSON)")

    def run(self):
        args = self.parser.parse_args()

        if args.command == "init":
            self.cmd_init(args.name)
        elif args.command == "verify":
            self.cmd_verify(args.code, args.intent, args.output)
        else:
            self.parser.print_help()

    def cmd_init(self, name):
        filename = f"{name.lower().replace(' ', '_')}.vip"
        template = f"""INTENT {name.replace(' ', '')}
  VERSION 1.0.0
  DESCRIPTION "Descreva o propósito deste módulo aqui."

  PERMISSIONS
    ALLOW CPU_COMPUTATION;

  CONSTRAINTS
    DENY NETWORK;
    DENY FILESYSTEM;
    ENSURE NO_VULNERABILITIES;

  ASSERTIONS
    ON execute ASSERT result_is_correct;
END INTENT
"""
        with open(filename, "w") as f:
            f.write(template)
        print(f"✅ Contrato de intenção criado com sucesso: {filename}")
        print("Edite o arquivo para definir suas permissões e restrições.")

    def cmd_verify(self, code_path, intent_path, output_path):
        if not os.path.exists(code_path):
            print(f"❌ Erro: Arquivo de código não encontrado: {code_path}")
            return
        if not os.path.exists(intent_path):
            print(f"❌ Erro: Arquivo de intenção não encontrado: {intent_path}")
            return

        with open(code_path, "r") as f:
            code = f.read()
        with open(intent_path, "r") as f:
            intent_dsl = f.read()

        print(f"🔍 Iniciando verificação VIP para '{code_path}'...")
        result = self.engine.analyze_code(code, intent_dsl)

        if result["status"] == "APPROVED":
            print("\n" + "="*40)
            print("✅ CÓDIGO APROVADO PELO PROTOCOLO VIP")
            print(f"Módulo: {result['intent_name']}")
            print(f"Prova de Conformidade (PC): {result['pc']}")
            print("="*40)
        elif result["status"] == "REJECTED":
            print("\n" + "!"*40)
            print("❌ CÓDIGO REJEITADO - VIOLAÇÃO DETECTADA")
            print(f"Módulo: {result['intent_name']}")
            for violation in result["violations"]:
                print(f" - {violation}")
            print("!"*40)
        else:
            print(f"⚠️ Erro durante a verificação: {result.get('errors')}")

        if output_path:
            with open(output_path, "w") as f:
                json.dump(result, f, indent=4)
            print(f"\n📄 Resultado detalhado salvo em: {output_path}")

def main():
    cli = VIPCLI()
    cli.run()

if __name__ == "__main__":
    main()
  

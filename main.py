"""
TED 03 - Gerenciador de Persistência de Dados em CSV e JSON

Projeto acadêmico desenvolvido em Python.
Funcionalidades:
- Leitura de CSV e JSON;
- Conversão CSV -> JSON e JSON -> CSV;
- Inclusão e atualização de registros;
- Backup automático antes de sobrescrever arquivos existentes;
- Escrita atômica para reduzir o risco de corrupção dos dados;
- Tratamento de erros de arquivo, permissão, codificação e formato.
"""

import csv
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


Registro = Dict[str, Any]


class DataPersistenceManager:
    """Centraliza as operações de persistência em arquivos CSV e JSON."""

    @staticmethod
    def _validar_extensao(caminho: str, extensoes: Sequence[str]) -> Path:
        path = Path(caminho)
        if path.suffix.lower() not in extensoes:
            raise ValueError(
                f"Extensão inválida para '{path.name}'. "
                f"Utilize: {', '.join(extensoes)}."
            )
        return path

    @staticmethod
    def criar_backup(caminho: str) -> Optional[str]:
        """
        Cria backup do arquivo existente.
        Retorna o caminho do backup ou None quando o arquivo ainda não existe.
        Se a cópia falhar, levanta a exceção para impedir a alteração do original.
        """
        origem = Path(caminho)

        if not origem.exists():
            print(f"[BACKUP] '{origem}' ainda não existe; não há versão anterior para copiar.")
            return None

        if not origem.is_file():
            raise IsADirectoryError(f"'{origem}' não é um arquivo.")

        pasta_backup = origem.parent / "backups"
        pasta_backup.mkdir(parents=True, exist_ok=True)

        marca_tempo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        destino = pasta_backup / f"{origem.stem}_{marca_tempo}{origem.suffix}.bak"

        # A abertura explícita dos dois arquivos é feita com gerenciador de contexto.
        with open(origem, "rb") as arquivo_origem:
            with open(destino, "wb") as arquivo_backup:
                shutil.copyfileobj(arquivo_origem, arquivo_backup)

        shutil.copystat(origem, destino)
        print(f"[BACKUP] Cópia criada: {destino}")
        return str(destino)

    @staticmethod
    def _gravar_atomicamente(caminho: str, gravador) -> bool:
        """
        Grava primeiro em um arquivo temporário no mesmo diretório e depois
        substitui o destino. O backup é criado antes desta função ser chamada.
        """
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        arquivo_temporario = None

        try:
            descritor, nome_temporario = tempfile.mkstemp(
                prefix=f".{destino.stem}_",
                suffix=".tmp",
                dir=str(destino.parent)
            )
            os.close(descritor)
            arquivo_temporario = Path(nome_temporario)

            gravador(str(arquivo_temporario))
            os.replace(arquivo_temporario, destino)
            return True

        except Exception:
            if arquivo_temporario and arquivo_temporario.exists():
                try:
                    arquivo_temporario.unlink()
                except OSError:
                    pass
            raise

    @classmethod
    def ler_csv(cls, caminho: str) -> Optional[List[Registro]]:
        """Lê CSV UTF-8 e devolve uma lista de dicionários."""
        try:
            path = cls._validar_extensao(caminho, [".csv"])
            with open(path, "r", encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.DictReader(arquivo)
                if leitor.fieldnames is None:
                    raise ValueError("O CSV está vazio ou não possui cabeçalho.")
                dados = list(leitor)

            print(f"[LEITURA CSV] {len(dados)} registro(s) lido(s) de '{path}'.")
            return dados

        except FileNotFoundError:
            print(f"[ERRO] Arquivo CSV não encontrado: '{caminho}'.")
        except PermissionError:
            print(f"[ERRO] Sem permissão para ler '{caminho}'.")
        except UnicodeDecodeError:
            print(f"[ERRO] Codificação inválida em '{caminho}'. Salve o arquivo em UTF-8.")
        except (csv.Error, ValueError) as erro:
            print(f"[ERRO CSV] Não foi possível interpretar o arquivo: {erro}")
        except OSError as erro:
            print(f"[ERRO DE ARQUIVO] {erro}")
        return None

    @classmethod
    def ler_json(cls, caminho: str) -> Optional[Any]:
        """Lê um arquivo JSON codificado em UTF-8."""
        try:
            path = cls._validar_extensao(caminho, [".json"])
            with open(path, "r", encoding="utf-8-sig") as arquivo:
                dados = json.load(arquivo)

            print(f"[LEITURA JSON] Arquivo '{path}' lido com sucesso.")
            return dados

        except FileNotFoundError:
            print(f"[ERRO] Arquivo JSON não encontrado: '{caminho}'.")
        except PermissionError:
            print(f"[ERRO] Sem permissão para ler '{caminho}'.")
        except UnicodeDecodeError:
            print(f"[ERRO] Codificação inválida em '{caminho}'. Salve o arquivo em UTF-8.")
        except json.JSONDecodeError as erro:
            print(f"[ERRO JSON] Estrutura inválida: linha {erro.lineno}, coluna {erro.colno}.")
        except (ValueError, OSError) as erro:
            print(f"[ERRO DE LEITURA] {erro}")
        return None

    @classmethod
    def escrever_csv(
        cls,
        caminho: str,
        dados: List[Registro],
        nomes_colunas: Optional[List[str]] = None,
        backup: bool = True
    ) -> bool:
        """Escreve uma lista de dicionários em CSV, com backup prévio."""
        try:
            path = cls._validar_extensao(caminho, [".csv"])

            if not isinstance(dados, list):
                raise TypeError("Os dados para CSV devem estar em uma lista.")
            if any(not isinstance(item, dict) for item in dados):
                raise TypeError("Cada registro do CSV deve ser um dicionário.")

            if nomes_colunas is None:
                nomes_colunas = []
                for registro in dados:
                    for chave in registro:
                        if chave not in nomes_colunas:
                            nomes_colunas.append(chave)

            if not nomes_colunas:
                print("[AVISO] Não há colunas para gravar. Informe nomes_colunas para um CSV vazio.")
                return False

            if backup:
                cls.criar_backup(str(path))

            def gravar(arquivo_temporario: str) -> None:
                with open(arquivo_temporario, "w", encoding="utf-8", newline="") as arquivo:
                    escritor = csv.DictWriter(
                        arquivo,
                        fieldnames=nomes_colunas,
                        extrasaction="raise"
                    )
                    escritor.writeheader()
                    escritor.writerows(dados)

            cls._gravar_atomicamente(str(path), gravar)
            print(f"[ESCRITA CSV] {len(dados)} registro(s) gravado(s) em '{path}'.")
            return True

        except PermissionError:
            print(f"[ERRO] Sem permissão para gravar ou criar backup de '{caminho}'.")
        except (TypeError, ValueError, csv.Error) as erro:
            print(f"[ERRO CSV] {erro}")
        except OSError as erro:
            print(f"[ERRO DE ESCRITA] Não foi possível salvar CSV: {erro}")
        return False

    @classmethod
    def escrever_json(cls, caminho: str, dados: Any, backup: bool = True) -> bool:
        """Escreve dados em JSON UTF-8, preservando acentos e com backup prévio."""
        try:
            path = cls._validar_extensao(caminho, [".json"])

            # Valida previamente se o objeto pode ser serializado como JSON.
            json.dumps(dados, ensure_ascii=False)

            if backup:
                cls.criar_backup(str(path))

            def gravar(arquivo_temporario: str) -> None:
                with open(arquivo_temporario, "w", encoding="utf-8") as arquivo:
                    json.dump(dados, arquivo, ensure_ascii=False, indent=4)

            cls._gravar_atomicamente(str(path), gravar)
            print(f"[ESCRITA JSON] Dados gravados em '{path}'.")
            return True

        except PermissionError:
            print(f"[ERRO] Sem permissão para gravar ou criar backup de '{caminho}'.")
        except (TypeError, ValueError) as erro:
            print(f"[ERRO JSON] Os dados não podem ser convertidos para JSON: {erro}")
        except OSError as erro:
            print(f"[ERRO DE ESCRITA] Não foi possível salvar JSON: {erro}")
        return False

    @classmethod
    def csv_para_json(cls, caminho_csv: str, caminho_json: str) -> bool:
        """Converte CSV em JSON, mantendo os nomes dos campos e seus valores."""
        print(f"\n[CONVERSÃO] CSV -> JSON")
        dados = cls.ler_csv(caminho_csv)
        if dados is None:
            print("[CONVERSÃO CANCELADA] Não foi possível ler o CSV de origem.")
            return False
        return cls.escrever_json(caminho_json, dados, backup=True)

    @classmethod
    def json_para_csv(cls, caminho_json: str, caminho_csv: str) -> bool:
        """Converte uma lista de objetos JSON em CSV."""
        print(f"\n[CONVERSÃO] JSON -> CSV")
        dados = cls.ler_json(caminho_json)

        if dados is None:
            print("[CONVERSÃO CANCELADA] Não foi possível ler o JSON de origem.")
            return False

        if not isinstance(dados, list):
            print("[CONVERSÃO CANCELADA] O JSON deve conter uma lista de objetos.")
            return False

        if any(not isinstance(item, dict) for item in dados):
            print("[CONVERSÃO CANCELADA] Todos os elementos da lista devem ser objetos.")
            return False

        if len(dados) == 0:
            print("[CONVERSÃO CANCELADA] A lista JSON está vazia; não há colunas para montar o CSV.")
            return False

        # Une as chaves de todos os registros, evitando perder colunas posteriores.
        colunas: List[str] = []
        for registro in dados:
            for chave in registro:
                if chave not in colunas:
                    colunas.append(chave)

        return cls.escrever_csv(caminho_csv, dados, nomes_colunas=colunas, backup=True)

    @classmethod
    def adicionar_registro(
        cls,
        caminho: str,
        registro: Registro
    ) -> bool:
        """Adiciona um registro a um CSV ou JSON existente."""
        extensao = Path(caminho).suffix.lower()

        if not isinstance(registro, dict):
            print("[ERRO] O novo registro precisa ser um dicionário.")
            return False

        if extensao == ".csv":
            dados = cls.ler_csv(caminho)
            if dados is None:
                return False
            dados.append(registro)
            colunas = list(dict.fromkeys(
                [chave for item in dados for chave in item.keys()]
            ))
            return cls.escrever_csv(caminho, dados, colunas, backup=True)

        if extensao == ".json":
            dados = cls.ler_json(caminho)
            if not isinstance(dados, list) or any(not isinstance(item, dict) for item in dados):
                print("[ERRO] O JSON precisa conter uma lista de objetos para receber registros.")
                return False
            dados.append(registro)
            return cls.escrever_json(caminho, dados, backup=True)

        print("[ERRO] Utilize um arquivo com extensão .csv ou .json.")
        return False

    @classmethod
    def atualizar_registro(
        cls,
        caminho: str,
        campo_identificador: str,
        valor_identificador: Any,
        alteracoes: Registro
    ) -> bool:
        """Atualiza o primeiro registro cujo campo identificador corresponda ao valor informado."""
        extensao = Path(caminho).suffix.lower()

        if not isinstance(alteracoes, dict) or not alteracoes:
            print("[ERRO] Informe um dicionário com pelo menos uma alteração.")
            return False

        if extensao == ".csv":
            dados = cls.ler_csv(caminho)
            gravador = cls.escrever_csv
        elif extensao == ".json":
            dados = cls.ler_json(caminho)
            gravador = cls.escrever_json
        else:
            print("[ERRO] Utilize um arquivo .csv ou .json.")
            return False

        if not isinstance(dados, list) or any(not isinstance(item, dict) for item in dados):
            print("[ERRO] O arquivo precisa conter uma lista de registros.")
            return False

        for registro in dados:
            if str(registro.get(campo_identificador)) == str(valor_identificador):
                registro.update(alteracoes)
                if extensao == ".csv":
                    colunas = list(dict.fromkeys(
                        [chave for item in dados for chave in item.keys()]
                    ))
                    return gravador(caminho, dados, colunas, backup=True)
                return gravador(caminho, dados, backup=True)

        print("[AVISO] Nenhum registro correspondeu ao identificador informado.")
        return False


def menu() -> None:
    """Interface de linha de comando para demonstrar as funcionalidades."""
    arquivo_csv = "dados/alunos.csv"
    arquivo_json = "dados/alunos.json"

    while True:
        print("\n" + "=" * 48)
        print("       GERENCIADOR DE PERSISTÊNCIA - TED 03")
        print("=" * 48)
        print("1 - Ler arquivo CSV")
        print("2 - Ler arquivo JSON")
        print("3 - Converter CSV para JSON")
        print("4 - Converter JSON para CSV")
        print("5 - Adicionar aluno (CSV)")
        print("6 - Atualizar aluno (CSV)")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            dados = DataPersistenceManager.ler_csv(arquivo_csv)
            if dados is not None:
                print(json.dumps(dados, ensure_ascii=False, indent=4))

        elif opcao == "2":
            dados = DataPersistenceManager.ler_json(arquivo_json)
            if dados is not None:
                print(json.dumps(dados, ensure_ascii=False, indent=4))

        elif opcao == "3":
            DataPersistenceManager.csv_para_json(arquivo_csv, arquivo_json)

        elif opcao == "4":
            DataPersistenceManager.json_para_csv(arquivo_json, arquivo_csv)

        elif opcao == "5":
            nome = input("Nome: ").strip()
            idade = input("Idade: ").strip()
            curso = input("Curso: ").strip()

            if not nome or not idade or not curso:
                print("[ERRO] Preencha todos os campos.")
                continue

            DataPersistenceManager.adicionar_registro(
                arquivo_csv,
                {"nome": nome, "idade": idade, "curso": curso}
            )

        elif opcao == "6":
            identificador = input("Nome do aluno que deseja atualizar: ").strip()
            novo_curso = input("Novo curso: ").strip()

            if not identificador or not novo_curso:
                print("[ERRO] Informe o nome e o novo curso.")
                continue

            DataPersistenceManager.atualizar_registro(
                arquivo_csv,
                "nome",
                identificador,
                {"curso": novo_curso}
            )

        elif opcao == "0":
            print("Programa encerrado. Até logo!")
            break

        else:
            print("[ERRO] Opção inválida. Escolha uma opção do menu.")


if __name__ == "__main__":
    menu()

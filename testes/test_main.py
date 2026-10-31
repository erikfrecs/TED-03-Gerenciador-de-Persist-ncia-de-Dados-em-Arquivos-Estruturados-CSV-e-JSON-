"""Testes automatizados do Gerenciador de Persistência CSV e JSON."""

import json
import tempfile
import unittest
from pathlib import Path

from main import DataPersistenceManager


class TestDataPersistenceManager(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.temp.name)
        self.csv_path = self.pasta / "teste.csv"
        self.json_path = self.pasta / "teste.json"

        with open(self.csv_path, "w", encoding="utf-8", newline="") as arquivo:
            arquivo.write(
                "nome,idade,curso\n"
                "Ana,20,ADS\n"
                "Bruno,21,Redes\n"
            )

    def tearDown(self):
        self.temp.cleanup()

    def test_leitura_csv(self):
        dados = DataPersistenceManager.ler_csv(str(self.csv_path))
        self.assertEqual(len(dados), 2)
        self.assertEqual(dados[0]["nome"], "Ana")

    def test_conversao_csv_para_json(self):
        resultado = DataPersistenceManager.csv_para_json(
            str(self.csv_path), str(self.json_path)
        )
        self.assertTrue(resultado)
        with open(self.json_path, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        self.assertEqual(dados[1]["curso"], "Redes")

    def test_conversao_json_para_csv(self):
        registros = [
            {"nome": "Lúcia", "idade": "22", "curso": "ADS"},
            {"nome": "Caio", "idade": "24", "curso": "Redes"}
        ]
        with open(self.json_path, "w", encoding="utf-8") as arquivo:
            json.dump(registros, arquivo, ensure_ascii=False)

        resultado = DataPersistenceManager.json_para_csv(
            str(self.json_path), str(self.csv_path)
        )
        self.assertTrue(resultado)
        dados = DataPersistenceManager.ler_csv(str(self.csv_path))
        self.assertEqual(dados[0]["nome"], "Lúcia")
        self.assertEqual(len(dados), 2)

    def test_backup_antes_de_sobrescrever(self):
        resultado = DataPersistenceManager.escrever_csv(
            str(self.csv_path),
            [{"nome": "Carla", "idade": "23", "curso": "ADS"}]
        )
        self.assertTrue(resultado)
        pasta_backups = self.pasta / "backups"
        backups = list(pasta_backups.glob("*.bak"))
        self.assertEqual(len(backups), 1)
        with open(backups[0], "r", encoding="utf-8") as arquivo:
            conteudo_backup = arquivo.read()
        self.assertIn("Ana", conteudo_backup)

    def test_adicionar_registro(self):
        resultado = DataPersistenceManager.adicionar_registro(
            str(self.csv_path),
            {"nome": "Carla", "idade": "23", "curso": "ADS"}
        )
        self.assertTrue(resultado)
        dados = DataPersistenceManager.ler_csv(str(self.csv_path))
        self.assertEqual(len(dados), 3)
        self.assertEqual(dados[-1]["nome"], "Carla")

    def test_atualizar_registro(self):
        resultado = DataPersistenceManager.atualizar_registro(
            str(self.csv_path), "nome", "Ana", {"curso": "Engenharia de Software"}
        )
        self.assertTrue(resultado)
        dados = DataPersistenceManager.ler_csv(str(self.csv_path))
        self.assertEqual(dados[0]["curso"], "Engenharia de Software")
        self.assertEqual(dados[1]["nome"], "Bruno")

    def test_arquivo_inexistente(self):
        resultado = DataPersistenceManager.ler_csv(
            str(self.pasta / "nao_existe.csv")
        )
        self.assertIsNone(resultado)


if __name__ == "__main__":
    unittest.main()

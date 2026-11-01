# TED 03 — Gerenciador de Persistência de Dados (CSV e JSON)

## Integrantes
- Fernando Lemke da Silveira
- Erik Alves de Sousa

## Disciplina
Algoritmos e Programação Avançada — UNIBALSAS

## Descrição
Aplicação em Python para leitura, escrita, conversão, inclusão e atualização de dados em arquivos CSV e JSON. O projeto utiliza UTF-8, `with open(...)`, tratamento de exceções, backup automático antes de sobrescrever arquivos existentes e gravação por arquivo temporário seguida de substituição.

## Funcionalidades
- Leitura de arquivos CSV e JSON.
- Conversão CSV para JSON e JSON para CSV.
- Inclusão e atualização de registros em CSV e JSON por meio dos métodos da classe gerenciadora.
- Backup automático em uma pasta `backups/` junto ao arquivo alterado.
- Gravação temporária e substituição do arquivo de destino.
- Tratamento de erros de arquivo, permissão, codificação e estrutura dos dados.
- Menu interativo com opções de inclusão e atualização de registros em arquivos CSV.
- Sete testes automatizados.

## Requisitos
- Python 3.9 ou superior.
- Apenas bibliotecas da biblioteca padrão do Python.

## Como executar
Na pasta raiz do projeto:

```bash
python main.py
```

O menu utiliza inicialmente `dados/alunos.csv` e `dados/alunos.json`.

## Como executar os testes
Na pasta raiz do projeto:

```bash
python -m unittest discover -s testes -v
```

O resultado esperado é a aprovação de sete testes (`OK`).

## Estrutura
```text
## Estrutura

```text
TED03_Projeto_Final_Corrigido/
├── main.py
├── dados/
│   ├── alunos.csv
│   ├── alunos.json
│   └── backups/
├── testes/
│   ├── __init__.py
│   └── test_main.py
├── README.md
└── Relatorio_Tecnico_TED03_Final_Limpo.pdf
```

## Segurança dos arquivos
Antes de sobrescrever um arquivo existente, o programa cria uma cópia na pasta `backups/`. Se a criação do backup falhar, a gravação não deve prosseguir. A gravação é realizada em arquivo temporário e, após finalizar, o arquivo temporário substitui o destino. Quando o arquivo ainda não existe, não há versão anterior a preservar.

## Cenários para demonstração
1. Opção 1: leitura do CSV.
2. Opção 2: leitura do JSON.
3. Opção 3: conversão CSV para JSON.
4. Opção 4: conversão JSON para CSV.
5. Opção 5 ou 6: inclusão ou atualização com backup.
6. Leitura de um caminho inexistente para demonstrar o tratamento de `FileNotFoundError`.

As capturas locais de tela podem ser acrescentadas ao relatório, caso o professor exija evidências feitas diretamente no computador dos integrantes.

## Relatório técnico

O relatório técnico completo está disponível no arquivo `Relatorio_Tecnico_TED03_Final_Limpo.pdf`, localizado na raiz deste repositório.

## Declaração de uso de IA

A declaração de uso de Inteligência Artificial está disponível no arquivo `Declaracao_Uso_de_IA.pdf`, localizado na raiz deste repositório.
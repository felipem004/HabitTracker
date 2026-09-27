## Arquivo de Contexto para o Projeto ##

# Contexto #
Estou com diversos hábitos e ideias que gostaria de concretizar, quero ter uma forma digital e prática de controlar todos os hábitos que quero manter praticando e os que não quero manter praticando. 

# Objetivo #
 O objetivo deste projeto é desenvolver um rasatreador de hábitos pessoais via terminal (CLI).

# Tecnologias #
Interface: Terminal (CLI)
Linguagem: Python
Banco de Dados: SQLite (módulo `sqlite3` da biblioteca padrão do Python)
Leitura de comandos (CLI): argparse (biblioteca padrão do Python)
Visual no terminal: Rich

# Requisitos Não Funcionais #
- RNF-01: Deve ser visualmente agradável - com informações bem definidas e de claro entendimento.
- RNF-02: Deve ser leve em consumo de recursos e simples em estrutura.

# Requisitos Funcionais #
- RF-01: Deve ser chamado via terminal com um comando simples: "habit" (tudo minúsculo)
- RF-02: Deve ter a função de cadastrar novos hábitos.
- RF-03: Deve ter a função de excluir hábitos já cadastrados.
- RF-04: Deve ter a função de editar hábitos já cadastrados.
- RF-05: Deve ter um visualizador (dentro do terminal) de todos os hábitos cadastrados de forma indiviadual ou geral.
- RF-06: Deve ter uma tabela de frequência de prática de cada hábito.
- RF-07: Deve permitir registrar a prática (check-in) de um hábito numa data.

# Decisões Tomadas #
- Banco de dados: SQLite — arquivo único, sem servidor, já incluso no Python (atende RNF-02).
- Hábitos ruins (que não quero manter): registrar quando eu "caio" (pratico o hábito ruim); a métrica exibida é "dias sem".
- Nome do comando: "habit", com h minúsculo (convenção de comandos no Linux).
- CLI: argparse (para aprender como uma CLI funciona por dentro) + Rich (tabelas e cores no terminal).
- Periodicidade: variável, definida no cadastro como meta semanal (ex: exercício físico 3x/semana, leitura 7x/semana).
- Tabela de frequência (RF-06): grade de quadradinhos por dia, no estilo do gráfico de contribuições do GitHub.

"""Habit Tracker — rastreador de hábitos pessoais via terminal.

A simples existência deste arquivo transforma a pasta "habit" em um
PACOTE Python: é o que permite escrever "import habit" ou
"from habit.cli import main" em outros lugares.

Tudo que estiver aqui é executado uma única vez, na primeira vez que
o pacote for importado. Por isso mantemos este arquivo bem enxuto.
"""

# importlib.metadata lê as informações do pacote INSTALADO
# (as que vieram do pyproject.toml). Faz parte da biblioteca padrão.
# Referência: https://docs.python.org/3/library/importlib.metadata.html
from importlib.metadata import PackageNotFoundError, version

try:
    # Buscamos a versão pelo NOME DO PACOTE definido no pyproject.toml
    # ("habit-tracker"), e não pelo nome da pasta ("habit").
    # Assim a versão fica escrita em UM lugar só (o pyproject.toml):
    # é o princípio da "fonte única da verdade" — evita que duas cópias
    # do mesmo número fiquem diferentes com o tempo.
    __version__ = version("habit-tracker")
except PackageNotFoundError:
    # Acontece se alguém rodar o código sem ter instalado o pacote
    # (ex: sem o "pip install -e ."). Em vez de quebrar, usamos um
    # valor que deixa claro que algo está fora do normal.
    __version__ = "0.0.0-desconhecida"

"""Permite executar o pacote com: python -m habit

Quando você roda "python -m habit", o Python procura um arquivo
chamado __main__.py dentro do pacote e o executa.
Referência: https://docs.python.org/3/library/__main__.html

É uma alternativa ao comando "habit" — útil, por exemplo, se o
comando não estiver no PATH ou para depurar.
"""

from habit.cli import main

# main() devolve um número (o "código de saída" do programa):
#   0      -> tudo certo
#   != 0   -> algo deu errado
# "raise SystemExit(codigo)" encerra o programa entregando esse código
# ao terminal. Você pode vê-lo rodando "echo $?" logo depois do comando.
raise SystemExit(main())

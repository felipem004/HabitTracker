"""Interface de linha de comando (CLI) do Habit Tracker.

Responsabilidade deste módulo: LER o que o usuário digitou no terminal
e decidir qual ação executar. Ele não acessa o banco nem desenha
tabelas diretamente — isso fica para db.py, habits.py e display.py
(separação de responsabilidades).

Por enquanto é só o esqueleto: mostra uma mensagem de boas-vindas
e responde a "--version" e "--help".
"""

# argparse: módulo da biblioteca padrão para ler argumentos da CLI.
# Referência: https://docs.python.org/3/library/argparse.html
import argparse

# Console é o objeto central do Rich: tudo que for "impresso" com cor,
# tabela, painel etc. passa por ele.
# Referência: https://rich.readthedocs.io/en/stable/console.html
from rich.console import Console
from rich.panel import Panel

from habit import __version__

# Um único Console para o módulo inteiro (criá-lo é um pouco custoso,
# então não faz sentido criar um novo a cada impressão).
console = Console()


def build_parser() -> argparse.ArgumentParser:
    """Monta e devolve o parser: a "gramática" dos comandos aceitos.

    Separar a construção do parser numa função própria facilita
    testar a CLI depois, sem precisar executar o programa inteiro.
    """
    parser = argparse.ArgumentParser(
        prog="habit",  # nome exibido nas mensagens de ajuda e de erro
        description="Rastreador de hábitos pessoais via terminal.",
    )

    # action="version" é um atalho do argparse: imprime o texto e
    # encerra o programa sozinho. "%(prog)s" é substituído por "habit".
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Subcomandos (add, list, check, ...) — como em "git commit" ou
    # "git push". Ainda não criamos nenhum; eles entram nos próximos
    # passos. dest="command" guarda o nome do subcomando escolhido em
    # args.command (fica None se o usuário não digitar nenhum).
    parser.add_subparsers(dest="command", title="comandos")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada do programa.

    É esta a função chamada quando você digita "habit" no terminal
    (veja [project.scripts] no pyproject.toml).

    Args:
        argv: lista de argumentos. Se for None, o argparse lê
              automaticamente os argumentos reais do terminal
              (sys.argv). Poder passar uma lista manualmente é
              o que vai permitir testar a CLI no futuro, ex:
              main(["add", "Leitura", "--meta", "7"]).

    Returns:
        Código de saída: 0 significa sucesso.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        # Nenhum subcomando digitado: mostramos as boas-vindas.
        # Os colchetes são a "marcação" do Rich para estilos:
        # [bold] = negrito, [cyan] = ciano, [/] fecha o estilo aberto.
        # Referência: https://rich.readthedocs.io/en/stable/markup.html
        console.print(
            Panel.fit(
                f"[bold cyan]Habit Tracker[/] [dim]v{__version__}[/]\n"
                "Use [bold]habit --help[/] para ver os comandos disponíveis.",
                border_style="cyan",
            )
        )

    return 0

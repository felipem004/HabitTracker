"""Camada de acesso ao banco de dados (SQLite).

Responsabilidade deste módulo: saber ONDE o banco fica, COMO abrir
uma conexão com ele e QUAIS tabelas existem. Nenhuma regra de negócio
(metas, "dias sem" etc.) mora aqui — isso fica em habits.py.

Referências:
  - Módulo sqlite3: https://docs.python.org/3/library/sqlite3.html
  - Sintaxe SQL do SQLite: https://www.sqlite.org/lang.html
"""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# ------------------------------------------------------------
# Esquema do banco (as tabelas)
# ------------------------------------------------------------
# "CREATE TABLE IF NOT EXISTS" só cria a tabela se ela ainda não
# existir. Assim podemos rodar este script toda vez que o programa
# abre, sem apagar dados nem dar erro de "tabela já existe".
SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    -- INTEGER PRIMARY KEY: o SQLite gera o id automaticamente
    -- (1, 2, 3, ...) quando não informamos um valor.
    id          INTEGER PRIMARY KEY,

    -- NOT NULL: campo obrigatório.
    -- UNIQUE: não permite dois hábitos com o mesmo nome.
    -- COLLATE NOCASE: ao comparar, ignora maiúsculas/minúsculas,
    --   então "Leitura" e "leitura" contam como o MESMO nome.
    --   (Limitação: só vale para letras sem acento — A-Z.)
    name        TEXT    NOT NULL UNIQUE COLLATE NOCASE,

    -- 'good' = hábito que quero manter; 'bad' = hábito que quero largar.
    -- CHECK: o próprio banco recusa qualquer valor fora da lista.
    kind        TEXT    NOT NULL CHECK (kind IN ('good', 'bad')),

    -- Meta semanal (quantos dias por semana). Só faz sentido para
    -- hábitos bons; em hábitos ruins fica NULL (vazio).
    weekly_goal INTEGER,

    -- Data de cadastro no formato ISO 'AAAA-MM-DD'.
    -- O SQLite não tem tipo DATE: datas são guardadas como TEXT.
    -- DEFAULT: se não informarmos, o banco preenche com a data de hoje
    -- (no fuso horário local, graças ao modificador 'localtime').
    created_at  TEXT    NOT NULL DEFAULT (date('now', 'localtime')),

    -- Regra que envolve DUAS colunas ao mesmo tempo:
    --   hábito bom  -> meta obrigatória, entre 1 e 7
    --   hábito ruim -> sem meta
    --
    -- ATENÇÃO (lógica de três valores do SQL): comparar com NULL
    -- resulta em NULL ("desconhecido"), e um CHECK só REJEITA quando
    -- o resultado é FALSO — NULL passa! Por isso o "IS NOT NULL"
    -- explícito: sem ele, um hábito bom sem meta seria aceito.
    -- Referência: https://www.sqlite.org/lang_createtable.html#ckconst
    CHECK (
        (kind = 'good' AND weekly_goal IS NOT NULL AND weekly_goal BETWEEN 1 AND 7)
        OR
        (kind = 'bad'  AND weekly_goal IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS checkins (
    id        INTEGER PRIMARY KEY,

    -- Chave estrangeira (FOREIGN KEY): liga o check-in ao hábito.
    -- ON DELETE CASCADE: ao excluir um hábito, os check-ins dele
    -- são excluídos junto (sem sobrar registros "órfãos").
    -- ATENÇÃO: só funciona com "PRAGMA foreign_keys = ON" (veja abaixo).
    habit_id  INTEGER NOT NULL REFERENCES habits (id) ON DELETE CASCADE,

    -- Dia da prática (ou da "queda", em hábitos ruins): 'AAAA-MM-DD'.
    date      TEXT    NOT NULL,

    -- No máximo UM check-in por hábito por dia.
    -- Bônus: o UNIQUE cria automaticamente um índice em
    -- (habit_id, date), deixando rápidas as buscas por hábito/data.
    UNIQUE (habit_id, date)
);
"""


# ------------------------------------------------------------
# Localização do arquivo do banco
# ------------------------------------------------------------
def get_db_path() -> Path:
    """Devolve o caminho do arquivo do banco, seguindo o padrão XDG.

    O padrão XDG (freedesktop.org) define onde programas no Linux
    devem guardar seus arquivos. Dados do usuário ficam em
    $XDG_DATA_HOME, que, quando não está definido, vale
    ~/.local/share.
    Referência: https://specifications.freedesktop.org/basedir-spec/latest/

    Resultado típico: /home/<usuario>/.local/share/habit/habits.db

    Guardar o banco FORA da pasta do projeto é uma decisão de
    segurança: como o repositório é público, não existe risco de o
    banco com seus dados pessoais ser commitado por engano.
    """
    # os.environ.get(nome) devolve None se a variável não existir.
    # O "or" usa o valor padrão nesse caso (e também se ela estiver vazia).
    data_home = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(data_home) / "habit" / "habits.db"


def _prepare_db_file(path: Path) -> None:
    """Cria a pasta e o arquivo do banco com permissões restritas.

    Permissões no Linux (em octal):
      0o700 na pasta   -> só o dono pode entrar, ler e escrever (rwx------)
      0o600 no arquivo -> só o dono pode ler e escrever        (rw-------)
    Assim, outros usuários da mesma máquina não conseguem ler seus dados.
    Referência: https://docs.python.org/3/library/os.html#os.chmod

    O "_" no início do nome é uma convenção do Python para indicar
    que a função é de uso interno deste módulo.
    """
    # parents=True: cria também as pastas intermediárias, se faltarem.
    # exist_ok=True: não dá erro se a pasta já existir.
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    if not path.exists():
        # Criamos o arquivo vazio JÁ com a permissão 0o600, antes de o
        # SQLite abri-lo. Se deixássemos o SQLite criar, ele usaria a
        # permissão padrão do sistema (normalmente legível por todos),
        # e haveria um intervalo em que o arquivo ficaria exposto.
        # os.open (baixo nível) permite definir a permissão NA CRIAÇÃO;
        # o open() comum não permite.
        fd = os.open(path, os.O_CREAT | os.O_WRONLY, 0o600)
        os.close(fd)


# ------------------------------------------------------------
# Conexão
# ------------------------------------------------------------
@contextmanager
def get_connection(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Abre uma conexão com o banco, pronta para uso, e a fecha no fim.

    Uso:
        with get_connection() as conn:
            conn.execute("SELECT ...")

    @contextmanager transforma esta função (um "gerador", por causa do
    yield) em algo que funciona com "with". O que vem ANTES do yield
    roda na entrada do bloco; o que vem DEPOIS, na saída.
    Referência: https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager

    Por que não usar só "with sqlite3.connect(...) as conn"?
    Pegadinha clássica: nesse caso o "with" faz commit/rollback, mas
    NÃO fecha a conexão. Aqui garantimos as duas coisas.

    Args:
        path: caminho do banco. Se None, usa o padrão (get_db_path).
              Poder escolher o caminho será útil nos testes, para
              usar um banco temporário em vez do seu banco real.
    """
    if path is None:
        path = get_db_path()
    _prepare_db_file(path)

    conn = sqlite3.connect(path)
    try:
        # Liga a verificação de chaves estrangeiras. No SQLite ela vem
        # DESLIGADA por padrão, e precisa ser ligada a CADA conexão.
        # Sem isso, o ON DELETE CASCADE é simplesmente ignorado.
        # Referência: https://www.sqlite.org/foreignkeys.html#fk_enable
        conn.execute("PRAGMA foreign_keys = ON")

        # Por padrão, cada linha de um SELECT vem como tupla:
        #   row[0], row[1]...  (fácil de confundir as posições)
        # Com sqlite3.Row, podemos acessar pelo nome da coluna:
        #   row["name"], row["weekly_goal"]...
        conn.row_factory = sqlite3.Row

        # Cria as tabelas, se ainda não existirem.
        # executescript executa vários comandos SQL de uma vez.
        conn.executescript(SCHEMA)

        yield conn  # <- aqui o código dentro do "with" é executado

        # Chegou aqui sem erro: grava definitivamente as alterações.
        conn.commit()
    except Exception:
        # Deu erro no meio: desfaz TUDO o que foi feito nesta conexão.
        # Isso é uma TRANSAÇÃO: ou tudo é gravado, ou nada é —
        # o banco nunca fica "pela metade".
        conn.rollback()
        raise  # repassa o erro adiante, para não escondê-lo
    finally:
        # "finally" roda SEMPRE, com ou sem erro: a conexão é fechada.
        conn.close()

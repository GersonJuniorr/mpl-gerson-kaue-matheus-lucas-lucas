"""O erro do compilador. Formato fixado em CONTRATOS.md, secao 7."""


class ErroMPL(Exception):
    """Erro de compilacao ou de execucao, com o lugar onde aconteceu."""

    def __init__(self, fase, linha, coluna, mensagem):
        super().__init__(mensagem)
        self.fase = fase          # 'lexico', 'sintatico', 'semantico' ou 'execucao'
        self.linha = linha        # a primeira linha do arquivo e 1
        self.coluna = coluna      # a primeira coluna de cada linha e 1
        self.mensagem = mensagem

    def __str__(self):
        return f"erro {self.fase}: linha {self.linha}, coluna {self.coluna}: {self.mensagem}"


class NaoImplementado(Exception):
    """Marca uma fase que ainda nao foi escrita. Some conforme voces avancam."""

"""
Entrega 1 — analise lexica.

Transformar o texto do programa numa lista de tokens.

O que voces tem que devolver: uma lista de Token. O ultimo elemento e sempre
um token FIM_ARQUIVO. A regra de posicao dele esta em CONTRATOS.md, secao 7.

Leiam antes: LINGUAGEM.md secao 2, e CONTRATOS.md secao 2.
"""
from mplc.erros import ErroMPL

# Palavras reservadas (LINGUAGEM.md secao 2.1) -> tipo de token.
PALAVRAS_RESERVADAS = {
    'funcao': 'FUNCAO',
    'retorne': 'RETORNE',
    'se': 'SE',
    'senao': 'SENAO',
    'enquanto': 'ENQUANTO',
    'escreva': 'ESCREVA',
    'inteiro': 'TIPO_INTEIRO',
    'real': 'TIPO_REAL',
    'logico': 'TIPO_LOGICO',
    'texto': 'TIPO_TEXTO',
    'vazio': 'TIPO_VAZIO',
    'verdadeiro': 'LOGICO',
    'falso': 'LOGICO',
    'e': 'E',
    'ou': 'OU',
    'nao': 'NAO',
}

# Operadores/delimitadores de dois caracteres. Tem que ser tentados ANTES dos
# de um caractere so — e essa e a armadilha da entrega: <= antes de <, ==
# antes de =, != antes de !, >= antes de >.
SIMBOLOS_DOIS = {
    '==': 'IGUAL',
    '!=': 'DIFERENTE',
    '<=': 'MENOR_IGUAL',
    '>=': 'MAIOR_IGUAL',
}

# Operadores/delimitadores de um caractere.
SIMBOLOS_UM = {
    '+': 'MAIS',
    '-': 'MENOS',
    '*': 'VEZES',
    '/': 'DIVIDE',
    '%': 'RESTO',
    '<': 'MENOR',
    '>': 'MAIOR',
    '=': 'ATRIBUI',
    '(': 'ABRE_PAR',
    ')': 'FECHA_PAR',
    '{': 'ABRE_CHAVE',
    '}': 'FECHA_CHAVE',
    ',': 'VIRGULA',
    ';': 'PONTO_VIRGULA',
}

# Escapes aceitos dentro de texto (LINGUAGEM.md secao 2.3).
ESCAPES = {
    'n': '\n',
    't': '\t',
    '"': '"',
    '\\': '\\',
}


class Token:
    __slots__ = ('tipo', 'lexema', 'linha', 'coluna')

    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo          # 'ID', 'INTEIRO', 'MAIS', ... (a lista esta no contrato)
        self.lexema = lexema      # o texto exato como apareceu no fonte
        self.linha = linha
        self.coluna = coluna      # a coluna do PRIMEIRO caractere do token

    def __str__(self):
        # esta e a linha que o --tokens imprime; nao mexam no formato
        return f"{self.linha},{self.coluna},{self.tipo},{self.lexema}"


class _Leitor:
    """Percorre o fonte caractere a caractere, controlando linha e coluna.

    A primeira linha e a primeira coluna sao 1 (CONTRATOS.md, secao 7).
    """

    def __init__(self, fonte):
        self.fonte = fonte
        self.tam = len(fonte)
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    def fim(self):
        return self.pos >= self.tam

    def atual(self):
        return self.fonte[self.pos] if self.pos < self.tam else ''

    def ver(self, deslocamento=0):
        i = self.pos + deslocamento
        return self.fonte[i] if 0 <= i < self.tam else ''

    def avancar(self):
        c = self.fonte[self.pos]
        self.pos += 1
        if c == '\n':
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c


def _erro(leitor, linha, coluna, mensagem):
    raise ErroMPL('lexico', linha, coluna, mensagem)


def _ignorar_espacos_e_comentarios(leitor):
    """Consome espacos, tabulacoes, quebras de linha e comentarios."""
    while not leitor.fim():
        c = leitor.atual()
        if c in ' \t\r\n':
            leitor.avancar()
            continue
        if c == '/' and leitor.ver(1) == '/':
            # comentario de linha: ate o fim da linha (nao inclui o \n)
            while not leitor.fim() and leitor.atual() != '\n':
                leitor.avancar()
            continue
        if c == '/' and leitor.ver(1) == '*':
            linha_abertura = leitor.linha
            coluna_abertura = leitor.coluna
            leitor.avancar()  # '/'
            leitor.avancar()  # '*'
            fechado = False
            while not leitor.fim():
                if leitor.atual() == '*' and leitor.ver(1) == '/':
                    leitor.avancar()
                    leitor.avancar()
                    fechado = True
                    break
                leitor.avancar()
            if not fechado:
                _erro(leitor, linha_abertura, coluna_abertura,
                      'comentario de bloco aberto e nunca fechado')
            continue
        break


def _ler_identificador_ou_palavra(leitor):
    linha, coluna = leitor.linha, leitor.coluna
    inicio = leitor.pos
    while not leitor.fim() and (leitor.atual().isalnum() or leitor.atual() == '_'):
        leitor.avancar()
    lexema = leitor.fonte[inicio:leitor.pos]
    tipo = PALAVRAS_RESERVADAS.get(lexema, 'ID')
    return Token(tipo, lexema, linha, coluna)


def _ler_numero(leitor):
    linha, coluna = leitor.linha, leitor.coluna
    inicio = leitor.pos
    while not leitor.fim() and leitor.atual().isdigit():
        leitor.avancar()

    if leitor.atual() == '.':
        # "3." e erro: o ponto de literal real exige digito nos dois lados.
        lin_ponto, col_ponto = leitor.linha, leitor.coluna
        leitor.avancar()  # consome o '.'
        if leitor.fim() or not leitor.atual().isdigit():
            _erro(leitor, lin_ponto, col_ponto,
                  "'.' de literal real precisa de digito dos dois lados")
        while not leitor.fim() and leitor.atual().isdigit():
            leitor.avancar()
        lexema = leitor.fonte[inicio:leitor.pos]
        return Token('REAL', lexema, linha, coluna)

    lexema = leitor.fonte[inicio:leitor.pos]
    return Token('INTEIRO', lexema, linha, coluna)


def _ler_texto(leitor):
    linha, coluna = leitor.linha, leitor.coluna
    inicio = leitor.pos
    leitor.avancar()  # consome a aspa de abertura
    while True:
        if leitor.fim() or leitor.atual() == '\n':
            _erro(leitor, linha, coluna, 'texto nao fechado antes do fim da linha')
        c = leitor.atual()
        if c == '"':
            leitor.avancar()
            break
        if c == '\\':
            lin_barra, col_barra = leitor.linha, leitor.coluna
            leitor.avancar()  # consome '\'
            if leitor.fim() or leitor.atual() not in ESCAPES:
                _erro(leitor, lin_barra, col_barra, 'escape desconhecido em texto')
            leitor.avancar()  # consome o caractere de escape
            continue
        leitor.avancar()
    lexema = leitor.fonte[inicio:leitor.pos]
    return Token('TEXTO', lexema, linha, coluna)


def analisar(fonte):
    """Recebe o texto do programa. Devolve a lista de Token."""
    leitor = _Leitor(fonte)
    tokens = []

    while True:
        _ignorar_espacos_e_comentarios(leitor)
        if leitor.fim():
            break

        c = leitor.atual()
        linha, coluna = leitor.linha, leitor.coluna

        if c.isalpha() or c == '_':
            tokens.append(_ler_identificador_ou_palavra(leitor))
            continue

        if c.isdigit():
            tokens.append(_ler_numero(leitor))
            continue

        if c == '"':
            tokens.append(_ler_texto(leitor))
            continue

        dois = c + leitor.ver(1)
        if dois in SIMBOLOS_DOIS:
            leitor.avancar()
            leitor.avancar()
            tokens.append(Token(SIMBOLOS_DOIS[dois], dois, linha, coluna))
            continue

        if c in SIMBOLOS_UM:
            leitor.avancar()
            tokens.append(Token(SIMBOLOS_UM[c], c, linha, coluna))
            continue

        _erro(leitor, linha, coluna, f'caractere invalido {c!r}')

    # FIM_ARQUIVO: regra de posicao em CONTRATOS.md, secao 7.
    # Se o arquivo termina com quebra de linha, o leitor ja avancou linha e
    # voltou a coluna 1 — e exatamente o que se pede. Se nao termina com
    # quebra de linha, leitor.linha/leitor.coluna ja apontam logo depois do
    # ultimo caractere.
    tokens.append(Token('FIM_ARQUIVO', '', leitor.linha, leitor.coluna))
    return tokens

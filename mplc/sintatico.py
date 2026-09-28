"""
Entrega 2 — analise sintatica.

Transformar a lista de tokens numa arvore.

Sugestao forte: descida recursiva, uma funcao por nivel de precedencia, na
ordem da secao 3.3 da especificacao. E como voces vao enxergar a precedencia
virar formato de arvore.

Gerador de parser (ANTLR, PLY, yacc) esta proibido nesta entrega e na
anterior — o objetivo e entender, e o gerador esconde exatamente a parte
que esta sendo ensinada.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 3.
"""
from mplc.erros import ErroMPL


class No:
    """Um no da arvore. O rotulo e o que sai no --ast."""

    def __init__(self, rotulo, filhos=None, linha=0, coluna=0, **extra):
        self.rotulo = rotulo      # 'binario +', 'literal inteiro 1', 'bloco', ...
        self.filhos = filhos or []
        self.linha = linha
        self.coluna = coluna
        self.extra = extra        # o que a semantica quiser pendurar depois


def analisar(tokens):
    """Recebe a lista de Token. Devolve a raiz da arvore (um No 'programa')."""
    return _Parser(tokens).analisar_programa()


def despejar(no, nivel=0, saida=None):
    """Imprime a arvore no formato do --ast. Ja esta pronto: dois espacos por nivel."""
    saida = saida if saida is not None else []
    saida.append('  ' * nivel + no.rotulo)
    for f in no.filhos:
        despejar(f, nivel + 1, saida)
    return saida


TIPOS_TOKEN = {
    'TIPO_INTEIRO': 'inteiro',
    'TIPO_REAL': 'real',
    'TIPO_LOGICO': 'logico',
    'TIPO_TEXTO': 'texto',
    'TIPO_VAZIO': 'vazio',
}

TIPOS_SEM_VAZIO = {'TIPO_INTEIRO', 'TIPO_REAL', 'TIPO_LOGICO', 'TIPO_TEXTO'}
LITERAIS = {'INTEIRO', 'REAL', 'LOGICO', 'TEXTO'}


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def atual(self):
        return self.tokens[self.pos]

    def avancar(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def aceitar(self, tipo):
        if self.atual().tipo == tipo:
            return self.avancar()
        return None

    def erro(self, token, mensagem):
        raise ErroMPL('sintatico', token.linha, token.coluna, mensagem)

    def esperar(self, tipo, mensagem=None):
        token = self.atual()
        if token.tipo != tipo:
            self.erro(token, mensagem or f'esperava {tipo}')
        return self.avancar()

    def esperar_um(self, tipos, mensagem):
        token = self.atual()
        if token.tipo not in tipos:
            self.erro(token, mensagem)
        return self.avancar()

    def analisar_programa(self):
        funcoes = []
        while self.atual().tipo != 'FIM_ARQUIVO':
            funcoes.append(self.funcao())
        self.esperar('FIM_ARQUIVO')
        return No('programa', funcoes)

    def tipo(self, aceitar_vazio):
        tipos = set(TIPOS_SEM_VAZIO)
        if aceitar_vazio:
            tipos.add('TIPO_VAZIO')
        token = self.esperar_um(tipos, 'esperava um tipo')
        return TIPOS_TOKEN[token.tipo], token

    def funcao(self):
        inicio = self.esperar('FUNCAO')
        tipo_retorno, _ = self.tipo(aceitar_vazio=True)
        nome = self.esperar('ID', 'esperava o nome da funcao')
        self.esperar('ABRE_PAR', 'esperava (')
        parametros = self.parametros()
        self.esperar('FECHA_PAR', 'esperava )')
        bloco = self.bloco()
        return No(
            f'funcao {nome.lexema} {tipo_retorno}',
            [No('parametros', parametros), bloco],
            linha=inicio.linha,
            coluna=inicio.coluna,
        )

    def parametros(self):
        params = []
        if self.atual().tipo == 'FECHA_PAR':
            return params
        while True:
            tipo_nome, tipo_tok = self.tipo(aceitar_vazio=False)
            nome = self.esperar('ID', 'esperava o nome do parametro')
            params.append(
                No(
                    f'parametro {nome.lexema} {tipo_nome}',
                    linha=tipo_tok.linha,
                    coluna=tipo_tok.coluna,
                )
            )
            if not self.aceitar('VIRGULA'):
                break
        return params

    def bloco(self):
        abre = self.esperar('ABRE_CHAVE', 'esperava {')
        comandos = []
        while self.atual().tipo not in ('FECHA_CHAVE', 'FIM_ARQUIVO'):
            comandos.append(self.comando())
        self.esperar('FECHA_CHAVE', 'esperava }')
        return No('bloco', comandos, linha=abre.linha, coluna=abre.coluna)

    def comando(self):
        tipo = self.atual().tipo
        if tipo in TIPOS_SEM_VAZIO:
            return self.declaracao()
        if tipo == 'ID':
            return self.atribuicao_ou_chamada()
        if tipo == 'SE':
            return self.comando_se()
        if tipo == 'ENQUANTO':
            return self.comando_enquanto()
        if tipo == 'ESCREVA':
            return self.comando_escreva()
        if tipo == 'RETORNE':
            return self.comando_retorne()
        if tipo == 'ABRE_CHAVE':
            return self.bloco()
        self.erro(self.atual(), 'comando invalido')

    def declaracao(self):
        tipo_nome, tipo_tok = self.tipo(aceitar_vazio=False)
        nome = self.esperar('ID', 'esperava o nome da variavel')
        no = No(
            f'declaracao {nome.lexema} {tipo_nome}',
            linha=tipo_tok.linha,
            coluna=tipo_tok.coluna,
        )
        if self.aceitar('ATRIBUI'):
            no.filhos.append(self.expressao())
        self.esperar('PONTO_VIRGULA', 'esperava ;')
        return no

    def atribuicao_ou_chamada(self):
        nome = self.esperar('ID')
        if self.aceitar('ATRIBUI'):
            valor = self.expressao()
            self.esperar('PONTO_VIRGULA', 'esperava ;')
            return No(
                f'atribuicao {nome.lexema}',
                [valor],
                linha=nome.linha,
                coluna=nome.coluna,
            )
        if self.aceitar('ABRE_PAR'):
            chamada = self.chamada(nome)
            self.esperar('PONTO_VIRGULA', 'esperava ;')
            return chamada
        self.erro(self.atual(), 'esperava = ou (')

    def comando_se(self):
        inicio = self.esperar('SE')
        self.esperar('ABRE_PAR', 'esperava (')
        condicao = self.expressao()
        self.esperar('FECHA_PAR', 'esperava )')
        entao = self.bloco()
        filhos = [condicao, entao]
        if self.aceitar('SENAO'):
            filhos.append(self.bloco())
        return No('se', filhos, linha=inicio.linha, coluna=inicio.coluna)

    def comando_enquanto(self):
        inicio = self.esperar('ENQUANTO')
        self.esperar('ABRE_PAR', 'esperava (')
        condicao = self.expressao()
        self.esperar('FECHA_PAR', 'esperava )')
        bloco = self.bloco()
        return No('enquanto', [condicao, bloco], linha=inicio.linha, coluna=inicio.coluna)

    def comando_escreva(self):
        inicio = self.esperar('ESCREVA')
        self.esperar('ABRE_PAR', 'esperava (')
        valor = self.expressao()
        self.esperar('FECHA_PAR', 'esperava )')
        self.esperar('PONTO_VIRGULA', 'esperava ;')
        return No('escreva', [valor], linha=inicio.linha, coluna=inicio.coluna)

    def comando_retorne(self):
        inicio = self.esperar('RETORNE')
        filhos = []
        if self.atual().tipo != 'PONTO_VIRGULA':
            filhos.append(self.expressao())
        self.esperar('PONTO_VIRGULA', 'esperava ;')
        return No('retorne', filhos, linha=inicio.linha, coluna=inicio.coluna)

    def expressao(self):
        return self.expr_ou()

    def expr_ou(self):
        no = self.expr_e()
        while True:
            op = self.aceitar('OU')
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_e()], linha=op.linha, coluna=op.coluna)

    def expr_e(self):
        no = self.expr_igualdade()
        while True:
            op = self.aceitar('E')
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_igualdade()], linha=op.linha, coluna=op.coluna)

    def expr_igualdade(self):
        no = self.expr_relacional()
        while True:
            op = self.aceitar('IGUAL') or self.aceitar('DIFERENTE')
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_relacional()], linha=op.linha, coluna=op.coluna)

    def expr_relacional(self):
        no = self.expr_aditiva()
        while True:
            op = (
                self.aceitar('MENOR')
                or self.aceitar('MENOR_IGUAL')
                or self.aceitar('MAIOR')
                or self.aceitar('MAIOR_IGUAL')
            )
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_aditiva()], linha=op.linha, coluna=op.coluna)

    def expr_aditiva(self):
        no = self.expr_multiplicativa()
        while True:
            op = self.aceitar('MAIS') or self.aceitar('MENOS')
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_multiplicativa()], linha=op.linha, coluna=op.coluna)

    def expr_multiplicativa(self):
        no = self.expr_unaria()
        while True:
            op = self.aceitar('VEZES') or self.aceitar('DIVIDE') or self.aceitar('RESTO')
            if not op:
                return no
            no = No(f'binario {op.lexema}', [no, self.expr_unaria()], linha=op.linha, coluna=op.coluna)

    def expr_unaria(self):
        op = self.aceitar('NAO') or self.aceitar('MENOS')
        if op:
            return No(f'unario {op.lexema}', [self.expr_unaria()], linha=op.linha, coluna=op.coluna)
        return self.primario()

    def primario(self):
        if self.aceitar('ABRE_PAR'):
            expr = self.expressao()
            self.esperar('FECHA_PAR', 'esperava )')
            return expr

        atual = self.atual()
        if atual.tipo in LITERAIS:
            token = self.avancar()
            return No(self.rotulo_literal(token), linha=token.linha, coluna=token.coluna)

        if atual.tipo == 'ID':
            nome = self.avancar()
            if self.aceitar('ABRE_PAR'):
                return self.chamada(nome)
            return No(f'variavel {nome.lexema}', linha=nome.linha, coluna=nome.coluna)

        self.erro(atual, 'esperava expressao')

    def chamada(self, nome):
        args = []
        if self.atual().tipo != 'FECHA_PAR':
            while True:
                args.append(self.expressao())
                if not self.aceitar('VIRGULA'):
                    break
        self.esperar('FECHA_PAR', 'esperava )')
        return No(f'chamada {nome.lexema}', args, linha=nome.linha, coluna=nome.coluna)

    def rotulo_literal(self, token):
        if token.tipo == 'INTEIRO':
            return f'literal inteiro {token.lexema}'
        if token.tipo == 'REAL':
            return f'literal real {float(token.lexema):.6f}'
        if token.tipo == 'LOGICO':
            return f'literal logico {token.lexema}'
        return f'literal texto {token.lexema}'

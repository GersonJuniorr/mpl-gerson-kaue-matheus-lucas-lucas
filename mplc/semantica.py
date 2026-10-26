"""
Entrega 3 — analise semantica.

Tabela de simbolos, escopos aninhados e verificacao de tipos.

Tres coisas que costumam ser esquecidas e valem nota:
  - o corpo de uma funcao abre DOIS escopos (o dos parametros e o do bloco);
  - uma funcao pode ser chamada antes de aparecer no arquivo, entao a
    primeira passada so coleta assinaturas;
  - funcao com retorno declarado precisa garantir o retorno em TODOS os
    caminhos.

Leiam antes: LINGUAGEM.md secoes 3 a 5, e CONTRATOS.md secao 4.
"""
from dataclasses import dataclass, field

from mplc.erros import ErroMPL


TIPOS_NUMERICOS = {'inteiro', 'real'}


@dataclass
class Simbolo:
    nome: str
    categoria: str
    tipo: str
    linha: int


@dataclass
class Escopo:
    id: int
    descricao: str
    pai: int | None
    simbolos: list[Simbolo] = field(default_factory=list)
    _por_nome: dict[str, Simbolo] = field(default_factory=dict)

    def adicionar(self, simbolo: Simbolo):
        if simbolo.nome in self._por_nome:
            return False
        self._por_nome[simbolo.nome] = simbolo
        self.simbolos.append(simbolo)
        return True

    def buscar_local(self, nome: str):
        return self._por_nome.get(nome)


@dataclass
class AssinaturaFuncao:
    nome: str
    retorno: str
    parametros: list[tuple[str, str, int, int]]  # (nome, tipo, linha, coluna)
    linha: int
    coluna: int

    @property
    def tipo_tabela(self):
        tipos = ','.join(tipo for _, tipo, _, _ in self.parametros)
        return f'{self.retorno}({tipos})'


class TabelaSemantica:
    def __init__(self):
        self.escopos: list[Escopo] = [Escopo(0, 'global', None)]

    @property
    def global_(self):
        return self.escopos[0]

    def abrir_escopo(self, descricao, pai):
        escopo = Escopo(len(self.escopos), descricao, pai.id)
        self.escopos.append(escopo)
        return escopo


class AnalisadorSemantico:
    def __init__(self, arvore):
        self.arvore = arvore
        self.tabela = TabelaSemantica()
        self.funcoes: dict[str, AssinaturaFuncao] = {}

    def erro(self, no, mensagem):
        raise ErroMPL('semantico', no.linha, no.coluna, mensagem)

    def analisar(self):
        self._coletar_assinaturas()
        self._validar_principal()
        for funcao in self.arvore.filhos:
            self._analisar_funcao(funcao)
        return self.tabela

    def _coletar_assinaturas(self):
        for funcao in self.arvore.filhos:
            nome, retorno = self._ler_funcao(funcao)
            if nome in self.funcoes:
                self.erro(funcao, f'funcao {nome} redeclarada')

            parametros = []
            for param in funcao.filhos[0].filhos:
                p_nome, p_tipo = self._ler_parametro(param)
                parametros.append((p_nome, p_tipo, param.linha, param.coluna))

            assinatura = AssinaturaFuncao(nome, retorno, parametros, funcao.linha, funcao.coluna)
            self.funcoes[nome] = assinatura
            self.tabela.global_.adicionar(
                Simbolo(nome, 'funcao', assinatura.tipo_tabela, funcao.linha)
            )

    def _validar_principal(self):
        principal = self.funcoes.get('principal')
        if not principal:
            linha = self.arvore.filhos[0].linha if self.arvore.filhos else 1
            coluna = self.arvore.filhos[0].coluna if self.arvore.filhos else 1
            raise ErroMPL('semantico', linha, coluna, 'funcao principal ausente')

        if principal.retorno != 'vazio' or principal.parametros:
            raise ErroMPL(
                'semantico', principal.linha, principal.coluna,
                'principal deve ser funcao vazio sem parametros',
            )

    def _analisar_funcao(self, no_funcao):
        nome, retorno = self._ler_funcao(no_funcao)
        assinatura = self.funcoes[nome]

        escopo_param = self.tabela.abrir_escopo(f'funcao {nome}', self.tabela.global_)
        for p_nome, p_tipo, linha, coluna in assinatura.parametros:
            simbolo = Simbolo(p_nome, 'parametro', p_tipo, linha)
            if not escopo_param.adicionar(simbolo):
                raise ErroMPL('semantico', linha, coluna, f'parametro {p_nome} redeclarado')

        escopo_bloco = self.tabela.abrir_escopo('bloco', escopo_param)
        garantiu = self._analisar_comandos(no_funcao.filhos[1].filhos, escopo_bloco, retorno)

        if retorno != 'vazio' and not garantiu:
            self.erro(no_funcao, f'funcao {nome} pode terminar sem retorne')

    def _analisar_comandos(self, comandos, escopo, retorno_funcao):
        garantiu = False
        for comando in comandos:
            comando_garante = self._analisar_comando(comando, escopo, retorno_funcao)
            if comando_garante:
                garantiu = True
        return garantiu

    def _analisar_comando(self, no, escopo, retorno_funcao):
        rotulo = no.rotulo

        if rotulo.startswith('declaracao '):
            nome, tipo = self._ler_declaracao(no)
            simbolo = Simbolo(nome, 'variavel', tipo, no.linha)
            if not escopo.adicionar(simbolo):
                self.erro(no, f'{nome} redeclarado no mesmo escopo')
            if no.filhos:
                tipo_expr = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
                self._exigir_atribuicao(tipo, tipo_expr, no)
            return False

        if rotulo.startswith('atribuicao '):
            nome = rotulo.split(' ', 1)[1]
            simbolo = self._buscar_variavel(nome, escopo, no)
            tipo_expr = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            self._exigir_atribuicao(simbolo.tipo, tipo_expr, no)
            return False

        if rotulo == 'se':
            tipo_cond = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            if tipo_cond != 'logico':
                self.erro(no.filhos[0], 'condicao de se deve ser logico')

            bloco_entao = self._analisar_bloco(no.filhos[1], escopo, retorno_funcao)
            if len(no.filhos) == 3:
                bloco_senao = self._analisar_bloco(no.filhos[2], escopo, retorno_funcao)
                return bloco_entao and bloco_senao
            return False

        if rotulo == 'enquanto':
            tipo_cond = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            if tipo_cond != 'logico':
                self.erro(no.filhos[0], 'condicao de enquanto deve ser logico')
            self._analisar_bloco(no.filhos[1], escopo, retorno_funcao)
            return False

        if rotulo == 'escreva':
            self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            return False

        if rotulo == 'retorne':
            if retorno_funcao == 'vazio':
                if no.filhos:
                    self.erro(no, 'funcao vazio nao aceita retorne com valor')
            else:
                if not no.filhos:
                    self.erro(no, 'funcao com retorno exige retorne com valor')
                tipo_expr = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
                self._exigir_atribuicao(retorno_funcao, tipo_expr, no)
            return True

        if rotulo.startswith('chamada '):
            self._tipo_chamada(no, escopo, exigir_nao_vazio=False)
            return False

        if rotulo == 'bloco':
            return self._analisar_bloco(no, escopo, retorno_funcao)

        self.erro(no, f'comando desconhecido: {rotulo}')

    def _analisar_bloco(self, no_bloco, escopo_pai, retorno_funcao):
        escopo = self.tabela.abrir_escopo('bloco', escopo_pai)
        return self._analisar_comandos(no_bloco.filhos, escopo, retorno_funcao)

    def _tipo_expressao(self, no, escopo, exigir_nao_vazio):
        rotulo = no.rotulo

        if rotulo.startswith('literal '):
            return self._ler_literal(no)

        if rotulo.startswith('variavel '):
            nome = rotulo.split(' ', 1)[1]
            return self._buscar_variavel(nome, escopo, no).tipo

        if rotulo.startswith('chamada '):
            tipo = self._tipo_chamada(no, escopo, exigir_nao_vazio)
            return tipo

        if rotulo.startswith('unario '):
            op = rotulo.split(' ', 1)[1]
            tipo = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            if op == 'nao':
                if tipo != 'logico':
                    self.erro(no, 'operador nao exige operando logico')
                return 'logico'
            if op == '-':
                if tipo not in TIPOS_NUMERICOS:
                    self.erro(no, 'sinal unario exige operando numerico')
                return tipo
            self.erro(no, f'operador unario desconhecido: {op}')

        if rotulo.startswith('binario '):
            op = rotulo.split(' ', 1)[1]
            esq = self._tipo_expressao(no.filhos[0], escopo, exigir_nao_vazio=True)
            dir_ = self._tipo_expressao(no.filhos[1], escopo, exigir_nao_vazio=True)
            return self._tipo_binario(op, esq, dir_, no)

        self.erro(no, f'expressao invalida: {rotulo}')

    def _tipo_chamada(self, no, escopo, exigir_nao_vazio):
        nome = no.rotulo.split(' ', 1)[1]
        assinatura = self.funcoes.get(nome)
        if not assinatura:
            self.erro(no, f'funcao {nome} nao declarada')

        if len(no.filhos) != len(assinatura.parametros):
            self.erro(no, f'quantidade de argumentos invalida em {nome}')

        for arg_no, (_, tipo_param, _, _) in zip(no.filhos, assinatura.parametros):
            tipo_arg = self._tipo_expressao(arg_no, escopo, exigir_nao_vazio=True)
            self._exigir_atribuicao(tipo_param, tipo_arg, arg_no)

        if exigir_nao_vazio and assinatura.retorno == 'vazio':
            self.erro(no, f'funcao {nome} retorna vazio e nao pode estar em expressao')

        return assinatura.retorno

    def _tipo_binario(self, op, tipo_esq, tipo_dir, no):
        if op in {'e', 'ou'}:
            if tipo_esq != 'logico' or tipo_dir != 'logico':
                self.erro(no, f'operador {op} exige operandos logicos')
            return 'logico'

        if op in {'==', '!='}:
            if tipo_esq == tipo_dir:
                return 'logico'
            if tipo_esq in TIPOS_NUMERICOS and tipo_dir in TIPOS_NUMERICOS:
                return 'logico'
            self.erro(no, f'operador {op} exige operandos compativeis')

        if op in {'<', '<=', '>', '>='}:
            if tipo_esq in TIPOS_NUMERICOS and tipo_dir in TIPOS_NUMERICOS:
                return 'logico'
            self.erro(no, f'operador {op} exige operandos numericos')

        if op == '+':
            if tipo_esq == 'texto' and tipo_dir == 'texto':
                return 'texto'
            if tipo_esq in TIPOS_NUMERICOS and tipo_dir in TIPOS_NUMERICOS:
                return 'real' if 'real' in (tipo_esq, tipo_dir) else 'inteiro'
            self.erro(no, 'soma aceita apenas numeros ou texto com texto')

        if op in {'-', '*', '/'}:
            if tipo_esq in TIPOS_NUMERICOS and tipo_dir in TIPOS_NUMERICOS:
                if op == '/':
                    return 'real' if 'real' in (tipo_esq, tipo_dir) else 'inteiro'
                return 'real' if 'real' in (tipo_esq, tipo_dir) else 'inteiro'
            self.erro(no, f'operador {op} exige operandos numericos')

        if op == '%':
            if tipo_esq == 'inteiro' and tipo_dir == 'inteiro':
                return 'inteiro'
            self.erro(no, 'operador % exige operandos inteiros')

        self.erro(no, f'operador desconhecido: {op}')

    def _exigir_atribuicao(self, tipo_destino, tipo_origem, no):
        if tipo_destino == tipo_origem:
            return
        if tipo_destino == 'real' and tipo_origem == 'inteiro':
            return
        self.erro(no, f'nao posso converter {tipo_origem} para {tipo_destino}')

    def _buscar_variavel(self, nome, escopo, no):
        atual = escopo
        while atual is not None:
            simbolo = atual.buscar_local(nome)
            if simbolo and simbolo.categoria in {'variavel', 'parametro'}:
                return simbolo
            atual = self.tabela.escopos[atual.pai] if atual.pai is not None else None
        self.erro(no, f'identificador {nome} nao declarado')

    @staticmethod
    def _ler_funcao(no):
        _, nome, retorno = no.rotulo.split(' ', 2)
        return nome, retorno

    @staticmethod
    def _ler_parametro(no):
        _, nome, tipo = no.rotulo.split(' ', 2)
        return nome, tipo

    @staticmethod
    def _ler_declaracao(no):
        _, nome, tipo = no.rotulo.split(' ', 2)
        return nome, tipo

    @staticmethod
    def _ler_literal(no):
        _, tipo, _ = no.rotulo.split(' ', 2)
        return tipo


def analisar(arvore):
    """Percorre a arvore, monta a tabela e confere os tipos. Devolve a tabela."""
    return AnalisadorSemantico(arvore).analisar()


def despejar(tabela):
    """Devolve as linhas do --tabela, no formato da secao 4 do contrato."""
    linhas = []
    for escopo in tabela.escopos:
        if escopo.id == 0:
            linhas.append('escopo 0 global')
        else:
            linhas.append(f'escopo {escopo.id} {escopo.descricao} pai {escopo.pai}')

        for simbolo in escopo.simbolos:
            linhas.append(
                f'  {simbolo.nome}|{simbolo.categoria}|{simbolo.tipo}|{simbolo.linha}'
            )

    return linhas

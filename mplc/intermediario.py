"""Codigo intermediario em tres enderecos para a MPL."""
import ast


def _literal(rotulo):
    _, tipo, valor = rotulo.split(' ', 2)
    if tipo == 'inteiro': return int(valor)
    if tipo == 'real': return float(valor)
    if tipo == 'logico': return valor == 'verdadeiro'
    return ast.literal_eval(valor)


class _GeradorIR:
    def __init__(self):
        self.funcoes, self.f = [], None
        self.escopos, self.tipos = [], {}
        self.local_id = self.label_id = 0

    def emit(self, op, *args, linha=0):
        self.f['codigo'].append({'op': op, 'args': list(args), 'linha': linha})

    def label(self):
        r = f'L{self.label_id}'; self.label_id += 1; return r

    def local(self, nome, tipo):
        r = f'v{self.local_id}'; self.local_id += 1
        self.escopos[-1][nome] = r; self.tipos[r] = tipo; return r

    def find(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo: return escopo[nome]
        return nome

    def gerar(self, arvore):
        for no in arvore.filhos:
            _, nome, retorno = no.rotulo.split(' ', 2)
            self.f = {'nome': nome, 'retorno': retorno, 'parametros': [], 'codigo': []}
            self.escopos, self.tipos = [{}], {}; self.local_id = 0
            for p in no.filhos[0].filhos:
                _, pn, pt = p.rotulo.split(' ', 2)
                self.f['parametros'].append(self.local(pn, pt))
            self.bloco(no.filhos[1], False)
            if not self.f['codigo'] or self.f['codigo'][-1]['op'] != 'ret':
                self.emit('ret', False, linha=no.linha)
            self.funcoes.append(self.f)
        return {'versao': 1, 'funcoes': self.funcoes}

    def bloco(self, no, novo=True):
        if novo: self.escopos.append({})
        for c in no.filhos: self.comando(c)
        if novo: self.escopos.pop()

    def coerces(self, local, linha):
        if self.tipos.get(local) == 'real': self.emit('cast_real', linha=linha)

    def comando(self, no):
        r = no.rotulo
        if r.startswith('declaracao '):
            _, nome, tipo = r.split(' ', 2); local = self.local(nome, tipo)
            if no.filhos: self.expr(no.filhos[0])
            else: self.emit('const', None, linha=no.linha)
            self.coerces(local, no.linha); self.emit('store', local, linha=no.linha)
        elif r.startswith('atribuicao '):
            local = self.find(r.split(' ', 1)[1]); self.expr(no.filhos[0])
            self.coerces(local, no.linha); self.emit('store', local, linha=no.linha)
        elif r.startswith('chamada '):
            self.call(no); self.emit('pop', linha=no.linha)
        elif r == 'escreva':
            self.expr(no.filhos[0]); self.emit('print', linha=no.linha)
        elif r == 'retorne':
            if no.filhos:
                self.expr(no.filhos[0])
                if self.f['retorno'] == 'real': self.emit('cast_real', linha=no.linha)
                self.emit('ret', True, linha=no.linha)
            else: self.emit('ret', False, linha=no.linha)
        elif r == 'se':
            falso, fim = self.label(), self.label(); self.expr(no.filhos[0])
            self.emit('jump_false', falso, linha=no.linha); self.bloco(no.filhos[1])
            if len(no.filhos) == 3:
                self.emit('jump', fim, linha=no.linha); self.emit('label', falso, linha=no.linha)
                self.bloco(no.filhos[2]); self.emit('label', fim, linha=no.linha)
            else: self.emit('label', falso, linha=no.linha)
        elif r == 'enquanto':
            inicio, fim = self.label(), self.label(); self.emit('label', inicio, linha=no.linha)
            self.expr(no.filhos[0]); self.emit('jump_false', fim, linha=no.linha)
            self.bloco(no.filhos[1]); self.emit('jump', inicio, linha=no.linha); self.emit('label', fim, linha=no.linha)
        elif r == 'bloco': self.bloco(no)

    def call(self, no):
        for a in no.filhos: self.expr(a)
        self.emit('call', no.rotulo.split(' ', 1)[1], len(no.filhos), linha=no.linha)

    def expr(self, no):
        r = no.rotulo
        if r.startswith('literal '): self.emit('const', _literal(r), linha=no.linha)
        elif r.startswith('variavel '): self.emit('load', self.find(r.split(' ', 1)[1]), linha=no.linha)
        elif r.startswith('chamada '): self.call(no)
        elif r.startswith('unario '):
            self.expr(no.filhos[0]); self.emit('un', r.split(' ', 1)[1], linha=no.linha)
        elif r.startswith('binario '):
            self.expr(no.filhos[0]); self.expr(no.filhos[1]); self.emit('bin', r.split(' ', 1)[1], linha=no.linha)


def gerar(arvore, tabela): return _GeradorIR().gerar(arvore)


def despejar(codigo):
    linhas = []
    for f in codigo['funcoes']:
        linhas.append(f"funcao {f['nome']} {f['retorno']} ({' '.join(f['parametros'])})")
        for i in f['codigo']:
            op, args = i['op'], i['args']
            if op == 'label': linhas.append(f'{args[0]}:')
            elif op == 'const': linhas.append(f'  const {args[0]!r}' if isinstance(args[0], str) else f'  const {args[0]}')
            else: linhas.append('  ' + op + ((' ' + ' '.join(map(str, args))) if args else ''))
        linhas.append('fim')
    return linhas

#!/usr/bin/env python3
"""
Verificador das entregas do trabalho semestral de Compiladores.

  python3 verificar.py 1      confere a Entrega 1
  python3 verificar.py 4      confere a Entrega 4 (e todas as anteriores)
  python3 verificar.py todas

Ele NAO le o codigo de voces. Ele roda ./compilar e ./executar e compara o
que sai. Se passar aqui, passa na correcao — e vice-versa.
"""
import os, re, subprocess, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))

# O corpus pode vir de fora, pela variavel MPL_TESTES. A correcao usa um
# corpus diferente do que esta aqui: um compilador de verdade passa nos dois,
# uma tabela que decora as saidas deste passa so neste.
T = os.path.abspath(os.environ.get('MPL_TESTES') or os.path.join(RAIZ, 'testes'))


def caminho_teste(*partes):
    """Caminho do programa a passar para ./compilar."""
    caminho = os.path.join(T, *partes)
    rel = os.path.relpath(caminho, RAIZ)
    return rel if not rel.startswith('..') else caminho
VERDE, VERMELHO, AMARELO, CINZA, ZERO = '\033[32m', '\033[31m', '\033[33m', '\033[90m', '\033[0m'
if not sys.stdout.isatty():
    VERDE = VERMELHO = AMARELO = CINZA = ZERO = ''

# Onde se escreve cada fase — para o verificador dizer por onde comecar.
ONDE = [
    ('analise lexica',        'mplc/lexico.py',        'LINGUAGEM.md secao 2 e CONTRATOS.md secao 2'),
    ('analise sintatica',     'mplc/sintatico.py',     'LINGUAGEM.md secoes 3 a 5 e CONTRATOS.md secao 3'),
    ('analise semantica',     'mplc/semantica.py',     'LINGUAGEM.md secao 3 e CONTRATOS.md secao 4'),
    ('tabela de simbolos',    'mplc/semantica.py',     'CONTRATOS.md secao 4'),
    ('codigo de tres',        'mplc/intermediario.py', 'CONTRATOS.md secao 5'),
    ('codigo intermediario',  'mplc/intermediario.py', 'CONTRATOS.md secao 5'),
    ('geracao de codigo',     'mplc/gerador.py',       'CONTRATOS.md secao 6'),
    ('maquina virtual',       'mplc/vm.py',            'CONTRATOS.md secao 6'),
]

def onde_escrever(fase):
    for chave, arquivo, leitura in ONDE:
        if chave in fase:
            return arquivo, leitura
    return None, None

class Placar:
    def __init__(self):
        self.ok = self.falhas = 0
        self.pendentes = {}          # fase ainda nao escrita -> quantas provas dependem dela
        self.quebras = {}            # excecao do compilador -> quantas provas ela derrubou
    def certo(self, nome):
        self.ok += 1
        print(f'  {VERDE}ok{ZERO}   {nome}')
    def errado(self, nome, esperado, veio):
        self.falhas += 1
        # Uma fase que ainda NAO FOI ESCRITA nao e a mesma coisa que uma fase
        # escrita e errada. Repetir dezessete vezes a mesma frase vira um muro
        # vermelho que nao ensina nada; aqui isso vira uma linha por prova e
        # UMA orientacao no fim.
        if 'quebrou: ' in veio:
            # Uma excecao derruba TODAS as provas pela mesma causa. Mostrar o
            # mesmo traceback dezessete vezes esconde a unica linha que importa.
            causa = veio.split('quebrou: ', 1)[1]
            self.quebras[causa] = self.quebras.get(causa, 0) + 1
            print(f'  {VERMELHO}!!{ZERO}   {nome} {CINZA}(o compilador quebrou){ZERO}')
            return
        m = re.search(r'ainda falta escrever: (.+?)(?: \(Entrega|$)', veio)
        if m:
            fase = m.group(1).strip()
            self.pendentes[fase] = self.pendentes.get(fase, 0) + 1
            print(f'  {CINZA}--{ZERO}   {nome} {CINZA}(espera: {fase}){ZERO}')
            return
        print(f'  {VERMELHO}FALHA{ZERO} {nome}')
        print(f'         esperado: {CINZA}{esperado}{ZERO}')
        print(f'         veio:     {CINZA}{veio}{ZERO}')

def rodar(cmd, entrada=None, limite=20):
    try:
        p = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=limite)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, '', f'passou de {limite} s sem terminar'
    except OSError as e:
        return 127, '', str(e)

def ler(caminho):
    with open(caminho, encoding='utf-8') as f:
        return f.read()

def resumo_erro(err, cod=None):
    """
    O que MOSTRAR quando o compilador escreve na saida de erro.

    Traceback do Python tem a informacao util na ULTIMA linha; as primeiras
    sao encanamento do interpretador. Cortar em 120 caracteres joga fora
    exatamente a mensagem e guarda o lixo — foi o que aconteceu comigo.
    """
    err = (err or '').strip()
    if 'Traceback (most recent call last)' in err:
        linhas = [l for l in err.split('\n') if l.strip()]
        excecao = linhas[-1].strip()
        onde = ''
        for l in reversed(linhas):
            m = re.match(r'\s*File "([^"]+)", line (\d+)', l)
            if m and 'frozen' not in m.group(1):
                onde = f' — {os.path.basename(m.group(1))}, linha {m.group(2)}'
                break
        return f'quebrou: {excecao}{onde}'
    if err:
        return err[:120]
    return f'codigo {cod}' if cod is not None else ''


def diferenca(esperado, veio):
    """Primeira linha em que os dois textos divergem, para a mensagem de erro."""
    a, b = esperado.rstrip('\n').split('\n'), veio.rstrip('\n').split('\n')
    for i in range(max(len(a), len(b))):
        la = a[i] if i < len(a) else '<acabou>'
        lb = b[i] if i < len(b) else '<acabou>'
        if la != lb:
            return f'linha {i + 1}: {la!r}', f'linha {i + 1}: {lb!r}'
    return repr(esperado[:60]), repr(veio[:60])

# --------------------------------------------------------------- os exames

def exigir_executaveis(p):
    for nome in ('compilar', 'executar'):
        caminho = os.path.join(RAIZ, nome)
        if not os.path.exists(caminho):
            p.errado(f'existe ./{nome}', 'um arquivo executavel na raiz', 'nao existe')
        elif not os.access(caminho, os.X_OK):
            p.errado(f'./{nome} tem permissao de execucao', 'executavel',
                     'sem permissao — falta um chmod +x')
        else:
            p.certo(f'./{nome} existe e e executavel')

def conferir_despejo(p, modo, extensao):
    """--tokens, --ast e --tabela: a saida tem que bater com o gabarito."""
    for prog in sorted(os.listdir(os.path.join(T, 'positivos'))):
        if not prog.endswith('.mpl'):
            continue
        base = prog[:-4]
        fonte = caminho_teste('positivos', prog)
        esperado = ler(os.path.join(T, 'fases', base + '.' + extensao))
        cod, saida, err = rodar(['./compilar', modo, fonte])
        nome = f'{modo} de {base}'
        if cod != 0:
            p.errado(nome, 'sair com codigo 0', f'codigo {cod}: {resumo_erro(err)}')
        elif saida.rstrip('\n') != esperado.rstrip('\n'):
            e, v = diferenca(esperado, saida)
            p.errado(nome, e, v)
        else:
            p.certo(nome)

def conferir_erros(p, prefixo, confere_coluna):
    """Os programas que TEM que ser recusados, na fase certa e no lugar certo."""
    for prog in sorted(os.listdir(os.path.join(T, 'negativos'))):
        if not prog.startswith(prefixo) or not prog.endswith('.mpl'):
            continue
        base = prog[:-4]
        fase_e, linha_e, coluna_e = ler(os.path.join(T, 'negativos', base + '.erro')).strip().split('|')
        fonte = caminho_teste('negativos', prog)
        cod, saida, err = rodar(['./compilar', fonte])
        nome = f'recusa {base}'
        if cod == 0:
            p.errado(nome, f'erro {fase_e} na linha {linha_e}', 'compilou sem reclamar')
            continue
        if cod != 1:
            p.errado(nome, 'codigo de saida 1', f'codigo {cod}: {resumo_erro(err)}')
            continue
        m = re.search(r'erro (\w+): linha (\d+), coluna (\d+):', err)
        if not m:
            p.errado(nome, 'erro <fase>: linha L, coluna C: ...', resumo_erro(err) or '(stderr vazio)')
            continue
        veio = (m.group(1), m.group(2), m.group(3))
        alvo = (fase_e, linha_e, coluna_e)
        if confere_coluna:
            if veio != alvo:
                p.errado(nome, 'fase %s, linha %s, coluna %s' % alvo, 'fase %s, linha %s, coluna %s' % veio)
            else:
                p.certo(nome)
        else:
            if veio[:2] != alvo[:2]:
                p.errado(nome, f'fase {fase_e}, linha {linha_e}', f'fase {veio[0]}, linha {veio[1]}')
            else:
                p.certo(nome)

def conferir_positivos_compilam(p, modo):
    """
    Nenhum programa valido pode ser recusado pelas fases ja exigidas.

    ⚠️ Roda ate a fase DESTA entrega, nunca o compilador inteiro. Antes daqui
    a prova mandava compilar tudo — e um grupo que tivesse terminado a Entrega
    3 corretamente via vermelho, porque a geracao de codigo (Entrega 4) ainda
    nao existia. A prova cobrava trabalho que a entrega nao pede.
    """
    for prog in sorted(os.listdir(os.path.join(T, 'positivos'))):
        if not prog.endswith('.mpl'):
            continue
        cod, _, err = rodar(['./compilar', modo, caminho_teste('positivos', prog)])
        if cod != 0:
            p.errado(f'aceita {prog[:-4]}', 'passar sem erro', resumo_erro(err, cod))
        else:
            p.certo(f'aceita {prog[:-4]}')

def conferir_execucao(p):
    """O teste que vale por todos: o programa roda e imprime o que devia."""
    for prog in sorted(os.listdir(os.path.join(T, 'positivos'))):
        if not prog.endswith('.mpl'):
            continue
        base = prog[:-4]
        fonte = caminho_teste('positivos', prog)
        alvo = os.path.join(T, 'positivos', base + '.mplb')
        if os.path.exists(alvo):
            os.remove(alvo)
        cod, _, err = rodar(['./compilar', fonte])
        if cod != 0:
            p.errado(f'executa {base}', 'compilar', resumo_erro(err)); continue
        if not os.path.exists(alvo):
            p.errado(f'executa {base}', f'gerar {base}.mplb ao lado do fonte', 'o arquivo nao apareceu')
            continue
        cod, saida, err = rodar(['./executar', caminho_teste('positivos', base + '.mplb')])
        esperado = ler(os.path.join(T, 'positivos', base + '.saida'))
        if cod != 0:
            p.errado(f'executa {base}', 'sair com codigo 0', f'codigo {cod}: {resumo_erro(err)}')
        elif saida != esperado:
            e, v = diferenca(esperado, saida)
            p.errado(f'executa {base}', e, v)
        else:
            p.certo(f'executa {base}')

def conferir_execucao_erros(p):
    for prog in sorted(os.listdir(os.path.join(T, 'negativos'))):
        if not prog.startswith('exec') or not prog.endswith('.mpl'):
            continue
        base = prog[:-4]
        fase_e, linha_e, _ = ler(os.path.join(T, 'negativos', base + '.erro')).strip().split('|')
        cod, _, err = rodar(['./compilar', caminho_teste('negativos', prog)])
        if cod != 0:
            p.errado(f'execucao {base}', 'compilar (o erro e em tempo de execucao)',
                     resumo_erro(err)); continue
        cod, _, err = rodar(['./executar', caminho_teste('negativos', base + '.mplb')])
        if cod != 2:
            p.errado(f'execucao {base}', 'codigo de saida 2', f'codigo {cod}: {resumo_erro(err)}')
            continue
        m = re.search(r'erro (execucao): linha (\d+), coluna (\d+):', err)
        if not m:
            p.errado(f'execucao {base}', 'erro execucao: linha L, coluna C: ...',
                     resumo_erro(err) or '(stderr vazio)')
        elif m.group(2) != linha_e:
            p.errado(f'execucao {base}', f'linha {linha_e}', f'linha {m.group(2)}')
        else:
            p.certo(f'execucao {base}')

OPERADORES = ['==', '!=', '<=', '>=', '+', '-', '*', '/', '%', '<', '>']

def conta_operadores(linha):
    linha = re.sub(r'"(\\.|[^"\\])*"', '""', linha)          # tira os textos
    n = 0
    resto = linha
    for op in OPERADORES:
        n += resto.count(op)
        resto = resto.replace(op, ' ')
    n += len(re.findall(r'(?<![a-zA-Z_])(e|ou|nao)(?![a-zA-Z_])', resto))
    return n

def conferir_ir(p):
    """
    Tres enderecos de verdade: no maximo UM operador por linha.
    O formato do despejo e livre; o que se mede e essa propriedade — que e a
    definicao da representacao, nao um gosto de formatacao.
    """
    for prog in sorted(os.listdir(os.path.join(T, 'positivos'))):
        if not prog.endswith('.mpl'):
            continue
        base = prog[:-4]
        cod, saida, err = rodar(['./compilar', '--ir', caminho_teste('positivos', prog)])
        if cod != 0:
            p.errado(f'--ir de {base}', 'sair com codigo 0', f'codigo {cod}: {resumo_erro(err)}')
            continue
        if not saida.strip():
            p.errado(f'--ir de {base}', 'o codigo de tres enderecos', 'saida vazia')
            continue
        culpada = None
        for i, linha in enumerate(saida.split('\n'), 1):
            if conta_operadores(linha) > 1:
                culpada = (i, linha.strip())
                break
        if culpada:
            p.errado(f'--ir de {base}', 'no maximo um operador por linha',
                     f'linha {culpada[0]}: {culpada[1]!r}')
        else:
            p.certo(f'--ir de {base}')

def conferir_saida_limpa(p):
    """
    A saida nao pode comecar com BOM.

    Fim de linha NAO e problema: o verificador le a saida com traducao
    universal, entao CRLF vira \n sozinho e quem edita no Windows nao perde
    nada. O BOM e outra coisa — ele entra como caractere invisivel na PRIMEIRA
    linha e derruba a comparacao com um diff que nao explica nada.
    """
    progs = [x for x in sorted(os.listdir(os.path.join(T, 'positivos'))) if x.endswith('.mpl')]
    if not progs:
        return
    nome = 'a saida nao comeca com BOM'
    cod, saida, err = rodar(['./compilar', '--tokens', caminho_teste('positivos', progs[0])])
    if cod != 0:
        p.errado(nome, 'a lista de tokens', resumo_erro(err, cod))
    elif saida.startswith('\ufeff'):
        p.errado(nome, 'a saida comecando direto no primeiro token',
                 'ha um BOM (U+FEFF) antes do primeiro caractere — '
                 'grave os arquivos como "UTF-8 sem BOM"')
    else:
        p.certo(nome)


def conferir_tokens_sobrevivem_a_sintaxe(p):
    """
    --tokens tem que funcionar num programa com erro de SINTAXE: a fase lexica
    nao olha a sintaxe. Sem esta prova, passa um compilador que so despeja
    tokens depois de o parser aprovar tudo.
    """
    # qualquer programa com erro de sintaxe serve — o corpus escolhe, nao o nome
    sintaticos = sorted(x for x in os.listdir(os.path.join(T, 'negativos'))
                        if x.startswith('sin') and x.endswith('.mpl'))
    if not sintaticos:
        return
    alvo = caminho_teste('negativos', sintaticos[0])
    cod, saida, err = rodar(['./compilar', '--tokens', alvo])
    if cod != 0 or not saida.strip():
        p.errado('--tokens funciona apesar de erro de sintaxe',
                 'a lista de tokens, codigo 0', f'codigo {cod}: {resumo_erro(err)}')
    elif 'FIM_ARQUIVO' not in saida:
        p.errado('--tokens funciona apesar de erro de sintaxe',
                 'a lista terminando em FIM_ARQUIVO', 'nao veio FIM_ARQUIVO')
    else:
        p.certo('--tokens funciona apesar de erro de sintaxe')

# --------------------------------------------------------------- as entregas

def entrega1(p):
    exigir_executaveis(p)
    conferir_despejo(p, '--tokens', 'tokens')
    conferir_erros(p, 'lex', confere_coluna=True)
    conferir_tokens_sobrevivem_a_sintaxe(p)
    conferir_saida_limpa(p)

def entrega2(p):
    entrega1(p)
    conferir_despejo(p, '--ast', 'ast')
    conferir_erros(p, 'sin', confere_coluna=True)

def entrega3(p):
    entrega2(p)
    conferir_despejo(p, '--tabela', 'tabela')
    conferir_erros(p, 'sem', confere_coluna=False)
    conferir_positivos_compilam(p, '--tabela')

def entrega4(p):
    entrega3(p)
    conferir_ir(p)
    conferir_execucao(p)
    conferir_execucao_erros(p)

ENTREGAS = {1: entrega1, 2: entrega2, 3: entrega3, 4: entrega4}

def main(argv):
    if not argv or argv[0] not in ('1', '2', '3', '4', 'todas'):
        print(__doc__.strip()); return 1
    quais = [1, 2, 3, 4] if argv[0] == 'todas' else [int(argv[0])]
    geral = 0
    for n in quais:
        print(f'\n{AMARELO}══ Entrega {n} ══{ZERO}')
        p = Placar()
        ENTREGAS[n](p)
        total = p.ok + p.falhas
        esperando = sum(p.pendentes.values())
        if not p.falhas:
            print(f'{VERDE}Entrega {n}: {p.ok} de {total} passaram.{ZERO}')
            continue
        geral = 1
        quebrado = sum(p.quebras.values())
        if quebrado:
            print(f'{VERMELHO}Entrega {n}: {p.falhas} de {total} falharam '
                  f'({quebrado} porque o compilador quebrou).{ZERO}')
        elif esperando == p.falhas:
            # nada quebrado: so ainda nao escrito
            print(f'{AMARELO}Entrega {n}: {p.ok} de {total} provas passaram; '
                  f'{esperando} esperam codigo que ainda nao existe.{ZERO}')
        else:
            print(f'{VERMELHO}Entrega {n}: {p.falhas} de {total} falharam'
                  + (f' ({esperando} por falta de codigo).' if esperando else '.') + ZERO)
        if p.quebras:
            print(f'\n{VERMELHO}▸ O compilador quebrou{ZERO}')
            for causa, quantas in p.quebras.items():
                print(f'  {causa}')
                print(f'  {quantas} prova(s) morreram nessa mesma pedra — conserte-a primeiro.')
            print(f'  Para ver o erro inteiro, rode o compilador direto:')
            print(f'  {CINZA}./compilar --tokens testes/positivos/01-fatorial.mpl{ZERO}')
        if p.pendentes:
            print(f'\n{AMARELO}▸ Por onde comecar{ZERO}')
            for fase, quantas in p.pendentes.items():
                arquivo, leitura = onde_escrever(fase)
                print(f'  Falta escrever: {fase} — {quantas} prova(s) dependem dela.')
                if arquivo:
                    print(f'  Escreva em {VERDE}{arquivo}{ZERO}. Leia antes: {CINZA}{leitura}{ZERO}')
            print(f'  O enunciado completo esta em {CINZA}entregas/E{n}.md{ZERO}')
    return geral

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

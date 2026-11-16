"""Maquina virtual da MPL, com um registro de ativacao por chamada."""
import json
from mplc.erros import ErroMPL

MAX_FRAMES = 1000


def _inteiro(a, b):
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _resto(a, b): return a - _inteiro(a, b) * b


def _texto(v):
    if isinstance(v, bool): return 'verdadeiro' if v else 'falso'
    if isinstance(v, float): return f'{v:.6f}'
    return str(v)


def executar(texto_mplb, saida):
    linhas = [x for x in texto_mplb.splitlines() if x.strip()]
    if not linhas or linhas[0].strip() != 'MPLB 1': raise ErroMPL('execucao', 1, 1, 'arquivo mplb invalido')
    funcoes, atual = {}, None
    for n, linha in enumerate(linhas[1:], 2):
        try: obj = json.loads(linha)
        except json.JSONDecodeError as e: raise ErroMPL('execucao', n, 1, 'instrucao mplb invalida') from e
        if obj['op'] == 'func':
            atual = {'nome': obj['nome'], 'retorno': obj['retorno'], 'parametros': obj['parametros'], 'codigo': []}; funcoes[atual['nome']] = atual
        elif obj['op'] == 'end': atual = None
        elif atual is not None: atual['codigo'].append(obj)
    if 'principal' not in funcoes: raise ErroMPL('execucao', 1, 1, 'funcao principal ausente')
    for f in funcoes.values(): f['labels'] = {i['args'][0]: p for p, i in enumerate(f['codigo']) if i['op'] == 'label'}
    frames = [{'funcao': funcoes['principal'], 'ip': 0, 'pilha': [], 'locais': {}, 'linha_chamada': 1}]
    ultima_linha_chamada = 1
    while frames:
        if len(frames) > MAX_FRAMES: raise ErroMPL('execucao', ultima_linha_chamada, 1, 'estouro de pilha')
        frame, codigo = frames[-1], frames[-1]['funcao']['codigo']
        if frame['ip'] >= len(codigo):
            frames.pop()
            if frames: frames[-1]['pilha'].append(None)
            continue
        instr = codigo[frame['ip']]; frame['ip'] += 1
        op, args, linha = instr['op'], instr.get('args', []), instr.get('linha', 1); pilha = frame['pilha']
        if op == 'label': continue
        if op == 'const': pilha.append(args[0])
        elif op == 'load': pilha.append(frame['locais'].get(args[0]))
        elif op == 'store': frame['locais'][args[0]] = pilha.pop()
        elif op == 'cast_real': pilha.append(float(pilha.pop()))
        elif op == 'pop': pilha.pop()
        elif op == 'print': saida.write(_texto(pilha.pop()) + '\n')
        elif op == 'jump': frame['ip'] = frame['funcao']['labels'][args[0]]
        elif op == 'jump_false':
            if not pilha.pop(): frame['ip'] = frame['funcao']['labels'][args[0]]
        elif op == 'un':
            a = pilha.pop(); pilha.append(not a if args[0] == 'nao' else -a)
        elif op == 'bin':
            b, a = pilha.pop(), pilha.pop(); operador = args[0]
            if operador in {'/', '%'} and b == 0: raise ErroMPL('execucao', linha, 1, 'divisao por zero')
            if operador == '+': v = a + b
            elif operador == '-': v = a - b
            elif operador == '*': v = a * b
            elif operador == '/': v = _inteiro(a, b) if isinstance(a, int) and isinstance(b, int) else a / b
            elif operador == '%': v = _resto(a, b)
            elif operador == '==': v = a == b
            elif operador == '!=': v = a != b
            elif operador == '<': v = a < b
            elif operador == '<=': v = a <= b
            elif operador == '>': v = a > b
            elif operador == '>=': v = a >= b
            elif operador == 'e': v = bool(a and b)
            else: v = bool(a or b)
            pilha.append(v)
        elif op == 'call':
            nome, quantidade = args; chamada = funcoes.get(nome)
            if chamada is None: raise ErroMPL('execucao', linha, 1, f'funcao {nome} ausente')
            valores = [pilha.pop() for _ in range(quantidade)][::-1]
            ultima_linha_chamada = linha
            frames.append({'funcao': chamada, 'ip': 0, 'pilha': [], 'locais': dict(zip(chamada['parametros'], valores)), 'linha_chamada': linha})
        elif op == 'ret':
            valor = pilha.pop() if args[0] else None; frames.pop()
            if frames: frames[-1]['pilha'].append(valor)

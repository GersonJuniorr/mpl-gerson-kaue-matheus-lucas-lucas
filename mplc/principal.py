"""
A linha de comando do compilador. Ja vem pronta — nao precisa mexer.

Ela existe para que ninguem perca nota por causa do contrato: os codigos de
saida, o formato da mensagem de erro e os modos de despejo ja estao certos
aqui. Voces preenchem as fases; isto aqui costura.
"""
import sys

from mplc.erros import ErroMPL, NaoImplementado
from mplc import lexico, sintatico, semantica, intermediario, gerador, vm

MODOS = {'--tokens': 'tokens', '--ast': 'ast', '--tabela': 'tabela', '--ir': 'ir'}


def compilar_ate(fonte, ate):
    """Roda as fases ate a pedida e devolve as linhas para imprimir."""
    tokens = lexico.analisar(fonte)
    if ate == 'tokens':
        return [str(t) for t in tokens]

    arvore = sintatico.analisar(tokens)
    if ate == 'ast':
        return sintatico.despejar(arvore)

    tabela = semantica.analisar(arvore)
    if ate == 'tabela':
        return semantica.despejar(tabela)

    codigo = intermediario.gerar(arvore, tabela)
    if ate == 'ir':
        return intermediario.despejar(codigo)

    return gerador.gerar(codigo)


def main(argv):
    ate, rodar, arquivos = 'bytecode', False, []
    for a in argv:
        if a in MODOS:
            ate = MODOS[a]
        elif a == '--rodar':
            rodar = True
        else:
            arquivos.append(a)

    if len(arquivos) != 1:
        print('uso: ./compilar [--tokens|--ast|--tabela|--ir] programa.mpl', file=sys.stderr)
        print('     ./executar programa.mplb', file=sys.stderr)
        return 1

    caminho = arquivos[0]
    try:
        if rodar:
            with open(caminho, encoding='utf-8') as f:
                vm.executar(f.read(), sys.stdout)
            return 0

        with open(caminho, encoding='utf-8') as f:
            fonte = f.read()
        linhas = compilar_ate(fonte, ate)

        if ate == 'bytecode':
            destino = caminho[:-4] + '.mplb' if caminho.endswith('.mpl') else caminho + '.mplb'
            with open(destino, 'w', encoding='utf-8') as f:
                f.write('\n'.join(linhas) + '\n')
        else:
            print('\n'.join(linhas))
        return 0

    except ErroMPL as e:
        print(e, file=sys.stderr)
        return 2 if e.fase == 'execucao' else 1
    except NaoImplementado as e:
        print(f'ainda falta escrever: {e}', file=sys.stderr)
        return 3
    except FileNotFoundError:
        print(f'nao achei o arquivo {caminho}', file=sys.stderr)
        return 1
    except RecursionError:
        print('erro execucao: linha 1, coluna 1: estouro de pilha', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

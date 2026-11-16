"""Geracao do .mplb textual: uma instrucao JSON por linha."""
import json


def gerar(codigo_intermediario):
    linhas = ['MPLB 1']
    for funcao in codigo_intermediario['funcoes']:
        linhas.append(json.dumps({'op': 'func', 'nome': funcao['nome'], 'retorno': funcao['retorno'], 'parametros': funcao['parametros']}, ensure_ascii=False))
        for instrucao in funcao['codigo']:
            linhas.append(json.dumps(instrucao, ensure_ascii=False))
        linhas.append(json.dumps({'op': 'end'}, ensure_ascii=False))
    return linhas

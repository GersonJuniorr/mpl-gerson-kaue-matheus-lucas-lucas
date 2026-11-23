# Comandos da apresentação

Copiar e colar no terminal, na ordem. Tudo a partir da raiz do repositório.

## 0. Antes de começar (fora do tempo)

```
make verificar
```

Tem que terminar com `Entrega 4: 93 de 93 passaram`.

## 1. O programa rodando (30 s)

```
./compilar exemplos/relatorio.mpl && ./executar exemplos/relatorio.mplb
```

Saída esperada: `soma de 1 a 10`, `55`, `3.000000`.

## 2. A linha 13 pelas quatro fases (2 min)

Linha: `real divisao = 7 / 2;`

Tokens:

```
./compilar --tokens exemplos/relatorio.mpl | grep '^13,'
```

Árvore:

```
./compilar --ast exemplos/relatorio.mpl | grep -A3 'declaracao divisao'
```

Tabela de símbolos (procurar `divisao|variavel|real|13` no escopo 6):

```
./compilar --tabela exemplos/relatorio.mpl
```

Código intermediário (procurar `bin /` antes de `cast_real`):

```
./compilar --ir exemplos/relatorio.mpl | sed -n '/principal/,/fim/p'
```

## 3. O .mplb aberto (1 min)

Abrir `exemplos/relatorio.mplb` no editor, ou:

```
cat exemplos/relatorio.mplb
```

## 4. O defeito (1,5 min)

Sem comando. Sintoma: `real x = 7 / 2;` imprimia `3`. Diagnóstico: a VM
guardava o int num local real e o print formata pelo tipo do valor. Correção:
o IR emite `cast_real` no store, no argumento de call e no retorne.

## 5. Alteração ao vivo

Escrever um `teste.mpl` que use o recurso sorteado e rodar:

```
./compilar teste.mpl && ./executar teste.mplb
```

Conferir que o resto não quebrou:

```
make verificar
```

Se o sorteio for curto-circuito, o `07-logica` fica vermelho de propósito:
a especificação manda avaliar os dois lados (LINGUAGEM.md, linha 110).

## Depois

Desfazer a alteração e apagar os arquivos gerados:

```
git checkout -- mplc/ && make limpar && rm -f teste.mpl
```

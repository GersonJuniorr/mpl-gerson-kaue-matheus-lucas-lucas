# Contratos — o que o verificador exige

A [especificação da linguagem](LINGUAGEM.md) diz **o que** o compilador aceita.
Este arquivo diz **como** ele se comunica: a linha de comando e o formato dos
artefatos que cada fase despeja.

Por que isso existe: um compilador que só cospe o resultado final é uma caixa
preta — não dá para corrigir a fase, só o produto. Exigindo que cada fase
mostre o seu artefato, a Entrega 1 pode ser verificada sem que exista parser,
e vocês conseguem enxergar onde o próprio compilador errou.

É a memória de cálculo do compilador.

---

## 1. Linha de comando

Dois executáveis na raiz do repositório, com **exatamente** esses nomes:

```
./compilar   programa.mpl
./executar   programa.mplb
```

Podem ser script de shell, `.py` com shebang, ou um lançador que chama Java —
o verificador não olha para dentro. Só precisam ter permissão de execução
(`chmod +x`) e funcionar a partir da raiz do repositório.

`./compilar programa.mpl` grava `programa.mplb` ao lado do fonte e não imprime
nada em caso de sucesso.

Modos de despejo — cada um imprime na **saída padrão** e **não** grava arquivo:

| Comando | Entrega | O que imprime |
|---|---|---|
| `./compilar --tokens programa.mpl` | E1 | a lista de tokens |
| `./compilar --ast programa.mpl` | E2 | a árvore sintática |
| `./compilar --tabela programa.mpl` | E3 | a tabela de símbolos |
| `./compilar --ir programa.mpl` | E4 | o código de três endereços |

Cada modo executa as fases **até** a dele e para. `--tokens` num programa com
erro de sintaxe tem que funcionar: a sintaxe ainda não foi olhada.

---

## 2. Formato dos tokens (`--tokens`)

Uma linha por token, quatro campos separados por vírgula, sem espaços:

```
linha,coluna,TIPO,lexema
```

A coluna é a do **primeiro caractere** do token, contando a partir de 1.

Os `TIPO` possíveis, em maiúsculas:

```
INTEIRO  REAL  LOGICO  TEXTO          (literais)
ID                                    (identificador)
FUNCAO RETORNE SE SENAO ENQUANTO ESCREVA
TIPO_INTEIRO TIPO_REAL TIPO_LOGICO TIPO_TEXTO TIPO_VAZIO
E OU NAO
MAIS MENOS VEZES DIVIDE RESTO
IGUAL DIFERENTE MENOR MENOR_IGUAL MAIOR MAIOR_IGUAL
ATRIBUI
ABRE_PAR FECHA_PAR ABRE_CHAVE FECHA_CHAVE VIRGULA PONTO_VIRGULA
FIM_ARQUIVO
```

O `lexema` é o texto exato como apareceu no fonte. Para `TEXTO`, é o conteúdo
**com** as aspas e **com** os escapes ainda na forma original: o fonte
`"a\nb"` vira o lexema `"a\nb"`, cinco caracteres entre aspas.

A última linha é sempre o `FIM_ARQUIVO`, cujo lexema é vazio — a linha termina
em vírgula.

Exemplo. Para o fonte:

```mpl
funcao vazio principal() {
  escreva(1 + 2);
}
```

a saída é exatamente:

```
1,1,FUNCAO,funcao
1,8,TIPO_VAZIO,vazio
1,14,ID,principal
1,23,ABRE_PAR,(
1,24,FECHA_PAR,)
1,26,ABRE_CHAVE,{
2,3,ESCREVA,escreva
2,10,ABRE_PAR,(
2,11,INTEIRO,1
2,13,MAIS,+
2,15,INTEIRO,2
2,16,FECHA_PAR,)
2,17,PONTO_VIRGULA,;
3,1,FECHA_CHAVE,}
4,1,FIM_ARQUIVO,
```

---

## 3. Formato da árvore (`--ast`)

Um nó por linha. A profundidade é marcada por **dois espaços** por nível.
Sem parênteses, sem vírgulas.

Os nós e seus filhos, na ordem:

| Nó | Escrito como | Filhos, em ordem |
|---|---|---|
| programa | `programa` | as funções, na ordem do arquivo |
| função | `funcao <nome> <tipo>` | `parametros`, depois `bloco` |
| lista de parâmetros | `parametros` | zero ou mais `parametro` |
| parâmetro | `parametro <nome> <tipo>` | nenhum |
| bloco | `bloco` | os comandos |
| declaração | `declaracao <nome> <tipo>` | a expressão inicial, se houver |
| atribuição | `atribuicao <nome>` | a expressão |
| condicional | `se` | condição, bloco do então, bloco do senão (se houver) |
| repetição | `enquanto` | condição, bloco |
| escrita | `escreva` | a expressão |
| retorno | `retorne` | a expressão, se houver |
| chamada | `chamada <nome>` | os argumentos, na ordem |
| binário | `binario <op>` | esquerda, direita |
| unário | `unario <op>` | o operando |
| literal | `literal <tipo> <valor>` | nenhum |
| variável | `variavel <nome>` | nenhum |

O `<op>` é o próprio símbolo: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `<=`,
`>`, `>=`, `e`, `ou`, `nao`. O `-` unário é escrito `unario -`.

No `se` com `senao`, o terceiro filho é o bloco do `senao`. Sem `senao`, há
só dois filhos.

No `literal`, o `<valor>` sai assim: `inteiro` em dígitos; `real` com seis
casas decimais; `logico` como `verdadeiro`/`falso`; `texto` entre aspas, com
os escapes na forma original.

Exemplo. Para `escreva(1 + 2 * 3);` dentro do `principal`:

```
programa
  funcao principal vazio
    parametros
    bloco
      escreva
        binario +
          literal inteiro 1
          binario *
            literal inteiro 2
            literal inteiro 3
```

Repare que a árvore **prova** a precedência. Se o seu parser devolver o `*`
por cima do `+`, a diferença aparece aqui — e é exatamente esse o teste.

---

## 4. Formato da tabela de símbolos (`--tabela`)

Um cabeçalho por escopo, e os símbolos dele indentados com dois espaços.

O escopo 0 é o global, e contém só funções. Os demais são numerados na ordem
em que **abrem**, percorrendo o programa de cima para baixo e entrando nos
blocos.

```
escopo 0 global
  <nome>|funcao|<tipo de retorno>(<tipos dos parametros>)|<linha>
escopo <n> <descricao> pai <p>
  <nome>|parametro|<tipo>|<linha>
  <nome>|variavel|<tipo>|<linha>
```

A `<descricao>` do escopo é `funcao <nome>` para o corpo de uma função, e
`bloco` para qualquer outro. A lista de tipos dos parâmetros vem separada por
vírgula, sem espaço; sem parâmetros, fica `()`.

Os símbolos saem na ordem de declaração. Um escopo sem símbolos aparece com
o cabeçalho e nenhuma linha abaixo.

Repare que o corpo de uma função abre **dois** escopos: o da função, que
guarda os parâmetros, e o do bloco, que guarda as variáveis locais. Cada `se`
e cada `enquanto` abre mais um, mesmo que fique vazio.

Exemplo. Para este programa:

```mpl
funcao inteiro dobro(inteiro n) {
  retorne n * 2;
}

funcao vazio principal() {
  inteiro x = dobro(21);
  escreva(x);
}
```

a saída é exatamente:

```
escopo 0 global
  dobro|funcao|inteiro(inteiro)|1
  principal|funcao|vazio()|5
escopo 1 funcao dobro pai 0
  n|parametro|inteiro|1
escopo 2 bloco pai 1
escopo 3 funcao principal pai 0
escopo 4 bloco pai 3
  x|variavel|inteiro|6
```

---

## 5. Formato do código intermediário (`--ir`)

Código de três endereços, em texto. Ao contrário dos três formatos acima,
este **não** é comparado linha a linha com um gabarito — porque existe mais
de uma tradução correta. O verificador confere três propriedades:

1. **Três endereços de verdade:** cada linha de operação tem **no máximo um
   operador**. `t2 = t0 + t1` passa; `t2 = a + b * c` não passa. Essa é a
   propriedade que define a representação, e é ela que o verificador mede.
2. Todo destino de desvio existe como rótulo.
3. Toda função declarada no fonte aparece no código intermediário.

O esqueleto abaixo é uma sugestão, não uma exigência:

```
funcao fatorial inteiro (n inteiro)
  t0 = n <= 1
  seFalso t0 desvie L0
  retorne 1
L0:
  t1 = n - 1
  t2 = chama fatorial t1
  t3 = n * t2
  retorne t3
fim
```

---

## 6. O arquivo executável (`.mplb`)

O formato é **de vocês**, com uma exigência: tem que ser **texto legível**,
não binário. Numa auditoria — ou na apresentação — a gente abre o `.mplb` e
lê o que o compilador gerou. Um formato que só a sua VM entende, mas que uma
pessoa consegue ler, está perfeito.

`./executar programa.mplb` roda e imprime na saída padrão o que os comandos
`escreva` produzirem, na forma exata da seção 4.5 da especificação.

---

## 6.1 Codificação da saída

Três regras, e uma delas é uma tolerância:

- A saída é **UTF-8**, **sem BOM**. O BOM entra como um caractere invisível
  antes do primeiro token e derruba a comparação com um erro que não explica
  nada — por isso existe uma prova só para ele. No editor, gravem como
  "UTF-8 sem BOM".
- **O fim de linha não importa.** O verificador lê a saída com tradução
  universal: `\r\n` vira `\n` sozinho. Quem edita no Windows não perde nada
  por isso. (Confirmado rodando um compilador que emite CRLF: passa nas 20
  provas da Entrega 1.)
- A comparação é byte a byte **depois** dessa normalização de fim de linha.

## 7. Erros

Formato, fases e códigos de saída: seção 6 da [especificação](LINGUAGEM.md).

O verificador **nunca** confere o texto da mensagem. O que ele confere muda
conforme a fase, e a razão é simples: em algumas fases a posição do erro é
única, e em outras existe mais de uma resposta defensável.

| Fase | O que é conferido | Onde a posição é ancorada |
|---|---|---|
| `lexico` | fase, linha **e coluna** | o caractere que estragou o token |
| `sintatico` | fase, linha **e coluna** | o **token que apareceu** no lugar do esperado |
| `semantico` | fase e linha | — |
| `execucao` | fase e linha | — |

Nas duas primeiras fases a posição é objetiva, então ela é cobrada. Nas duas
últimas não é: em `inteiro x = "texto";` dá para apontar a declaração ou o
literal, e as duas escolhas são razoáveis — cobrar a minha seria cobrar
gosto, não correção. Por isso ali vale a linha. Os programas do corpus são
escritos com um comando por linha, para que a linha nunca seja ambígua.

Duas convenções que valem a pena escrever, porque quase todo mundo tropeça:

- A coluna do primeiro caractere de uma linha é **1**, não 0. Errar por um é
  o defeito mais comum desta disciplina.
- O erro sintático fica no token **errado**, não no fim do token anterior.
  Faltando o `;` no fim da linha 2, o erro é relatado no primeiro token da
  linha 3 — que é onde o parser percebeu o problema.
- O `FIM_ARQUIVO` fica na linha seguinte à última e na coluna 1 quando o
  arquivo termina com quebra de linha; se não terminar, fica logo depois do
  último caractere.
- O erro de execução é relatado na linha do **comando** que estava rodando.

# MPL — Minha Pequena Linguagem

Especificação da linguagem que o compilador de vocês tem que aceitar.
Este documento é a **fonte da verdade**: quando o verificador e a sua intuição
discordarem, é este arquivo que vale.

Arquivo-fonte: extensão `.mpl`, codificação UTF-8.

---

## 1. Estrutura de um programa

Um programa é uma sequência de funções. Uma delas, obrigatoriamente, se chama
`principal`, não recebe parâmetros e devolve `vazio`. A execução começa por ela.

```mpl
funcao vazio principal() {
  escreva("oi");
}
```

Não existe código fora de função. Não existe variável global.

---

## 2. Léxico

### 2.1 Palavras reservadas

```
funcao   retorne   se   senao   enquanto   escreva
inteiro  real      logico  texto  vazio
verdadeiro  falso  e  ou  nao
```

Palavra reservada **não** pode ser usada como nome de variável ou de função.

### 2.2 Identificadores

Começa por letra (`a-z`, `A-Z`) ou `_`, seguido de letras, dígitos ou `_`.
Sensível a maiúsculas: `soma` e `Soma` são nomes diferentes.

### 2.3 Literais

| Tipo | Forma | Exemplos |
|---|---|---|
| `inteiro` | um ou mais dígitos | `0`, `42`, `1000` |
| `real` | dígitos, ponto, dígitos — **obrigatório dos dois lados** | `3.14`, `0.5`, `10.0` |
| `logico` | `verdadeiro` ou `falso` | |
| `texto` | entre aspas duplas, numa linha só | `"oi"`, `"linha\n"` |

Escapes aceitos dentro de `texto`: `\n`, `\t`, `\"`, `\\`. Qualquer outro
escape é **erro léxico**.

`3.` e `.5` são erro léxico. O ponto exige dígito dos dois lados.

### 2.4 Operadores e delimitadores

```
+  -  *  /  %
==  !=  <  <=  >  >=
=
(  )  {  }  ,  ;
```

`e`, `ou` e `nao` são operadores lógicos escritos como palavra.

### 2.5 Comentários

`// até o fim da linha` e `/* de bloco, podendo atravessar linhas */`.
Comentário de bloco **não** aninha: o primeiro `*/` fecha.
Comentário de bloco aberto e não fechado é erro léxico, apontando a linha
onde ele **começou**.

### 2.6 Espaços

Espaço, tabulação, `\r` e `\n` separam tokens e não geram token.

---

## 3. Tipos

Quatro tipos: `inteiro`, `real`, `logico`, `texto`. Mais o tipo `vazio`,
que só aparece como retorno de função.

### 3.1 Regra de conversão

Existe **uma única** conversão implícita: `inteiro` vira `real` quando o
contexto exige `real`. Vale na atribuição, no argumento de chamada, no
retorno e nos dois lados de um operador aritmético ou relacional.

Nenhuma outra conversão existe. `real` não vira `inteiro`. `logico` não vira
número. Número não vira `texto`.

### 3.2 Operadores e seus tipos

| Operador | Operandos aceitos | Resultado |
|---|---|---|
| `+` | `inteiro`/`real` (ou os dois `texto`) | numérico, ou `texto` |
| `-` `*` `/` | `inteiro`/`real` | `inteiro` se os dois forem `inteiro`, senão `real` |
| `%` | só `inteiro` e `inteiro` | `inteiro` |
| `==` `!=` | dois do mesmo tipo (com a conversão de 3.1) | `logico` |
| `<` `<=` `>` `>=` | `inteiro`/`real` | `logico` |
| `e` `ou` | `logico` e `logico` | `logico` |
| `nao` | `logico` | `logico` |
| `-` unário | `inteiro`/`real` | mesmo tipo |

`+` com um `texto` e um número é **erro de tipo**, não concatenação.

`e` e `ou` avaliam **os dois lados, sempre**. Não há curto-circuito: em
`falso e f()`, a função `f` é chamada do mesmo jeito. É uma simplificação
deliberada, para que todos os grupos produzam a mesma saída — curto-circuito
é um dos bônus previstos na apresentação.

`/` entre dois `inteiro` é divisão inteira truncada em direção a zero:
`7 / 2` é `3`, `-7 / 2` é `-3`.

`%` tem o sinal do dividendo: `-7 % 2` é `-1`.

Divisão ou resto por zero é **erro de execução**, não de compilação.

### 3.3 Precedência, da mais fraca para a mais forte

```
1.  ou
2.  e
3.  ==  !=
4.  <  <=  >  >=
5.  +  -
6.  *  /  %
7.  nao   - (unário)
8.  chamada de função,  ( )
```

Todos os binários são associativos à esquerda. `nao` e o `-` unário são
associativos à direita. `a - b - c` é `(a - b) - c`.

---

## 4. Comandos

### 4.1 Declaração

```mpl
inteiro x;
inteiro y = 10;
real taxa = 2.5;
```

Declarar sem inicializar dá o valor padrão do tipo: `0`, `0.0`, `falso`, `""`.

Declarar duas vezes o mesmo nome **no mesmo escopo** é erro semântico.

### 4.2 Atribuição

```mpl
x = 3 + 4;
```

A variável precisa ter sido declarada antes, no escopo atual ou num escopo
que o contenha. O tipo do lado direito tem que caber no da variável (3.1).

### 4.3 Condicional

```mpl
se (x > 0) {
  escreva("positivo");
} senao {
  escreva("nao positivo");
}
```

O `senao` é opcional. A condição tem que ser `logico` — `se (x)` com `x`
inteiro é erro de tipo. As chaves são **obrigatórias**, inclusive para um
comando só.

### 4.4 Repetição

```mpl
enquanto (i < 10) {
  i = i + 1;
}
```

Mesmas regras da condição do `se`. Não existe `para`, `pare` nem `continue`.

### 4.5 Escrita

```mpl
escreva(expressao);
```

Aceita qualquer tipo, menos `vazio`. Imprime o valor seguido de uma quebra
de linha. A forma impressa de cada tipo:

| Tipo | Como sai |
|---|---|
| `inteiro` | dígitos, com `-` se negativo: `42`, `-7` |
| `real` | sempre com casa decimal, **6 casas**: `3.140000`, `-0.500000` |
| `logico` | `verdadeiro` ou `falso` |
| `texto` | o conteúdo, sem as aspas |

Essa tabela é literal. O verificador compara a saída byte a byte.

### 4.6 Retorno

```mpl
retorne;          // só em funcao vazio
retorne expr;     // nas demais
```

Toda função de retorno não-`vazio` precisa garantir o retorno em **todos**
os caminhos. `funcao inteiro f() { se (x > 0) { retorne 1; } }` é erro
semântico: falta o caminho do `senao`.

### 4.7 Bloco

`{ ... }` cria um escopo novo. Uma variável declarada dentro dele some ao
fechar, e pode ter o mesmo nome de uma de fora — a de dentro esconde a de
fora enquanto durar.

---

## 5. Funções

```mpl
funcao inteiro fatorial(inteiro n) {
  se (n <= 1) {
    retorne 1;
  }
  retorne n * fatorial(n - 1);
}
```

- O tipo de retorno vem antes do nome.
- Zero ou mais parâmetros, cada um com tipo.
- **Recursão é obrigatória de funcionar**, direta e indireta.
- Chamada exige a quantidade certa de argumentos, e cada argumento tem que
  caber no tipo do parâmetro (3.1).
- Chamada de função `vazio` só pode aparecer como comando, nunca dentro de
  uma expressão.
- Uma função pode ser chamada antes de aparecer no arquivo.
- Dois nomes iguais de função é erro semântico. Não existe sobrecarga.

Parâmetros são passados **por valor**.

---

## 6. Erros

Toda mensagem de erro sai na **saída de erro** (`stderr`), numa linha só,
neste formato exato:

```
erro <fase>: linha <L>, coluna <C>: <mensagem livre>
```

Onde `<fase>` é uma de: `lexico`, `sintatico`, `semantico`, `execucao`.

A coluna do primeiro caractere de uma linha é **1**, não 0.

O compilador para no **primeiro** erro. Recuperação de erro é bônus, e se
vocês implementarem, o primeiro erro relatado tem que continuar sendo o
mesmo.

Códigos de saída:

| Código | Quando |
|---|---|
| 0 | tudo certo |
| 1 | erro de compilação (léxico, sintático ou semântico) |
| 2 | erro de execução (divisão por zero, estouro de pilha) |

O texto da `<mensagem livre>` é de vocês. O verificador confere a fase, a
linha e a coluna — não o texto. Mas escreva mensagens boas: parte da nota
da apresentação é mostrar o compilador errando com elegância.

---

## 7. O que **não** existe na MPL

Para não restar dúvida sobre o escopo: não há vetores, `para`, `pare`,
`leia`, registros, ponteiros, classes, importação de arquivo, sobrecarga,
parâmetro por referência nem variável global.

Vários desses são bônus previstos na apresentação. Nenhum deles é cobrado
nas entregas.

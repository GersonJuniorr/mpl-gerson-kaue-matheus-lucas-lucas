# Minha pequena linguagem

Trabalho semestral de **Compiladores** — Ciência da Computação, UNISAGRADO.
Prof. Luiz Ricardo Mantovani da Silva · 2026-2

## Integrantes

- Gerson de Oliveira Lopes Junior
- Kauê Kanagusko Ruiz
- Matheus de Amorim Favero
- Lucas Antonio Pires de Souza
- Lucas Souza dos Santos

Cada grupo escreve um **compilador completo** para a MPL, uma linguagem
pequena de palavras-chave em português. O compilador de vocês vai ler um
programa em `.mpl`, atravessar as quatro fases da disciplina e produzir um
arquivo que **roda de verdade** numa máquina virtual que vocês também vão
escrever.

No fim do semestre vocês executam um programa escrito por vocês, numa
linguagem compilada por vocês.

---

## Comece por aqui

```bash
git clone https://github.com/LuizRMSilva1973/compiladores-lab.git
cd compiladores-lab
```

```bash
make verificar E=1
```

Vai dar vermelho — é para dar. O esqueleto responde à linha de comando mas
ainda não tem nenhuma fase escrita. O vermelho é o seu ponto de partida, e
ele vai virando verde conforme vocês preenchem `mplc/`.

Não precisa instalar nada além do Python 3. Se o notebook de vocês der
trabalho, o [Google Cloud Shell](https://shell.cloud.google.com) já vem com
Python 3.12, Java 21 e git — e é o mesmo ambiente da correção.

---

## Os três documentos que mandam

| Arquivo | O que decide |
|---|---|
| [LINGUAGEM.md](LINGUAGEM.md) | **o que** o compilador aceita: a sintaxe e as regras de tipo da MPL |
| [CONTRATOS.md](CONTRATOS.md) | **como** ele se comunica: a linha de comando e o formato de cada despejo |
| [entregas/](entregas/) | o enunciado de cada entrega, com o que vale nota |

Quando a sua intuição discordar de um deles, é o arquivo que vale. Se o
arquivo estiver errado, me procurem — já aconteceu de eu escrever um exemplo
errado no contrato e só descobrir rodando.

---

## As entregas

| # | Entrega | Turma A (quarta) | Turma B (segunda) | Vale |
|---|---|---|---|---|
| [E1](entregas/E1.md) | Analisador léxico | 02/09 | 31/08 | 0,8 |
| [E2](entregas/E2.md) | Analisador sintático e árvore | 30/09 | 28/09 | 1,2 |
| [E3](entregas/E3.md) | Tabela de símbolos e tipos | 28/10 | 26/10 | 1,2 |
| [E4](entregas/E4.md) | Código intermediário, geração e VM | 18/11 | 16/11 | 1,8 |
| [Apres.](entregas/APRESENTACAO.md) | Demonstração e defesa | 25/11 | 23/11 | 1,0 |

São **quatro entregas sobre o mesmo compilador**, não quatro trabalhos. O que
vocês escreverem na E1 continua rodando na E4 — e o verificador da E4 confere
tudo o que veio antes. Deixar a E1 pela metade custa caro em novembro.

---

## Regras do jogo

**A entrega é o repositório, nunca a máquina de vocês.** A correção clona o
repositório numa máquina limpa e roda `make verificar E=n`. Se não passar
lá, não conta como entregue. Testem antes de entregar — de preferência na
Cloud Shell, que é o ambiente da correção.

**Grupos de até 3.** O mesmo grupo do começo ao fim. Mudança de grupo só até
a E1.

**Gerador de parser proibido nas Entregas 1 e 2.** ANTLR, PLY, yacc, lark e
parentes escondem exatamente a parte que está sendo ensinada. Da E3 em diante
o assunto é outro, e aí não faz diferença. Na apresentação vocês podem — e
devem — comparar o parser de vocês com o que um gerador produziria.

**A linguagem de implementação é de vocês, entre as que o ambiente da correção
já tem:** Python 3.12, Java 21, C e C++ (gcc 13), Ruby 3.2 ou PHP 8.3. O
verificador não olha para dentro — ele roda `./compilar` e `./executar` e
compara o que sai. O esqueleto em `mplc/` é Python porque é o caminho mais
curto, mas ninguém é obrigado a usá-lo.

A lista existe por um motivo prático: a correção roda numa Cloud Shell limpa, e
o que não estiver lá não roda. Querem outra linguagem? Falem comigo **antes** de
começar — o critério é ela existir no ambiente sem instalação. Em nenhum caso
dependam de biblioteca externa: só a biblioteca padrão.

**Escrever o compilador é a tarefa.** Usar IA para explicar um conceito,
revisar uma mensagem de erro ou entender um trecho é bem-vindo, e eu faço
isso também. Entregar um compilador que vocês não sabem alterar é outra
coisa — e a apresentação foi desenhada para separar os dois casos: cada grupo
recebe **uma alteração pequena na linguagem, na hora, com 10 minutos para
fazer**. Quem escreveu o compilador faz. Não é desconfiança; é o formato.

---

## O verificador

```bash
make verificar E=2      # confere a Entrega 2 e, junto, a 1
make verificar          # confere as quatro
make evidencias E=2     # grava evidencias/verificacao-2.txt, que vai na entrega
```

**Antes de entregar, rodem `make prova`.** Ele clona o repositório de vocês num
diretório limpo e verifica lá — que é exatamente o que a correção faz. É o
teste que pega o defeito mais comum de todos, e que não tem nada a ver com
compiladores: *funciona aqui e não no clone*. Arquivo esquecido fora do commit,
caminho absoluto, passo de compilação que ninguém roda. Vale para qualquer
linguagem, e é a única prova que realmente antecipa a correção.

Ele não lê o código de vocês. Ele roda o compilador e compara a saída com um
corpus de **10 programas válidos**, **26 programas que precisam ser
recusados na compilação** e **3 que precisam falhar na execução** — com a
fase e a linha do erro conferidas.

Os programas recusados são metade da nota escondida do trabalho. Um
compilador que aceita tudo passa em todos os testes positivos e não vale
nada: é por isso que o corpus tem mais programas errados do que certos.

**A correção usa um segundo corpus, que vocês não têm.** Mesma linguagem,
mesmas regras, programas diferentes. Um compilador de verdade passa nos dois
sem que vocês precisem fazer nada; um programa que apenas reproduza as saídas
esperadas deste corpus passa aqui e reprova lá. Estou dizendo isto abertamente
para ninguém perder tempo pelo caminho errado.

---

## Tabela de tokens (Entrega 1)

Reconhecidos por `mplc/lexico.py`. `[0-9]` é dígito, `[A-Za-z_]` é letra ou
`_`, `[A-Za-z0-9_]` é letra, dígito ou `_`.

### Palavras reservadas

Reconhecidas como `ID` pelo mesmo autômato dos identificadores; se o lexema
bate com a tabela abaixo, o tipo troca de `ID` para o da palavra.

| Lexema | TIPO |
|---|---|
| `funcao` | `FUNCAO` |
| `retorne` | `RETORNE` |
| `se` | `SE` |
| `senao` | `SENAO` |
| `enquanto` | `ENQUANTO` |
| `escreva` | `ESCREVA` |
| `inteiro` | `TIPO_INTEIRO` |
| `real` | `TIPO_REAL` |
| `logico` | `TIPO_LOGICO` |
| `texto` | `TIPO_TEXTO` |
| `vazio` | `TIPO_VAZIO` |
| `verdadeiro`, `falso` | `LOGICO` |
| `e`, `ou`, `nao` | `E`, `OU`, `NAO` |

### Identificadores e literais

| TIPO | Expressão regular | Observações |
|---|---|---|
| `ID` | `[A-Za-z_][A-Za-z0-9_]*` | só se o lexema **não** for palavra reservada |
| `INTEIRO` | `[0-9]+` | |
| `REAL` | `[0-9]+\.[0-9]+` | dígito obrigatório dos dois lados do `.`; `3.` e `.5` são erro léxico |
| `LOGICO` | `verdadeiro\|falso` | tratado como palavra reservada acima |
| `TEXTO` | `"([^"\\\n]\|\\[nt"\\])*"` | entre aspas, numa linha só; escapes aceitos: `\n` `\t` `\"` `\\` |

### Operadores e delimitadores

Autômato: primeiro tenta casar dois caracteres; só cai para um caractere se
os dois não formarem um símbolo válido. É a ordem que resolve a armadilha de
`<=`/`<`, `==`/`=`, `!=`/`!`, `>=`/`>`.

| Lexema | TIPO |
|---|---|
| `+` | `MAIS` |
| `-` | `MENOS` |
| `*` | `VEZES` |
| `/` | `DIVIDE` |
| `%` | `RESTO` |
| `==` | `IGUAL` |
| `!=` | `DIFERENTE` |
| `<` | `MENOR` |
| `<=` | `MENOR_IGUAL` |
| `>` | `MAIOR` |
| `>=` | `MAIOR_IGUAL` |
| `=` | `ATRIBUI` |
| `(` | `ABRE_PAR` |
| `)` | `FECHA_PAR` |
| `{` | `ABRE_CHAVE` |
| `}` | `FECHA_CHAVE` |
| `,` | `VIRGULA` |
| `;` | `PONTO_VIRGULA` |

### Comentários e espaços (não geram token)

| Forma | Expressão regular |
|---|---|
| comentário de linha | `//[^\n]*` |
| comentário de bloco | `/\*.*?\*/` (não aninha; o primeiro `*/` fecha; se não fechar, erro léxico na linha onde abriu) |
| espaços | `[ \t\r\n]+` |

Fim de arquivo gera sempre um `FIM_ARQUIVO` com lexema vazio, na posição
descrita em `CONTRATOS.md`, seção 7.

---

## Como entregar

1. `git push` no repositório do grupo.
2. Abram a [página do trabalho](https://profluiz.mantovanitec.com/disciplinas/aulas/compiladores/trabalho.html).
3. No formulário do fim da página: escolham a entrega, identifiquem os
   integrantes (nome, RA e e-mail), colem a URL do repositório e anexem o
   `evidencias/verificacao-N.txt`.
4. Cada integrante recebe uma cópia por e-mail. **Guardem esse e-mail**: é o
   comprovante.

# Apresentação — demonstração e defesa

**Vale 1,0** · **Turma A: 25/11** · **Turma B: 23/11** · em aula

Oito minutos por grupo: **cinco de apresentação e três de alteração ao vivo**.

---

## Os cinco minutos de apresentação

Quatro coisas, nessa ordem:

1. **O programa de vocês rodando.** Comece pelo fim: o programa MPL que o
   grupo escreveu, compilado e executado na hora. Trinta segundos.
2. **Uma expressão atravessando as quatro fases.** Escolham uma linha do
   programa — algo como `x = a + b * 2;` — e mostrem os tokens, o pedaço da
   árvore, o que a tabela de símbolos sabe sobre ela, o código de três
   endereços e as instruções da VM. É a espinha da disciplina inteira numa
   linha só.
3. **O `.mplb` aberto.** A gente lê junto um trecho do que o compilador de
   vocês gerou. É por isso que o contrato exige texto legível.
4. **O defeito mais difícil que vocês enfrentaram.** Sintoma, diagnóstico,
   correção. Essa parte vale tanto quanto as outras — provavelmente é onde
   vocês mais aprenderam.

## Os três minutos de alteração ao vivo

Cada grupo recebe **uma alteração pequena na linguagem**, sorteada na hora, e
tem dez minutos para fazê-la funcionar — os três minutos são para mostrar o
resultado. Exemplos do tipo de coisa que pode cair:

- aceitar o operador `**` de potência, com a precedência certa;
- aceitar `senaose` encadeado;
- fazer `escreva` aceitar dois argumentos separados por vírgula;
- acrescentar o comando `pare` dentro do `enquanto`;
- fazer `e` e `ou` avaliarem em curto-circuito.

Todas as alterações mexem em pelo menos duas fases, e todas são de tamanho
parecido. **Podem consultar o código de vocês, a internet e o que quiserem** —
o que não dá para consultar é o entendimento de onde mexer.

Se a alteração não ficar pronta em dez minutos, mostrem até onde chegaram e
expliquem o que faltava. Grupo que sabe dizer exatamente onde mexeria perde
pouco. Grupo que não sabe por onde começar é outro assunto.

## Como entregar

1. Slides em PDF, no espaço da apresentação, **até as 23h59 do dia anterior**.
   Nome do arquivo: `apresentacao-grupo-NN.pdf`.
2. O repositório com a Entrega 4 completa. Só apresenta quem entregou.
3. O ambiente **pronto para rodar** na hora — testado antes, no computador que
   vocês vão usar.

## Como é avaliado

| | |
|---|---|
| A demonstração funciona e a expressão é rastreada pelas quatro fases | 0,4 |
| A alteração ao vivo | 0,3 |
| O defeito contado com honestidade — sintoma, diagnóstico, correção | 0,2 |
| Todos os integrantes falam, e o tempo é respeitado | 0,1 |

Uma observação sobre honestidade, que vale para o trabalho inteiro: dizer "essa
parte não ficou pronta, e o que faltava era isto" custa menos do que esconder.
Compilador com limitação declarada é um compilador que vocês entenderam.

#!/bin/sh
# Autoteste do verificador.
#
# Nao confere o compilador de voces. Confere o VERIFICADOR: constroi
# compiladores sabotados de proposito e exige que cada um fique VERMELHO.
#
# Um verificador que so sabe ficar verde nao esta verificando nada. Ja
# aconteceu comigo, num outro laboratorio: dez provas verdes com quatro
# entregas quebradas, porque as provas conferiam as pecas e nao o
# comportamento. Este arquivo existe para isso nao se repetir aqui.
#
# Rode quando quiser ter certeza de que um verde seu vale alguma coisa.

set -u
RAIZ=$(cd "$(dirname "$0")" && pwd)
REF="${MPL_REFERENCIA:-$HOME/projetos/compiladores-lab-gabarito/referencia.py}"
VERDE='\033[32m'; VERMELHO='\033[31m'; ZERO='\033[0m'
falhas=0

if [ ! -f "$REF" ]; then
  echo "Este autoteste precisa da implementacao de referencia, que fica com o"
  echo "professor. Voces nao precisam dele: rodem 'make verificar E=n'."
  exit 3
fi

banca=$(mktemp -d)
trap 'rm -rf "$banca"' EXIT
cp "$RAIZ/verificar.py" "$banca/"
cp -r "$RAIZ/testes" "$banca/"

# monta um par compilar/executar a partir de uma copia (talvez sabotada) da referencia
montar() {
  cp "$REF" "$banca/motor.py"
  [ -n "${2:-}" ] && python3 - "$banca/motor.py" "$2" "$3" <<'PY'
import sys
caminho, antes, depois = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(caminho, encoding='utf-8').read()
if antes not in s:
    print(f'SABOTAGEM FALHOU: nao achei {antes!r}', file=sys.stderr); sys.exit(9)
open(caminho, 'w', encoding='utf-8').write(s.replace(antes, depois, 1))
PY
  [ $? -eq 9 ] && return 9
  printf '#!/bin/sh\nexec python3 "%s/motor.py" "$@"\n' "$banca" > "$banca/compilar"
  printf '#!/bin/sh\nexec python3 "%s/motor.py" --rodar "$@"\n' "$banca" > "$banca/executar"
  chmod +x "$banca/compilar" "$banca/executar"
  return 0
}

# exige VERMELHO
exigir_vermelho() {
  nome="$1"; entrega="$2"
  if (cd "$banca" && python3 verificar.py "$entrega" >/dev/null 2>&1); then
    printf "  ${VERMELHO}CEGO${ZERO}  %s — o verificador passou mesmo assim\n" "$nome"
    falhas=$((falhas + 1))
  else
    printf "  ${VERDE}pega${ZERO}  %s\n" "$nome"
  fi
}

echo "── controle positivo: a referencia intacta"
montar intacta
if (cd "$banca" && python3 verificar.py todas >/dev/null 2>&1); then
  printf "  ${VERDE}ok${ZERO}    a referencia passa nas quatro entregas\n"
else
  printf "  ${VERMELHO}FALHA${ZERO} a referencia NAO passa — o verificador esta exigindo o impossivel\n"
  falhas=$((falhas + 1))
fi

echo "── sabotagens: cada uma tem que ser pega"

printf '#!/bin/sh\nexit 0\n' > "$banca/compilar"
printf '#!/bin/sh\nexit 0\n' > "$banca/executar"
chmod +x "$banca/compilar" "$banca/executar"
exigir_vermelho "compilador que nao faz nada e diz que deu certo" 1

montar s2 "return pos - inicio_linha + 1" "return pos - inicio_linha" \
  && exigir_vermelho "colunas contadas a partir de zero" 1

# a sabotagem TROCA os dois niveis, mantendo todos os operadores parseaveis.
# Apagar um operador tambem deixaria o verificador vermelho — mas por erro de
# sintaxe, e ai a prova nao seria sobre precedencia nenhuma.
montar s3 "    def nivel_aditivo(self):
        return self.bin_esq(self.nivel_multiplicativo, {'MAIS': '+', 'MENOS': '-'})
    def nivel_multiplicativo(self):
        return self.bin_esq(self.nivel_unario, {'VEZES': '*', 'DIVIDE': '/', 'RESTO': '%'})" \
          "    def nivel_aditivo(self):
        return self.bin_esq(self.nivel_multiplicativo, {'VEZES': '*', 'DIVIDE': '/', 'RESTO': '%'})
    def nivel_multiplicativo(self):
        return self.bin_esq(self.nivel_unario, {'MAIS': '+', 'MENOS': '-'})" \
  && exigir_vermelho "precedencia invertida entre + e * (1+2*3 vira 9)" 2

montar s4 "def cabe(destino, origem):" "def cabe(destino, origem):
    return True" \
  && exigir_vermelho "verificacao de tipos desligada (aceita tudo)" 3

montar s5 "nome = 'DIV_I' if d.tipo == 'inteiro' else 'DIV_R'" "nome = 'DIV_R'" \
  && exigir_vermelho "divisao inteira virando divisao real" 4

montar s6 "linhas.append(f'  {ins[1]} = {ins[3]} {ins[2]} {ins[4]}')" \
          "linhas.append(f'  {ins[1]} = {ins[3]} {ins[2]} {ins[4]} {ins[2]} {ins[4]}')" \
  && exigir_vermelho "codigo intermediario com dois operadores por linha" 4

# ── o caminho do aluno ────────────────────────────────────────────────────
# Sabotagem prova que o verificador sabe reprovar. Isto prova o contrario: que
# ele sabe APROVAR quem fez a parte dela. Foi este teste que pegou a Entrega 3
# exigindo geracao de codigo — trabalho da Entrega 4 — e reprovando um grupo
# que tinha feito tudo certo.
SOL="${MPL_SOLUCAO:-$HOME/projetos/compiladores-lab-gabarito/solucao}"
if [ -d "$SOL/mplc" ]; then
  echo "── caminho do aluno: cada entrega verde com as fases DELA, nem uma a mais"
  aluno=$(mktemp -d)
  cp -r "$RAIZ/mplc" "$RAIZ/testes" "$RAIZ/verificar.py" "$RAIZ/Makefile" \
        "$RAIZ/compilar" "$RAIZ/executar" "$aluno/"
  passo() {
    n="$1"; shift
    for arq in "$@"; do cp "$SOL/mplc/$arq" "$aluno/mplc/$arq"; done
    if (cd "$aluno" && python3 verificar.py "$n" >/dev/null 2>&1); then
      printf "  ${VERDE}ok${ZERO}    Entrega %s passa com as fases 1..%s escritas\n" "$n" "$n"
    else
      printf "  ${VERMELHO}FALHA${ZERO} Entrega %s reprova quem a fez certo — a prova cobra fase que ela nao pede\n" "$n"
      falhas=$((falhas + 1))
    fi
  }
  passo 1 lexico.py
  passo 2 sintatico.py
  passo 3 semantica.py
  passo 4 intermediario.py gerador.py vm.py
  rm -rf "$aluno"
fi

echo
if [ "$falhas" -eq 0 ]; then
  printf "${VERDE}O verificador sabe ficar vermelho. Um verde dele vale.${ZERO}\n"
  exit 0
fi
printf "${VERMELHO}%s sabotagem(ns) passaram batido. O verificador esta cego ali.${ZERO}\n" "$falhas"
exit 1

# Trabalho semestral de Compiladores — MPL
#
#   make verificar E=1     confere a Entrega 1
#   make verificar E=4     confere a Entrega 4 (e as anteriores)
#   make verificar         confere as quatro
#   make prova             roda a verificacao num CLONE LIMPO (o que a correcao faz)
#   make evidencias E=1    grava evidencias/verificacao-1.txt para entregar
#   make exemplo           compila e roda um programa de exemplo
#   make limpar            apaga os .mplb gerados

PY := python3
E  :=

.PHONY: verificar prova evidencias exemplo limpar autoteste ajuda

ajuda:
	@sed -n '/^# Trabalho/,/^$$/p' Makefile | sed 's/^# \{0,1\}//'

verificar:
	@$(PY) verificar.py $(if $(E),$(E),todas)

# A correcao clona o repositorio de voces numa maquina limpa. Isto faz o mesmo,
# aqui, antes de entregar: se passa no clone e nao passa aqui (ou o contrario),
# o problema e empacotamento — arquivo nao commitado, caminho absoluto, passo de
# build que ninguem roda. Vale para qualquer linguagem.
prova:
	@if [ ! -d .git ]; then \
	  echo "Isto precisa de um clone git do repositorio (nao achei a pasta .git)."; \
	  exit 1; \
	fi
	@sujos=`git status --porcelain | wc -l`; \
	 if [ "$$sujos" -gt 0 ]; then \
	   echo "ATENCAO: $$sujos arquivo(s) alterado(s) e ainda NAO commitado(s):"; \
	   git status --porcelain | sed 's/^/     /'; \
	   echo "  A correcao so enxerga o que esta commitado."; \
	   echo ""; \
	 fi
	@tmp=`mktemp -d`; \
	 git clone -q . $$tmp/prova; \
	 echo "Verificando um clone limpo do que esta commitado:"; \
	 ( cd $$tmp/prova && $(PY) verificar.py $(if $(E),$(E),todas) ); \
	 estado=$$?; \
	 rm -rf $$tmp; \
	 echo ""; \
	 if [ $$estado -eq 0 ]; then \
	   echo "O clone limpo passou. Isto e o que a correcao vai ver."; \
	 else \
	   echo "O clone limpo NAO passou. Se aqui na sua pasta passa, falta commitar algo."; \
	 fi; \
	 exit $$estado

evidencias:
	@if [ -z "$(E)" ]; then echo "diga qual: make evidencias E=1"; exit 1; fi
	@mkdir -p evidencias
	@$(PY) verificar.py $(E) > evidencias/verificacao-$(E).txt 2>&1; \
	  estado=$$?; \
	  echo "gravado em evidencias/verificacao-$(E).txt"; \
	  if [ $$estado -ne 0 ]; then \
	    echo "ATENCAO: a verificacao falhou. A evidencia registra a falha —"; \
	    echo "e isso e melhor do que entregar sem evidencia nenhuma."; \
	  fi

exemplo:
	@./compilar exemplos/ola.mpl && ./executar exemplos/ola.mplb

limpar:
	@find . -name '*.mplb' -delete
	@echo "os .mplb foram apagados"

autoteste:
	@./autoteste.sh

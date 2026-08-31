funcao logico ehPrimo(inteiro n) {
  se (n < 2) {
    retorne falso;
  }
  inteiro d = 2;
  enquanto (d * d <= n) {
    se (n % d == 0) {
      retorne falso;
    }
    d = d + 1;
  }
  retorne verdadeiro;
}

funcao vazio principal() {
  inteiro n = 2;
  inteiro achados = 0;
  enquanto (achados < 8) {
    se (ehPrimo(n)) {
      escreva(n);
      achados = achados + 1;
    }
    n = n + 1;
  }
}

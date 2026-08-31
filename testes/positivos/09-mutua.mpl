funcao logico par(inteiro n) {
  se (n == 0) {
    retorne verdadeiro;
  }
  retorne impar(n - 1);
}

funcao logico impar(inteiro n) {
  se (n == 0) {
    retorne falso;
  }
  retorne par(n - 1);
}

funcao vazio principal() {
  inteiro i = 0;
  enquanto (i < 5) {
    escreva(par(i));
    i = i + 1;
  }
}

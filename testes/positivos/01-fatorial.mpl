funcao inteiro fatorial(inteiro n) {
  se (n <= 1) {
    retorne 1;
  } senao {
    retorne n * fatorial(n - 1);
  }
}

funcao vazio principal() {
  inteiro i = 1;
  enquanto (i <= 6) {
    escreva(fatorial(i));
    i = i + 1;
  }
}

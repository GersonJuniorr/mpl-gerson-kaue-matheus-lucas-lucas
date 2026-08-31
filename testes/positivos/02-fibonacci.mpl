funcao vazio principal() {
  inteiro a = 0;
  inteiro b = 1;
  inteiro n = 10;
  enquanto (n > 0) {
    escreva(a);
    inteiro t = a + b;
    a = b;
    b = t;
    n = n - 1;
  }
}

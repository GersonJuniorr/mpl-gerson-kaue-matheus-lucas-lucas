// Exemplo proprio: recursao, conversao e formatacao de reais.
funcao inteiro somaAte(inteiro n) {
  se (n <= 0) {
    retorne 0;
  } senao {
    retorne n + somaAte(n - 1);
  }
}

funcao vazio principal() {
  escreva("soma de 1 a 10");
  escreva(somaAte(10));
  real divisao = 7 / 2;
  escreva(divisao);
}

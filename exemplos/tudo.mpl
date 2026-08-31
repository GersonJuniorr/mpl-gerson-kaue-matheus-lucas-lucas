// Um programa que usa quase tudo o que a MPL tem.
// Serve de alvo de testes enquanto voces constroem o compilador.

funcao inteiro mdc(inteiro a, inteiro b) {
  enquanto (b != 0) {
    inteiro t = b;
    b = a % b;
    a = t;
  }
  retorne a;
}

funcao real areaCirculo(real raio) {
  retorne 3.141593 * raio * raio;
}

funcao texto sinal(inteiro n) {
  se (n > 0) {
    retorne "positivo";
  } senao {
    se (n < 0) {
      retorne "negativo";
    } senao {
      retorne "zero";
    }
  }
}

funcao vazio principal() {
  escreva(mdc(48, 18));
  escreva(areaCirculo(2.0));
  escreva(sinal(-5));
  escreva(sinal(0));
  inteiro i = 1;
  enquanto (i <= 3) {
    escreva("volta " + sinal(i));
    i = i + 1;
  }
}

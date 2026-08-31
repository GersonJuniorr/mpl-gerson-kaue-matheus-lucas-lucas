funcao vazio principal() {
  inteiro x = 1;
  escreva(x);
  {
    inteiro x = 2;
    escreva(x);
    {
      inteiro x = 3;
      escreva(x);
    }
    escreva(x);
  }
  escreva(x);
  inteiro i = 0;
  enquanto (i < 2) {
    inteiro x = 10 + i;
    escreva(x);
    i = i + 1;
  }
  escreva(x);
}

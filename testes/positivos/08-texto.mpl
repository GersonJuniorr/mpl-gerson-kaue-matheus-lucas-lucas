funcao texto juntar(texto a, texto b) {
  retorne a + " " + b;
}

funcao vazio principal() {
  escreva(juntar("bom", "dia"));
  escreva("com\ttab");
  escreva("com\"aspas\"");
  escreva("barra\\invertida");
  escreva("duas\nlinhas");
  escreva("");
  escreva("a" + "b" + "c");
}

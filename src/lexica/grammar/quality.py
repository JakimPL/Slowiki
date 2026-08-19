from enum import StrEnum


class Quality(StrEnum):
    AKCENTOWANY = "akcentowany"
    NIEAKCENTOWANY = "nieakcentowany"
    POPRZYIMKOWY = "poprzyimkowy"
    NIEPOPRZYIMKOWY = "niepoprzyimkowy"
    AGLUTYNACYJNY = "aglutynacyjny"
    NIEAGLUTYNACYJNY = "nieaglutynacyjny"
    WOKALICZNY = "wokaliczny"
    NIEWOKALICZNY = "niewokaliczny"
    UZGADNIAJĄCY = "uzgadniający"
    RZĄDZĄCY = "rządzący"
    ZBIOROWY = "zbiorowy"
    NIEZBIOROWY = "niezbiorowy"
    PLURALE_TANTUM = "plurale tantum"
    KROPKOWANY = "kropkowany"
    NIEKROPKOWANY = "niekropkowany"
    ZŁOŻONY = "złożony"

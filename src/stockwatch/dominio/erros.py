"""Erros de regra de negócio, com mensagens prontas para o operador."""


class ErroDominio(Exception):
    """Base de toda regra de negócio violada."""


class NomeInvalido(ErroDominio):
    """Nome vazio ou longo demais."""

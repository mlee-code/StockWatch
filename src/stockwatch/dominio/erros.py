"""Erros de regra de negócio, com mensagens prontas para o operador."""


class ErroDominio(Exception):
    """Base de toda regra de negócio violada."""


class NomeInvalido(ErroDominio):
    """Nome vazio ou longo demais."""


class ProdutoDuplicado(ErroDominio):
    """Já existe produto com o mesmo nome, sem diferenciar maiúsculas (H6)."""

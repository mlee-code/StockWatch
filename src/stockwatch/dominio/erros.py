"""Erros de regra de negócio, com mensagens prontas para o operador."""


class ErroDominio(Exception):
    """Base de toda regra de negócio violada."""


class NomeInvalido(ErroDominio):
    """Nome vazio ou longo demais."""


class ProdutoDuplicado(ErroDominio):
    """Já existe produto com o mesmo nome, sem diferenciar maiúsculas (H6)."""


class QuantidadeInvalida(ErroDominio):
    """Quantidade não é um inteiro maior que zero."""


class DataInvalida(ErroDominio):
    """Data inexistente ou fora dos formatos aceitos."""


class MovimentacaoInvalida(ErroDominio):
    """Movimentação incoerente (sem linhas, ou tipo e motivo incompatíveis)."""


class SaldoInvalido(ErroDominio):
    """Saldo de lote negativo: violaria o invariante de estoque."""

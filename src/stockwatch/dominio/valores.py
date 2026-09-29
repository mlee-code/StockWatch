"""Objetos de valor imutáveis do domínio."""

from dataclasses import dataclass
from typing import ClassVar

from stockwatch.dominio.erros import NomeInvalido


@dataclass(frozen=True, slots=True, eq=False)
class NomeValido:
    """Nome de produto, categoria ou fornecedor (REQ-001 CA-1).

    A comparação ignora maiúsculas e minúsculas (H6), mas o texto original,
    sem os espaços das pontas, é preservado para exibição.
    """

    valor: str
    TAMANHO_MAXIMO: ClassVar[int] = 100

    def __post_init__(self) -> None:
        limpo = self.valor.strip()
        if not limpo:
            raise NomeInvalido("O nome é obrigatório.")
        if len(limpo) > self.TAMANHO_MAXIMO:
            raise NomeInvalido(f"O nome deve ter no máximo {self.TAMANHO_MAXIMO} caracteres.")
        object.__setattr__(self, "valor", limpo)

    @property
    def chave(self) -> str:
        """Forma normalizada usada em comparações."""
        return self.valor.casefold()

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, NomeValido) and self.chave == outro.chave

    def __hash__(self) -> int:
        return hash(self.chave)

    def __str__(self) -> str:
        return self.valor

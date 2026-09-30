"""Reaproveita o banco de volume da SUITE-VOL (gerado uma vez por sessão)."""

from tests.volume.conftest import banco_volume, caminho_volume, servico_volume

__all__ = ["banco_volume", "caminho_volume", "servico_volume"]

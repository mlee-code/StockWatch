# StockWatch

Controle de estoque com interface de terminal (TUI) para pequenos comércios: registro de entradas e saídas de produtos e acompanhamento de datas de validade.

> **Estado:** em desenvolvimento — primeira versão em planejamento.

## Objetivo

Dar a mercearias e pequenos varejos visibilidade do saldo de cada produto e do que está vencido ou perto de vencer, num programa local, leve e operável só pelo teclado, sem depender de rede ou de serviços externos.

## Primeira versão (planejada)

- Cadastro de produtos, com fornecedor e categoria opcionais.
- Registro de entradas com data de validade obrigatória.
- Registro de saídas por venda, perda ou descarte por vencimento, consumindo primeiro os lotes que vencem antes (FEFO).
- Consulta do estoque atual.
- Alerta de produtos vencidos ou perto de vencer, com antecedência configurável (padrão: 30 dias).

## Tecnologias

- [Python](https://www.python.org/)
- [Textual](https://textual.textualize.io/) para a TUI
- [SQLite](https://www.sqlite.org/) para a persistência local

## Engenharia

O projeto é desenvolvido com TDD e uma bateria de testes unitários, baseados em propriedades, de integração com SQLite, fuzzing e de volume. Instalação, uso e capturas da TUI serão documentados quando a primeira versão estiver disponível.

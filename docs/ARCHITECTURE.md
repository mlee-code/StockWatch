# ARCHITECTURE.md

## Visão geral
Monolito Python local, com uma única parte e processo único (EXEC-001), organizado em camadas com dependências apontando para o domínio (arquitetura hexagonal simplificada).

```text
tui ──► aplicacao ──► dominio
            │            ▲
            ▼            │
      persistencia ──────┘
```

- `dominio` não importa nenhuma outra camada, nem `sqlite3` ou `textual`.
- `aplicacao` conhece o domínio e as **portas** (interfaces `Protocol`) dos repositórios, nunca o SQLite.
- `persistencia` implementa as portas sobre SQLite.
- `tui` conversa só com `aplicacao`.
- Monta tudo: `__main__.py`, a raiz de composição.

## Objetivos arquiteturais
1. Regras de estoque testáveis sem banco nem interface (REQ-004, REQ-006).
2. Troca de persistência ou de interface sem tocar no domínio.
3. Menor fatia vertical primeiro (ROADMAP V010-03).

## Cobertura das necessidades

| Requisito | Componente | Contrato |
|---|---|---|
| REQ-001, 002 | `aplicacao.ServicoEstoque.cadastrar_produto` / `listar_produtos` | `RepositorioProdutos` |
| REQ-003 | `ServicoEstoque.registrar_entrada` | `RepositorioLotes`, `RepositorioMovimentacoes` |
| REQ-004 | `dominio.fefo.planejar_saida` (pura) + `ServicoEstoque.registrar_saida` | idem |
| REQ-005, 006 | `dominio.validade.classificar` (pura) + consultas do serviço | `RepositorioLotes` |
| REQ-007 | `ServicoEstoque.configurar_dias_alerta` | `RepositorioConfiguracao` |
| REQ-008 | `ServicoEstoque.historico` | `RepositorioMovimentacoes` |
| REQ-009 | `tui.telas.painel` | serviço |
| REQ-010 | `persistencia.UnidadeDeTrabalhoSqlite` | transação por caso de uso |

## Componentes principais

### COMP-001 Domínio (`stockwatch.dominio`)
- **Responsabilidade:** entidades e valores imutáveis (`Produto`, `Lote`, `Movimentacao`, `Quantidade`, `NomeValido`, `MotivoSaida`); regras puras `planejar_saida` (FEFO com H1–H4) e `classificar` (vencido, perto de vencer, ok).
- **Estilo:**
  - orientação a objetos para identidade e invariantes, validadas no construtor;
  - estilo funcional (funções puras sobre `dataclass(frozen=True)`) para FEFO e validade, o que permite testes por propriedades.
- **Erros:** hierarquia `ErroDominio` (`NomeInvalido`, `QuantidadeInvalida`, `SaldoInsuficiente`...), com mensagens em português prontas para a TUI.

### COMP-002 Persistência (`stockwatch.persistencia`)
- **Responsabilidade:**
  - repositórios SQLite e unidade de trabalho (commit ou rollback por caso de uso);
  - migrações por `PRAGMA user_version`;
  - `PRAGMA foreign_keys = ON`.
- **Dados possuídos:** o banco do produto (`docs/data/DATA_MODEL.md`).
- **Falhas:** exceção dentro da unidade de trabalho faz rollback; nada fica gravado pela metade.

### Aplicação (`stockwatch.aplicacao`)
- **Responsabilidade:** o `ServicoEstoque` orquestra os casos de uso: valida a entrada, busca lotes com saldo, chama as regras puras, grava pela unidade de trabalho e devolve DTOs imutáveis para a TUI.
- **Relógio:** injetado (`Callable[[], date]`), conforme NFR-004.
- Faz parte do nó COMP-001 no grafo: é a borda de casos de uso do domínio, sem fronteira de execução própria.

### COMP-003 TUI (`stockwatch.tui`)
- **Responsabilidade:** app Textual com uma tela por função e atalhos de teclado no rodapé.
- **Estados:** a TUI converte `ErroDominio` em mensagem de erro e nunca mostra traceback ao operador.
- **Telas:** painel, produtos, entrada, saída, estoque, validades, histórico, configuração.

## Diretórios

```text
src/stockwatch/
  dominio/        entidades, valores, erros, fefo.py, validade.py
  aplicacao/      servico.py, portas.py (Protocols), dtos.py
  persistencia/   sqlite.py, migracoes.py
  tui/            app.py, telas/
  __main__.py     composição e argumentos (--banco)
tests/
  unit/           domínio e serviço com repositórios em memória
  propriedades/   Hypothesis
  integracao/     SQLite real em arquivo temporário
  tui/            App.run_test()
  fuzzing/        máquina de estados do Hypothesis
  volume/         marcador volume
  desempenho/     pytest-benchmark
  arquitetura/    guard rails de dependência
```

## Guard rails arquiteturais
- `tests/arquitetura/` verifica, pelos imports, que `dominio` não importa `aplicacao`, `persistencia`, `tui`, `sqlite3` nem `textual`, e que `tui` não importa `persistencia`.
- mypy estrito em todo o código.

## Tecnologias

| Tecnologia | Uso | Motivo |
|---|---|---|
| Python 3.12 | linguagem | decisão do responsável |
| Textual 8.x | TUI | decisão do responsável; testes com `run_test()` |
| sqlite3 (biblioteca padrão) | persistência | sem dependência extra; SQL explícito é defensável em entrevista |
| pytest, Hypothesis, pytest-benchmark | testes | ver `docs/testing/TESTS.md` |
| ruff, mypy | qualidade estática | lint, formatação e tipos |

Sem ORM: o modelo é pequeno, e SQL explícito deixa as consultas de volume e FEFO visíveis e mensuráveis.

## Segurança, desempenho e observabilidade
- **Segurança:** sem rede; SQL sempre parametrizado; o arquivo do banco fica sob as permissões do usuário.
- **Desempenho:** saldo derivado por agregação indexada; materialização só se a medição de NFR-003 exigir.
- **Observabilidade:** a TUI mostra os erros; o profiling vai para o `metadata` (DECISION-003). Não há log de operação na v0.1.0.

## Grafo arquitetural versionado
`GRAPH-001` em `metadata`. Este documento é uma projeção humana do grafo; mudanças de componente atualizam o grafo primeiro.

## Questões em aberto
Nenhuma para a v0.1.0.

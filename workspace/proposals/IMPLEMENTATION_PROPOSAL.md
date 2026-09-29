<!-- Proposta transitória da IA para a primeira versão ou qualquer evolução posterior; exige aprovação antes da implementação. -->

# Proposta de implementação

## Identificação

- Proposal ID: PROP-001
- Revisão: 1
- Hash: SHA-256 do arquivo no commit que o introduz, registrado em `metadata`
- Solicitação de origem: `workspace/PROJECT_CONTEXT.md` (commit `5d949b2`), hipóteses confirmadas em 2026-09-28
- Tipo: FEATURE (primeira versão)
- Projeto, versão e commit de base: StockWatch, v0.1.0, `e49982d`
- Agente autor: Claude Code (Opus 5.5)
- Data: 2026-09-28
- Estado: Aprovada por DECISION-004 (implementação primeiro, validação humana depois)

## Entendimento da solicitação

TUI local para um pequeno comércio controlar saldo e validade de produtos: cadastro, entradas com validade obrigatória, saídas com motivo consumindo lotes por FEFO, estoque atual, alertas de vencido e perto de vencer (N dias, padrão 30, configurável) e histórico.

## Hipóteses

Assumidas por esta proposta, a validar no review da versão:

- **H1.** Uma **venda** consome somente lotes **não vencidos**. Vender produto vencido é justamente o risco que o projeto quer evitar.
- **H2.** Um **descarte por vencimento** consome somente lotes **vencidos**.
- **H3.** Uma **perda** consome qualquer lote, por FEFO.
- **H4.** Entre lotes com a mesma validade, sai primeiro o que entrou antes.
- **H5.** "Vencido" significa validade anterior a hoje. O produto vence ao fim do dia da validade.
- **H6.** O nome do produto é único, sem distinguir maiúsculas de minúsculas.

## Solução recomendada

Monolito Python em três camadas (EXEC-001), com dependências apontando para o domínio:

```text
stockwatch/
  dominio/      entidades, valores, regras (FEFO, alertas) — Python puro, sem I/O
  aplicacao/    serviço de estoque: casos de uso e unidade de trabalho
  persistencia/ repositórios e migrações sobre sqlite3 da biblioteca padrão
  tui/          app Textual, telas e atalhos
```

- **Orientação a objetos** no domínio: `Produto`, `Lote` e `Movimentacao`, com invariantes validados no construtor.
- **Estilo funcional** onde simplifica: o plano de saída FEFO e a classificação de validade são funções puras sobre valores imutáveis. Isso permite testá-los por propriedades.
- **Saldo derivado:** o saldo é calculado a partir das movimentações, nunca armazenado. Assim existe uma única fonte de verdade.
- **Relógio injetado:** as regras de validade recebem a data de hoje como parâmetro, o que torna os testes determinísticos.

## Escopo

### Incluído
Cadastro de produto (categoria opcional); entrada com quantidade, validade e fornecedor opcional; saída com motivo; estoque atual; validades com alerta; configuração de N; histórico de movimentações; painel inicial com resumo e alertas.

### Não incluído
Exclusão de produtos, edição e exclusão de movimentações (a edição de produtos entrou por DECISION-009), estorno, relatórios, importação e exportação, múltiplos usuários, rede e integração com PDV. Uma correção de movimentação será feita por movimentação compensatória num ciclo futuro.

## Estrutura de dados proposta

Banco do produto: SQLite em `$XDG_DATA_HOME/stockwatch/stockwatch.db` (padrão `~/.local/share/...`). O local pode ser trocado com `--banco`.

| Tabela | Campos principais | Regras |
|---|---|---|
| `categoria` | id, nome | nome único |
| `fornecedor` | id, nome | nome único |
| `produto` | id, nome, categoria_id? | nome único (NOCASE) |
| `lote` | id, produto_id, validade, fornecedor_id?, criado_em | 1 lote por entrada |
| `movimentacao` | id, tipo (entrada/saida), motivo?, produto_id, ocorrida_em | motivo obrigatório em saída |
| `movimentacao_lote` | movimentacao_id, lote_id, quantidade > 0 | uma saída pode tocar vários lotes |
| `configuracao` | chave, valor | `dias_alerta` = 30 |

- Cardinalidade: produto 1–N lote, movimentação 1–N movimentacao_lote, lote 1–N movimentacao_lote.
- Índices: por `lote(produto_id, validade)` e por `movimentacao_lote(lote_id)`.
- Migrações: versionadas por `PRAGMA user_version`.
- Detalhes: `docs/data/DATA_MODEL.md` e o DBML, gerados na parte 2.

## Plano incremental

Cada parte fica num branch próprio. Ao fim de cada uma, o agente para e envia um resumo (DECISION-005). Os incrementos seguem TDD: commit `test:` com o teste vermelho, `feat:` com o teste verde, `refactor:` quando houver.

| Parte | Entrega | Branch |
|---|---|---|
| 1 | Plano: esta proposta, roadmap, decisões | `docs/documentacao-inicial` |
| 2 | Fundação: pyproject, ferramentas, arquitetura, requisitos, modelo de dados, critérios de teste, TUI vazia que abre | `chore/fundacao` |
| 3 | Cadastro e listagem de produtos (primeira fatia vertical) | `feat/cadastro-produto` |
| 4 | Entrada com lote e validade + estoque atual | `feat/entrada-estoque` |
| 5 | Saída FEFO com motivo | `feat/saida-fefo` |
| 6 | Validades, alertas, configuração de N e painel | `feat/validades-alertas` |
| 7 | Histórico de movimentações | `feat/historico` |
| 8 | Fuzzing, volume, profiling em `metadata`, README final e release v0.1.0 | `chore/release-0.1.0` |

## Estratégia de testes

| Tipo | Ferramenta | Critério |
|---|---|---|
| Unitário | pytest | regras do domínio e serviço com repositórios falsos |
| Propriedades | Hypothesis | FEFO: soma consumida = pedida, saldo ≥ 0, ordem de validade respeitada |
| Integração | pytest + SQLite real (arquivo temporário) | repositórios, migrações, transações e rollback |
| TUI | `App.run_test()` do Textual | fluxos por teclado e estados de vazio, erro e sucesso |
| Fuzzing | Hypothesis (entradas aleatórias e máquina de estados) | nenhuma sequência de comandos quebra invariantes nem gera exceção inesperada |
| Volume | pytest marcado `volume` | 10 mil produtos e 1 milhão de movimentações dentro de limites de tempo definidos em `TESTS.md` |
| Desempenho | pytest-benchmark, cProfile, tracemalloc | métricas registradas em `metadata` contra a baseline (DECISION-003) |

Qualidade estática: ruff (lint e formatação) e mypy estrito.

## Riscos e mitigação

- **Prazo:** o escopo funcional é cortado antes do rigor de teste.
- **Hipóteses H1–H6 erradas:** ficam isoladas em funções puras, e trocá-las é barato.
- **Volume lento com saldo derivado:** índices, medição na parte 8, e materialização somente se a medição exigir.

## Critérios de conclusão

Os de `PROJECT_CONTEXT.md` ("Critérios para considerar a primeira versão pronta"), com toda a bateria verde, ruff e mypy sem erros e métricas de baseline registradas em `metadata`.

## Gate de aprovação

- Revisão exata aprovada: 1
- Hash aprovado: registrado em `metadata` ao commitar
- Responsável: M Lee
- Data: 2026-09-28
- Estado: Aprovada (DECISION-004)

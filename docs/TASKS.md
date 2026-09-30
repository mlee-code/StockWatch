# TASKS.md

Tarefas executáveis derivadas de `ROADMAP.md`. Cada tarefa aponta a origem, as fontes e os testes. `[x]` só com os testes verdes.

## V010-02 — Fundação
- [x] TASK-001 — Arquivos de higiene do repositório. Fonte: ENGINEERING_PRACTICES. Teste: presença no commit `fb4ccbc`.
- [x] TASK-002 — Pacote Python, dependências, ruff e mypy. Fonte: ARCHITECTURE "Tecnologias". Teste: `ruff`/`mypy` sem erros.
- [x] TASK-003 — TUI inicial que abre e fecha. Fonte: REQ-009 (parcial), NFR-001. Teste: TEST-TUI-001.
- [x] TASK-004 — CI no GitHub Actions. Fonte: ENGINEERING_PRACTICES "CI/CD". Teste: workflow verde no GitHub (run 36500216951).
- [x] TASK-005 — Documentação técnica da v0.1.0. Fonte: PROP-001. Teste: revisão humana.
- [x] TASK-006 — Guard rail de arquitetura. Fonte: ARCHITECTURE "Guard rails". Teste: SUITE-ARQ.

## V010-03 — Cadastro e listagem de produtos
- [x] TASK-010 — Valor `NomeValido` e entidade `Produto`. Fonte: REQ-001 CA-1. Testes: SUITE-UNIT.
- [x] TASK-011 — Serviço `cadastrar_produto`/`listar_produtos` com repositório em memória. Fonte: REQ-001, 002. Testes: SUITE-UNIT.
- [x] TASK-012 — Migração v1 e repositório SQLite de produtos. Fonte: DATA_MODEL. Testes: SUITE-INT (DT-001, DT-003).
- [x] TASK-013 — Tela de produtos. Fonte: REQ-001, 002, UX_UI. Testes: SUITE-TUI.

## V010-04 — Entrada com lote e validade + estoque atual
- [x] TASK-020 — Leitura de quantidade e data digitadas. Fonte: REQ-003 CA-1, CA-2. Testes: TEST-UNIT-030 a 033.
- [x] TASK-021 — Lote, Consumo e Movimentacao com invariantes. Fonte: CON-008, DATA_MODEL. Testes: TEST-UNIT-050 a 056.
- [x] TASK-022 — Serviço `registrar_entrada`, `estoque_atual`, `lotes_do_produto`. Fonte: REQ-003, 005. Testes: TEST-UNIT-040 a 048.
- [x] TASK-023 — Repositórios SQLite de lotes e movimentações. Fonte: DATA_MODEL. Testes: TEST-INT-020 a 025.
- [x] TASK-024 — Telas de entrada e de estoque. Fonte: REQ-003, 005, UX_UI. Testes: TEST-TUI-010 a 022.
- [x] TASK-025 — Validade opcional no lote e migração 2. Fonte: FR-001, DECISION-007. Testes: TEST-UNIT-034, 035, 049, 057; TEST-INT-030 a 032; TEST-TUI-013, 017, 023.

## V010-09 — Modos normal e inserção
- [x] TASK-090 — TelaModal, CampoTexto e TabelaVim; telas de produtos, entrada e estoque migradas. Fonte: FR-002, DECISION-008, UX_UI. Testes: TEST-TUI-030 a 038.

## V010-10 — Edição de produto e atalhos com contexto
- [x] TASK-100 — Serviço e SQLite: `editar_produto`, `buscar_por_id`, `atualizar`. Fonte: REQ-011. Testes: TEST-UNIT-060 a 066, TEST-INT-040 a 042.
- [x] TASK-101 — TUI: edição na tela de produtos e `e` com o produto em foco. Fonte: REQ-011, REQ-012, UX_UI. Testes: TEST-TUI-040 a 045.

## V010-05 — Saída FEFO com motivo
- [x] TASK-050 — `planejar_saida`, `vencido`, `elegivel` (funções puras). Fonte: REQ-004, H1 a H5, DECISION-007. Testes: TEST-UNIT-070 a 076, TEST-PROP-001 a 004.
- [x] TASK-051 — Serviço `registrar_saida` com relógio de data. Fonte: REQ-004, NFR-004. Testes: TEST-UNIT-080 a 084, TEST-INT-050 a 052.
- [x] TASK-052 — Tela de saída, `ler_motivo` e `s` com contexto. Fonte: REQ-004, REQ-012, UX_UI. Testes: TEST-UNIT-036, 037, TEST-TUI-050 a 055.

## V010-11 — Exclusão de produto
- [x] TASK-110 — Serviço e SQLite: `excluir_produto`, `possui_movimentacoes`, `remover`. Fonte: REQ-013, DECISION-010. Testes: TEST-UNIT-090 a 093, TEST-INT-060, 061.
- [x] TASK-111 — TUI: `d` com confirmação. Fonte: REQ-013, UX_UI. Testes: TEST-TUI-060 a 063.

## V010-06 — Validades, alertas, configuração de N e painel
- [x] TASK-060 — `classificar`, `Situacao`, `ler_dias_alerta`; `vencido` derivado de `classificar`. Fonte: REQ-006, 007, H5. Testes: TEST-UNIT-100 a 104, TEST-PROP-005 a 007.
- [x] TASK-061 — Serviço e SQLite: `validades`, `dias_alerta`, `configurar_dias_alerta`, `painel`. Fonte: REQ-006, 007, 009. Testes: TEST-UNIT-110 a 114, TEST-INT-070, 071.
- [x] TASK-062 — TUI: telas de validades e configuração, e painel inicial. Fonte: REQ-006, 007, 009, UX_UI. Testes: TEST-TUI-070 a 077.

## V010-07 — Histórico de movimentações
- [x] TASK-070 — Serviço e SQLite: `historico` com limite e filtro por produto. Fonte: REQ-008. Testes: TEST-UNIT-120 a 123, TEST-INT-080, 081.
- [x] TASK-071 — TUI: tela de histórico (`m`) em hora local. Fonte: REQ-008, UX_UI. Testes: TEST-TUI-090 a 093.
- [x] TASK-072 — Painel: quadro na largura toda e texto centralizado (pedido do responsável). Testes: TEST-TUI-078.
- [x] TASK-073 — `scripts/verificar.sh`: portão local igual ao CI. Fonte: ENGINEERING_PRACTICES.

## V010-08 — Fuzzing, volume, profiling, README e release
- [x] TASK-080 — Fuzzing dos leitores e máquina de estados sobre SQLite. Fonte: SUITE-FUZZ. Testes: TEST-FUZZ-001, 002.
- [x] TASK-081 — Gerador de volume e metas de NFR-003. Fonte: SUITE-VOL, DT-006, DT-010. Testes: TEST-VOL-001 a 006.
- [x] TASK-082 — Otimizações guiadas por cProfile (painel, validades, produtos) e limite de alertas. Fonte: NFR-003, REQ-006 CA-5. Testes: TEST-UNIT-115, SUITE-VOL.
- [x] TASK-083 — Benchmarks e registro de métricas no metadata. Fonte: DECISION-003. Testes: TEST-DES-001 a 003.
- [x] TASK-084 — README com capturas, CHANGELOG derivado dos commits, versão 0.1.0 e job de volume sob demanda no CI.

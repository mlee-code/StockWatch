# TESTS.md

## Objetivo
Transformar `REQUIREMENTS.md` em verificações executáveis, construídas por TDD canônico (Red → Green → Refactor → Regression), da regra pura até a jornada completa na TUI.

## Princípios
- Os critérios de aceitação ficam em `REQUIREMENTS.md`; cada teste cita o `REQ`/`CA` que verifica, na docstring.
- Todo teste novo falha pelo motivo correto antes da implementação; o commit `test:` registra o Red, e o `feat:` registra o Green.
- Nenhum teste é enfraquecido, ignorado ou removido para avançar.
- Testes que não verificam integração usam repositórios em memória e relógio fixo.

## Como executar
```sh
.venv/bin/pytest                    # padrão: tudo menos volume
.venv/bin/pytest -m volume          # volume (lento)
.venv/bin/pytest tests/desempenho --benchmark-only
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
```
O CI (`.github/workflows/ci.yml`) roda o conjunto padrão a cada push.

## Tipos de teste e critérios de aceitação

### SUITE-UNIT — Unitários (`tests/unit/`)
- **Objeto:** entidades, valores, regras puras e serviço com repositórios em memória.
- **Critério:** todos os CA de REQ-001 a REQ-009 com pelo menos um caso de sucesso, um de erro e os limites (por exemplo, nome com 0, 1, 100 e 101 caracteres; N = 0 e 365). Cobertura de linhas do domínio ≥ 95%.

### SUITE-PROP — Baseados em propriedades (`tests/propriedades/`)
- **Objeto:** `planejar_saida` (FEFO) e `classificar` (validade).
- **Critério:** Hypothesis com pelo menos 500 exemplos por propriedade, sem falha. Propriedades obrigatórias:
  - a soma consumida é igual à pedida, ou a saída é rejeitada;
  - nenhum lote fica com saldo negativo;
  - um lote só é consumido depois que todos os lotes elegíveis de validade anterior se esgotaram;
  - venda nunca toca lote vencido; descarte nunca toca lote válido;
  - a classificação é consistente com a definição de H5 para qualquer data e N.

### SUITE-INT — Integração com SQLite real (`tests/integracao/`)
- **Objeto:** repositórios, migrações, unidade de trabalho.
- **Critério:**
  - banco em arquivo temporário real, não `:memory:`;
  - cada restrição de `DATA_MODEL.md` rejeita um dado inválido;
  - rollback deixa o banco idêntico ao anterior;
  - os dados sobrevivem ao fechamento e à reabertura (REQ-010).

### SUITE-TUI — Interface (`tests/tui/`)
- **Objeto:** telas via `App.run_test()` e piloto de teclado.
- **Critério:** cada tela cobre os estados vazio, erro e sucesso (NFR-002), e cada fluxo é executado só pelo teclado (NFR-001).

### SUITE-FUZZ — Fuzzing (`tests/fuzzing/`)
- **Objeto:** analisadores de entrada (quantidade, data, nome) e o serviço completo.
- **Critério:**
  - texto arbitrário nos analisadores gera um valor válido ou `ErroDominio`, nunca outra exceção;
  - a máquina de estados do Hypothesis (sequências aleatórias de cadastrar, entrar, sair e avançar a data) mantém todas as invariantes;
  - pelo menos 200 sequências de até 50 passos, sem falha.

### SUITE-VOL — Volume (`tests/volume/`, marcador `volume`)
- **Objeto:** banco com 10 mil produtos e 1 milhão de movimentações.
- **Critério:** as metas de NFR-003 atendidas, e o invariante de saldo verificado por consulta sobre o banco inteiro.

### SUITE-DES — Desempenho e profiling (`tests/desempenho/`)
- **Objeto:** operações de NFR-003 com pytest-benchmark; cProfile e tracemalloc nos mesmos cenários.
- **Critério:** as métricas são registradas em `metadata` com o ambiente e a baseline (DECISION-003). Uma regressão acima de 20% no p95 contra a baseline no mesmo ambiente reprova o portão.

### SUITE-ARQ — Arquitetura (`tests/arquitetura/`)
- **Critério:** as regras de dependência de `ARCHITECTURE.md` ("Guard rails arquiteturais") são respeitadas.

## Casos
Cada arquivo de teste identifica seus casos como `TEST-<SUITE>-NNN` na docstring. Os casos implementados:

| ID | Verifica | Arquivo |
|---|---|---|
| TEST-TUI-001, 002 | a aplicação abre, fecha com `q` e usa o tema neutro | `tests/tui/test_app.py` |
| TEST-TUI-003 a 008 | tela de produtos: vazio, cadastro por teclado, erros, Esc | `tests/tui/test_tela_produtos.py` |
| TEST-UNIT-001 a 006 | `NomeValido` (REQ-001 CA-1, H6) | `tests/unit/test_nome_valido.py` |
| TEST-UNIT-010 a 016 | cadastro e listagem no serviço (REQ-001, 002) | `tests/unit/test_servico_produtos.py` |
| TEST-UNIT-020 a 022 | local do banco (REQ-010 CA-3) | `tests/unit/test_main.py` |
| TEST-UNIT-030 a 035 | leitura de quantidade e data, validade opcional (REQ-003, DECISION-007) | `tests/unit/test_leitura.py` |
| TEST-UNIT-040 a 049, 057 | entradas e estoque no serviço, lotes sem validade (REQ-003, 005) | `tests/unit/test_servico_entrada.py` |
| TEST-UNIT-050 a 056 | invariantes de lotes e movimentações (CON-008) | `tests/unit/test_movimentacao.py` |
| TEST-INT-020 a 025 | lotes, movimentações, estoque e restrições no SQLite | `tests/integracao/test_entradas_sqlite.py` |
| TEST-INT-030 a 032 | migração 2 (validade opcional) com dados existentes | `tests/integracao/test_migracao_v2.py` |
| TEST-TUI-010 a 017 | tela de entrada | `tests/tui/test_tela_entrada.py` |
| TEST-TUI-020 a 023 | tela de estoque | `tests/tui/test_tela_estoque.py` |
| TEST-INT-001 a 010 | migração, transações, unicidade e persistência de produtos | `tests/integracao/test_produtos_sqlite.py` |
| TEST-INT-011 | fluxo TUI → SQLite com reinício | `tests/integracao/test_fluxo_produtos.py` |
| TEST-INT-012 | rollback de migração com erro | `tests/integracao/test_migracoes.py` |
| TEST-TUI-030 a 038 | modos normal e inserção (DECISION-008) | `tests/tui/test_modos.py` |
| TEST-UNIT-060 a 066 | edição de produto no serviço (REQ-011) | `tests/unit/test_servico_edicao.py` |
| TEST-INT-040 a 042 | edição de produto no SQLite (REQ-011) | `tests/integracao/test_edicao_sqlite.py` |
| TEST-TUI-040 a 045 | edição na TUI e atalhos com contexto (REQ-011, 012) | `tests/tui/test_contexto_e_edicao.py` |
| TEST-UNIT-070 a 076 | plano FEFO (REQ-004 CA-2 a CA-5, H1 a H4) | `tests/unit/test_fefo.py` |
| TEST-PROP-001 a 004 | propriedades do FEFO, 500 exemplos cada | `tests/propriedades/test_fefo_propriedades.py` |
| TEST-UNIT-080 a 084 | saídas no serviço (REQ-004) | `tests/unit/test_servico_saida.py` |
| TEST-UNIT-036, 037 | leitura do motivo | `tests/unit/test_leitura.py` |
| TEST-INT-050 a 052 | saídas no SQLite, atomicidade e invariante de saldo (DT-006, DT-007) | `tests/integracao/test_saidas_sqlite.py` |
| TEST-TUI-050 a 055 | tela de saída e `s` com produto em foco | `tests/tui/test_tela_saida.py` |
| TEST-ARQ-001, 002 | camadas e dependências | `tests/arquitetura/test_dependencias.py` |

## Portões por parte
Cada parte do roadmap só termina com: suíte padrão verde, ruff e mypy sem erros, e os tipos de teste que a parte exige presentes.

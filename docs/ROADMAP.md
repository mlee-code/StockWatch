# ROADMAP.md

## Visão geral
A v0.1.0 entrega, em um único ciclo, a primeira versão utilizável: cadastro, entradas, saídas FEFO, estoque, validades e histórico numa TUI local. Os ciclos seguintes nascem do review da versão.

## Convenções de estado
- `[ ]` Planejada / em desenvolvimento / bloqueada: o estado aparece por extenso no item
- `[x]` Entregue, somente com testes e evidências verdes

## Painel de progresso

- Versão em construção: 0.1.0
- Ciclo atual: CYC-001
- Itens planejados: 10
- Itens concluídos (`[x]`): 6
- Percentual concluído: 60%
- Itens bloqueados: 0
- Horas restantes estimadas: 10 a 16 h
- Confiança da estimativa: baixa. As fatias ainda não foram medidas, e as partes 5 e 8 concentram o risco.
- Previsão e limitações: conclusão até 2026-09-30 se o ritmo se mantiver; a estimativa não é linear.

---

# Versão 0.1.0

## Ciclo CYC-001 — Primeiro ciclo

## Objetivo
Controlar saldo e validade de produtos de um pequeno comércio pela TUI.

## Valor entregue
Saber quanto há de cada produto e o que está vencido ou perto de vencer, sem rede e sem ERP.

## Escopo
Origem: `workspace/proposals/IMPLEMENTATION_PROPOSAL.md` (PROP-001). Branches e testes de cada item estão na proposta.

- [x] V010-01 — Plano da versão (proposta, roadmap, decisões). Prioridade: Crítica. Ciclo-alvo: CYC-001. Versão-alvo: 0.1.0. Dependências: nenhuma. Teste: revisão humana. Estado: entregue.
- [x] V010-02 — Fundação: projeto Python, ferramentas, arquitetura, requisitos, modelo de dados, critérios de teste e TUI que abre. Prioridade: Crítica. Dependências: V010-01. Teste: smoke da TUI e verificação de ruff e mypy. Estado: entregue (aprovado pelo responsável em 2026-09-29).
- [x] V010-03 — Cadastro e listagem de produtos. Prioridade: Crítica. Dependências: V010-02. Testes: unitários, integração e TUI. Estado: entregue (aprovado pelo responsável em 2026-09-29).
- [x] V010-04 — Entrada com lote e validade + estoque atual, com validade opcional (DECISION-007). Prioridade: Crítica. Dependências: V010-03. Testes: unitários, integração e TUI. Estado: entregue (aprovado pelo responsável em 2026-09-29).
- [ ] V010-05 — Saída FEFO com motivo. Prioridade: Crítica. Dependências: V010-04. Testes: unitários, propriedades, integração e TUI. Estado: em validação.
- [ ] V010-06 — Validades, alertas, configuração de N e painel. Prioridade: Alta. Dependências: V010-04. Testes: unitários, propriedades e TUI. Estado: planejado.
- [ ] V010-07 — Histórico de movimentações. Prioridade: Média. Dependências: V010-05. Testes: integração e TUI. Estado: planejado.
- [ ] V010-08 — Fuzzing, volume, profiling em `metadata`, README final e release. Prioridade: Alta. Dependências: V010-03 a V010-07. Testes: fuzzing, volume e benchmark. Estado: planejado.
- [x] V010-09 — Modos normal e inserção na TUI, como no vim (FR-002, DECISION-008). Prioridade: Alta. Ciclo-alvo: CYC-001. Versão-alvo: 0.1.0. Dependências: V010-04. Testes: TUI. Estado: entregue (aprovado pelo responsável em 2026-09-29).
- [x] V010-10 — Edição de produto e atalhos com contexto (FR-003, FR-004, DECISION-009). Prioridade: Alta. Ciclo-alvo: CYC-001. Versão-alvo: 0.1.0. Dependências: V010-09. Testes: unitários, integração e TUI. Estado: entregue (aprovado pelo responsável em 2026-09-29).

## Fora de escopo
Ver "Não incluído" em PROP-001.

## Critérios de conclusão
- [ ] Fluxo principal completo operável pela TUI.
- [ ] Todos os tipos de teste presentes e passando.
- [ ] README com instalação, uso e capturas da TUI.
- [ ] Histórico Git limpo, em Conventional Commits.

## Riscos
Ver "Riscos e mitigação" em PROP-001.

## Estado
Em desenvolvimento

## Datas
- Início: 2026-09-28
- Meta: 2026-09-30

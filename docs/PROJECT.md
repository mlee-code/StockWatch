# PROJECT.md

## Identidade
StockWatch: controle de estoque e validade com interface de terminal para pequenos comércios. Pacote e comando: `stockwatch`.

## Problema
Pequenos comércios perdem produtos por vencimento não percebido e divergência entre o estoque real e o percebido, porque controlam em papel ou planilha, sem alertas.

## Objetivo
Registrar entradas e saídas de produtos e acompanhar suas validades por uma TUI local, rápida e operável só pelo teclado.

## Público
- Principal: operador de mercearia ou pequeno varejo, num único computador.
- Secundário: avaliadores técnicos do portfólio.

## Escopo da v0.1.0
`docs/REQUIREMENTS.md`. Fora de escopo: "Não incluído" em PROP-001.

## Não objetivos
API, rede, múltiplos usuários, execução em servidor, integração com PDV ou nota fiscal (CON-002, CON-003).

## Critérios de sucesso
Os critérios de conclusão da v0.1.0 em `docs/ROADMAP.md`.

## Mapa da documentação

| Documento | Conteúdo |
|---|---|
| `REQUIREMENTS.md`, `CONSTRAINTS.md` | o que o sistema faz e seus limites |
| `UX_UI.md` | telas e interação |
| `ARCHITECTURE.md`, `execution/EXECUTION_MODEL.md` | como o sistema é organizado |
| `data/DATA_MODEL.md`, `data/DATA_TESTS.md` | banco do produto |
| `engineering/ENGINEERING_PRACTICES.md` | práticas técnicas |
| `testing/TESTS.md` | estratégia e critérios de teste |
| `DECISIONS.md` | decisões e motivos |
| `ROADMAP.md`, `TASKS.md` | planejamento e trabalho |
| `project_knowledge/PROJECT_KNOWLEDGE_DB.md` | banco `metadata` |

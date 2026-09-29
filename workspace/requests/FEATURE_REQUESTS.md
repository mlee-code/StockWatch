# Solicitações de feature

## FR-001 — Produto sem validade
- Origem: revisão da V010-04 pelo responsável, 2026-09-29.
- Pedido: "quando não colocamos data de vencimento significa que o produto não perde".
- Interpretação confirmada: a validade passa a ser opcional **no lote**. Um lote sem validade não vence, não gera alerta e é consumido por último no FEFO. Um mesmo produto pode ter lotes com e sem validade.

## FR-002 — Modos normal e inserção, como no vim e no lazygit
- Origem: revisão da V010-04 pelo responsável, 2026-09-29.
- Pedido: "um modo normal e de inserção [...] usar hjkl para navegar entre os campos e i para inserir textos".
- Interpretação confirmada:
  - as telas abrem no **modo normal**;
  - `i` começa a digitar no campo focado;
  - `Esc` no modo inserção volta ao modo normal, e `Esc` no modo normal volta ao painel;
  - `Enter` confirma o formulário.

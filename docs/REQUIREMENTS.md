# REQUIREMENTS.md

Fonte: `workspace/PROJECT_CONTEXT.md` e PROP-001 (hipóteses H1–H6), aprovados em 2026-09-28. Estado de todos os itens: **aprovado** para a v0.1.0.

## Requisitos funcionais

### REQ-001 — Cadastrar produto
O operador cadastra um produto com nome e categoria opcional.
- CA-1: o nome é obrigatório; espaços nas pontas são removidos; tem de 1 a 100 caracteres.
- CA-2: o nome é único, sem distinguir maiúsculas de minúsculas (H6). Um nome repetido é rejeitado com mensagem clara.
- CA-3: a categoria é opcional; se informada, segue as regras de CA-1 e é reaproveitada pelo nome.

### REQ-002 — Listar produtos
- CA-1: lista todos os produtos em ordem alfabética, com categoria e saldo atual.
- CA-2: sem produtos, a tela mostra um estado vazio que explica como cadastrar.

### REQ-003 — Registrar entrada
O operador registra a entrada de um produto existente. Cada entrada cria um lote.
- CA-1: a quantidade é um inteiro maior que zero.
- CA-2: a data de validade é obrigatória e precisa ser uma data válida (`AAAA-MM-DD` ou `DD/MM/AAAA`).
- CA-3: o fornecedor é opcional, com as mesmas regras de nome de REQ-001 CA-1, e é reaproveitado pelo nome.
- CA-4: depois da entrada, o saldo do produto aumenta exatamente na quantidade informada.

### REQ-004 — Registrar saída
O operador registra uma saída com produto, quantidade e motivo.
- CA-1: a quantidade é um inteiro maior que zero; o motivo é obrigatório: `venda`, `perda` ou `descarte por vencimento`.
- CA-2: as unidades saem por FEFO: primeiro o lote de validade mais próxima; em empate, o lote que entrou antes (H4).
- CA-3: uma venda consome só lotes não vencidos (H1); um descarte por vencimento, só lotes vencidos (H2); uma perda, qualquer lote (H3).
- CA-4: se o saldo elegível for menor que a quantidade, a saída é rejeitada inteira e nada é gravado.
- CA-5: uma saída pode consumir vários lotes; a soma consumida é igual à quantidade pedida.

### REQ-005 — Consultar estoque atual
- CA-1: mostra, por produto com saldo positivo, o saldo total e a validade mais próxima.
- CA-2: mostra o detalhe dos lotes com saldo de um produto.

### REQ-006 — Consultar validades
- CA-1: um lote está **vencido** quando a validade é anterior a hoje (H5).
- CA-2: um lote está **perto de vencer** quando faltam de 0 a N dias para a validade.
- CA-3: lista os lotes com saldo vencidos e perto de vencer, ordenados por validade.
- CA-4: lotes sem saldo não geram alerta.

### REQ-007 — Configurar antecedência do alerta
- CA-1: N é um inteiro de 0 a 365, alterado pela TUI; o padrão é 30.
- CA-2: o valor persiste entre execuções.

### REQ-008 — Consultar histórico
- CA-1: lista as movimentações da mais recente para a mais antiga, com data e hora, tipo, motivo, produto e quantidade.
- CA-2: o histórico é somente leitura.

### REQ-009 — Painel inicial
- CA-1: ao abrir, a TUI mostra o total de produtos, o total de unidades, a quantidade de lotes vencidos e a de lotes perto de vencer.
- CA-2: a partir do painel, cada tela é alcançável por uma tecla.

### REQ-010 — Persistência local
- CA-1: os dados ficam num arquivo SQLite local e sobrevivem ao reinício.
- CA-2: cada operação é atômica: em caso de erro, nada é gravado.
- CA-3: o local padrão é `$XDG_DATA_HOME/stockwatch/stockwatch.db` e pode ser trocado com `--banco CAMINHO`.

## Requisitos não funcionais

### NFR-001 — Operação por teclado
Todas as funções são acessíveis só pelo teclado, com os atalhos visíveis no rodapé.

### NFR-002 — Estados da interface
Toda tela trata os estados vazio, erro de validação e sucesso com mensagem explícita (REQ-002 CA-2).

### NFR-003 — Volume
Com 10 mil produtos e 1 milhão de movimentações:
- registrar uma entrada ou uma saída leva menos de 50 ms (p95);
- carregar o estoque atual ou as validades leva menos de 1 s (p95).

Metas iniciais, confirmadas ou revistas com a medição da parte 8 (DECISION-003).

### NFR-004 — Determinismo
As regras dependem da data de hoje só por um relógio injetável, e os testes fixam essa data.

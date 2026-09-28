<!-- Fonte oficial da composição de execução: classifica o sistema e seus componentes, define herança documental e liga o grafo versionado ao orquestrador. -->

# EXECUTION_MODEL.md

## Identificação
- ID estável: EXEC-001
- Versão/ciclo: v0.1.0 / ciclo 1
- Estado: aprovado
- Decisão aprovada em: 2026-09-28, pelo responsável (M Lee), no chat

## Classificação composta
- Modo do sistema: `deterministic`
- Justificativa: todas as capacidades da primeira versão — cadastro, entradas, saídas por FEFO, saldo e alertas de validade — são regras de negócio exatas, resolvidas por código tradicional e SQL. Não há necessidade que justifique inferência probabilística, e as instruções do projeto proíbem IA no produto.
- Perfis herdados: núcleo documental comum do modelo v3.0; nenhum perfil especializado de IA.
- Documentos ativados: definidos pela proposta da primeira versão; previstos `PROJECT.md`, `REQUIREMENTS.md`, `CONSTRAINTS.md`, `UX_UI.md`, `ARCHITECTURE.md`, `engineering/ENGINEERING_PRACTICES.md`, `data/DATA_MODEL.md`, `data/DATA_TESTS.md`, `DECISIONS.md`, `ROADMAP.md`, `TASKS.md` e `testing/TESTS.md`.
- Documentos omitidos e justificativa:
  - `PROMPT_AI.md`, `AGENTIC_AI.md`, `HYBRID_SYSTEM.md`: não há componente de IA.
  - `ORCHESTRATION.md`: o software tem uma única parte (ver "Orquestração").
  - Documentos condicionais (desempenho, acessibilidade, segurança, release): aplicabilidade decidida em `DECISIONS.md`.

## Componentes e modos
Camadas internas de uma única parte. Responsabilidades e contratos detalhados pertencem a `ARCHITECTURE.md`.

| ID | Componente | Modo | Responsabilidade | Entrada/saída | Dependências | Fallback | Teste |
|---|---|---|---|---|---|---|---|
| COMP-001 | Domínio | deterministic | Produtos, lotes com validade, movimentações, FEFO e invariantes de estoque | Comandos do serviço / entidades e erros de domínio | Nenhuma | Não aplicável: erro de regra é rejeitado com mensagem explícita | Unitários e baseados em propriedades |
| COMP-002 | Persistência | deterministic | Repositórios sobre SQLite local, com transações | Entidades do domínio / registros no SQLite | COMP-001, SQLite | Rollback da transação e erro exibido; nenhum estado parcial | Integração com SQLite real e volume |
| COMP-003 | TUI | deterministic | Telas de teclado para cadastro, movimentações e consultas | Teclado do operador / chamadas ao serviço e estados de vazio, erro e sucesso | COMP-001, COMP-002, Textual | Não aplicável: falhas aparecem como estado de erro na tela | Testes de interface do Textual e fuzzing das entradas |

## Orquestração
- Há múltiplas partes? não — um monolito local, processo único, usuário único.
- `ORCHESTRATION.md` obrigatório quando sim: não aplicável.
- Existe orquestrador executável? não.
- Responsabilidade limitada do orquestrador: não aplicável.
- Contratos que coordena (referencie IDs): não aplicável.
- Estado e transições: não aplicável.
- Política de retry, timeout, autorização e rollback: não aplicável; rollback de dados é transacional em COMP-002.
- Relações que não pertencem ao orquestrador: não aplicável.

## Grafo canônico
- `graph_id` em `metadata`: pendente — `metadata` ainda não inicializado.
- Escopo (global/subsistema/componente): global.
- Arquivo DBML/Mermaid derivado: pendente.
- Consulta/projeção e versão: pendente.
- Última validação: pendente.

## Fluxo macroscópico
```text
[teclado] → [TUI: validação de formato] → [Domínio: regras e invariantes] → [Persistência: transação SQLite] → [TUI: estado de sucesso ou erro]
```

## Portabilidade
- Contratos neutros de fornecedor: não aplicável ao produto; não há IA.
- Adaptadores Codex/Hermes/outros: não aplicável ao produto. O agente de desenvolvimento lê `AGENTS.md`, importado por `CLAUDE.md`.
- Diferenças cobertas por testes: não aplicável.

## Critérios de mudança
Alterações no modo, fronteira, relação ou contrato exigem nova revisão, atualização do grafo, testes isolados e integrados e nova aprovação.

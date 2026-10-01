<!-- Configuração local do banco de conhecimento de engenharia. O contrato completo pertence ao pacote do modelo documental e não é copiado aqui. -->

# PROJECT_KNOWLEDGE_DB.md

## Contrato de referência
O contrato de `metadata` (entidades, vocabulários, regras de preenchimento, projeções e consultas obrigatórias) é o de `templates/docs/project_knowledge/PROJECT_KNOWLEDGE_DB.md` no modelo documental v3.0 (StudyLab, commit `563d17c`); a visibilidade dos artefatos segue a v3.1 (DECISION-012). Este documento registra somente as escolhas locais.

## Instância
- Arquivo: `metadata/metadata.sqlite3`.
- Esquema: `schemas/project_knowledge/schema.sql`, copiado sem alterações do pacote, commit `563d17c`.
- SHA-256 do esquema: `78b331d6c1b8c701c13f9e0d353f921e702ef6f0d1f715a3f3f05cf4824f5699`.
- Diagramas: `schemas/project_knowledge/full.dbml` e `summary.dbml`.
- O esquema não é alterado localmente; uma mudança exige nova versão do pacote.

## Configuração
- Perfil: amplo (DECISION-002).
- Criptografia: nenhuma adicional, sem backups cifrados (DECISION-002).
- Pessoas: somente pseudônimos; nenhum e-mail ou nome real no banco.

## Convenção de IDs
Prefixo do tipo e número sequencial com três dígitos, estáveis e nunca reutilizados:

| Entidade | Formato | Exemplo |
|---|---|---|
| Projeto | `PRJ-<nome>` | `PRJ-STOCKWATCH` |
| Configuração | `MCFG-NNN` | `MCFG-001` |
| Pessoa | `PER-NNN` | `PER-001` |
| Item de conhecimento | `KI-<ID externo>` | `KI-DECISION-001` |
| Grafo | `GRAPH-NNN` | `GRAPH-001` |
| Nó / aresta | `NODE-<ID estável>` / `EDGE-GRAPH-NNN-NNN` | `NODE-COMP-001` / `EDGE-GRAPH-001-001` |
| Versão / ciclo | `VER-<semver>` / `CYC-NNN` | `VER-0.1.0` / `CYC-001` |

## Métricas de profiling
Tempo, memória, perfis brutos e ambientes são registrados conforme DECISION-003. Uma comparação entre versões só usa medições do mesmo `environment_id`.

## Validação local
Depois de cada escrita no banco:

```sh
sqlite3 metadata/metadata.sqlite3 "PRAGMA foreign_key_check;" "PRAGMA integrity_check;"
```

O resultado esperado é nenhuma linha de `foreign_key_check` e `ok` em `integrity_check`.

## Pendências
- Versão e ciclo: registrados quando houver o commit correspondente, porque `versions.commit_hash` é obrigatório.
- Projeções Markdown: definidas junto com `docs/testing/TESTS.md`.

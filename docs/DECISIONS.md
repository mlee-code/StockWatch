# DECISIONS.md

# DECISION-001 — Identificadores do código em português

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee

## Contexto
Conversa, documentação e mensagens de commit do projeto são escritas em português. Falta definir o idioma dos identificadores do código: classes, funções, variáveis, módulos, tabelas e colunas.

## Problema
Misturar idiomas entre domínio, documentação e código obriga a traduzir cada conceito e enfraquece a rastreabilidade entre requisitos, testes e implementação.

## Decisão
Identificadores do domínio e da aplicação são escritos em português, sem acentos e seguindo a PEP 8 (por exemplo, `Produto`, `Lote`, `registrar_saida`). Palavras reservadas, bibliotecas, APIs de terceiros e termos técnicos consagrados sem tradução usual (`repository`, `fixture`) permanecem como estão.

## Motivação
O vocabulário do código fica igual ao da documentação e do glossário, o que torna direta a ligação entre requisito, teste e implementação.

## Alternativas consideradas
### Alternativa A
- Descrição: identificadores em inglês.
- Vantagens: padrão da indústria, legível para avaliadores estrangeiros.
- Desvantagens: tradução constante entre documentação e código.
- Motivo da rejeição: a coerência com o domínio documentado foi priorizada.

## Consequências
### Positivas
- Um único vocabulário entre documentos, testes e código.
### Negativas
- Código menos familiar para leitores que não falam português.
### Riscos
- Mistura acidental de idiomas. Mitigação: revisão de nomenclatura no `STYLE.md` e nos reviews.

## Documentos afetados
- `docs/GLOSSARY.md` e `docs/STYLE.md`, quando criados.

## Código ou módulos afetados
- Todo o pacote `stockwatch` e o esquema do banco do produto.

## Critério para revisar esta decisão
Intenção de abrir o projeto para contribuição internacional.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-002 — Configuração do banco `metadata`

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee

## Contexto
O modelo documental v3.0 exige inicializar `metadata` antes do primeiro ciclo, com perfil de armazenamento e proteção dos dados decididos pelo responsável.

## Problema
Definir quanto o banco registra e se precisa de criptografia adicional.

## Decisão
- Perfil **amplo**: registra todas as categorias do esquema, sem segredos nem dados pessoais desnecessários; pessoas aparecem por pseudônimo.
- **Sem criptografia adicional** (`encryption_scope = none`), sem backups cifrados.
- Instância em `metadata/metadata.sqlite3`, criada a partir do esquema do pacote em `schemas/project_knowledge/schema.sql`, sem alterações locais.

## Motivação
O conteúdo tem baixa sensibilidade (hashes, métricas, IDs, pseudônimos) e pertence a um projeto de portfólio público. O perfil amplo preserva as comparações entre versões previstas em DECISION-003.

## Alternativas consideradas
### Alternativa A
- Descrição: perfil essencial.
- Vantagens: menos dados.
- Desvantagens: perde métricas detalhadas e comparações entre versões.
- Motivo da rejeição: a comparação de desempenho entre versões é um objetivo explícito.

### Alternativa B
- Descrição: banco criptografado (por exemplo, SQLCipher).
- Vantagens: proteção em repouso.
- Desvantagens: gestão de chave e dependência extra sem risco que as justifique.
- Motivo da rejeição: sem dado sensível a proteger.

## Consequências
### Positivas
- Consultas e comparações diretas com `sqlite3`.
### Negativas
- O arquivo binário no Git não tem diff legível.
### Riscos
- Registrar por engano um dado sensível. Mitigação: minimização e revisão antes de cada inserção.

## Documentos afetados
- `docs/project_knowledge/PROJECT_KNOWLEDGE_DB.md`.

## Código ou módulos afetados
- `metadata/metadata.sqlite3`, `schemas/project_knowledge/`.

## Critério para revisar esta decisão
Inclusão de dados sensíveis, repositório compartilhado com terceiros ou volume que exija outro SGBD.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-003 — Métricas de profiling como base de comparação entre versões

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee

## Contexto
Refatorações futuras precisam demonstrar, com números, que não degradaram desempenho nem consumo de recursos.

## Problema
Sem medições reproduzíveis ligadas a versão, commit e ambiente, a comparação entre versões é subjetiva.

## Decisão
Cada versão executa um conjunto fixo de cenários de profiling e registra os resultados em `metadata`:
- tempo por operação: `performance_metrics`, com estatísticas (média, mediana, desvio, p50/p95/p99, mínimo e máximo), unidade explícita e `baseline_metric_id` apontando para a mesma métrica da versão anterior;
- memória e outros recursos: `resource_measurements`;
- perfis brutos (por exemplo, a saída do `cProfile`): arquivos em `artifacts`, referenciados por URI e hash;
- máquina, sistema e dependências: `environments`, para comparar só medições do mesmo ambiente.

Ferramentas iniciais: `pytest-benchmark` (tempo), `cProfile` (pontos quentes) e `tracemalloc` (memória), confirmadas em `docs/testing/TESTS.md`.

## Motivação
Transforma "a refatoração não piorou o desempenho" numa consulta verificável, usando o esquema existente sem alterá-lo.

## Alternativas consideradas
### Alternativa A
- Descrição: guardar relatórios de benchmark soltos no repositório.
- Vantagens: simples.
- Desvantagens: sem baseline, ambiente ou consulta; comparação manual.
- Motivo da rejeição: não permite comparação sistemática entre versões.

## Consequências
### Positivas
- Regressões de desempenho detectáveis por consulta.
### Negativas
- Custo de execução e registro a cada versão.
### Riscos
- Ruído de medição entre máquinas. Mitigação: comparar somente medições do mesmo `environment` e registrar o intervalo de confiança.

## Documentos afetados
- `docs/testing/TESTS.md` e `docs/project_knowledge/PROJECT_KNOWLEDGE_DB.md`.

## Código ou módulos afetados
- `tests/performance/`.

## Critério para revisar esta decisão
Quando as ferramentas não medirem um cenário relevante ou o custo de execução atrapalhar o ciclo.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-004 — Primeira versão implementada antes da validação detalhada

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee

## Contexto
O projeto é genérico e de portfólio; o responsável ainda não tem preferências detalhadas de produto além de `workspace/PROJECT_CONTEXT.md`, cujas hipóteses aprovou integralmente em 2026-09-28.

## Problema
O loop de proposta exige negociar a proposta até a aprovação exata antes de implementar, mas sem preferências detalhadas a negociação não converge e consome o prazo de dois dias.

## Decisão
`PROJECT_CONTEXT.md`, com todas as hipóteses confirmadas, é o escopo aprovado da v0.1.0. O agente registra o plano em `workspace/proposals/IMPLEMENTATION_PROPOSAL.md` e implementa a primeira versão sem rodadas prévias de feedback. O responsável valida a versão pronta pela TUI e pelo `VERSION_REVIEW.md`; os ajustes seguem o loop normal de proposta a partir do ciclo seguinte.

## Motivação
Um produto utilizável gera feedback mais concreto do que uma discussão abstrata.

## Alternativas consideradas
### Alternativa A
- Descrição: loop de proposta completo antes da implementação.
- Vantagens: aderência total ao processo.
- Desvantagens: negociação sem preferências definidas, com custo alto de prazo.
- Motivo da rejeição: decisão explícita do responsável.

## Consequências
### Positivas
- Versão utilizável dentro do prazo.
### Negativas
- Retrabalho possível após a validação.
### Riscos
- Divergência entre o que foi implementado e o desejado. Mitigação: escopo restrito ao `PROJECT_CONTEXT.md` e review da versão.

## Documentos afetados
- `workspace/proposals/IMPLEMENTATION_PROPOSAL.md`, `docs/ROADMAP.md`.

## Código ou módulos afetados
- Toda a v0.1.0.

## Critério para revisar esta decisão
Válida somente para a v0.1.0; os ciclos seguintes voltam ao loop de proposta.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-005 — Agente executa Git durante a implementação

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee

## Contexto
A prática deliberada 4 do `AGENTS.md` reservava ao humano todas as operações Git. O responsável praticou staging, commits, branches e push pelo lazygit na fundação do repositório e considera o exercício suficiente.

## Problema
Exigir que o humano faça cada commit durante toda a implementação atrasa o ciclo sem novo ganho de aprendizado em Git.

## Decisão
O agente cria branches, commits em Conventional Commits e push durante a v0.1.0, em partes com sentido próprio. Ao fim de cada parte, para e envia um resumo curto e a lista dos arquivos a ler. Merge no `main` e operações destrutivas exigem autorização explícita do humano.

## Motivação
Mantém o aprendizado no que ainda importa, entender o código produzido, e preserva o controle humano sobre o `main`.

## Alternativas consideradas
### Alternativa A
- Descrição: o humano continua fazendo todos os commits.
- Vantagens: mais prática de Git.
- Desvantagens: exercício já considerado suficiente; custo alto de prazo.
- Motivo da rejeição: decisão explícita do responsável.

## Consequências
### Positivas
- Histórico TDD (`test:` → `feat:` → `refactor:`) produzido de forma consistente.
### Negativas
- Menos prática manual de Git.
### Riscos
- Commits além do combinado. Mitigação: parada obrigatória ao fim de cada parte.

## Documentos afetados
- `AGENTS.md` (prática deliberada 4).

## Código ou módulos afetados
- Nenhum.

## Critério para revisar esta decisão
A pedido do responsável.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

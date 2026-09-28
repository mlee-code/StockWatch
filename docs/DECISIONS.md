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

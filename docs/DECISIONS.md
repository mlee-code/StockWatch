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

# DECISION-006 — Documentos condicionais e práticas omitidas na v0.1.0

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-28

## Responsável
M Lee (delegado ao agente por DECISION-004)

## Contexto
O modelo documental pede avaliar documentos condicionais e registrar as omissões. O prazo é de um ciclo.

## Problema
Criar documentos sem uso real diluiria as fontes oficiais e consumiria o prazo.

## Decisão
- `PERFORMANCE_TESTS.md`: omitido; critérios em `TESTS.md` (SUITE-VOL, SUITE-DES) e NFR-003.
- `ACCESSIBILITY_REVIEWS.md`: omitido; a acessibilidade relevante é teclado e texto além da cor (NFR-001, `UX_UI.md`), verificada pela SUITE-TUI.
- `SECURITY_REVIEWS.md`: omitido; sem rede, sem autenticação e sem dados sensíveis. Controles em `ENGINEERING_PRACTICES.md`.
- `DEPLOYMENT.md`, `OPERATIONS.md`: omitidos; a instalação é local por `pipx`, documentada no README.
- `RELEASE_VALIDATION.md`: omitido; os critérios de conclusão estão em `ROADMAP.md` e a validação humana no `VERSION_REVIEW.md`.
- `GLOSSARY.md`, `STYLE.md`, `EXAMPLES.md`: omitidos; os termos do domínio estão definidos em `REQUIREMENTS.md` e o estilo em `ENGINEERING_PRACTICES.md`.
- Containerização e testes de mutação: desvios PRACTICE-DEV-001 e 002.

## Motivação
Proporcionalidade exigida pelo `AGENTS.md`; o rigor dos testes é mantido.

## Alternativas consideradas
### Alternativa A
- Descrição: criar todos os documentos do modelo.
- Vantagens: aderência formal completa.
- Desvantagens: documentos vazios ou duplicados.
- Motivo da rejeição: violaria a unicidade de fontes.

## Consequências
### Positivas
- Menos documentos, cada um com conteúdo real.
### Negativas
- Revisões de segurança e acessibilidade menos formais.
### Riscos
- Surgir um requisito que exija o documento omitido. Mitigação: reavaliar no review da versão.

## Documentos afetados
- `docs/execution/EXECUTION_MODEL.md` ("Documentos omitidos").

## Código ou módulos afetados
- Nenhum.

## Critério para revisar esta decisão
Rede, múltiplos usuários, dados sensíveis ou distribuição pública em larga escala.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-007 — Validade opcional no lote

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-29

## Responsável
M Lee

## Contexto
FR-001: nem todo produto de um pequeno comércio vence (utensílios, produtos de limpeza). A v0.1.0 exigia validade em toda entrada (REQ-003 CA-2, CON-008).

## Problema
Obrigar uma data fictícia distorceria os alertas e o FEFO.

## Decisão
A validade é opcional em cada lote. Um lote sem validade:
- nunca está vencido nem perto de vencer;
- é consumido por último no FEFO, depois de todos os lotes com data;
- pode ser vendido; não entra num descarte por vencimento.

O esquema passa a aceitar `lote.validade` nulo pela migração 2, que reconstrói a tabela conforme o procedimento oficial do SQLite.

## Motivação
O modelo por lote não exige cadastro extra e permite o mesmo produto com lotes com e sem validade.

## Alternativas consideradas
### Alternativa A
- Descrição: marca "não perecível" no produto.
- Vantagens: a entrada nunca pede a data desses produtos.
- Desvantagens: campo e regra a mais; não cobre o mesmo produto com e sem validade.
- Motivo da rejeição: escolha do responsável pela opção recomendada.

## Consequências
### Positivas
- Suporta todo o estoque do comércio.
### Negativas
- Uma validade esquecida numa entrada vira um lote que não vence. A mensagem de sucesso deixa isso explícito.
### Riscos
- Perecível registrado sem data. Mitigação: a mensagem de sucesso mostra "sem validade".

## Documentos afetados
- `REQUIREMENTS.md` (REQ-003 CA-2, REQ-004 CA-2, REQ-005, REQ-006), `CONSTRAINTS.md` (CON-008), `data/DATA_MODEL.md`.

## Código ou módulos afetados
- `dominio.estoque`, `dominio.leitura`, `aplicacao`, `persistencia` (migração 2), `tui`.

## Critério para revisar esta decisão
Pedidos de alerta para produtos sem validade.

## Substitui
- Parte de REQ-003 CA-2 da revisão inicial ("validade obrigatória").

## Substituída por
- Nenhuma.

# DECISION-008 — Modos normal e inserção na TUI

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-29

## Responsável
M Lee

## Contexto
FR-002: o responsável usa vim e lazygit e quer navegar sem tirar as mãos da fileira central do teclado.

## Problema
Com os campos sempre em modo de digitação, as letras não podem servir de comandos dentro dos formulários.

## Decisão
- **Modo normal**, em que as telas abrem:
  - `h`/`l` movem o foco entre áreas (campos, tabelas);
  - `j`/`k` descem e sobem entre campos ou linhas de tabela;
  - `i` entra no modo inserção no campo focado;
  - `Enter` confirma o formulário;
  - `Esc` volta ao painel;
  - as teclas globais (`p`, `e`, `t`, `q`) funcionam.
- **Modo inserção:** o texto vai para o campo, e `Esc` volta ao modo normal.
- O modo atual aparece na tela (`NORMAL` / `INSERÇÃO`).

## Motivação
Atende ao pedido e mantém a TUI operável só pelo teclado (NFR-001), com os atalhos visíveis.

## Alternativas consideradas
### Alternativa A
- Descrição: abrir no modo inserção no primeiro campo.
- Vantagens: lançamento um toque mais rápido.
- Desvantagens: menos previsível para quem espera o comportamento do vim.
- Motivo da rejeição: escolha do responsável.

## Consequências
### Positivas
- Navegação consistente entre telas.
### Negativas
- Um toque a mais (`i`) para começar a digitar.
### Riscos
- Estranheza para quem não conhece o vim. Mitigação: o modo aparece na tela e os atalhos ficam no rodapé.

## Documentos afetados
- `UX_UI.md`, `REQUIREMENTS.md` (NFR-001).

## Código ou módulos afetados
- `tui`.

## Critério para revisar esta decisão
Dificuldade de uso relatada no review da versão.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

# DECISION-009 — Edição de produto e atalhos com contexto na v0.1.0

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-29

## Responsável
M Lee

## Contexto
PROP-001 deixava a edição de produtos fora da v0.1.0. Na validação, o responsável pediu a edição (FR-003) e atalhos que levem o produto em foco para a entrada (FR-004).

## Problema
Sem edição, um erro de digitação no nome ficaria permanente. Sem contexto, o operador redigita o produto que acabou de ver.

## Decisão
- Incluir a edição de nome e categoria na v0.1.0 (REQ-011). A exclusão de produtos continua fora.
- Os atalhos de movimentação (`e`, e `s` na V010-05) herdam o produto destacado na tabela em foco (REQ-012).

## Motivação
Correção de cadastro é necessidade real de uso. Como lotes e movimentações referenciam o produto pelo `id`, renomear não afeta o histórico.

## Alternativas consideradas
### Alternativa A
- Descrição: adiar a edição para o próximo ciclo.
- Vantagens: menor escopo.
- Desvantagens: produto inutilizável depois de um erro de digitação.
- Motivo da rejeição: pedido do responsável na validação.

## Consequências
### Positivas
- Cadastro corrigível; fluxo produto → entrada mais rápido.
### Negativas
- Mais estados na tela de produtos (cadastro e edição).
### Riscos
- Renomear para um nome existente. Mitigação: a mesma regra de unicidade do cadastro (REQ-001 CA-2).

## Documentos afetados
- `REQUIREMENTS.md` (REQ-011, REQ-012), `UX_UI.md`, `ROADMAP.md` (V010-10), PROP-001 ("Não incluído").

## Código ou módulos afetados
- `aplicacao`, `persistencia`, `tui`.

## Critério para revisar esta decisão
Pedido de exclusão de produtos ou de edição de movimentações.

## Substitui
- A exclusão da edição de produtos em PROP-001, "Não incluído".

## Substituída por
- Nenhuma.

# DECISION-010 — Exclusão de produto somente sem movimentações

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-29

## Responsável
M Lee (regra proposta pelo agente, a validar no review da versão)

## Contexto
FR-005 pede a exclusão de produtos. O estoque e o histórico são derivados das movimentações de cada produto.

## Problema
Excluir um produto com movimentações apagaria lotes e histórico, ou deixaria linhas órfãs, e tornaria o estoque passado irreconstituível.

## Decisão
- Um produto só pode ser excluído se nunca teve movimentação: por exemplo, um cadastro feito por engano.
- Com movimentações, a exclusão é rejeitada, e a mensagem explica que o histórico seria perdido.
- A exclusão pede confirmação explícita na TUI.
- A categoria do produto excluído permanece cadastrada.

## Motivação
Preserva o invariante "o estoque é derivado do histórico" e ainda permite desfazer um cadastro errado.

## Alternativas consideradas
### Alternativa A
- Descrição: exclusão lógica (produto "inativo", oculto das listas).
- Vantagens: permite retirar de linha um produto com histórico.
- Desvantagens: estado e filtros a mais em todas as consultas.
- Motivo da rejeição: escopo da v0.1.0; candidata a um ciclo futuro.

### Alternativa B
- Descrição: exclusão em cascata (produto, lotes e movimentações).
- Vantagens: simples.
- Desvantagens: destrói o histórico sem possibilidade de recuperação.
- Motivo da rejeição: perda de dados.

## Consequências
### Positivas
- Cadastros errados podem ser removidos sem risco para o histórico.
### Negativas
- Um produto com histórico continua visível mesmo sem uso.
### Riscos
- O operador não entender por que não consegue excluir. Mitigação: a mensagem explica o motivo.

## Documentos afetados
- `REQUIREMENTS.md` (REQ-013), `UX_UI.md`, `ROADMAP.md` (V010-11).

## Código ou módulos afetados
- `aplicacao`, `persistencia`, `tui`.

## Critério para revisar esta decisão
Pedido para retirar de linha um produto com histórico, o que levaria à exclusão lógica.

## Substitui
- A exclusão de produtos em PROP-001, "Não incluído".

## Substituída por
- Nenhuma.

# DECISION-011 — Licença MIT

## Estado
- [ ] Proposta
- [x] Aceita
- [ ] Rejeitada
- [ ] Substituída
- [ ] Obsoleta

## Data
2026-09-30

## Responsável
M Lee

## Contexto
O repositório é público e faz parte do portfólio; sem licença, legalmente valem todos os direitos reservados.

## Problema
Visitantes e avaliadores não saberiam se podem usar, estudar ou adaptar o código.

## Decisão
Licenciar o StockWatch sob a MIT (`LICENSE`), declarada no `pyproject.toml` (PEP 639) e no README.

## Motivação
É permissiva, curta, amplamente reconhecida e adequada a projetos de portfólio.

## Alternativas consideradas
### Alternativa A
- Descrição: GPL-3.0.
- Vantagens: obriga derivados a manter o código aberto.
- Desvantagens: restringe o reuso em projetos proprietários.
- Motivo da rejeição: o objetivo é divulgação e reuso livre.

## Consequências
### Positivas
- Uso, estudo e adaptação liberados, com atribuição.
### Negativas
- Derivados podem fechar o código.
### Riscos
- Nenhum relevante.

## Documentos afetados
- `README.md`, `pyproject.toml`.

## Código ou módulos afetados
- Nenhum.

## Critério para revisar esta decisão
Uso comercial que exija outra licença.

## Substitui
- Nenhuma.

## Substituída por
- Nenhuma.

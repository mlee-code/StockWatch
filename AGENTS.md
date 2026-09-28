<!-- Instruções operacionais para agentes do projeto StockWatch, adaptadas de templates/AGENTS.md do modelo documental v3.0. -->

# Instruções operacionais locais para agentes

Este arquivo orienta o agente que trabalha neste projeto e nas subpastas sob seu diretório. Ele não é uma API, um protocolo de comunicação entre softwares, uma garantia de segurança ou uma autorização para alterar outras partes do repositório. Agentes e ferramentas que não carregarem este arquivo não ficam automaticamente obrigados por ele.

## Processo obrigatório

Este projeto adota o Processo de Desenvolvimento Assistido por IA disponível em `~/projects/StudyLab/programming/documentation_model/AI_ASSISTED_DEVELOPMENT_NORMATIVE_SPECIFICATION.md` (repositório `github.com/mlee-code/StudyLab`, commit `563d17c`), versão `3.0`.

No início de cada iniciativa, registre `docs/execution/EXECUTION_MODEL.md`. Ele classifica o sistema e cada parte como `deterministic`, `prompt_ai`, `agentic_ai` ou `hybrid`, define a herança documental e identifica o orquestrador somente quando necessário. A classificação pode ser composta: o sistema não precisa ter um único modo.

## Escopo e conexão com o modelo documental

Este arquivo contém as instruções operacionais do agente e é o ponto de entrada para o modelo documental. Ao iniciar o agente, localize a especificação versionada indicada acima; se o caminho estiver ausente, interrompa alterações e peça sua configuração. Leia a especificação e consulte os templates públicos; crie no projeto somente os documentos aplicáveis, sob demanda. Não copie a árvore inteira nem procure ou exponha a governança interna do pacote que produziu o modelo.

Antes de adotar este modelo, se o pacote estiver disponível no repositório ou em caminho local, leia também `programming/documentation_model/AGENTS.md`. Ele é o guia do agente que mantém o modelo e explica sua organização, seus limites e a separação entre materiais públicos e governança interna. Se o pacote for obtido remotamente, use a versão publicada equivalente desse arquivo. Não copie esse `AGENTS.md` mantenedor para o projeto: adapte somente este template para a raiz do consumidor.

O agente deve informar ao humano, em uma frase curta, que encontrou o modelo, qual versão está usando e se o repositório parece novo ou já existente. Um projeto novo segue a inicialização documental. Um projeto com código ou histórico existente deve receber esta pergunta antes de qualquer alteração:

> Este projeto já possui implementação. Deseja criar agora um ponto de retorno no Git e adaptar o software ao modelo documental? Se concordar, farei um commit e push explícitos da versão anterior à adaptação; depois apresentarei a proposta de adoção em `workspace/adoption/EXISTING_SOFTWARE_ASSESSMENT.md` e `workspace/proposals/IMPLEMENTATION_PROPOSAL.md` antes de modificar documentação ou código.

### Adoção autorizada de software existente

Só execute esta sequência depois de uma resposta afirmativa e inequívoca:

1. Inspecione `git status`, branch, remote, histórico recente e arquivos potencialmente sensíveis. Não inclua segredos, chaves, credenciais, artefatos privados ou arquivos fora do repositório.
2. Se houver alterações não versionadas, mostre o escopo e confirme que elas representam o estado que será preservado. Não misture uma mudança nova do usuário com o checkpoint sem explicitar a decisão.
3. Crie um checkpoint antes da adaptação. Use uma mensagem inequívoca, por exemplo: `chore(documentation): checkpoint before documentation-model adoption`. O corpo deve dizer: “Snapshot autorizado do software antes da adaptação ao modelo documental. Esta revisão é o ponto de retorno e não contém a adaptação documental.” Inclua versão, commit, data, branch e estado de testes conhecidos quando disponíveis.
4. Confirme que o commit contém exatamente o estado pré-adaptação, depois faça push para o remote e branch autorizados. Se não houver remote/branch publicável ou o push falhar, pare e informe o bloqueio; não simule sucesso.
5. Registre o hash do checkpoint em `EXISTING_SOFTWARE_ASSESSMENT.md` e em `metadata` quando ele for inicializado.
6. Faça somente inspeção não mutante, testes de caracterização e inventário. Separe comportamento observado, desejado, desconhecido, dívida e hipótese.
7. Produza a proposta de adoção com arquitetura atual, arquitetura-alvo, bancos, migrações, riscos, fatias utilizáveis, testes e plano de compatibilidade. Negocie-a no loop de proposta antes de reorganizar o projeto.

O checkpoint não substitui backup, tag ou branch protegida quando o risco exigir esses mecanismos. O agente deve recomendar a proteção adicional, mas não criá-la silenciosamente.

Antes de alterar documentação ou implementação:

1. Leia o processo e as fontes oficiais aplicáveis em `docs/` e suas subpastas temáticas.
2. Trate `workspace/` como entrada humana ainda não validada e `docs/` como fonte oficial após aprovação.
3. Não transforme hipóteses, exemplos ou observações em requisitos silenciosamente.
4. Preserve uma única fonte oficial para cada conceito e use referências em vez de duplicação.
5. Mantenha requisitos, decisões, tarefas, testes e mudanças rastreáveis entre si.
6. Não implemente enquanto decisões estratégicas necessárias estiverem pendentes.
7. Execute os portões e validações proporcionais ao risco antes de declarar conclusão.
8. Quando o projeto adotar o banco de conhecimento, registre nele execuções de testes, métricas, reviews, aprovações, rastreabilidade e o grafo. Conteúdo e histórico dos documentos ficam em Markdown versionado no Git; o banco só os referencia por caminho, hash e commit.
9. Trate sínteses de evidências (resumos de testes, métricas, reviews e changelog) como projeções regeneráveis do banco. Atualize a consulta ou o template, não o resultado manualmente. Documentos autorais são editados diretamente.
10. Para persistência, leia `docs/data/DATA_MODEL.md` e `docs/data/DATA_TESTS.md` e valide cardinalidade, taxonomias, integridade, navegação, estatística, privacidade e desempenho.
11. Leia `docs/engineering/ENGINEERING_PRACTICES.md` antes de definir arquitetura, código, dados, APIs ou portões técnicos; aplique as práticas pertinentes e justifique desvios em `docs/DECISIONS.md`. Isso inclui a convenção de commits (Conventional Commits, por padrão) e os arquivos de higiene do repositório (`.gitignore`/`.editorconfig`) definidos lá.
12. Para trabalho especializado não coberto, pesquise primeiro padrões, especificações e documentação oficial da tecnologia; registre fonte, versão, data, aplicabilidade e critérios verificáveis.
13. Chame o banco reutilizável de `metadata`. Ele registra o processo de engenharia e é separado dos bancos funcionais do produto.
14. Antes de aprovar arquitetura ou tarefas, confirme que `ARCHITECTURE.md` cobre todas as necessidades iniciais aplicáveis, permite expansão, divide o sistema em capacidades coesas e minimiza dependências.
15. Prefira software determinístico e decomponha soluções para isolar IA na menor parte necessária. Toda dependência de IA exige justificativa, avaliação, orçamento de custo/tokens/latência, guardrails, observabilidade e fallback ou degradação documentada.
16. Modele a arquitetura como um grafo versionado de componentes, fluxos, contratos, dados e dependências. O grafo canônico deve ser persistido em `metadata`; DBML, Mermaid e diagramas humanos são projeções derivadas. Use referências estáveis, não cópias do mesmo fato em IA, agentes e orquestrador.
17. Ordene o trabalho pela menor fatia vertical minimamente utilizável que entregue valor e feedback, sem adiar indefinidamente o funcionamento visível em favor de fundações não bloqueantes.
18. Preserve a independência das partes: em testes que não avaliam integração, simule dependências; altere uma parte por vez, valide-a, depois altere a próxima e somente então integre.
19. Não modifique outra parte ou software externo fora do escopo sem permissão explícita do usuário, necessidade demonstrada, proposta aprovada, testes de compatibilidade e rollback.
20. Mantenha `docs/ROADMAP.md` como fonte do planejamento de ciclos. Cada item deve ter prioridade, ciclo-alvo, versão-alvo, dependências, testes e estado explícito; use `[x]` somente após evidência de conclusão.
21. Atualize o painel de progresso no workspace a partir dos checkboxes de `ROADMAP.md`; o histórico do progresso é o histórico do Git. Percentuais e previsões devem indicar premissas, intervalo e confiança.
22. Mantenha `workspace/PROJECT_STATUS.md` organizado em concluídas, em andamento e próximas. A IA pode extrair campos de texto livre do humano, mas deve mostrar a interpretação e pedir confirmação antes de converter intenção em planejamento aprovado.

## Inicialização de `metadata`

Antes do primeiro ciclo:

1. Apresente ao humano, em resumo, as categorias armazenadas: projeto e versões; pessoas pseudonimizadas; ciclos; identidades de itens de conhecimento e suas relações; grafo arquitetural; referências e hashes de solicitações, propostas e feedback e as aprovações exatas; testes, ambientes, resultados, métricas e avaliações; reviews; projeções e artefatos. Explique que o conteúdo e o histórico dos documentos ficam no Git, não no banco.
2. Recomende o perfil **amplo**, que registra todas essas categorias e referências a evidências, mas nunca segredos, credenciais, chaves privadas, conteúdo pessoal desnecessário ou payload sensível quando um hash/URI protegido bastar.
3. Ofereça também perfil **essencial**, limitado à rastreabilidade indispensável, quando minimização, regulação ou custo justificar. Registre a escolha; silêncio não muda o perfil recomendado.
4. Apresente classificação dos dados e opções de proteção: sem criptografia adicional, arquivo/banco criptografado, campos sensíveis criptografados e backups/exportações criptografados. Informe efeitos sobre busca, correlação, desempenho, recuperação e gestão de chaves.
5. Recomende criptografia em repouso e de backups quando o repositório, dispositivo, sincronização ou conteúdo representar risco. Solicite a decisão humana, registre método e referência da chave; nunca armazene a própria chave no banco ou no repositório.
6. Crie a instância a partir do esquema já validado. O projeto consumidor não altera esse esquema silenciosamente; mudança no formato pertence a uma nova versão do pacote.

### Regras de preenchimento

- Use IDs estáveis e únicos; não use título, posição ou texto mutável como identidade.
- Insira um fato atômico uma vez e relacione-o por chaves estrangeiras.
- Registre timestamps em UTC e versão/commit/ciclo/ambiente sempre que aplicáveis.
- Preserve revisões, eventos, execuções, feedback e avaliações como append-only; correções criam novo registro relacionado.
- Valide enums, unidades, hashes, contagens, JSON e referências antes do commit da transação.
- Diferencie ausente, desconhecido, não aplicável e zero; não invente valores para completar campos.
- Guarde conteúdo estruturado na entidade própria; JSON é reservado a extensões variáveis cuja decomposição não tem consultas ou invariantes próprias.
- Armazene regra/consulta para valores derivados; materializações exigem invalidação e teste de equivalência.
- Referencie artefatos grandes por URI, hash, tipo, sensibilidade e criptografia.
- Use transação: validar → inserir → conferir contagens e chaves → commit. Em falha, rollback; nunca limpe a origem antes da conferência.
- Aplique minimização mesmo no perfil amplo: “máximo” significa máxima rastreabilidade útil, não coleta indiscriminada.

## Comunicação com o humano

- Responda de forma curta e resumida no chat: resultado, decisão necessária, estado e próximo passo.
- Registre entendimento, alternativas, justificativas, plano, riscos, perguntas e evidências com detalhe moderado e organizado em `workspace/`.
- Não despeje análises extensas no chat nem esconda decisões relevantes apenas em mensagens transitórias.
- Não interprete silêncio, ausência de objeção ou aprovação de revisão anterior como autorização.

## Loop obrigatório de proposta

1. Leia uma solicitação em `workspace/requests/`.
2. Produza ou revise `workspace/proposals/IMPLEMENTATION_PROPOSAL.md`, tanto na primeira versão quanto em correções, evoluções ou refatorações.
3. Responda ao humano apenas com uma síntese e solicite avaliação da revisão e hash apresentados.
4. Leia `PROPOSAL_FEEDBACK.md`.
5. Se houver objeção, dúvida ou sugestão, produza nova revisão, novo hash e volte ao passo 3.
6. Faça commit de cada revisão da solicitação, da proposta e do feedback. Registre em `metadata` caminho, SHA-256, commit e decisão de cada revisão e a aprovação exata, associadas ao ciclo e à versão; não copie o texto para o banco.
7. Só avance para documentação e planejamento depois de consultar `metadata` e confirmar que a revisão e o hash exatos estão aprovados; chegar à etapa seguinte significa que essa persistência já foi verificada.
8. Implemente somente a proposta aprovada e formalize documentação, roadmap, tarefas e testes antes de alterar o software.

```text
solicitação → proposta n → feedback → proposta n+1 → ...
→ aprovação exata → documentação → testes → implementação
```

## Modos de trabalho

### Projeto novo

Crie apenas `workspace/PROJECT_CONTEXT.md` e o `AGENTS.md` local inicialmente. Depois de definir a composição de execução, gere sob demanda os documentos necessários, valide-os, negocie a proposta da primeira versão e só então implemente incrementalmente.

### Evolução normal

Classifique a solicitação como correção, feature ou refatoração; execute o loop de proposta; atualize as fontes oficiais; derive tarefas e testes; implemente a revisão aprovada.

### Software existente

1. Comece somente com inspeção não mutante.
2. Preencha `workspace/adoption/EXISTING_SOFTWARE_ASSESSMENT.md` com código, dados, arquitetura, testes, operação e comportamento observados.
3. Separe comportamento observado, comportamento desejado, bugs, dívida técnica, decisões desconhecidas e hipóteses.
4. Crie testes de caracterização antes de mudanças arriscadas.
5. Proponha uma baseline documental e obtenha validação humana.
6. Importe apenas fatos verificados para o banco de conhecimento e para os Markdown preenchidos do próprio projeto.
7. Adote o processo incrementalmente; não reescreva nem reorganize o software inteiro sem proposta aprovada.

Em software existente, não copie templates por antecipação. Crie primeiro somente `workspace/adoption/EXISTING_SOFTWARE_ASSESSMENT.md` e os arquivos necessários para caracterização; adicione cada documento oficial quando a avaliação demonstrar que ele é aplicável.

### Projetos globais, subsistemas e orquestradores

Quando o software possuir duas ou mais partes coordenadas, crie obrigatoriamente `docs/execution/ORCHESTRATION.md` como contrato documental global, mesmo que não exista um orquestrador executável. Ele mantém somente requisitos transversais, ordem, contratos, dependências, políticas de integração, riscos e seleção das versões filhas. Cada parte conserva documentação própria para decisões locais, testes e dados. O agente relaciona as fontes por IDs e pelo grafo em `metadata`, sem copiar requisitos ou históricos. Em um software de uma única parte, `EXECUTION_MODEL.md` pode declarar que não há orquestração global.

## Local dos artefatos

Os Markdown preenchidos, schemas adaptados, banco de conhecimento e evidências pertencem ao repositório do projeto consumidor. Este pacote fornece modelos; o agente deve copiá-los, preenchê-los e mantê-los organizados no projeto em desenvolvimento.

## Encerramento e reinício de versão

Depois de finalizar e testar uma versão:

1. Solicite ou aguarde o preenchimento de `workspace/reviews/VERSION_REVIEW.md`.
2. Valide versão, commit, nota de 0 a 100, comentário, decisão e achados.
3. Para cada achado, proponha o tipo (bug/feature/refatoração) em `workspace/reviews/VERSION_REVIEW_FEEDBACK.md` e aguarde confirmação ou correção do responsável antes de prosseguir. Achados já claramente tipados e sem ambiguidade também passam por esse gate — a confirmação é obrigatória, não opcional para casos óbvios.
4. Persista o review final, seus itens e achados — já com a classificação confirmada — em `metadata`, associado à versão e ao ciclo.
5. Confira hash da entrada, contagens, chaves estrangeiras e consultas de leitura.
6. Formalize cada achado em `docs/reviews/BUGS.md`, `FEATURES.md` ou `REFACTORINGS.md`, registrando no achado qualquer divergência entre o tipo original em `VERSION_REVIEW.md` e o tipo confirmado, e relacione tarefas e testes.
7. Gere os resumos Markdown pelas projeções aprovadas.
8. Limpe somente os campos transitórios do review e do feedback de classificação depois da confirmação da persistência; preserve os templates e registre a limpeza.
9. Reinicie o ciclo como evolução, correção de bug ou refatoração. Nunca apague a única cópia de uma informação.

## Documentos condicionais

Avalie acessibilidade, implantação, operação, desempenho, segurança e validação de release conforme o tipo, o risco e o ambiente do projeto. Registre em `docs/DECISIONS.md` a justificativa para omitir um documento aplicável.

## Limite do contrato documental

Use somente a especificação versionada e os arquivos publicados para o projeto. A governança interna do pacote que produz estes modelos não integra a superfície disponível ao projeto e não deve ser buscada como dependência.

## Regras específicas do projeto

### Natureza do projeto

StockWatch é um projeto de estudo e portfólio que deve parecer e funcionar como um produto real e utilizável. Não há atalhos "de exercício": código limpo, testado e documentado é requisito, não acabamento. Cada decisão deve ser defensável numa entrevista técnica.

### Práticas deliberadas

O projeto existe também para treinar as práticas abaixo. Ao propor ou implementar, torne cada uma visível e verificável; não a substitua por uma alternativa mais rápida sem decisão registrada em `docs/DECISIONS.md`.

1. **TDD canônico:** Red → Green → Refactor → Regression em cada incremento, com o teste falhando pelo motivo correto antes da implementação.
2. **Orientação a objetos e outros paradigmas:** modelagem de domínio orientada a objetos, com uso justificado de estilo funcional (funções puras, imutabilidade) onde ele simplificar regras e testes.
3. **TUI:** a interface de terminal é o produto; teclado primeiro, estados claros de vazio, erro e sucesso.
4. **Git:** o humano executa pessoalmente todas as operações Git — staging, commits, branches, merges, rebase e push —, principalmente pelo **lazygit**, como prática deliberada de aprendizado. O agente ajuda com a divisão dos commits, mensagens em Conventional Commits, nomes de branches e explicações, e não executa comandos Git que alterem o repositório. Comandos somente leitura (`git status`, `git log`, `git diff`) são permitidos.
5. **Bateria de testes:** unitários, baseados em propriedades, integração com SQLite real, fuzzing e testes de volume, cada tipo com critério de aceitação próprio em `docs/testing/TESTS.md`.

### Escopo e prazo

- Meta: concluir a primeira versão em **um único ciclo**, em menos de dois dias a partir de 2026-09-28.
- Proporcionalidade: crie somente os documentos que esse ciclo exige e registre em `docs/DECISIONS.md` a omissão de documentos condicionais. O rigor dos testes não é reduzido pelo prazo; o escopo funcional é.
- O sistema é um monolito local, para um único usuário, sem API e sem acesso concorrente. Não introduza servidor, rede, filas ou multiusuário sem proposta aprovada.
- O sistema é determinístico; não introduza IA no produto.

### Encerramento

Ao concluir a versão, lembre o humano de incluir o projeto no seu banco de dados de perfil, no currículo, no LinkedIn e nos demais canais profissionais.

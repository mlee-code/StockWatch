# PROJECT_CONTEXT.md

> Este arquivo recebe o contexto humano inicial do projeto.
> Preenchido pela IA a partir da descrição do responsável em 2026-09-28.
> Itens marcados **(hipótese)** foram inferidos pela IA e precisam de confirmação; `Pendente` indica resposta ainda inexistente.

## Identidade

### Nome
StockWatch (pacote Python e comando: `stockwatch`, em minúsculas, conforme a PEP 8)

### Descrição curta
Sistema de controle de estoque com interface TUI para pequenos comércios, com registro de entradas e saídas de produtos e controle de validade.

### Estado atual
Planejamento

### Responsável
M Lee

## Origem e motivação

### Como a ideia surgiu
Projeto de estudo e portfólio, escolhido para treinar deliberadamente TDD, orientação a objetos e outros paradigmas, TUI, boas práticas de Git com lazygit e uma bateria completa de testes.

### Por que vale a pena resolver
Pequenos comércios lidam com produtos perecíveis; perder o controle de validade gera desperdício e risco de vender produto vencido. **(hipótese)**

### Resultado que motivou o projeto
Um produto real e utilizável, apresentável no currículo e no LinkedIn, que demonstre código limpo, bem testado e bem documentado.

## Problema

### Descrição
Pequenos comércios precisam saber quanto têm de cada produto e o que está perto de vencer, sem adotar um ERP caro ou complexo. **(hipótese)**

### Contexto
Mercearias e pequenos varejos, operados por uma pessoa num único computador.

### Quem é afetado
- Donos e operadores de pequenos comércios.

### Impacto
- Perdas por vencimento não percebido. **(hipótese)**
- Divergência entre estoque real e estoque percebido. **(hipótese)**

### Frequência e dimensão
Pendente — volume típico de produtos e de movimentações por dia.

### Causas conhecidas ou suspeitas
- Controle feito em papel ou planilha, sem alerta de validade. **(hipótese)**

### Como o problema é resolvido atualmente
Pendente

### Limitações das soluções atuais
- Pendente

### Aspectos atuais que devem ser preservados
- Não se aplica: projeto novo.

## Objetivos

### Objetivo principal
Registrar entradas e saídas de produtos e controlar suas datas de validade por meio de uma TUI local.

### Objetivos secundários
- Servir de portfólio profissional que funcione como produto real.
- Treinar TDD, orientação a objetos e outros paradigmas, TUI, Git com lazygit e testes unitários, baseados em propriedades, de integração com SQLite, fuzzing e de volume.

### Não objetivos
- API ou acesso por outros sistemas.
- Múltiplos usuários ou uso concorrente.
- Execução em servidor ou nuvem.

### Critérios gerais de sucesso
- Uma pessoa sem contato com o código consegue instalar, cadastrar produtos, registrar movimentações e consultar validades apenas pela TUI.
- Todos os tipos de teste listados em "Estratégia de testes esperada" existem e passam.
- README e documentação permitem entender o projeto sem ler o código.

## Público

### Público principal
Operador de pequeno comércio (mercearia, pequeno varejo).

### Públicos secundários
- Recrutadores e avaliadores técnicos que analisam o portfólio.

### Necessidades do público
- Registrar movimentações rapidamente.
- Ver o saldo atual de cada produto.
- Saber o que está vencido ou perto de vencer. **(hipótese)**

### Contexto de uso
Um computador local, uso diário durante o expediente. **(hipótese)**

### Conhecimento esperado
Uso básico de terminal. **(hipótese)**

### Limitações e necessidades de acessibilidade
- Operação completa por teclado.
- Pendente — demais necessidades.

## Proposta

### Solução imaginada
Aplicação de terminal com telas para cadastro de produtos, registro de entradas e saídas e consulta de estoque e validades.

### Valor entregue
Visibilidade do estoque e das validades sem depender de rede ou de serviços externos.

### Diferenciais
- Local, leve e sem dependência de rede.
- Rigor de engenharia visível: testes extensivos e documentação.

### Hipótese de valor
Um fluxo de teclado rápido e alertas de validade bastam para um pequeno comércio controlar perecíveis. **(hipótese)**

## Escopo

### Primeira versão
- Cadastro de produtos.
- Registro de entrada de produtos com data de validade obrigatória.
- Registro de saída de produtos.
- Fornecedor e categoria opcionais.
- Consulta de estoque atual.
- Consulta de produtos vencidos ou perto de vencer, com antecedência configurável pela TUI (padrão: 30 dias).
- Motivo da saída: venda, perda ou descarte por vencimento.

### Fora da primeira versão
- Pendente

### Fora do projeto
- API, rede e múltiplos usuários.

### Funcionalidades futuras conhecidas
- Pendente

### Limites entre o sistema e o ambiente externo
- O sistema não se integra a caixa, PDV ou nota fiscal. **(hipótese)**

## Comportamentos e regras

### Fluxo principal esperado
1. O operador cadastra um produto.
2. O operador registra uma entrada informando quantidade e data de validade.
3. O sistema atualiza o saldo e passa a acompanhar a validade dessa entrada.
4. O operador registra saídas conforme vende ou descarta.

### Fluxos alternativos conhecidos
1. Pendente

### Exceções e falhas conhecidas
- Entrada sem data de validade é rejeitada.
- Saída maior que o saldo disponível. **(hipótese: é rejeitada)**

### Regras de negócio conhecidas
- A data de validade é obrigatória em toda entrada.
- Fornecedor e categoria são opcionais.
- A saída consome primeiro os lotes que vencem antes (FEFO).
- Um produto está "perto de vencer" quando faltam até N dias para a validade; N é configurável pela TUI e vale 30 por padrão.
- Quantidades são unidades inteiras; peso e volume podem ser derivados das unidades.
- Toda saída tem um motivo: venda, perda ou descarte por vencimento.

### Invariantes
- O saldo de um produto nunca é negativo. **(hipótese)**
- Toda quantidade em estoque está associada a uma data de validade.

### Dados de entrada
- Produto: nome e demais campos (Pendente).
- Entrada: produto, quantidade (unidades inteiras), data de validade, fornecedor (opcional).
- Saída: produto, quantidade (unidades inteiras), motivo.
- Categoria (opcional).

### Resultados e saídas
- Saldo atual por produto.
- Lista de produtos vencidos ou perto de vencer. **(hipótese)**
- Histórico de movimentações. **(hipótese)**

## Experiência e interface

### Experiência desejada
- Rápida e operável só pelo teclado.
- Clara quanto ao resultado de cada ação.

### Experiência que deve ser evitada
- Formulários longos para operações frequentes.

### Jornada principal do usuário
1. Abrir o programa no terminal.
2. Ver o resumo do estoque e os alertas de validade. **(hipótese)**
3. Registrar entradas e saídas.

### Informações que precisam estar visíveis
- Saldo por produto.
- Validades próximas ou vencidas. **(hipótese)**

### Estados importantes da interface
- Vazio / Erro de validação / Sucesso / Confirmação.

### Dispositivos e tamanhos de tela
- Terminais de desktop; tamanho mínimo Pendente.

### Acessibilidade
- Navegação completa por teclado.

## Restrições

### Técnicas
- Monolito local, um único usuário, sem acesso concorrente.
- Persistência em SQLite.
- Interface TUI.

### Tecnologias proibidas
- Pendente

### Segurança
- Sem superfície de rede; a proteção é a do sistema operacional local. **(hipótese)**

### Privacidade e dados sensíveis
- Dados de fornecedores podem incluir contatos. **(hipótese)**

### Legais e regulatórias
- Pendente

### Financeiras
- Sem custo: somente ferramentas gratuitas e de código aberto. **(hipótese)**

### Prazo
- Primeira versão em menos de dois dias, a partir de 2026-09-28, em um único ciclo.

### Desempenho e escala
- Pendente — volume alvo para os testes de volume.

### Compatibilidade
- Linux. Pendente — macOS e Windows.

## Arquitetura imaginada

### Visão geral
Monolito local em camadas: domínio orientado a objetos, persistência em SQLite e TUI. **(hipótese)**

### Componentes principais
- Domínio: produtos, lotes com validade e movimentações. **(hipótese)**
- Persistência: repositórios sobre SQLite. **(hipótese)**
- Interface: TUI. **(hipótese)**

### Fluxo de dados esperado
1. TUI → serviço de domínio → repositório → SQLite. **(hipótese)**

### Persistência
Arquivo SQLite local. Pendente — local do arquivo e política de backup.

### Integrações externas
- Nenhuma.

### Tecnologias desejadas
- SQLite.
- Python.
- Textual para a TUI.

### Ambientes e deploy
- Execução local. Pendente — forma de distribuição (pacote, executável, instalação via gerenciador).

## Desenvolvimento e qualidade

### Prioridades
1. Correção das regras de estoque e validade.
2. Qualidade e cobertura da bateria de testes.
3. Usabilidade da TUI.
4. Documentação apresentável.

### Estratégia de testes esperada
- TDD em todos os incrementos.
- Testes unitários.
- Testes baseados em propriedades.
- Testes de integração com SQLite.
- Fuzzing.
- Testes de volume.

### Critérios para considerar a primeira versão pronta
- [ ] Fluxo principal completo operável pela TUI.
- [ ] Todos os tipos de teste presentes e passando.
- [ ] README com instalação, uso e capturas da TUI.
- [ ] Histórico Git limpo, em Conventional Commits.

### Manutenção esperada
Mantido pelo responsável, sem frequência definida.

### Observabilidade esperada
- Pendente

## Riscos, hipóteses e dependências

### Riscos
- Prazo curto para o rigor exigido. Mitigação: cortar escopo funcional, não testes.
- O processo documental completo é pesado para dois dias. Mitigação: criar somente os documentos aplicáveis.

### Hipóteses que precisam ser validadas
- As marcadas **(hipótese)** neste arquivo.

### Dependências externas
- Nenhuma em tempo de execução além do SQLite.

### Decisões já tomadas
- TUI local, monolito, usuário único, sem API.
- Data de validade obrigatória; fornecedor e categoria opcionais.
- Projeto de portfólio com padrão de produto real.
- Um único ciclo.
- Todas as operações Git são feitas pelo humano, principalmente via lazygit; a IA ajuda com mensagens e divisão dos commits.
- Saída por FEFO.
- Antecedência de "perto de vencer" configurável na TUI, padrão 30 dias.
- Quantidades em unidades inteiras.
- Saída registra motivo.
- Linguagem: Python.
- TUI: Textual.

## Referências

### Projetos semelhantes
- Referência: Pendente
- O que observar:
- O que não copiar:

### Referências visuais
- Referência: Pendente
- Elemento relevante:
- Intenção:

### Referências técnicas
- Referência: Pendente
- Por que é relevante:

### Artigos e documentos
- Referência: Pendente
- Informação importante:

## Questões em aberto

### Dúvidas estratégicas
- Nenhuma no momento.

### Dúvidas de produto
- Nenhuma no momento.

### Dúvidas técnicas
- Qual volume de dados os testes de volume devem cobrir?
- Como o software será distribuído?

## Observações adicionais
Ao concluir a versão, incluir o projeto no banco de dados de perfil, no currículo, no LinkedIn e nos demais canais profissionais.

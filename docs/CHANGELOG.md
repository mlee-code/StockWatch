# CHANGELOG

Gerado por `scripts/changelog.py` a partir dos commits convencionais; não editar à mão.

## 0.1.0 — 2026-09-30

### Funcionalidades
- adiciona TUI inicial que abre e fecha com q
- cria pacotes das camadas da arquitetura
- aplica tema neutro em tons de cinza
- adiciona NomeValido e a hierarquia ErroDominio
- cadastra e lista produtos no serviço de estoque
- persiste produtos em SQLite com migrações versionadas
- adiciona tela de produtos com cadastro e listagem
- escolhe o arquivo do banco por --banco ou XDG_DATA_HOME
- permite injetar migrações para testar o rollback
- lê quantidade e data digitadas pelo operador
- modela lotes e movimentações com invariantes
- registra entradas e consulta o estoque no serviço
- persiste lotes e movimentações e deriva o estoque no SQLite
- adiciona telas de entrada e de estoque atual
- aceita lotes sem validade
- adiciona modos normal e inserção às telas
- edita nome e categoria de produto no serviço
- persiste a edição de produto no SQLite
- edita produtos na TUI e abre a entrada com o produto em foco
- planeja saídas por FEFO com regras por motivo
- registra saídas por FEFO no serviço
- adiciona a tela de saída com motivo e produto em foco
- exclui produto sem movimentações no serviço
- exclui produto sem movimentações no SQLite
- exclui produto pela TUI com confirmação
- classifica a validade dos lotes e lê a antecedência do alerta
- consulta validades, configura a antecedência e resume o painel no serviço
- persiste a antecedência e consulta os lotes com saldo no SQLite
- adiciona validades, configuração e painel inicial na TUI
- consulta o histórico de movimentações no serviço
- consulta o histórico no SQLite
- estende o quadro do painel à largura da tela e centraliza o texto
- adiciona a tela de histórico de movimentações

### Correções
- usa parâmetros nomeados na consulta do histórico

### Desempenho
- filtra alertas no banco e soma saldos sem materializar lotes
- limita os alertas listados e conta os alertas do painel no banco

### Refatorações
- centraliza a montagem de ResumoProduto
- extrai o widget LinhaMensagem das telas de formulário
- extrai TelaMovimentacao das telas de entrada e saída
- deriva vencido da classificação de validade

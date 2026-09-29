# UX_UI.md

## Princípios
1. **Teclado primeiro:** toda ação tem um atalho, e o rodapé mostra os atalhos da tela atual (NFR-001).
2. **Formulários curtos:** as operações frequentes (entrada e saída) cabem numa tela, e `Enter` confirma.
3. **Resultado explícito:** toda ação termina com uma mensagem de sucesso ou de erro. A mensagem de erro diz o que corrigir.
4. **Alertas visíveis:** o painel inicial mostra vencidos e perto de vencer sem precisar navegar.

## Jornada principal
Abrir `stockwatch` → painel com resumo e alertas → `e` para entrada ou `s` para saída → confirmar → voltar ao painel com os números atualizados.

## Mapa de telas e atalhos globais

| Tecla | Tela | Requisito |
|---|---|---|
| `i` | Painel inicial | REQ-009 |
| `p` | Produtos (lista e cadastro) | REQ-001, 002 |
| `e` | Registrar entrada | REQ-003 |
| `s` | Registrar saída | REQ-004 |
| `t` | Estoque atual | REQ-005 |
| `v` | Validades | REQ-006 |
| `h` | Histórico | REQ-008 |
| `c` | Configuração | REQ-007 |
| `q` | Sair | — |

## Modos normal e inserção (DECISION-008)
Inspirados no vim e no lazygit. O modo atual aparece na base da tela (`NORMAL` / `INSERÇÃO`).

| Modo | Tecla | Efeito |
|---|---|---|
| Normal (ao abrir uma tela) | `j` / `k` | próximo / anterior campo; numa tabela, próxima / anterior linha |
| | `h` / `l` | área anterior / próxima (campo ou tabela) |
| | `i` | começa a digitar no campo focado |
| | `Enter` | confirma o formulário |
| | `Esc` | volta ao painel |
| | `p` `e` `t` | abre outra tela (sem empilhar telas) |
| Inserção | texto | vai para o campo; `Tab` / `Shift+Tab` trocam de campo sem sair do modo |
| | `Enter` | confirma o formulário e volta ao modo normal |
| | `Esc` | volta ao modo normal |

No modo normal, as letras nunca alteram o conteúdo dos campos. `q` sai do programa somente a partir do painel inicial.

## Estados

| Estado | Apresentação |
|---|---|
| Vazio | texto centralizado que explica a próxima ação (por exemplo: "Nenhum produto. Pressione `p` para cadastrar.") |
| Erro de validação | linha de mensagem (`#mensagem`) em vermelho com o texto do domínio; o foco volta ao primeiro campo |
| Sucesso | linha de mensagem em verde; o formulário é limpo e o foco volta ao primeiro campo |
| Alerta de validade | vencido em vermelho (`$error`), perto de vencer em amarelo (`$warning`), sempre também com texto, nunca só com a cor |

## Layout
- Cabeçalho com o título e a tela atual; rodapé com os atalhos.
- Tabelas (`DataTable`) para listas; `Input` e `Select` para formulários.
- Tamanho mínimo do terminal: 80×24.

## Tema
Tema escuro neutro `stockwatch-neutro` (`src/stockwatch/tui/tema.py`): fundo, superfícies e cor primária em tons de cinza, sem cor dominante. A cor só aparece para estado: sucesso em verde, alerta em âmbar e erro em vermelho. Pedido do responsável em 2026-09-29, na revisão da V010-02.

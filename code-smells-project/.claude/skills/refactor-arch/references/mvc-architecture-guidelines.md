# Guidelines de Arquitetura MVC-Alvo (Fase 3)

Objetivo: definir o que "MVC bem aplicado" significa neste contexto, de forma que sirva de régua para qualquer linguagem/framework de backend — não apenas Flask ou Express.

## Papéis MVC e suas responsabilidades

| Papel | Responsabilidade | O que NÃO deve conter |
|---|---|---|
| **Model** | Representar e acessar dados (queries parametrizadas, mapeamento de entidade); pode conter métodos de domínio simples e coesos sobre o próprio dado (ex.: `is_overdue()`). | Lógica de orquestração entre múltiplas entidades, chamadas HTTP, formatação de resposta de API. |
| **View / Routing** | Registrar rotas HTTP e delegar para o Controller correspondente. Não decide regra de negócio. | Acesso a banco de dados, validação de regra de negócio, lógica condicional além de roteamento. |
| **Controller** | Traduzir a requisição HTTP (parse do body/params) em chamadas para a camada de Service, e traduzir o resultado de volta em uma resposta HTTP (status code, corpo). | SQL cru, regra de negócio complexa, cálculos de domínio — isso pertence ao Service/Model. |
| **Service** (camada de negócio, quando o domínio justifica) | Orquestrar regra de negócio que envolve mais de uma entidade ou passo (ex.: processar um pedido, calcular desconto, validar checkout). | Detalhes de SQL/ORM (isso é do Model) nem parsing de request HTTP (isso é do Controller). |
| **Infra** | Bootstrap de conexão com banco de dados, configuração de driver, criação de schema. | Regra de negócio, rotas. |
| **Config** | Centralizar valores de configuração, lidos de variáveis de ambiente, com defaults seguros apenas para desenvolvimento local. | Nenhum segredo de produção hardcoded. |
| **Middleware** | Cross-cutting concerns: tratamento de erro centralizado, autenticação/autorização, CORS, logging de request. | Lógica de negócio específica de um domínio. |

## Mapeamento agnóstico de nomes de pasta por stack

A mesma responsabilidade MVC pode ter nomes de pasta diferentes dependendo do idioma/convenção da stack — use o que for idiomático, mantendo o papel:

| Papel MVC | Python/Flask | Node.js/Express |
|---|---|---|
| Model | `models/*.py` | `repositories/*.js` (ou `models/` se houver ORM tipo Sequelize/Prisma) |
| Controller | `controllers/*.py` | `controllers/*.js` |
| Service | `services/*.py` | `services/*.js` |
| Routing | `views/*.py` (registra blueprints) | `routes/*.js` |
| Infra | `infra/database.py` | `infra/database.js` |
| Config | `config/settings.py` | `config/index.js` |
| Middleware | `middlewares/*.py` | `middlewares/*.js` |
| Schema/Validação | `schemas/validators.py` | validação dentro do controller ou `schemas/` se o volume justificar |
| Entry point | `app.py` (fino, cria a app via factory) | `app.js` (fino, monta middlewares/rotas e sobe o servidor) |

Regra prática: **não force a existência de uma camada que o projeto não precisa.** Se um projeto não tem regra de negócio complexa o suficiente para justificar uma camada `services/` separada dos controllers (ex.: CRUD simples sem orquestração), é aceitável manter a lógica fina diretamente no controller — desde que ele não vire um God Object. A decisão deve ser documentada no relatório/estrutura final, não assumida silenciosamente.

## Regras de validação da estrutura final

Depois de reestruturar, confirme que:

1. Existe um **entry point único e fino** (composition root) que monta a aplicação — ele não deve conter lógica de negócio nem SQL.
2. **Nenhuma configuração ou segredo está hardcoded** em nenhum arquivo dentro da nova estrutura — tudo passa por uma camada de config lendo de ambiente.
3. Toda query ao banco de dados está isolada na camada de Model (ou Repository), nunca dentro de Controller ou View/Routing.
4. Toda regra de negócio (cálculo, validação de domínio, orquestração) está em Model ou Service — nunca duplicada em múltiplos arquivos.
5. Existe tratamento de erro centralizado (middleware), em vez de cada handler decidir seu próprio formato de erro.
6. A aplicação sobe sem erro e os endpoints originais (capturados antes da refatoração) continuam respondendo, com a única exceção intencional de endpoints removidos por serem vulnerabilidades puras (esses devem passar a responder 404).

## Sobre projetos que já têm alguma organização (ex.: um projeto com `routes/`, `models/`, `services/` parcialmente preenchidos)

Não recrie do zero o que já está correto. Nesse caso:

- Avalie cada pasta/arquivo existente contra a tabela de papéis acima.
- Se um arquivo já cumpre o papel esperado (ex.: `models/task.py` já é um Model coeso), mantenha-o e apenas corrija os anti-patterns internos (duplicação, API deprecated, etc.), sem mover de lugar.
- Se a lógica de negócio estiver vazando para dentro de rotas que deveriam ser só roteamento (ex.: `routes/task_routes.py` fazendo o papel de Controller + regra de negócio ao mesmo tempo), extraia essa lógica para uma camada de Controller (e Service, se o domínio justificar), mantendo o arquivo de rota como fino roteador.
- Documente no relatório final quais pastas já existiam e foram mantidas vs. quais foram criadas/reorganizadas.

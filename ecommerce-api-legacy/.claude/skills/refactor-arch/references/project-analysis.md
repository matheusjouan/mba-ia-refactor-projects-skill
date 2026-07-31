# Heurísticas de Análise de Projeto (Fase 1)

Objetivo: identificar linguagem, framework, dependências, banco de dados e arquitetura atual **sem depender de nenhum projeto específico** — só de artefatos genéricos que qualquer backend expõe.

## 1. Detecção de linguagem

| Sinal | Linguagem |
|---|---|
| `requirements.txt`, `Pipfile`, `pyproject.toml`, arquivos `.py` | Python |
| `package.json`, arquivos `.js`/`.ts`, `node_modules/` | JavaScript/TypeScript (Node.js) |
| `pom.xml`/`build.gradle`, arquivos `.java` | Java |
| `Gemfile`, arquivos `.rb` | Ruby |
| `go.mod`, arquivos `.go` | Go |

Priorize o arquivo de manifesto de dependências (`requirements.txt`, `package.json`, etc.) como fonte de verdade — ele também dá a versão exata das dependências.

## 2. Detecção de framework

- **Python:** procure imports/dependências: `flask` → Flask; `django` → Django; `fastapi` → FastAPI. Confirme a versão lendo a linha exata no manifesto (ex.: `flask==3.1.1`).
- **Node.js:** procure na chave `dependencies` do `package.json`: `express` → Express; `fastify` → Fastify; `koa` → Koa. A versão vem do próprio `package.json` (ex.: `"express": "^4.18.2"`).
- Combine com o padrão de código: Flask usa `app.route`/`add_url_rule`/`Blueprint`; Express usa `app.get/post/put/delete` ou `express.Router()`.

## 3. Detecção de banco de dados

- Procure por strings de conexão, imports de driver (`sqlite3`, `psycopg2`, `pymysql`, `mysql2`, `pg`) e por comandos `CREATE TABLE` no código (SQL cru) ou classes de model de ORM (`db.Model` do Flask-SQLAlchemy, `class X(models.Model)` do Django, `Sequelize.define`).
- Se houver ORM, extraia as entidades pelos nomes das classes de model. Se houver SQL cru, extraia as tabelas pelos comandos `CREATE TABLE <nome>`.
- Note se a conexão é singleton global lazy-init (`if db_connection is None: ...`) ou gerenciada por request/sessão — isso já é um sinal de arquitetura para a Fase 2.

## 4. Inferência de domínio

Não pergunte ao usuário qual é o domínio da aplicação — deduza:

- Nomes de rotas (`/produtos`, `/pedidos`, `/tasks`, `/courses`, `/checkout`) indicam as entidades de negócio.
- Nomes de tabelas/models reforçam a inferência (ex.: `produtos` + `pedidos` + `itens_pedido` → e-commerce; `courses` + `enrollments` + `payments` → plataforma de cursos/LMS com checkout; `tasks` + `categories` + `users` → gerenciador de tarefas).
- Descreva o domínio em uma frase curta e concreta, citando as entidades principais (ex.: "E-commerce API (produtos, pedidos, usuários)").

## 5. Mapeamento da arquitetura atual

Classifique a arquitetura atual em um destes perfis (ou uma combinação):

- **Monólito de poucos arquivos:** toda a aplicação cabe em 3-5 arquivos na raiz, sem pastas de camada.
- **Parcialmente organizado:** já existem pastas por papel (`models/`, `routes/`, `services/`, `utils/`), mas a lógica de negócio ainda vaza para dentro das rotas/controllers, há duplicação entre arquivos, ou faltam camadas (ex.: sem `controllers/` dedicado).
- **God Object/Manager:** uma única classe ou arquivo concentra roteamento, acesso a dados e regra de negócio ao mesmo tempo, independentemente de existirem outras pastas no projeto.

Para chegar a essa classificação, observe:
- Quantos arquivos-fonte existem e qual o tamanho de cada um (arquivos de 200+ linhas fazendo múltiplas responsabilidades são um sinal forte).
- Se as funções de rota (handlers HTTP) contêm SQL/queries diretamente, ou se delegam para uma camada de dados.
- Se a mesma regra de negócio aparece copiada em mais de um lugar.

## 6. Contagem de arquivos analisados

Ao imprimir "Source files: N files analyzed" na Fase 1, conte apenas arquivos-fonte do projeto (código escrito pelo time, não dependências). Exclua explicitamente: `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `*.pyc`, arquivos de lock (`package-lock.json`, `poetry.lock`), bancos de dados (`*.db`), e a própria pasta `.claude/skills/`.

# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Documentação da Solução

> As seções abaixo (Análise Manual, Construção da Skill, Resultados e Como Executar) são a documentação exigida pelo desafio, produzida durante a resolução deste repositório.

## Análise Manual

Análise de código feita antes de construir a skill, para entender concretamente os problemas que ela precisaria detectar e corrigir. Os achados abaixo já refletem a lista completa usada para desenhar o catálogo de anti-patterns da skill (ver seção "Construção da Skill").

### Projeto 1 — `code-smells-project` (Python/Flask — API de E-commerce)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado por concatenação de string | `models.py` (~15 funções, ex.: `get_produto_por_id`, `criar_produto`, `login_usuario`, `buscar_produtos`) | Toda a camada de dados monta SQL concatenando valores vindos direto do request (`"WHERE id = " + str(id)`, `"WHERE email = '" + email + "'"`). Qualquer input malicioso no path, no body ou na query string compromete o banco inteiro — inclusive a rota de login, que compara senha em texto puro dentro da própria query. |
| 2 | **CRITICAL** | Endpoint administrativo executando SQL arbitrário e endpoint destrutivo sem autenticação | `app.py:59-78` (`/admin/query`) e `app.py:52-58` (`/admin/reset-db`) | `/admin/query` recebe uma string SQL do corpo da requisição e executa via `cursor.execute(query)` sem nenhuma validação — é uma backdoor de execução arbitrária de SQL exposta publicamente. `/admin/reset-db` apaga todas as tabelas sem exigir autenticação nem confirmação. |
| 3 | **CRITICAL** | `SECRET_KEY` hardcoded e vazada na resposta de `/health` | `app.py:8` e `controllers.py:289` (`health_check`) | A chave de assinatura de sessão está fixa no código-fonte versionado, e o próprio endpoint de health-check a devolve em texto puro no JSON, junto com `debug: True` — qualquer cliente externo consegue ler o segredo direto da API. |
| 4 | **HIGH** | Senhas armazenadas e retornadas em texto puro | `models.py` (`login_usuario`, `criar_usuario`) e `controllers.py` (`listar_usuarios`, `buscar_usuario`) | Não existe nenhum hashing — a senha do usuário é gravada como veio, comparada como string na query de login, e devolvida integralmente nos endpoints de listagem de usuários. |
| 5 | **MEDIUM** | Queries N+1 dentro de loop | `models.py::get_pedidos_usuario` e `get_todos_pedidos` | Para cada pedido, o código abre um novo cursor para buscar os itens, e para cada item abre outro cursor para buscar o nome do produto — 1 lista de pedidos gera dezenas de round-trips ao banco em vez de um JOIN. |
| 6 | **MEDIUM** | Validação de negócio duplicada e hardcoded em cascata de `if` | `controllers.py::criar_produto`/`atualizar_produto` | A lista de categorias válidas é declarada inline dentro da função (não é uma constante compartilhada), e a mesma sequência de 6+ validações se repete quase idêntica entre criar e atualizar produto. |
| 7 | **LOW** | Efeito colateral de notificação (I/O) misturado no controller | `controllers.py::criar_pedido` (3 `print()` simulando email/SMS/push) | Simulação de disparo de notificação vive dentro do mesmo handler HTTP que trata a criação do pedido, sem nenhuma camada de serviço — dificulta testar e reaproveitar a lógica de notificação. |
| 8 | **LOW** | Nomenclatura inconsistente e falta de padronização de resposta | `controllers.py` (mistura de `"erro"`/`"dados"`/`"mensagem"`/`"sucesso"` como chaves ad-hoc em cada função) | Cada endpoint decide seu próprio formato de resposta JSON, sem um padrão único de sucesso/erro — aumenta o custo de integração para qualquer cliente da API. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API com checkout)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | "God Manager" concentrando roteamento, acesso a dados e regra de negócio | `src/AppManager.js` (141 linhas: `initDb` + `setupRoutes` inteiros na mesma classe) | Uma única classe cria o schema do banco, define todas as rotas HTTP e implementa a regra de aprovação de pagamento no mesmo escopo — viola completamente a separação de camadas do MVC, exatamente o cenário de "God Class" descrito na definição de severidade CRITICAL do desafio. |
| 2 | **CRITICAL** | Credenciais e chave de gateway de pagamento hardcoded | `src/utils.js:2-6` (`dbPass`, `paymentGatewayKey: "pk_live_..."`, `smtpUser`) | Chave de produção de um gateway de pagamento fica hardcoded e versionada no repositório — comprometimento imediato caso o código vaze ou seja publicado. |
| 3 | **CRITICAL** | "Hash" de senha falso (não é criptografia real) | `src/utils.js::badCrypto` (Base64 repetido 10.000 vezes, cortado em 10 caracteres) | Não usa nenhum algoritmo de hash — é Base64 (reversível) repetido, e ainda trunca o resultado, o que aumenta a chance de colisão. Uma senha "protegida" assim é equivalente a texto puro para qualquer atacante. |
| 4 | **HIGH** | N+1 assíncrono com controle manual de callbacks aninhados | `src/AppManager.js::/api/admin/financial-report` (`forEach` de cursos → `forEach` de matrículas → `get` de usuário → `get` de pagamento, tudo em callback) | Em vez de `Promise.all`/`async-await`, o código usa contadores manuais (`coursesPending`, `enrPending`) para saber quando todas as callbacks assíncronas terminaram — frágil, difícil de entender e propenso a bugs de contagem (race conditions silenciosas). |
| 5 | **MEDIUM** | Falta de integridade referencial ao deletar usuário | `src/AppManager.js::DELETE /api/users/:id` | O próprio comentário no código admite o problema ("matrículas e pagamentos ficaram sujos no banco") — deletar um usuário não remove (nem trata) os registros filhos relacionados. |
| 6 | **MEDIUM** | Estado mutável global compartilhado entre requisições | `src/utils.js` (`globalCache = {}`, `totalRevenue = 0` como variáveis de módulo) | Variáveis de nível de módulo são lidas/escritas por qualquer request concorrente — não há isolamento por requisição, o que gera condições de corrida em produção sob carga. |
| 7 | **LOW** | Tratamento de erro inconsistente | Vários callbacks em `src/AppManager.js` (parâmetro `err` frequentemente ignorado ou tratado de forma diferente a cada rota) | Não existe um padrão único de tratamento/formatação de erro — cada rota decide individualmente o que fazer quando a query falha. |

### Projeto 3 — `task-manager-api` (Python/Flask — API de Task Manager, parcialmente organizado)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Hash de senha com MD5 e vazamento do campo `password` na serialização | `models/user.py:29,32` (`hashlib.md5`) e `to_dict()` (retorna `password`) | MD5 é criptograficamente quebrado para senhas (ataques de força bruta/rainbow table são triviais), e o campo de senha (mesmo hasheada) é devolvido em toda resposta de usuário — duplo problema de segurança. |
| 2 | **HIGH** | Lógica de negócio duplicada em 4+ lugares | `models/task.py::is_overdue`, `routes/task_routes.py` (2x), `routes/user_routes.py`, `routes/report_routes.py` (2x) — mesmo bloco `if due_date < utcnow(): if status not in (...)` | Mesmo cálculo de "atraso" é reimplementado manualmente em cada rota em vez de reutilizar o método do model — qualquer mudança na regra de negócio exige editar 5+ arquivos, com alto risco de divergência silenciosa entre eles. |
| 3 | **MEDIUM** | Queries N+1 em relatórios e endpoints de usuário | `routes/report_routes.py::summary_report` (loop `for u in users: Task.query.filter_by(...)`) e `routes/user_routes.py::get_user_tasks` | O relatório de produtividade por usuário dispara uma query de tasks por usuário dentro de um loop Python, em vez de agregar no banco — degrada rapidamente com o crescimento da base. |
| 4 | **MEDIUM** | Uso de APIs deprecated do próprio Flask/SQLAlchemy | `datetime.utcnow()` (~20 ocorrências em `models/`, `routes/`, `services/`, `seed.py`) e `Model.query.get(id)` (12 ocorrências em `routes/*.py`) | `datetime.utcnow()` está deprecated desde o Python 3.12 e `Query.get()` é o padrão legado do SQLAlchemy 1.x — ambos emitem warnings e têm substitutos modernos (`datetime.now(timezone.utc)` e `db.session.get()`), sinal de dívida técnica acumulada mesmo num projeto "organizado". |
| 5 | **LOW** | Código morto: serviço e função nunca usados | `services/notification_service.py` (classe inteira nunca importada) e `utils/helpers.py::process_task_data` (nunca chamada) | Ambos duplicam funcionalidade que deveria estar centralizada (envio de notificação, validação de payload de task) mas nunca chegaram a ser conectados ao fluxo real da aplicação — aumentam a superfície de manutenção sem entregar valor. |
| 6 | **LOW** | Dependências instaladas e nunca utilizadas | `requirements.txt` (`marshmallow`, `requests`, `python-dotenv`) | Três das seis dependências declaradas nunca são importadas em nenhum arquivo do projeto — aumentam a superfície de instalação/segurança (CVEs de pacotes não usados) sem necessidade.

## Construção da Skill

A skill `refactor-arch` foi construída dentro de `code-smells-project/.claude/skills/refactor-arch/` e depois copiada, sem nenhuma alteração, para os outros dois projetos — essa cópia literal (via `cp -r`) foi o próprio teste de agnosticismo: se a skill precisasse de ajuste para funcionar em Node/Express ou no projeto já parcialmente organizado, ela não seria realmente agnóstica.

### Decisões de design

- **`SKILL.md` como processo, arquivos de referência como conhecimento.** O `SKILL.md` só descreve as 3 fases e quando pausar para confirmação; todo o conhecimento de domínio (o que é um anti-pattern, qual severidade, como corrigir) vive nos 5 arquivos de referência. Isso significa que, para ensinar a skill um anti-pattern novo, basta editar `anti-patterns-catalog.md` — nunca o processo em si.
- **Sinais de detecção acionáveis, não descrições vagas.** Cada anti-pattern do catálogo tem um sinal de detecção concreto (ex.: regex `execute\(\s*["'].*["']\s*\+` para SQL Injection, "variável de módulo reatribuída dentro de um handler" para estado global mutável) em vez de "código mal escrito". Isso foi decisivo para a skill realmente *encontrar* os problemas nos 3 projetos, e não apenas produzir texto genérico.
- **Mapeamento de papéis MVC agnóstico de nome de pasta.** As guidelines de arquitetura não fixam nomes de diretório — definem o *papel* (Model, Controller, Service, Routing, Infra, Config, Middleware) e uma tabela de como esse papel se chama idiomaticamente em Flask (`models/`, `views/`) vs Express (`repositories/`, `routes/`). Isso permitiu que a mesma skill produzisse `controllers/produto_controller.py` no projeto 1 e `controllers/checkoutController.js` no projeto 2 sem nenhuma instrução condicional por linguagem no `SKILL.md`.
- **Playbook com transformação 1:1 por anti-pattern.** Cada padrão de refatoração (RF-01 a RF-12) resolve um anti-pattern específico do catálogo, com exemplo antes/depois em Python *e* JavaScript quando aplicável. Isso manteve a Fase 3 consistente entre execuções — a skill não "inventa" uma correção diferente a cada vez para o mesmo problema.

### Anti-patterns incluídos e por quê

O catálogo tem 15 anti-patterns (acima do mínimo de 8), cobrindo as 4 severidades e a detecção obrigatória de APIs deprecated (`datetime.utcnow()`, `Model.query.get()` no ecossistema Flask/SQLAlchemy). Os itens foram escolhidos por aparecerem de forma real nos 3 projetos durante a análise manual — nenhum é hipotético: SQL Injection por concatenação, credenciais hardcoded, hash de senha fraco e God Object/Manager cobrem os problemas CRITICAL/HIGH mais graves; duplicação de regra de negócio, estado global mutável, N+1 e APIs deprecated cobrem os MEDIUM; código morto e dependências não usadas cobrem os LOW. Essa distribuição não foi definida a priori — emergiu diretamente da análise manual dos 3 projetos.

### Como a skill garante agnosticismo de tecnologia

1. A Fase 1 nunca assume uma stack — ela deduz linguagem/framework a partir de artefatos genéricos (`requirements.txt` vs `package.json`, padrões de import, `app.route` vs `router.get`), descritos em `project-analysis.md`.
2. Os sinais de detecção do catálogo têm uma variante por stack quando o anti-pattern se manifesta de forma diferente (ex.: N+1 síncrono em loop `for` no Flask vs. callback assíncrono aninhado com contador manual no Express).
3. A estrutura MVC-alvo é definida por papel, não por nome de pasta fixo (ver tabela em `mvc-architecture-guidelines.md`).
4. O teste definitivo de agnosticismo foi prático: a mesma pasta `.claude/skills/refactor-arch/`, copiada byte a byte, produziu resultados corretos nos 3 projetos (Flask cru, Express com callback hell, Flask parcialmente organizado). Quando a skill precisou de correção (ver "Consolidação incompleta de regra duplicada" abaixo), a mudança foi feita uma vez nos arquivos de referência e copiada de novo para os 3 projetos, que continuam com cópias idênticas.

### Desafios encontrados

- **N+1 além do documentado.** Durante a Fase 3 do projeto 3, apareceu a mesma classe de problema (N+1) em `get_categories`/`get_users` (contagem de tasks por categoria/usuário dentro de um loop), além dos dois pontos já documentados na auditoria. Resolvido aplicando o mesmo padrão RF-08 (agregação via `GROUP BY`) de forma consistente, mesmo sem um finding específico para cada ocorrência.
- **Naive vs. aware datetime ao corrigir `datetime.utcnow()`.** A correção "óbvia" do anti-pattern de API deprecated seria trocar `datetime.utcnow()` por `datetime.now(timezone.utc)` diretamente — mas isso quebra a comparação com colunas `DateTime` do SQLite, que voltam do banco sem timezone (naive), gerando `TypeError` ao comparar naive com aware. A correção real foi um helper `utc_now()` que usa `datetime.now(timezone.utc).replace(tzinfo=None)`, eliminando a chamada deprecated mas preservando naive-datetime em todo o projeto.
- **Regra de negócio "invisível" já existente.** No projeto 3, `models/task.py` já tinha um método `is_overdue()` correto, mas nenhuma rota o chamava — as 6 reimplementações manuais do mesmo cálculo o ignoravam completamente. Isso não seria pego por uma busca ingênua por "código faltando"; só apareceu ao cruzar a definição do método com o grep por padrões duplicados de `if due_date <`.
- **Consolidação incompleta de regra duplicada (apontada na revisão).** Na primeira entrega, o relatório do projeto 3 marcava como HIGH a regra de atraso duplicada e recomendava trocar todas as reimplementações por `Task.is_overdue()`. Mesmo assim, `task_stats` e `summary_report` continuaram com a regra escrita à mão, agora como filtro SQLAlchemy (`due_date < utc_now()` + `status.notin_(["done", "cancelled"])`). A causa estava na skill:
  1. O playbook RF-09 só mostrava a consolidação da forma em memória (`if task.due_date < ...`).
  2. Ao aplicar o RF-08 (trocar o loop que carregava a tabela inteira por uma query), a regra foi reescrita como filtro de banco e a duplicação voltou.
  3. A Fase 3 não conferia se cada ocorrência listada no finding tinha sido resolvida.

  A correção foi feita na skill, não só no código:
  - **Playbook:** novo **RF-09b** (a regra fica no model nas duas formas, `is_overdue()` e `overdue_filter()`, derivadas da mesma constante `CLOSED_STATUSES`) e um aviso no RF-08.
  - **Catálogo:** o AP-08 passou a detectar a regra também em filtros de ORM e em `WHERE` de SQL cru, e exige listar todas as ocorrências no finding.
  - **SKILL.md:** novo passo obrigatório de **verificação de cobertura** na Fase 3, que refaz o grep dos sinais de cada finding no código refatorado e compara os valores calculados com a baseline.

  Depois disso, o `task-manager-api` foi restaurado ao código legado e a skill rodou de novo do zero. Na nova execução, a verificação de cobertura também pegou um N+1 residual em `/users/<id>` e `/users/<id>/tasks`, causado por lazy load de `category` dentro de `to_dict()`, e o corrigiu com `joinedload`.
- **Decisão sobre código morto com valor de negócio ambíguo.** `services/notification_service.py` (projeto 3) nunca era chamado, mas não era código sem propósito — só estava desconectado. A decisão (documentada no relatório) foi removê-lo em vez de conectá-lo, porque nenhuma rota do domínio de tasks tinha um gatilho natural de notificação, e forçar uma integração só para "usar" o código seria escopo além do que a auditoria pedia.

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 12 | 4 | 3 | 3 | 2 |
| 2 — ecommerce-api-legacy | Node/Express | 10 | 3 | 2 | 3 | 2 |
| 3 — task-manager-api | Python/Flask (parcial) | 14 | 2 | 4 | 4 | 4 |

Relatórios completos em [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md) e [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Comparação antes/depois

**Projeto 1 (code-smells-project):** 4 arquivos na raiz (`app.py`, `controllers.py`, `models.py`, `database.py`) → `src/{config,controllers,models,services,schemas,infra,middlewares,views}` + `app.py` fino. SQL Injection eliminado (queries parametrizadas), `/admin/query` (backdoor de SQL arbitrário) removido, `/admin/reset-db` agora exige token, senha com hash real, N+1 de pedidos virou 1 JOIN.

**Projeto 2 (ecommerce-api-legacy):** God Manager (`AppManager.js`, 141 linhas fazendo tudo) → `src/{config,controllers,services,repositories,infra,middlewares,routes}`. Callback hell do relatório financeiro virou `Promise.all`, regra de aprovação de pagamento isolada em `paymentService`, hash de senha reversível trocado por `crypto.scrypt`, `DELETE /api/users/:id` agora remove matrículas/pagamentos em cascade (confirmado via teste).

**Projeto 3 (task-manager-api):** já tinha `models/`, `routes/`, `services/`, `utils/`, mas com regra de negócio dentro das rotas → `src/{config,controllers,models,schemas,infra,middlewares,utils,views}`, com uma camada de `controllers/` nova extraindo a lógica que estava em `routes/*.py`. Outras mudanças:
- MD5 trocado por hash real.
- Regra de "atraso" (antes duplicada em 6 lugares) agora existe só em `src/models/task.py`, como `is_overdue()` (em memória) e `overdue_filter()` (query). `task_stats` e `summary_report` usam `Task.query.filter(Task.overdue_filter())`, e um grep pela condição fora do model não retorna nada.
- `datetime.utcnow()`/`Model.query.get()` deprecated substituídos.
- Exclusão de categoria desassocia as tasks.
- Código morto e dependências não usadas removidos.

### Checklist de validação

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| Fase 1 detecta stack corretamente | ✅ | ✅ | ✅ |
| Fase 2 segue o template de relatório | ✅ | ✅ | ✅ |
| Findings com arquivo + linha exatos | ✅ | ✅ | ✅ |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ (12) | ✅ (10) | ✅ (14) |
| Detecção de APIs deprecated | ✅ (`DEBUG` hardcoded) | — (n/a nesta stack) | ✅ (`datetime.utcnow`, `Query.get`) |
| Fase 2 pausa e pede confirmação | ✅ | ✅ | ✅ |
| Estrutura de diretórios em padrão MVC | ✅ | ✅ | ✅ |
| Configuração extraída, sem hardcoded | ✅ | ✅ | ✅ |
| Models abstraindo dados | ✅ | ✅ (`repositories/`) | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ | ✅ | ✅ |

### Logs de validação (aplicações rodando após a refatoração)

**Projeto 1** — boot + smoke tests:
```
SERVIDOR INICIADO / Rodando em http://localhost:5000
GET /produtos -> 200 | GET /produtos/1 -> 200 | GET /usuarios -> 200
POST /login (correto) -> 200 | POST /login (errado) -> 401
POST /pedidos -> 201 | POST /admin/reset-db sem token -> 401
POST /admin/query (removido) -> 404
```

**Projeto 2** — boot + smoke tests:
```
LMS API rodando na porta 3000...
POST /api/checkout (cartão válido) -> 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (cartão recusado) -> 400
GET /api/admin/financial-report -> 200 (Promise.all, sem contador manual)
DELETE /api/users/1 -> matrícula e pagamento removidos em cascade (confirmado no relatório seguinte)
```

**Projeto 3** — boot + smoke tests:
A mesma bateria de 39 requests rodou contra o código legado (baseline) e contra o refatorado, com o mesmo seed:
```
Serving Flask app 'app_factory' / Debug mode: off   (sem traceback/warning no log)
39/39 requests com o mesmo status code da baseline
  GET /tasks, /tasks/<id>, /tasks/search, /tasks/stats, /users, /users/<id>, /users/<id>/tasks,
  /categories, /reports/summary, /reports/user/<id> -> 200 | ids inexistentes -> 404
  POST /tasks -> 201 (400 com payload inválido) | PUT/DELETE /tasks/<id> -> 200
  POST /users -> 201 (409 email duplicado) | POST /login -> 200 (401 senha errada)
  POST/PUT/DELETE /categories -> 201/200/404

Regra de atraso: valor antes = valor depois, nos 2 momentos (seed e após escritas)
  /tasks/stats overdue           2 = 2   |  2 = 2
  /reports/summary overdue ids   [1, 4]  |  [4, 11]
  /reports/user/1 overdue        2 = 2   |  2 = 2
  /tasks, /tasks/1, /users/1/tasks (flags overdue) iguais

Queries por endpoint (constantes, sem N+1): /tasks 1 | /users/1 2 | /users/1/tasks 2 | /categories 2
DELETE /categories/4 -> 200, 0 tasks com category_id órfão
```

### Observações sobre o comportamento em stacks diferentes

A skill se comportou de forma consistente nos 3 projetos, mas a Fase 3 precisou de julgamento diferente em cada um: no projeto 1 (monólito cru), a maior parte do trabalho foi *criar* camadas que não existiam; no projeto 2, o desafio foi *decompor* uma única classe já grande; no projeto 3, o trabalho foi *extrair* lógica que vazava de uma estrutura já parcialmente correta, sem recriar o que já estava certo. As guidelines de arquitetura (regra "não force uma camada que o projeto não precisa") foram o que permitiu essa adaptação sem exigir instruções diferentes por projeto no `SKILL.md`.

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado e configurado.
- Python 3.12+ (projetos 1 e 3) com um ambiente virtual (`.venv`) e as dependências de cada `requirements.txt` instaladas.
- Node.js 18+ (projeto 2) com `npm install` executado dentro de `ecommerce-api-legacy/`.

### Executar cada projeto

```bash
# Projeto 1 — Python/Flask
cd code-smells-project
.venv/Scripts/python.exe app.py     # Windows; use .venv/bin/python em Linux/Mac
# Servidor em http://localhost:5000

# Projeto 2 — Node/Express
cd ../ecommerce-api-legacy
npm install
node src/app.js
# Servidor em http://localhost:3000

# Projeto 3 — Python/Flask (parcialmente organizado)
cd ../task-manager-api
.venv/Scripts/python.exe seed.py    # popula o banco antes do primeiro boot
.venv/Scripts/python.exe app.py
# Servidor em http://localhost:5000
```

### Executar a skill novamente (auditoria + refatoração)

Dentro de cada projeto, com o Claude Code instalado:

```bash
claude "/refactor-arch"
```

A skill vai (1) imprimir o resumo da Fase 1, (2) gerar e salvar o relatório de auditoria em `reports/audit-project-N.md`, pausando para confirmação, e (3) só reestruturar o código após a confirmação explícita.

### Como validar que a refatoração funcionou

1. Subir o servidor do projeto (comandos acima) e confirmar que não há traceback no console.
2. Testar os endpoints originais listados no relatório de auditoria correspondente (`reports/audit-project-N.md`) — todos devem responder com o status esperado.
3. Conferir que os endpoints removidos por serem vulnerabilidades puras (ex.: `/admin/query` no projeto 1) agora retornam 404.
4. Comparar a estrutura de diretórios resultante (`src/`) com a tabela de mapeamento MVC em `code-smells-project/.claude/skills/refactor-arch/references/mvc-architecture-guidelines.md`.
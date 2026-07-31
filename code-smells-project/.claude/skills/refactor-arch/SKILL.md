---
name: refactor-arch
description: Audita uma codebase (qualquer linguagem/framework), gera um relatório de anti-patterns por severidade e refatora o projeto para o padrão MVC, validando que a aplicação continua funcionando. Use quando o usuário pedir para analisar, auditar ou refatorar a arquitetura de um projeto de backend.
---

# refactor-arch — Auditoria e Refatoração Arquitetural para MVC

Você é um auditor e refatorador de arquitetura de software, agnóstico de linguagem e framework. Sua missão neste projeto é executar, em sequência, 3 fases: **Análise → Auditoria → Refatoração**. Nunca pule uma fase, nunca modifique arquivos antes de o usuário confirmar explicitamente ao final da Fase 2.

Antes de começar, leia os 5 arquivos de referência em `references/`:

- `references/project-analysis.md` — heurísticas para detectar linguagem, framework, banco de dados e mapear a arquitetura atual (Fase 1)
- `references/anti-patterns-catalog.md` — catálogo de anti-patterns com sinais de detecção e severidade (Fase 2)
- `references/audit-report-template.md` — formato exato do relatório de auditoria (Fase 2)
- `references/mvc-architecture-guidelines.md` — regras da arquitetura MVC-alvo e mapeamento agnóstico de camadas (Fase 3)
- `references/refactoring-playbook.md` — padrões concretos de transformação, com exemplos antes/depois (Fase 3)

Estes arquivos contêm o conhecimento de domínio; este SKILL.md contém o processo. Use os dois juntos.

---

## FASE 1 — ANÁLISE

Objetivo: entender a stack e a arquitetura atual antes de julgar qualquer coisa.

1. Detecte linguagem, framework, versão de dependências e banco de dados usando as heurísticas de `references/project-analysis.md` (arquivos-assinatura como `requirements.txt`, `package.json`, imports no código, strings de conexão).
2. Liste todos os arquivos-fonte relevantes do projeto (ignore `node_modules/`, `.venv/`, `__pycache__/`, arquivos de lock, artefatos de build).
3. Infira o domínio da aplicação (do que ela trata) lendo nomes de rotas, tabelas e entidades — não pergunte ao usuário, deduza do código.
4. Mapeie a arquitetura atual: é um monólito em poucos arquivos? Já existe alguma separação de camadas (mesmo que incompleta)? Onde vive a lógica de negócio hoje?
5. Conte tabelas/entidades de banco de dados encontradas (via `CREATE TABLE`, classes de model/ORM, migrations).
6. Imprima um resumo neste formato (adapte os campos ao que for aplicável, mas mantenha a estrutura):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework + versão>
Dependencies:  <dependências relevantes>
Domain:        <domínio inferido da aplicação>
Architecture:  <descrição curta da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/entidades>
================================
```

Não peça confirmação nesta fase — ela é somente leitura e segue direto para a Fase 2.

---

## FASE 2 — AUDITORIA

Objetivo: cruzar o código analisado contra o catálogo de anti-patterns e produzir um relatório confiável, **sem modificar nenhum arquivo**.

1. Para cada anti-pattern de `references/anti-patterns-catalog.md`, procure ativamente pelos sinais de detecção descritos (grep por padrões de código, não apenas leitura superficial) em todos os arquivos-fonte listados na Fase 1.
2. Para cada achado (finding), registre: nome do anti-pattern, severidade (CRITICAL/HIGH/MEDIUM/LOW conforme o catálogo), arquivo e **linha ou intervalo de linhas exato**, descrição do problema, impacto concreto, e recomendação (referenciando o padrão do playbook que resolve o problema).
3. Preste atenção especial à detecção de **APIs deprecated** (ver seção específica no catálogo) — isso é obrigatório no relatório sempre que aplicável à stack detectada.
4. Monte o relatório seguindo **exatamente** o template de `references/audit-report-template.md`, com os findings **ordenados por severidade decrescente (CRITICAL → HIGH → MEDIUM → LOW)**.
5. Garanta um mínimo de 5 findings, com pelo menos 1 CRITICAL ou HIGH, 2 MEDIUM e 2 LOW — se a varredura inicial não atingir isso, aprofunde a busca (heurísticas adicionais, duplicação de código, dependências não usadas, nomenclatura) antes de fechar o relatório.
6. Salve o relatório completo em `reports/audit-project-N.md` na raiz do repositório (mantenha os relatórios de execuções anteriores de outros projetos; não sobrescreva números diferentes do projeto atual).
7. Imprima o relatório no terminal.
8. **Pare e peça confirmação explícita ao usuário antes de prosseguir para a Fase 3.** Pergunte literalmente algo como "Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [y/n]" e aguarde a resposta real do usuário. Nunca assuma "sim" implicitamente. Se o usuário disser não, pare aqui e não modifique nenhum arquivo.

---

## FASE 3 — REFATORAÇÃO

Objetivo: reestruturar o projeto para o padrão MVC eliminando os findings da Fase 2, sem quebrar o comportamento observável da aplicação.

Só execute esta fase após confirmação explícita do usuário na Fase 2.

1. Use `references/mvc-architecture-guidelines.md` para definir a estrutura de diretórios MVC-alvo, adaptada à linguagem/framework detectados na Fase 1 (os nomes de camada mudam por stack — ex.: `models/` vs `repositories/`, `views/` vs `routes/` — mas os papéis MVC são os mesmos).
2. Para cada finding do relatório, aplique o padrão de transformação correspondente em `references/refactoring-playbook.md`. Não invente uma correção diferente do playbook sem justificativa — o playbook existe para manter consistência entre projetos.
3. Extraia toda configuração e segredo hardcoded para uma camada de config, lendo de variáveis de ambiente com defaults seguros apenas para desenvolvimento.
4. Elimine qualquer endpoint/rota que seja puramente uma vulnerabilidade sem valor de produto (ex.: execução de SQL arbitrário vindo do request) — não apenas proteja, remova.
5. Antes de mover código, **capture a lista de rotas/endpoints existentes** (método HTTP + path) para poder comparar depois.
6. Depois de reestruturar, valide a aplicação:
   - Suba o processo da aplicação (comando idiomático da stack: `python app.py` dentro do venv do projeto, `node src/app.js`, etc.) e confirme que ele continua rodando após alguns segundos, sem traceback/erro fatal no stderr.
   - Faça requisições de smoke test contra os mesmos endpoints capturados no passo 5 e confirme que os status codes fazem sentido (equivalentes aos observados antes da refatoração, exceto endpoints removidos por serem vulnerabilidades puras, que devem agora responder 404).
   - Encerre o processo ao final do teste.
7. Se algum boot ou endpoint falhar, corrija o código até a validação passar — nunca declare sucesso com uma falha conhecida.
8. Imprima um resumo final neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore de diretórios resultante>

Validation
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly
  ✓/✗ Findings from the audit report were addressed
================================
```

## Princípios gerais (valem para as 3 fases)

- Agnosticismo de tecnologia: nunca assuma Python ou Flask — sempre confirme a stack na Fase 1 antes de aplicar qualquer heurística ou padrão.
- Precisão sobre volume: um finding com arquivo/linha exatos e sinal de detecção real vale mais que dez findings genéricos.
- A skill deve ser copiável: não hardcode nomes de arquivo/projeto específicos do `code-smells-project` nesta instrução — as heurísticas devem funcionar em qualquer projeto de backend.

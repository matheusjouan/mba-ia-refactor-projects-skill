# Catálogo de Anti-Patterns (Fase 2)

Escala de severidade (definida pelo desafio, baseada em violações de MVC/SOLID):

- **CRITICAL:** falhas graves de arquitetura ou segurança — impedem funcionamento correto, expõem dados sensíveis, ou violam completamente a separação de responsabilidades.
- **HIGH:** fortes violações de MVC/SOLID que dificultam muito manutenção e testes.
- **MEDIUM:** problemas de padronização, duplicação ou performance moderada.
- **LOW:** melhorias de legibilidade, nomenclatura, magic numbers.

Cada anti-pattern abaixo tem um sinal de detecção **acionável** (o que procurar de fato no código, não uma impressão subjetiva). Ao auditar, procure ativamente por esses sinais — não dependa só de leitura corrida.

---

## CRITICAL

### AP-01 — SQL Injection por concatenação de string
**Sinal de detecção:** chamadas `execute(...)`/`cursor.execute(...)`/`db.run(...)`/`db.get(...)`/`db.all(...)` cujo argumento é montado por concatenação (`"SELECT ... " + var`) ou f-string/template string interpolando valores vindos de request/parâmetro, em vez de placeholders (`?`, `%s`, `$1`) com parâmetros separados.
**Por que é CRITICAL:** compromete a integridade e a confidencialidade do banco inteiro; qualquer input do usuário vira comando SQL.
**Correção:** ver playbook RF-01.

### AP-02 — Endpoint administrativo sem autenticação executando ação perigosa
**Sinal de detecção:** rota que executa uma operação destrutiva (deletar/resetar dados) ou executa código/SQL vindo diretamente do corpo da requisição, sem nenhum middleware, decorator ou checagem de token/role antes do handler.
**Por que é CRITICAL:** é uma porta aberta de comprometimento total do sistema, sem nenhuma barreira.
**Correção:** ver playbook RF-03 (proteger com auth) — se o endpoint só existe para permitir execução arbitrária de comandos, ele deve ser **removido**, não apenas protegido.

### AP-03 — Segredo/credencial hardcoded no código-fonte
**Sinal de detecção:** literais de string atribuídos a variáveis com nome `SECRET_KEY`, `password`, `pwd`, `api_key`, `*_KEY`, `token`, ou valores reconhecíveis de credencial (prefixos como `pk_live_`, `sk_`, strings de conexão com usuário/senha embutidos) diretamente no código versionado.
**Por que é CRITICAL:** qualquer pessoa com acesso ao repositório tem a credencial de produção.
**Correção:** ver playbook RF-04.

### AP-04 — Hash de senha fraco, inexistente ou reversível
**Sinal de detecção:** uso de `hashlib.md5`/`hashlib.sha1` para senha; funções de "hash" caseiras que na prática só codificam (Base64, XOR simples, reversíveis); comparação de senha em texto puro (`==` direto, ou dentro da própria query SQL).
**Por que é CRITICAL:** senhas comprometidas em caso de vazamento do banco, sem nenhuma barreira computacional real.
**Correção:** ver playbook RF-05.

---

## HIGH

### AP-05 — Vazamento de dado sensível na resposta da API
**Sinal de detecção:** serialização de model (`to_dict`/`jsonify`/serializer) que inclui campos como `password`, `senha`, `secret_key`, `debug`, tokens internos, sem exclusão explícita desses campos.
**Por que é HIGH:** expõe dados sensíveis a qualquer cliente da API, mesmo sem uma falha de autenticação.
**Correção:** ver playbook RF-06.

### AP-06 — God Object / God Manager (roteamento + dados + regra de negócio no mesmo escopo)
**Sinal de detecção:** uma classe ou arquivo único que (a) define/gerencia a conexão e o schema do banco, (b) registra todas as rotas HTTP, e (c) contém a lógica de negócio de domínio — tudo no mesmo arquivo/classe, geralmente com 100+ linhas fazendo essas 3 coisas juntas. Também se aplica quando funções de rota (controllers) chamam a camada de dados diretamente, sem nenhuma camada de serviço/model separada.
**Por que é HIGH:** impossível testar em isolamento, qualquer mudança tem alto risco de efeito colateral em outra responsabilidade.
**Correção:** ver playbook RF-02 e RF-07.

### AP-07 — Queries N+1 em loop (síncrono ou callback assíncrono aninhado)
**Sinal de detecção Python:** `for` seguido, no corpo do loop, de uma nova chamada `cursor()`/`.query.get(...)`/`session.query(...)`. **Sinal de detecção Node/callback:** `forEach`/`for` contendo uma chamada assíncrona (`db.get`/`db.all`) com callback aninhado, sem `Promise.all`/`await` agregando as chamadas.
**Por que é HIGH:** degrada exponencialmente com o volume de dados e, no caso de callbacks aninhados com contadores manuais, também é frágil e propenso a bugs de concorrência.
**Correção:** ver playbook RF-08.

---

## MEDIUM

### AP-08 — Duplicação de regra de negócio
**Sinal de detecção:** o mesmo bloco de condição/cálculo (3+ linhas, mesma lógica) aparece copiado em 2 ou mais arquivos/funções diferentes, em vez de centralizado em um método/função reutilizável.
**Por que é MEDIUM:** qualquer mudança de regra exige editar múltiplos lugares, com risco de divergência silenciosa entre eles.
**Correção:** ver playbook RF-09.

### AP-09 — Estado global mutável compartilhado entre requisições
**Sinal de detecção:** variável definida no escopo de módulo (fora de qualquer função/classe) que é lida e reatribuída dentro de handlers de rota (`let cache = {}`, `db_connection = None` com lazy-init global), sem isolamento por requisição.
**Por que é MEDIUM:** gera condições de corrida sob carga concorrente e dificulta testes (estado vaza entre testes/requests).
**Correção:** ver playbook RF-10.

### AP-10 — Falta de integridade referencial / cascade ausente
**Sinal de detecção:** operação de `DELETE`/remoção numa tabela "pai" sem nenhuma remoção ou tratamento correspondente nas tabelas/entidades "filhas" que referenciam aquele registro (via foreign key).
**Por que é MEDIUM:** gera dados órfãos e inconsistências que só aparecem depois, difíceis de depurar.
**Correção:** ver playbook RF-11.

### AP-11 — Validação manual duplicada em cascata de `if`, com listas de valores válidos hardcoded inline
**Sinal de detecção:** sequência de 4+ `if`/`elif` validando presença/tipo/formato de campos dentro do próprio handler HTTP, repetida de forma quase idêntica em mais de um endpoint; enums/listas de valores válidos declaradas dentro da função em vez de uma constante compartilhada.
**Por que é MEDIUM:** infla o controller com responsabilidade que não é dele (validação de schema) e duplica regras que deveriam ter uma única fonte de verdade.
**Correção:** ver playbook RF-02 (mover validação para uma camada de schema/service).

### AP-12 — Uso de APIs ou padrões deprecated *(detecção obrigatória)*
**Sinal de detecção — Python/Flask-SQLAlchemy:**
- `datetime.utcnow()` / `datetime.utcnow` — deprecated desde Python 3.12 (gera `DeprecationWarning`); substituto: `datetime.now(timezone.utc)`.
- `Model.query.get(id)` — API legada do Flask-SQLAlchemy/SQLAlchemy 1.x (gera `LegacyAPIWarning` em SQLAlchemy 2.x); substituto: `db.session.get(Model, id)`.
- `app.run(debug=True)` com debug hardcoded (sem gate por variável de ambiente) — não é deprecated, mas é uma configuração perigosa em produção (Werkzeug debugger exposto permite RCE); classificar junto por ser um padrão de configuração obsoleto/inseguro.

**Sinal de detecção — Node.js:** callbacks aninhados de I/O em vez de `async/await` sobre Promises (padrão superado desde Node 8+ com `util.promisify`); dependências no `package.json` com major version muito abaixo do atual/EOL.

**Por que é MEDIUM:** funciona hoje, mas quebra silenciosamente em upgrades futuros de linguagem/framework — dívida técnica que só cresce.
**Correção:** ver playbook RF-09 (consolida a troca de API deprecated junto com a correção de duplicação, quando aplicável) e aplicar a troca direta de API nos demais casos.

---

## LOW

### AP-13 — Efeito colateral de I/O (notificação/log) misturado no controller
**Sinal de detecção:** chamada de `print()`/`console.log()` simulando envio de email/SMS/notificação, ou chamada real de I/O (SMTP, fila), dentro do mesmo handler HTTP que também trata a requisição e a persistência, sem nenhuma camada de serviço dedicada.
**Por que é LOW:** não quebra nada hoje, mas dificulta testar o controller isoladamente e reaproveitar a lógica de notificação.
**Correção:** ver playbook RF-02 (extrair para `services/*_service`).

### AP-14 — Código morto (símbolo/arquivo nunca referenciado)
**Sinal de detecção:** buscar (grep) pelo nome de uma classe/função fora do próprio arquivo onde é definida — zero ocorrências de import ou chamada em qualquer outro lugar do projeto.
**Por que é LOW:** não afeta o comportamento em produção, mas aumenta o custo de manutenção e a confusão sobre o que realmente está em uso.
**Correção:** ver playbook RF-12.

### AP-15 — Dependências instaladas e nunca usadas
**Sinal de detecção:** comparar pacotes declarados em `requirements.txt`/`package.json` contra os `import`/`require` efetivamente usados no código — pacote listado sem nenhuma referência de import é candidato a remoção.
**Por que é LOW:** aumenta a superfície de instalação e de vulnerabilidades (CVEs) de dependências transitivas sem entregar valor algum.
**Correção:** ver playbook RF-12.

---

## Como usar este catálogo na Fase 2

1. Percorra cada anti-pattern e aplique o sinal de detecção nos arquivos-fonte reais do projeto (não pule nenhum arquivo listado na Fase 1).
2. Anote arquivo + linha(s) exatas para cada ocorrência encontrada — isso é obrigatório no relatório.
3. Um mesmo anti-pattern pode gerar múltiplos findings (uma ocorrência por arquivo/função afetada) ou um único finding agregando várias ocorrências semelhantes — use o bom senso: se são 15 funções com o mesmo problema de SQL Injection no mesmo arquivo, pode ser um finding agregado citando o intervalo de linhas; se são problemas em arquivos diferentes, normalmente merecem findings separados.
4. Este catálogo tem 15 anti-patterns, acima do mínimo de 8 exigido — não é necessário usar todos em todo projeto; use os que realmente se aplicam ao código analisado.

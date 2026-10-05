# Playbook de Refatoração (Fase 3)

Cada padrão abaixo (RF-xx) resolve um ou mais anti-patterns do catálogo (AP-xx). Use o exemplo antes/depois como referência de forma, adaptando nomes/domínio ao projeto real — não copie o exemplo literalmente se o código-fonte for diferente.

---

## RF-01 — Parametrização de queries
**Resolve:** AP-01 (SQL Injection).

```python
# ANTES
query = "SELECT * FROM produtos WHERE id = " + str(id)
cursor.execute(query)

# DEPOIS
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

```javascript
// ANTES
db.get(`SELECT * FROM courses WHERE id = ${cid}`, cb)

// DEPOIS
db.get("SELECT * FROM courses WHERE id = ?", [cid], cb)
```

Nunca monte SQL por concatenação ou interpolação de string com valor externo — sempre placeholder (`?`, `%s`, `$1`) + parâmetros separados.

---

## RF-02 — Separação Model (dados) / Service (regra de negócio) / Controller (HTTP)
**Resolve:** AP-06, AP-11, AP-13.

```python
# ANTES (controller fazendo tudo)
def criar_produto():
    dados = request.get_json()
    if not dados.get("nome"): return jsonify({"erro": "nome obrigatorio"}), 400
    # ...5 ifs de validação...
    categorias_validas = ["eletronicos", "livros", "roupas"]
    if dados["categoria"] not in categorias_validas: ...
    produto_id = models.criar_produto(dados["nome"], dados["preco"], ...)
    return jsonify({"id": produto_id})

# DEPOIS
# schemas/validators.py -> valida payload e categorias (constante compartilhada)
# services/produto_service.py -> regra de negócio (desconto, estoque)
# models/produto_model.py -> só SQL parametrizado
# controllers/produto_controller.py
def criar_produto():
    dados = validar_produto(request.get_json())
    produto = produto_service.criar(dados)
    return jsonify(produto.to_dict()), 201
```

O Controller só faz parse de request + chamada de service + resposta HTTP. Nada de SQL ou regra de negócio nele.

---

## RF-03 — Middleware de autenticação/autorização em rotas administrativas
**Resolve:** AP-02.

```python
# ANTES
@app.route("/admin/reset-db", methods=["POST"])
def reset_database(): ...

# DEPOIS
@require_admin_token  # valida header Authorization contra config; 401 se ausente/inválido
@admin_bp.route("/reset-db", methods=["POST"])
def reset_database(): ...
```

Se o endpoint só existe para permitir execução arbitrária de comando/SQL vindo do request (ex.: `/admin/query`), ele deve ser **removido por completo** — não é uma feature legítima, é uma backdoor. Proteger com auth não é suficiente nesse caso.

---

## RF-04 — Externalização de configuração e segredos
**Resolve:** AP-03.

```python
# ANTES
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# DEPOIS (config/settings.py)
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-default")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
```

```javascript
// ANTES (utils.js)
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_..." }

// DEPOIS (config/index.js)
module.exports = {
  dbPass: process.env.DB_PASS,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
}
```

Documente as chaves esperadas em um `.env.example` (sem valores reais), nunca commite `.env` com segredo real.

---

## RF-05 — Hash de senha real
**Resolve:** AP-04.

```python
# ANTES
self.password = hashlib.md5(pwd.encode()).hexdigest()

# DEPOIS (werkzeug já vem com Flask)
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

```javascript
// ANTES (utils.js)
function badCrypto(pwd) { /* base64 repetido 10000x */ }

// DEPOIS
const bcrypt = require('bcrypt')
const hash = await bcrypt.hash(pwd, 10)
const valid = await bcrypt.compare(pwd, hash)
```

---

## RF-06 — Serialização controlada (nunca vazar campos sensíveis)
**Resolve:** AP-05.

```python
# ANTES
def to_dict(self):
    return {"id": self.id, "name": self.name, "password": self.password, ...}

# DEPOIS
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email}
    # password nunca sai daqui — se algum consumidor interno precisar do hash,
    # ele acessa o atributo diretamente, nunca via serialização de API
```

O endpoint de health-check retorna apenas o estritamente necessário (`{"status": "ok"}`), nunca `secret_key`/`debug`/config interna.

---

## RF-07 — Quebra do God Object em Router + Service + Repository
**Resolve:** AP-06.

```javascript
// ANTES: uma classe faz tudo
class AppManager {
  initDb() { /* schema + seed */ }
  setupRoutes(app) {
    app.post('/api/checkout', (req, res) => { /* 5+ níveis de callback */ })
  }
}

// DEPOIS
// infra/database.js        -> só conexão/schema
// repositories/*.js         -> só acesso a dados (courseRepository, paymentRepository, ...)
// services/checkoutService.js -> orquestra com async/await
// controllers/checkoutController.js -> só parse request/response
// routes/checkoutRoutes.js -> router.post('/checkout', checkoutController.checkout)
async function checkout(req, res) {
  const result = await checkoutService.process(req.body)
  res.json(result)
}
```

---

## RF-08 — Eliminação de N+1 via query única (JOIN) ou agregação assíncrona
**Resolve:** AP-07.

```python
# ANTES
for row in pedidos:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))

# DEPOIS
cursor.execute("""
    SELECT p.*, i.* FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.usuario_id = ?
""", (usuario_id,))
```

```javascript
// ANTES: callback aninhado com contador manual
courses.forEach(c => { db.all(..., (err, enrollments) => { enrollments.forEach(...) }) })

// DEPOIS
const results = await Promise.all(courses.map(c => getCourseReportAsync(c.id)))
```

> Atenção: se o loop removido avaliava uma regra de negócio em memória (ex.: `if task.is_overdue()`), a query que o substitui deve usar o filtro exposto pelo model (RF-09b), nunca uma cópia inline da condição. Caso contrário, o RF-08 resolve o N+1 e reintroduz a duplicação do AP-08.

---

## RF-09 — Consolidação de regra duplicada e troca de API deprecated
**Resolve:** AP-08 (em memória e em query, ver RF-09b), AP-12.

```python
# ANTES: bloco repetido em 4+ lugares
if task.due_date < datetime.utcnow():
    if task.status not in ("done", "cancelled"):
        overdue = True

# DEPOIS (models/task.py, único ponto de verdade — também corrige datetime.utcnow deprecated)
from datetime import datetime, timezone

def is_overdue(self) -> bool:
    return self.due_date < datetime.now(timezone.utc) and self.status not in ("done", "cancelled")
# chamado como task.is_overdue() em todos os lugares que hoje reimplementam o cálculo
```

### RF-09b — A mesma regra também precisa existir como filtro de query

Uma regra de negócio costuma aparecer em **duas formas**: avaliada em memória sobre um objeto (`if task.due_date < now and task.status not in (...)`) e avaliada no banco como filtro (`.filter(Task.due_date < now, Task.status.notin_([...]))`, `WHERE due_date < ? AND status NOT IN (...)`, `.filter(t => ...)` sobre uma lista carregada). As duas são a **mesma regra duplicada** e precisam sair do mesmo ponto de verdade no model. Isso vale principalmente depois do RF-08: ao trocar um loop em memória por uma query agregada, **não** reescreva a condição inline. Use o filtro exposto pelo model.

```python
# ANTES: o model tem is_overdue(), mas os controllers reescrevem a regra como filtro SQL
# task_controller.py
overdue = Task.query.filter(
    Task.due_date.isnot(None),
    Task.due_date < utc_now(),
    Task.status.notin_(["done", "cancelled"]),
).count()
# report_controller.py (cópia idêntica)
overdue_tasks = Task.query.filter(
    Task.due_date.isnot(None),
    Task.due_date < utc_now(),
    Task.status.notin_(["done", "cancelled"]),
).all()

# DEPOIS: models/task.py concentra a regra nas duas formas, derivadas da mesma constante
CLOSED_STATUSES = ("done", "cancelled")

class Task(db.Model):
    def is_overdue(self) -> bool:                      # forma em memória
        if not self.due_date:
            return False
        return self.due_date < utc_now() and self.status not in CLOSED_STATUSES

    @classmethod
    def overdue_filter(cls):                           # forma de query (expressão SQL)
        return and_(
            cls.due_date.isnot(None),
            cls.due_date < utc_now(),
            cls.status.notin_(CLOSED_STATUSES),
        )

# controllers passam a só consumir a regra
overdue = Task.query.filter(Task.overdue_filter()).count()
overdue_tasks = Task.query.filter(Task.overdue_filter()).all()
```

O mesmo padrão em outras stacks:

```javascript
// ANTES: regra repetida em SQL cru em dois repositórios
db.all("SELECT * FROM enrollments WHERE expires_at < ? AND status NOT IN ('done','cancelled')", [now])

// DEPOIS: o model exporta o predicado em memória e o fragmento SQL, ambos da mesma constante
const CLOSED_STATUSES = ['done', 'cancelled']
const isExpired = (e, now = new Date()) => e.expiresAt < now && !CLOSED_STATUSES.includes(e.status)
const EXPIRED_WHERE = `expires_at < ? AND status NOT IN (${CLOSED_STATUSES.map(() => '?').join(',')})`
const expiredParams = (now = new Date()) => [now.toISOString(), ...CLOSED_STATUSES]
```

**Critério de conclusão do RF-09** (a Fase 3 deve verificar antes de marcar o finding como resolvido):
1. Todas as ocorrências listadas no finding, em memória **e** em query, foram trocadas por chamadas ao ponto único do model.
2. Um grep pelos sinais da regra no código refatorado (ex.: a comparação de data e a lista de status fechados) só retorna resultados dentro do model. Qualquer resultado em controller, service, view ou repository é uma ocorrência que ficou para trás e precisa ser corrigida.
3. Os endpoints que expõem o valor (contadores, listagens, relatórios) devolvem o mesmo resultado de antes da refatoração com o mesmo seed.

```python
# ANTES
user = User.query.get(user_id)   # API legada do SQLAlchemy 1.x

# DEPOIS
user = db.session.get(User, user_id)
```

---

## RF-10 — Remoção de estado global mutável
**Resolve:** AP-09.

```javascript
// ANTES
let globalCache = {};  // utils.js, compartilhado entre requests concorrentes

// DEPOIS: cache escopado (ex.: injetado no service com TTL/limite),
// ou removido por completo se não houver necessidade real de cache
```

```python
# ANTES
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(...)
    return db_connection

# DEPOIS: conexão gerenciada por request (flask.g) ou por sessão do ORM,
# nunca um singleton mutável em escopo de módulo
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(...)
    return g.db
```

---

## RF-11 — Cascade/integridade referencial explícita
**Resolve:** AP-10.

```javascript
// ANTES
db.run("DELETE FROM users WHERE id = ?", [id]) // enrollments/payments ficam órfãos

// DEPOIS (numa transação, dentro do service)
async function deleteUserCascade(id) {
  await paymentRepository.deleteByUserId(id)
  await enrollmentRepository.deleteByUserId(id)
  await userRepository.delete(id)
}
```

---

## RF-12 — Remoção de código morto e dependências não usadas
**Resolve:** AP-14, AP-15.

Regra objetiva: qualquer símbolo/arquivo sem nenhuma referência de import fora de si mesmo é removido, a menos que tenha valor de negócio óbvio — nesse caso, ele deve ser efetivamente conectado ao fluxo real (ex.: um serviço de notificação nunca chamado deve ser removido, ou passar a ser chamado no ponto do fluxo onde faz sentido, com a decisão documentada no relatório final). Dependências declaradas em `requirements.txt`/`package.json` sem nenhum `import`/`require` correspondente no código são removidas do manifesto.

---

## Ordem sugerida de aplicação na Fase 3

1. RF-04 (config/segredos) primeiro — desbloqueia testar com valores de ambiente sem hardcode.
2. RF-01, RF-05 (correções de segurança pontuais) — não dependem de reestruturação de pastas.
3. RF-02/RF-07 (separação de camadas) — move o código para a estrutura MVC definida nas guidelines.
4. RF-06, RF-03 (fechar vazamento de dados e proteger/remover endpoints perigosos).
5. RF-08, RF-09, RF-10, RF-11 (correções de performance/consistência) — mais fáceis de aplicar já com as camadas separadas.
6. RF-12 (limpeza final) por último, depois que a nova estrutura estiver estável.
7. Verificação de cobertura: para cada finding do relatório, refaça o grep dos sinais de detecção no código refatorado (ver critério de conclusão do RF-09). Isso é obrigatório porque passos anteriores (ex.: RF-08) podem reintroduzir um problema já corrigido.

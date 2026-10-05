```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (SQLAlchemy 2.x)
Dependencies:  flask-cors 4.0.0 (usada); marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0 (declaradas, nunca importadas)
Domain:        Task Manager API (tasks com status/prioridade/prazo, usuários, categorias, relatórios de produtividade e atraso)
Architecture:  Parcialmente em camadas (models/, routes/, services/, utils/), mas as rotas acumulam o papel de
               Controller + validação + acesso a dados + regra de negócio; services/ e utils/ não são usados por ninguém
Source files:  15 files analyzed (.py) + requirements.txt
DB tables:     tasks, users, categories (SQLite via SQLAlchemy, sqlite:///tasks.db)
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code

Summary
CRITICAL: 2 | HIGH: 4 | MEDIUM: 4 | LOW: 4

Findings

[CRITICAL] Hash de senha fraco (MD5)
File: models/user.py:27-32 (set_password e check_password usam hashlib.md5)
Description: A senha é armazenada como hashlib.md5(pwd).hexdigest(), sem salt e sem fator de custo; a verificação compara o MD5 diretamente.
Impact: Em caso de vazamento do banco, as senhas são revertidas por rainbow table ou força bruta em segundos (as senhas do seed, como '1234', saem instantaneamente).
Recommendation: RF-05 — trocar por werkzeug.security.generate_password_hash/check_password_hash.

[CRITICAL] Segredos e credenciais hardcoded no código-fonte
File: app.py:13 (SECRET_KEY = 'super-secret-key-123'), services/notification_service.py:7-10 (email_host, email_user = 'taskmanager@gmail.com', email_password = 'senha123')
Description: A chave de assinatura da aplicação e as credenciais SMTP estão em literais de string no código versionado. A URI do banco (app.py:11) também está fixa.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de sessão e a senha da conta de email.
Recommendation: RF-04 — mover para config/settings.py lendo variáveis de ambiente, com defaults apenas para desenvolvimento.

[HIGH] Vazamento do hash de senha nas respostas da API
File: models/user.py:16-25 (to_dict inclui 'password'), consumido em routes/user_routes.py:33 (GET /users/<id>), 85 (POST /users), 129 (PUT /users/<id>), 209 (POST /login)
Description: to_dict() serializa o campo password sem nenhuma exclusão, e quatro endpoints devolvem esse dicionário ao cliente.
Impact: Qualquer cliente da API recebe o hash MD5 da senha, que é reversível (ver finding anterior).
Recommendation: RF-06 — remover o campo da serialização (to_dict sem password).

[HIGH] Regra de negócio "task atrasada" duplicada em 6 lugares, ignorando o método do model
File: em memória: models/task.py:50-60 (is_overdue(), o ponto único, nunca chamado), routes/task_routes.py:30-39 (get_tasks), routes/task_routes.py:71-80 (get_task), routes/task_routes.py:283-287 (task_stats), routes/report_routes.py:33-43 (summary_report), routes/report_routes.py:132-135 (user_report), routes/user_routes.py:171-180 (get_user_tasks); query: nenhuma ocorrência hoje; SQL: nenhuma ocorrência
Description: A condição `due_date < datetime.utcnow() and status not in ('done', 'cancelled')` é reescrita à mão em 6 handlers, enquanto Task.is_overdue() implementa exatamente a mesma regra e não é chamado por nenhum deles (grep por "is_overdue(" fora da definição retorna zero). task_stats e summary_report carregam a tabela inteira (Task.query.all()) só para contar atrasadas em memória; ao trocar esses loops por query agregada (RF-08), a regra não pode ser reescrita inline como filtro de banco.
Impact: Qualquer mudança na regra (ex.: novo status fechado "archived") exige editar 7 lugares, com risco real de divergência entre /tasks, /tasks/stats, /reports/summary, /reports/user/<id> e /users/<id>/tasks.
Recommendation: RF-09 + RF-09b — expor no model Task a regra nas duas formas, derivadas da mesma constante CLOSED_STATUSES: is_overdue() para uso em memória e overdue_filter() para query. Substituir as 6 ocorrências: get_tasks, get_task, user_report e get_user_tasks passam a usar task.is_overdue(); task_stats e summary_report passam a usar Task.query.filter(Task.overdue_filter()).

[HIGH] Queries N+1 e carga da tabela inteira para agregações
File: routes/task_routes.py:41-57 (get_tasks: User.query.get na linha 42 e Category.query.get na linha 51, dentro do loop de tasks), routes/report_routes.py:53-61 (summary_report: Task.query.filter_by na linha 56, dentro do loop de usuários), routes/report_routes.py:161-163 (get_categories: count por categoria dentro do loop), routes/user_routes.py:22 (get_users: len(u.tasks) dispara lazy load por usuário), routes/task_routes.py:281 e routes/report_routes.py:30 (Task.query.all() só para contar)
Description: Os endpoints de listagem e de relatório fazem uma query por item dentro de loops Python, ou carregam todas as tasks para contar em memória.
Impact: O número de round-trips ao banco cresce linearmente com tasks, usuários e categorias, e as estatísticas leem a tabela inteira a cada request.
Recommendation: RF-08 — joinedload nos relacionamentos, agregação com GROUP BY/func.count e filtros no banco (usando Task.overdue_filter() para a regra de atraso, nunca uma cópia inline).

[HIGH] Rotas acumulam Controller, validação, acesso a dados e regra de negócio
File: routes/task_routes.py:11-299, routes/user_routes.py:10-211, routes/report_routes.py:12-223 (inclui o CRUD de /categories, que não é relatório)
Description: Os blueprints, que deveriam só registrar rotas, fazem parse do request, validação de payload, queries ORM, cálculo de regras e montagem manual da resposta. Não existe camada de Controller, e o CRUD de categorias está dentro de report_routes.py.
Impact: Não dá para testar regra de negócio sem subir o contexto HTTP, e cada mudança de regra exige mexer no arquivo de rotas.
Recommendation: RF-02/RF-07 — separar em views/ (registro de rotas), controllers/ (HTTP para chamada), schemas/ (validação) e models/ (dados e regra), mantendo os models existentes no lugar.

[MEDIUM] Uso de APIs deprecated e configuração insegura
File: datetime.utcnow em 22 ocorrências: models/task.py:15,16,52, models/user.py:14, models/category.py:11, routes/task_routes.py:31,72,215,285, routes/report_routes.py:35,42,45,71,133, routes/user_routes.py:172, services/notification_service.py:35, utils/helpers.py:38, seed.py:66,67,69,70,74; Model.query.get(id) em 16 ocorrências: routes/task_routes.py:42,51,67,117,122,158,188,195,227, routes/user_routes.py:29,94,136,155, routes/report_routes.py:105,192,213; app.run(debug=True) fixo em app.py:34
Description: datetime.utcnow() é deprecated desde o Python 3.12; Query.get() é API legada do SQLAlchemy 1.x (LegacyAPIWarning no 2.x); o debug está ligado no código, sem depender de variável de ambiente.
Impact: Warnings hoje e quebra em upgrades futuros; o debugger do Werkzeug exposto em 0.0.0.0 permite execução remota de código.
Recommendation: RF-09 — datetime.now(timezone.utc) (centralizado em um helper utc_now()) e db.session.get(Model, id); RF-04 — debug lido da config.

[MEDIUM] Validação manual duplicada com listas de valores inline
File: routes/task_routes.py:92-124 (create_task) e 166-198 (update_task), routes/user_routes.py:54-72 (create_user) e 102-122 (update_user); listas de status inline em task_routes.py:110,177, de roles em user_routes.py:71,120, e de novo em models/task.py:39 e utils/helpers.py:75,110-111
Description: Os mesmos if de presença, tamanho, status, prioridade, email e role são repetidos entre create e update, e a lista de status válidos aparece em 5 lugares.
Impact: As regras de validação já divergem (update aceita priority sem checar o tipo; create aceita title sem strip), e uma mudança de enum exige editar vários arquivos.
Recommendation: RF-02 — schemas/validators.py com constantes únicas (TASK_STATUSES, USER_ROLES) usado por create e update.

[MEDIUM] Tratamento de erro não centralizado (bare except)
File: routes/task_routes.py:62,137,204,236, routes/user_routes.py:130,149, routes/report_routes.py:186,207,221, utils/helpers.py:46,49,88
Description: 12 blocos `except:` sem tipo de exceção, cada handler montando o próprio JSON de erro.
Impact: Bugs de programação ficam escondidos atrás de "Erro interno", e o formato de erro varia entre endpoints.
Recommendation: middlewares/error_handler.py com handlers registrados no Flask e exceções de domínio (NotFound, ValidationError) com status code próprio.

[MEDIUM] Exclusão de categoria sem tratar as tasks filhas
File: routes/report_routes.py:211-223 (delete_category)
Description: A categoria é removida, mas as tasks que apontam para ela mantêm o category_id (o SQLite não aplica a foreign key por padrão).
Impact: Tasks ficam com referência para uma categoria inexistente, e /tasks devolve category_id preenchido com category_name null.
Recommendation: RF-11 — desassociar as tasks (category_id = None) na mesma transação, antes de remover a categoria.

[LOW] Código morto: NotificationService nunca usado
File: services/notification_service.py:4-48
Description: A classe nunca é importada fora do próprio arquivo (grep por "NotificationService" retorna só a definição).
Impact: Mantém uma credencial SMTP hardcoded e código sem uso no repositório.
Recommendation: RF-12 — remover.

[LOW] Código morto: utils/helpers.py e métodos de model nunca chamados
File: utils/helpers.py:9-116 (format_date e calculate_percentage são importados em routes/report_routes.py:7 mas nunca chamados; os demais nem são importados), models/task.py:38-48 (validate_status, validate_priority), models/user.py:34-38 (is_admin)
Description: Nenhuma dessas funções ou constantes é chamada em lugar algum do projeto.
Impact: Confunde qual validação e qual regra estão realmente em uso.
Recommendation: RF-12 — remover, aproveitando o que tiver valor (calculate_percentage, VALID_STATUSES) na nova camada de schemas/utils.

[LOW] Imports não utilizados
File: app.py:7 (os, sys, json), routes/task_routes.py:7 (json, os, sys, time), routes/user_routes.py:6 (hashlib, json), routes/report_routes.py:8 (json), models/task.py:3 (json), utils/helpers.py:3-7 (os, json, sys, math, hashlib)
Description: Módulos importados e nunca referenciados.
Impact: Ruído de leitura e falsa indicação de dependências.
Recommendation: RF-12 — remover.

[LOW] Dependências declaradas e nunca usadas
File: requirements.txt:4-6 (marshmallow, requests, python-dotenv)
Description: Nenhum dos três pacotes é importado em arquivo algum. A única menção a "marshmallow" é texto de uma task no seed.py:75.
Impact: Aumenta a superfície de instalação e de CVEs sem uso real.
Recommendation: RF-12 — remover do requirements.txt.

================================
Total: 14 findings
================================
```

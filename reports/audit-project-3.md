```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1160 lines of code

Summary
CRITICAL: 1 | HIGH: 2 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hash de senha com MD5 e vazamento do campo password na serialização
File: models/user.py:16-25 (to_dict retorna password), models/user.py:27-32 (set_password/check_password usam hashlib.md5)
Description: A senha é hasheada com MD5 (criptograficamente quebrado para senhas — ataques de força bruta e rainbow table são triviais), e o método to_dict() devolve o campo password (mesmo hasheado) em toda resposta de usuário.
Impact: Vazamento do banco ou de qualquer resposta de API expõe hashes de senha reversíveis por força bruta em segundos.
Recommendation: RF-05 (hash real com werkzeug.security) + RF-06 (nunca serializar o campo de senha).

[HIGH] Lógica de negócio duplicada em 6+ lugares, ignorando o método já existente no model
File: models/task.py:50-58 (is_overdue() definido mas nunca chamado), routes/task_routes.py:30-39 e 71-80 e 284-292, routes/report_routes.py:34-43 e 132-140, routes/user_routes.py:171-179
Description: O mesmo bloco `if due_date < utcnow(): if status not in (done, cancelled): overdue = True` é reimplementado manualmente em 6 lugares diferentes, mesmo já existindo um método is_overdue() no model Task que nunca é chamado por nenhuma rota.
Impact: Qualquer mudança na regra de "atraso" exige editar 6 arquivos, com alto risco de divergência silenciosa — o próprio código já demonstra esse risco ao ter o método correto ignorado.
Recommendation: RF-09 — consolidar em Task.is_overdue() e substituir todas as reimplementações por chamadas ao método.

[HIGH] Queries N+1 em listagem de tasks e no relatório de produtividade
File: routes/task_routes.py:11-63 (get_tasks: User.query.get e Category.query.get dentro do loop de tasks, linhas 42 e 51), routes/report_routes.py:55-68 (summary_report: Task.query.filter_by dentro do loop de usuários)
Description: Para cada task retornada, o endpoint busca o usuário e a categoria em queries separadas dentro do loop; o relatório de produtividade busca as tasks de cada usuário também dentro de um loop Python.
Impact: Tempo de resposta cresce linearmente com o número de tasks/usuários em vez de usar JOIN/agregação no banco.
Recommendation: RF-08 — substituir por JOIN (SQLAlchemy relationship/joinedload) ou agregação via query única.

[MEDIUM] Uso de APIs deprecated
File: datetime.utcnow() em ~18 ocorrências (models/task.py:52, routes/task_routes.py:31,72,215,285, routes/report_routes.py:35,42,45,71,133, routes/user_routes.py:172, services/notification_service.py:35, utils/helpers.py:38, seed.py) e Model.query.get(id) em 16 ocorrências (routes/task_routes.py:42,51,67,117,122,158,188,195,227, routes/user_routes.py:29,94,136,155, routes/report_routes.py:105,192,213)
Description: datetime.utcnow() está deprecated desde Python 3.12; Model.query.get(id) é a API legada do Flask-SQLAlchemy/SQLAlchemy 1.x, substituída por db.session.get(Model, id) no SQLAlchemy 2.x.
Impact: Ambos emitem warnings hoje e podem quebrar em upgrades futuros de linguagem/framework — dívida técnica silenciosa mesmo num projeto já "organizado".
Recommendation: RF-09 — trocar por datetime.now(timezone.utc) e db.session.get().

[MEDIUM] Tratamento de erro genérico (bare except) mascarando falhas
File: routes/task_routes.py:62,137,204,236, routes/user_routes.py:130,149, routes/report_routes.py:186,207,221, utils/helpers.py:46,49,88
Description: 12 blocos `except:` sem especificar o tipo de exceção, escondendo qualquer erro (incluindo bugs de programação) atrás de uma mensagem genérica de "erro interno".
Impact: Dificulta diagnosticar falhas reais em produção; erros inesperados (ex.: bug de código) são tratados igual a uma falha de negócio esperada.
Recommendation: Tratamento de erro centralizado via error handler do Flask, capturando exceções específicas.

[MEDIUM] SECRET_KEY hardcoded
File: app.py:13
Description: app.config['SECRET_KEY'] = 'super-secret-key-123' está fixo no código-fonte versionado.
Impact: Compromete a assinatura de sessão da aplicação caso o repositório vaze.
Recommendation: RF-04 — mover para variável de ambiente.

[LOW] Código morto: serviço nunca conectado ao fluxo real
File: services/notification_service.py:4-48 (classe NotificationService inteira)
Description: A classe é definida com métodos de envio de email/notificação, mas nunca é importada por nenhuma rota do projeto — grep por "NotificationService"/"notification_service" não retorna nenhum uso fora do próprio arquivo.
Impact: Aumenta a superfície de manutenção (inclusive contém uma senha de SMTP hardcoded) sem entregar nenhum valor real, já que nunca é executado.
Recommendation: RF-12 — remover, ou conectar de fato ao fluxo de criação/atraso de tasks se o valor de negócio for confirmado.

[LOW] Código morto: função de validação nunca chamada
File: utils/helpers.py:57-97 (process_task_data)
Description: Duplica a validação de payload de task já feita manualmente em routes/task_routes.py, mas nunca é importada/chamada por nenhuma rota.
Impact: Confunde qual é a validação "real" em uso, aumentando custo de manutenção.
Recommendation: RF-12 — remover ou usar como a validação oficial (substituindo a duplicada em task_routes.py).

[LOW] Dependências instaladas e nunca usadas
File: requirements.txt (marshmallow, requests, python-dotenv)
Description: Três das seis dependências declaradas nunca são importadas em nenhum arquivo do projeto (confirmado por busca em todo o código-fonte).
Impact: Aumenta a superfície de instalação e de vulnerabilidades (CVEs) de dependências transitivas sem necessidade.
Recommendation: RF-12 — remover do requirements.txt.

================================
Total: 9 findings
================================
```

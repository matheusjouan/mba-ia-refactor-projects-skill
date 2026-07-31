```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] SQL Injection por concatenação de string
File: models.py:28,68,92,105-120,133-169,171-233,275-283,289-299
Description: Praticamente toda a camada de dados monta SQL concatenando valores vindos direto do request, em vez de usar placeholders parametrizados. Ocorre em ~15 funções (get_produto_por_id, criar_produto, atualizar_produto, deletar_produto, get_usuario_por_id, login_usuario, criar_usuario, criar_pedido, get_pedidos_usuario, get_todos_pedidos, atualizar_status_pedido, buscar_produtos, entre outras).
Impact: Qualquer input malicioso no path, no body ou na query string compromete o banco inteiro (leitura, alteração ou destruição de dados).
Recommendation: RF-01 — parametrizar todas as queries com placeholders (?) e parâmetros separados.

[CRITICAL] Endpoint administrativo executando SQL arbitrário do request, sem autenticação
File: app.py:59-78
Description: A rota /admin/query recebe uma string SQL inteira no corpo da requisição (dados.get("sql")) e a executa diretamente via cursor.execute(query), sem nenhuma validação, autenticação ou allowlist de comandos.
Impact: Backdoor de execução arbitrária de SQL exposta publicamente — controle total do banco de dados por qualquer requisição HTTP não autenticada.
Recommendation: RF-03 — remover o endpoint por completo (não é uma feature legítima, é uma vulnerabilidade).

[CRITICAL] Endpoint destrutivo sem autenticação
File: app.py:47-58
Description: A rota /admin/reset-db apaga todo o conteúdo das 4 tabelas (produtos, usuarios, pedidos, itens_pedido) sem exigir nenhum token, sessão ou confirmação.
Impact: Qualquer cliente pode zerar a base de produção com uma única requisição POST.
Recommendation: RF-03 — proteger com middleware de autenticação/autorização de admin.

[CRITICAL] Segredo hardcoded e vazado na resposta da API
File: app.py:7 (SECRET_KEY) e controllers.py:289 (health_check retorna o mesmo valor no JSON)
Description: SECRET_KEY = "minha-chave-super-secreta-123" está fixo no código-fonte versionado, e o endpoint /health devolve esse mesmo valor (além de debug=True) em texto puro na resposta.
Impact: Qualquer cliente externo consegue ler a chave de assinatura de sessão da aplicação direto de um endpoint público de health-check.
Recommendation: RF-04 — mover para variável de ambiente; RF-06 — remover campos de config sensível da resposta de /health.

[HIGH] Senha armazenada e comparada em texto puro
File: models.py:105-120 (login_usuario compara senha direto na query SQL), models.py:122-131 (criar_usuario grava sem hash), controllers.py (listar_usuarios/buscar_usuario devolvem o campo senha)
Description: Não existe nenhum hashing de senha — o valor é gravado como veio, comparado como string literal dentro da própria query de login, e devolvido integralmente nos endpoints de usuário.
Impact: Vazamento do banco (ou de qualquer resposta de API) expõe todas as senhas dos usuários diretamente, sem nenhuma barreira computacional.
Recommendation: RF-05 — hash real com werkzeug.security; RF-06 — nunca serializar o campo de senha.

[HIGH] Controllers chamando a camada de dados diretamente, sem service nem schema de validação
File: controllers.py:1-292 (todas as funções — ex.: criar_produto:24-63, atualizar_produto:64-103)
Description: As funções do controller fazem parse do request, validação manual em cascata de if, e chamam models.* diretamente, sem nenhuma camada de serviço ou schema intermediária. Categorias válidas ficam hardcoded inline na função (linha 52), duplicadas entre criar e atualizar produto.
Impact: Impossível testar validação e regra de negócio isoladamente do Flask; qualquer mudança de regra exige tocar em múltiplas funções quase idênticas.
Recommendation: RF-02 — extrair schemas/validators.py (validação) e services/*_service.py (regra de negócio), deixando o controller fino.

[HIGH] Queries N+1 em loop
File: models.py:133-169 (criar_pedido — cursor novo por item do pedido), models.py:171-201 (get_pedidos_usuario) e models.py:203-233 (get_todos_pedidos) — cursor aninhado por pedido e por item
Description: Para cada pedido, o código abre um cursor novo para buscar os itens, e para cada item abre outro cursor para buscar o nome do produto — dezenas de round-trips ao banco para uma única listagem.
Impact: Degrada exponencialmente com o volume de pedidos/itens; tempo de resposta cresce de forma não-linear.
Recommendation: RF-08 — substituir por uma única query com JOIN.

[MEDIUM] Validação duplicada com valores válidos hardcoded inline
File: controllers.py:24-63 (criar_produto) e controllers.py:64-103 (atualizar_produto), especialmente linha 52 (categorias_validas declarada dentro da função)
Description: A mesma sequência de 6+ validações (nome, preço, estoque, categoria) é repetida quase idêntica entre criar e atualizar produto, e a lista de categorias válidas não é uma constante compartilhada.
Impact: Qualquer nova categoria ou regra de validação precisa ser alterada em múltiplos lugares, com risco de divergência.
Recommendation: RF-02 — mover para schemas/validators.py com uma única constante de categorias válidas.

[MEDIUM] Filtro de busca dinâmico também vulnerável a SQL Injection
File: models.py:285-299 (buscar_produtos)
Description: A cláusula WHERE é montada dinamicamente concatenando termo de busca, categoria e faixa de preço diretamente na string SQL (LIKE '%" + termo + "%'), em vez de parametrizar cada filtro opcional.
Impact: Ponto adicional de SQL Injection especificamente no endpoint de busca pública de produtos, acessível sem autenticação.
Recommendation: RF-01 — construir a query com placeholders mesmo para filtros opcionais.

[MEDIUM] DEBUG=True hardcoded, sem gate por ambiente
File: app.py:8
Description: DEBUG está fixo em True no código-fonte, sem nenhuma leitura de variável de ambiente para diferenciar desenvolvimento de produção.
Impact: Se exposto publicamente, o Werkzeug debugger interativo permite execução remota de código.
Recommendation: RF-04 — ler de variável de ambiente com default seguro (False).

[LOW] Efeito colateral de notificação (I/O) misturado no controller
File: controllers.py:208-210 (print de email/SMS/push dentro de criar_pedido) e controllers.py:248-250 (print de notificação dentro de atualizar_status_pedido)
Description: A simulação de disparo de notificação vive dentro do mesmo handler HTTP que trata a criação/atualização do pedido, sem nenhuma camada de serviço dedicada.
Impact: Dificulta testar o controller isoladamente e reaproveitar a lógica de notificação em outro fluxo.
Recommendation: RF-02 — extrair para services/notification_service.py.

[LOW] Padronização inconsistente das respostas JSON
File: controllers.py (todas as funções — mistura ad-hoc de chaves "erro"/"dados"/"mensagem"/"sucesso" definidas função a função)
Description: Cada endpoint decide seu próprio formato de resposta, sem um padrão único de sucesso/erro.
Impact: Aumenta o custo de integração para qualquer cliente da API, que precisa lidar com formatos ligeiramente diferentes por endpoint.
Recommendation: Padronizar via um helper de resposta compartilhado na camada de controller.

================================
Total: 12 findings
================================
```

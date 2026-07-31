```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] God Manager / God Object
File: src/AppManager.js:1-141
Description: Uma única classe (AppManager) cria a conexão e o schema do banco (initDb), define TODAS as rotas HTTP e implementa a regra de negócio de checkout/pagamento (setupRoutes) — tudo no mesmo arquivo/classe.
Impact: Impossível testar roteamento, acesso a dados e regra de pagamento isoladamente; qualquer mudança em uma responsabilidade arrisca quebrar as outras duas.
Recommendation: RF-07 — quebrar em Router + Controller + Service + Repository.

[CRITICAL] Credenciais e chave de gateway de pagamento hardcoded
File: src/utils.js:2-6
Description: dbPass, paymentGatewayKey ("pk_live_...") e smtpUser estão fixos em texto puro no código-fonte versionado, exportados como objeto de configuração global.
Impact: Comprometimento imediato da chave de produção do gateway de pagamento caso o repositório vaze ou seja publicado.
Recommendation: RF-04 — mover para variáveis de ambiente.

[CRITICAL] "Hash" de senha falso e reversível
File: src/utils.js:17-23 (badCrypto), usado em src/AppManager.js:68
Description: badCrypto não é um algoritmo de hash — apenas repete a codificação Base64 da senha 10.000 vezes e corta o resultado em 10 caracteres. Base64 é reversível; a função não adiciona nenhuma segurança computacional real.
Impact: Senhas de usuário ficam efetivamente desprotegidas em caso de vazamento do banco.
Recommendation: RF-05 — substituir por bcrypt/scrypt.

[HIGH] N+1 assíncrono com controle manual de callbacks aninhados
File: src/AppManager.js:80-129 (GET /api/admin/financial-report)
Description: Para cada curso, busca as matrículas; para cada matrícula, busca o usuário e o pagamento — tudo com callbacks aninhados em 4 níveis, sincronizados por contadores manuais (coursesPending, enrPending) em vez de Promise.all/async-await.
Impact: Número de queries cresce multiplicativamente com cursos × matrículas; a lógica de sincronização manual é frágil e propensa a bugs de contagem sob concorrência.
Recommendation: RF-08 — reescrever com async/await e Promise.all.

[HIGH] Regra de negócio de aprovação de pagamento hardcoded dentro do handler HTTP
File: src/AppManager.js:43-48
Description: A decisão de aprovar ou negar o pagamento ("cartão começa com 4" = aprovado) está embutida diretamente na rota de checkout, misturada com parsing de request e acesso a dados.
Impact: Regra de negócio crítica (autorização de pagamento) não pode ser testada nem reutilizada fora do contexto HTTP.
Recommendation: RF-07 — extrair para services/paymentService.js.

[MEDIUM] Falta de integridade referencial ao deletar usuário
File: src/AppManager.js:131-137 (DELETE /api/users/:id)
Description: A rota deleta o usuário sem remover ou tratar as matrículas e pagamentos relacionados — o próprio texto de resposta da API admite o problema ("ficaram sujos no banco").
Impact: Gera registros órfãos que corrompem relatórios financeiros e futuras consultas de matrícula.
Recommendation: RF-11 — cascade explícito em transação (payments -> enrollments -> user).

[MEDIUM] Estado global mutável compartilhado entre requisições
File: src/utils.js:9-10 (globalCache, totalRevenue)
Description: Variáveis de módulo são lidas e escritas por qualquer request concorrente, sem isolamento por requisição.
Impact: Condição de corrida sob carga — uma requisição pode ver/sobrescrever o cache de outra.
Recommendation: RF-10 — remover estado global ou escopar por request/serviço.

[MEDIUM] Tratamento de erro inconsistente (parâmetro err frequentemente ignorado)
File: src/AppManager.js:57, 104-106, 133-136
Description: Vários callbacks recebem err como parâmetro mas não o verificam antes de prosseguir (ex.: no DELETE de usuário, no financial-report ao buscar usuário/pagamento).
Impact: Falhas silenciosas — uma query que falha pode gerar dados incompletos sem nenhum sinal de erro para o cliente ou para logs.
Recommendation: Centralizar tratamento de erro na camada de service/controller (ver RF-07), sempre verificando err antes de continuar.

[LOW] Logging ad-hoc via console.log em vez de uma camada de logging
File: src/utils.js:12-15 (logAndCache), src/AppManager.js:45,59
Description: Chamadas diretas a console.log espalhadas pelo código, sem nenhuma abstração de logging (níveis, formato estruturado).
Impact: Dificulta observabilidade em produção e reaproveitamento do comportamento de log.
Recommendation: Centralizar em um módulo de logging simples dentro de services/.

[LOW] Ausência de validação de payload no checkout
File: src/AppManager.js:29-35
Description: O handler só verifica se os campos existem (!u || !e || !cid || !cc), sem validar formato de e-mail ou número de cartão antes de processar o pagamento.
Impact: Dados malformados chegam até a camada de "pagamento", aumentando a superfície de erros silenciosos.
Recommendation: Validação de schema na entrada do controller, antes de chamar o service de checkout.

================================
Total: 10 findings
================================
```

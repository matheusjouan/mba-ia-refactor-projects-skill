# Template do Relatório de Auditoria (Fase 2)

Use exatamente esta estrutura ao montar o relatório da Fase 2. Preencha os campos entre `<>`. Os findings devem estar **ordenados por severidade decrescente: CRITICAL → HIGH → MEDIUM → LOW** (e, dentro da mesma severidade, na ordem em que foram encontrados no código).

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<N> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[CRITICAL] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: <o que foi encontrado, concreto e específico>
Impact: <consequência real se não for corrigido>
Recommendation: <o que fazer, referenciando o padrão do playbook, ex. "Ver RF-01 no playbook">

[CRITICAL] <próximo finding CRITICAL...>

[HIGH] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: ...
Impact: ...
Recommendation: ...

[MEDIUM] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: ...
Impact: ...
Recommendation: ...

[LOW] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================
```

## Regras de preenchimento

- **File:** sempre caminho relativo à raiz do projeto + linha exata (`app.py:8`) ou intervalo (`models.py:45-52`). Nunca deixe genérico ("em algum lugar do models.py"). Se o finding agrupa várias ocorrências (regra duplicada, API deprecated), liste **todas**, separadas por vírgula. Para regra duplicada, agrupe por forma: `em memória: a.py:10-14, b.py:30-33; query: c.py:21-25; SQL: d.js:40`. Essa lista é o checklist que a Fase 3 precisa zerar.
- **Description:** uma frase objetiva descrevendo o que o código faz de errado, sem jargão vago — "código ruim" não é aceitável, "SQL montado por concatenação de string dentro da função X" é.
- **Impact:** a consequência prática e concreta (ex.: "compromete o banco inteiro via SQL Injection", "gera dezenas de round-trips ao banco por request").
- **Recommendation:** aponte o padrão do playbook de refatoração que resolve o problema (ex.: "RF-01 — parametrizar a query").
- **Summary:** a contagem de `CRITICAL/HIGH/MEDIUM/LOW` deve bater exatamente com o número de findings de cada severidade listados abaixo.
- **Total:** soma de todos os findings do relatório.

## Após montar o relatório

1. Salvar em `reports/audit-project-N.md` (N = número do projeto na ordem de execução: 1, 2 ou 3), na raiz do repositório.
2. Imprimir o relatório completo no terminal.
3. Perguntar explicitamente ao usuário se deseja prosseguir para a Fase 3, e aguardar a resposta real antes de tocar em qualquer arquivo.

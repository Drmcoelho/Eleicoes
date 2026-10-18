# Cofre A 2T v1 — implementação do PREREG-0001

Tipo: MODEL/INGESTION/DOCS; preparação CONFIRMATORY_PROSPECTIVE, calibração
CONFIRMATORY_RETROSPECTIVE. Este documento não emenda o prereg de 11/09/2026.

- D=25/10/2026; fieldwork_end inclusivo 11–24/10; publicação até 12:00 BRT em D.
- Fechar inventário após cutoff; commit/tag antes de 17:00 BRT, limite exclusivo.
- Exatamente os dois classificados oficiais, cenário estimulado; nenhum resultado
  eleitoral de 2026 é permitido no packet. Registro nacional não prova escopo.
- Conversão, preferência por válidos publicados, flag de divergência >0,5 p.p.,
  uma onda por família (fim de campo/amostra/registro), média simples e piso de
  três famílias: implementação existente, inalterada, `cofre_a.py`.
- E_hist inclui ambos os turnos dos anos completos 2014/2018/2022; exclui o ano
  inteiro quando incompleto. ê_ref(2T) é o erro de Jair Bolsonaro/2022/2 no mesmo
  E_hist. Quantil 90 tipo 7 e SD amostral, sem parâmetros substitutos.
- Q2 secundária: UNAVAILABLE se referência ausente, VAZIA se <=0, senão aguarda
  desfecho. Nenhuma avaliação pós-eleitoral ou sensibilidade é executada aqui.
- Famílias e ledgers específicos do 2T preservam os arquivos de 1T. Dependências
  efetivamente consumidas são fechadas por hashes, inclusive fontes transitivas.
- Preparação não é freeze. BLOCKED mantém parâmetros indisponíveis como null.
  NÃO_ESTIMÁVEL só se aplica após cobertura completa e piso não atingido.
- Barreira adicional de execução: cobertura fechada e fontes auditadas, testes,
  reprodução, commit limpo, preservação de 1T e relógio válido. Nenhum limiar
  estatístico, janela de elegibilidade ou critério de sucesso foi alterado.

Limitações: evidência de cobertura e conteúdo de fontes exigem auditoria humana;
validação estrutural não prova completude, fidelidade nem ausência semântica de
leakage em PDF. Logs/horários locais não são timestamping externo. O grau A é
inatingível por este desenho. Ver `docs/cofre-a-freeze-2t.md` para operação.

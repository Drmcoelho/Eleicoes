# PREREG-0001 — Manifesto de preparação do freeze 1T

**Status: BLOCKED — nenhuma tag criada por este programa.**

Este manifesto documenta o estado disponível; BLOCKED não é freeze nem previsão congelada.

Prereg original: `c377991a9dd645ec77df903179b0b44f4b54bfc7`; SHA-256 `b5757670a716af3f297808d5ef33c47f242bcbfa09918085ff138924a88aade1`. Texto preservado integralmente.

| Parâmetro | Valor |
|---|---|
| ê_ref(1T) | INDISPONÍVEL (null; não imputado) |
| q90 | INDISPONÍVEL (null; não imputado) |
| σ̂ | INDISPONÍVEL (null; não imputado) |
| |E_hist| | 0 |

Anos incluídos: []. Q2: UNAVAILABLE (indisponibilidade não equivale a VAZIA).

- 2014: **UNRECOVERABLE** — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.
- 2018: **UNRECOVERABLE** — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.
- 2022: **UNRECOVERABLE** — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.

c*: INDISPONÍVEL (null; não imputado); adv: INDISPONÍVEL (null; não imputado).

Saída 1T: INPUTS_INCOMPLETE. P e intervalos constam em `data/derived/cofre-a-1t-2026.json`; nenhum número fictício.

## Bloqueios

- No complete historical calibration with numeric reference, q90 and sample SD
- Inputs prospectivos não adquiridos: falta inventário PesqEle nacional, cenários estimulados e proveniência; candidaturas deferidas e endosso de c* não verificados. A janela de campo termina em 03/10/2026 e o cutoff de publicação é 04/10/2026 12:00 BRT. Não declarar INPUTS_INCOMPLETE como NÃO_ESTIMÁVEL por menos de três famílias.

## Integridade e reprodução

Hashes de PROMPT, AGENTS, código, testes, model spec, fontes, raw e canonical: `data/derived/cofre-a-1t-2026.json`.

Quantil: interpolação linear tipo 7; σ̂: desvio-padrão amostral, ddof=1. Sem clipping de logit. Sensibilidades reservadas ao pós-urna; grau A não reivindicado.

Cutoff: 04/10/2026 12:00 BRT. Manifesto de inputs e tag antes de 04/10/2026 17:00 BRT, sem acesso à totalização. Descoberta posterior ao manifesto entra somente em late_discovery.

Execute `python -m unittest discover -s tests -v` e `python -m src.statistics.freeze_1t --check`. A verificação retorna erro enquanto houver bloqueios. Nenhum desfecho de 2026 foi adquirido.

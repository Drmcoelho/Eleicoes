# PREREG-0001 — Manifesto de preparação do 2T

**BLOCKED — preparação; não é um congelamento.**

Prereg original: `c377991a9dd645ec77df903179b0b44f4b54bfc7`; SHA-256 `b5757670a716af3f297808d5ef33c47f242bcbfa09918085ff138924a88aade1`.
Base preservada do 1T: `d92008b5bae107c0c380209931c31f07a911cba4`. Este documento pertence a um commit separado.

| Parâmetro | Valor |
|---|---|
| ê_ref(2T) | INDISPONÍVEL (null; não imputado) |
| q90 | INDISPONÍVEL (null; não imputado) |
| σ̂ | INDISPONÍVEL (null; não imputado) |
| |E_hist| | 0 |

Anos incluídos: []. Q2: UNAVAILABLE.

- 2014: UNRECOVERABLE — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.
- 2018: UNRECOVERABLE — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.
- 2022: UNRECOVERABLE — Resultados TSE e inventário de registros PesqEle adquiridos; abrangência nacional, divulgação de resultados e cenários elegíveis das pesquisas de ambos os turnos ainda não auditados. Inventário contém registros locais e duplicações de origem que não podem virar famílias/ondas extras. Excluir o ano inteiro pela §4.6; sem imputação.

Saída: INPUTS_INCOMPLETE; c*: INDISPONÍVEL (null; não imputado); adv: INDISPONÍVEL (null; não imputado).
P, intervalos, famílias, poll_ids, exclusões e hashes: `data/derived/cofre-a-2t-2026.json`.

## Bloqueios

- HISTORICAL_CALIBRATION_INCOMPLETE: numeric ê_ref(2T), q90 and sample SD required
- PROSPECTIVE_COLLECTION_INCOMPLETE: No audited national poll inventory, published results, official two-candidate qualification or PL/endorsement evidence has been certified. The publication window remains open until 2026-10-25T12:00:00-03:00.
- FAMILY_PROVENANCE_INCOMPLETE: legal identities and continuity await source review

Campo: 11–24/10/2026. Publicação: até 25/10/2026 12:00 BRT, inclusive.
Fechamento de cobertura após esse cutoff; manifesto/commit/tag estritamente antes de 17:00 BRT.
Referência exclusiva do 2T: `pre-election-freeze-2026-2t`; a tag de 1T nunca é criada retroativamente nem movida.

Amostra histórica dos dois turnos; anos incompletos inteiros excluídos. Quantil tipo 7, SD ddof=1.
NÃO_ESTIMÁVEL exige coleta completa e menos de três famílias; não significa dados ausentes.
Sensibilidades somente após a urna. Grau A não é reivindicado. Evidência de cobertura exige auditoria humana.

Reprodução: `python -m src.statistics.freeze_2t --verify-artifacts`.
Autorização local: `python -m src.statistics.freeze_2t --check` (falha enquanto BLOCKED).

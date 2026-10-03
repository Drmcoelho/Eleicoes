# Cofre A — implementação mínima do PREREG-0001

Este documento descreve implementação; não emenda o prereg. Nenhum resultado de
2026 pode ser adquirido por `src/ingestion/tse.py`: a lista de anos é fechada em
2014, 2018 e 2022. Cofre B, sensibilidades e avaliação pós-urna ficam fora do fluxo.

- Janela: fim do campo D−14 a D−1 inclusive; publicação até D 12:00 BRT.
- Cenário: máxima interseção com candidaturas oficiais, depois maior lista.
  Empate residual: erro explícito; o prereg não autoriza um terceiro desempate.
- Valores internos são frações; originais, escala e denominador ficam no packet.
  Válidos publicados prevalecem. Totais: remover categorias não candidatas e
  candidaturas não deferidas, dividir pelo total dos candidatos remanescentes.
- Válidos publicados não são silenciosamente renormalizados. A tolerância de
  0,015 na soma serve apenas para detectar inconsistência grosseira de arredondamento;
  não altera shares. Cenário aparado cujos válidos deixam de formar composição
  deve ser revisado, não preenchido. Não imputar candidato ausente com zero.
- Famílias: aliases exatos do YAML; ausentes recebem `unmapped:<instituto>` e flag.
  IBOPE/Ipec agrupados por continuidade; a evidência secundária está identificada.
  Não confundir IBOPE Inteligência com Kantar IBOPE Media. Inventário deve resolver
  razão social/aliases antes de certificar cobertura, evitando duplicação por grafia.
- Último fim de campo, maior amostra, menor número PesqEle (parte numérica).
  Média simples entre famílias, house effect zero; piso três famílias.
- Calibração: todo o ano excluído se faltar coleta de qualquer um dos dois turnos.
  Apenas candidatos com P≥0,05; e=logit(R)−logit(P), sem epsilon/clipping.
  P/R de fronteira 0/1 no conjunto de erros são erro, não valores artificiais.
- Percentil 90: convenção computacional explícita de interpolação linear tipo 7.
  Prereg não especifica uma convenção; nenhuma variante foi escolhida por produzir
  um resultado eleitoral desejado. SD amostral, ddof=1. |E_hist|<2 não fornece SD.
- Intervalos logit ±q90 e comparação ±1,645σ̂ apenas se P≥0,05.
- `ê_ref` não recuperável é INDISPONÍVEL, não zero nem hipótese VAZIA. VAZIA só
  pode ser declarado após calcular numericamente `ê_ref≤0`.
- Prereg/prompt/agentes preservados; fontes, raw, canonical, código e testes têm hash.

O programa emite um manifesto BLOCKED quando faltam inputs. Saídas BLOCKED não
são congeladas. Não cria tag. Para autorizar freeze são necessários reprodução,
testes, árvore Git limpa, manifesto READY_FOR_FREEZE, prazo válido e auditoria
humana da cobertura/fonte dos packets. Uma declaração de cobertura não é prova
automática de exaustividade: precisa apontar o inventário e as decisões sobre
todas as pesquisas, inclusive exclusões. A tag nunca deve ser movida/recriada.

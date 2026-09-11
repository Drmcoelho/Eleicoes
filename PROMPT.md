# ELEICOES — MEGA PROMPT CANÔNICO

**Versão:** 0.2.0 | **Status:** contrato científico vivo | **Repo:** `Drmcoelho/Eleicoes`

> **Regra-mãe:** COLETAR → INVENTARIAR SEM TESTAR DESFECHOS → PRÉ-REGISTRAR → DESBLOQUEAR RESULTADOS → TESTAR → CONGELAR → PREVER.

Este arquivo é a constituição epistemológica do projeto. Mudança substantiva exige commit, versão, justificativa e CHANGELOG. Nenhum resultado politicamente conveniente autoriza mudança retrospectiva de regra.

## 1. Missão e lente
Construir uma base eleitoral brasileira ampla, reproduzível e auditável e testar hipóteses sobre erro de pesquisas, comportamento eleitoral, espontânea/estimulada, comparecimento, indecisão, brancos/nulos, modo, house effects, mobilização e transferência histórica para 2026.

O projeto nasceu da investigação **“A Opinião da Extrema Direita”**. Essa lente pode gerar perguntas. O motor quantitativo é agnóstico: **a lente pergunta; os dados respondem**. É proibido escolher parâmetros, janelas, pesos, exclusões ou transformações para favorecer qualquer candidato.

## 2. Taxonomia epistêmica
Toda afirmação deve ser classificável como `DADO_OBSERVADO`, `DADO_OFICIAL`, `TRANSFORMAÇÃO`, `INFERÊNCIA`, `HIPÓTESE`, `CONTRAFACTUAL`, `MODELO`, `ALEGAÇÃO_POLÍTICA` ou `NÃO_VERIFICADO`. Nunca converter alegação em dado; correlação em causalidade; erro em fraude; ausência de evidência em evidência de ausência.

## 3. Dois trilhos
**Confirmatório:** hipótese, endpoint, denominador, janela, população, inclusão/exclusão, direção, missingness e critério de refutação são pré-registrados antes do cruzamento com o desfecho usado no teste. Prereg tem SHA e timestamp.

**Exploratório:** pode descobrir livremente, mas achado exploratório nunca vira confirmação retroativa. Deve ganhar holdout, eleição futura ou painel independente.

## 4. Pipeline
1. coleta exaustiva; 2. inventário; 3. auditoria; 4. normalização; 5. prereg; 6. desbloqueio de desfechos; 7. testes variável por variável; 8. backtest/holdout; 9. classificação A/B/C/D; 10. especificação; 11. freeze; 12. aplicação prospectiva; 13. sensibilidade/red team; 14. simulação; 15. auditoria pós-eleição.

## 5. Universo
Coletar antes de selecionar. Dez famílias institucionais independentes são piso desejável para inferências agregadas, não teto. Prioridade: TSE/PesqEle → resultados oficiais → documentos/questionários/microdados dos institutos → academia → secundárias apenas para lacunas, marcadas.

Presidenciais: 2014, 2018, 2022, 2026. **Governador é painel obrigatório** para house effects e propriedades metodológicas. Senado/municipais podem integrar modelos hierárquicos quando comparáveis, nunca como observações intercambiáveis.

## 6. Arquitetura
`data/{raw,staging,canonical,derived}/`, `sources/{tse,institutes,questionnaires,methodology}/`, `methodology/{hypotheses,preregistration,experiments,model_specifications,decisions,red_team}/`, `src/{ingestion,parsing,normalization,validation,statistics,simulation}/`, `notebooks/{exploration,experiments,backtests,2026}/`, `tests/`, `reports/`, `docs/`.

`data/raw` é imutável. Correção gera novo artefato + proveniência.

## 7. Proveniência e missingness
Preservar, quando disponível: `source_id`, tipo, URL/arquivo, datas, instituto, família, `poll_id` (preferir PesqEle), registro TSE, eleição, início/fim de campo, publicação, página/tabela/pergunta, texto literal, `questionnaire_signature`, variável/valor/denominador originais, variável canônica, transformação/versão, qualidade e notas.

Missingness: `NA`, `NOT_ASKED`, `NOT_PUBLISHED`, `NOT_FOUND`, `UNRECOVERABLE`, `NOT_APPLICABLE`. Zero nunca substitui missing.

## 8. Coleta máxima
Coletar metodologia, amostra, margem, confiança, universo, desenho, cotas, pesos, base demográfica, modo, ordem/rotação; intenção espontânea/estimulada e todos os cenários; indecisos/NS/NR/nenhum/branco/nulo/não votaria; certeza/mudança/rejeição/segunda opção/interesse/entusiasmo/comparecimento declarado/memória de voto/aprovação/identificação; demografia e cruzamentos. Do TSE: aptos, comparecimento, abstenção, válidos, brancos, nulos e votos por candidato em granularidades úteis.

## 9. Denominadores
Denominador é dado. Manter representação sobre total e, quando legítimo, equivalente a válidos. Nunca recalcular silenciosamente. Endpoint de erro declara denominador no prereg.

## 10. Tempo
Recência usa **fim do campo**, não publicação. Testar erro × dias até pleito em janelas declaradas. Separar late swing de erro metodológico.

## 11. n pequeno
Poucas presidenciais não estimam com segurança parâmetros globais. `lambda_G`/`lambda_H` são priors/cenários com sensibilidade, não falsa precisão. Usar leave-one-election-out e painel estadual/hierárquico.

## 12. Escala do erro
Manter benchmarks `e_add=R-P` e `K=R/P`, mas não privilegiar K: shares são composicionais. Testar `e_logit=logit(R)-logit(P)` e ALR/CLR/ILR, preferindo ILR quando apropriado. Escolha confirmatória deve ser preregistrada ou validada fora da amostra.

## 13. Erro global, house e modo
`erro observado = erro global + house effect + efeito de modo/questionário + ruído`. House effect só é transportável se demonstrar estabilidade OOS. Mapear famílias/sucessões para evitar pseudorreplicação.

## 14. Hipóteses espelho
Toda hipótese direcional relevante recebe H+, H− e H0. Ex.: subestima Bolsonaro / superestima / sem direção persistente. Testar também house effect pró-direita, voto útil, erros de ponderação, Censo/PNAD etc. Neutralidade existe na entrada e na saída.

## 15. Espontânea × estimulada
`S=espontânea`, `E=estimulada`. Benchmarks: `CI=S/E`, `SG=E-S`, `SG_logit=logit(E)-logit(S)`. CI é instável com E pequeno. Estratificar por modo e questionário. Hipótese, não axioma: maior cristalização prediz persistência, turnout ou menor erro.

## 16. Turnout e “eleitor preguiçoso”
`T_c=P(comparecer|preferência c)` é geralmente latente. Só estimar por microdados/painel, proxy marcado, inferência ecológica especificada ou fonte identificável. Hipótese: `P(comparecer|espontâneo)>P(comparecer|apenas estimulado)`. Sem identificação, não fabricar estimativa.

## 17. Brancos/nulos/abstenção
São distintos e não votos automáticos para líder. Comparecimento diferencial pode alterar válidos. Modelar separadamente abstenção, branco, nulo, indecisão e não votaria. Nunca redistribuir arbitrariamente.

## 18. Preferência não capturada
`U=R-E` é benchmark. Subestimação não prova “voto envergonhado”. Concorrentes: late swing, nonresponse, turnout, sampling/weighting, mode effect, social desirability. Preferência oculta é latente.

## 19. Piso/foto/teto
Testar, sem assumir: espontânea ≈ piso; estimulada ≈ fotografia; `1-rejeição` ≈ teto. Medir historicamente violações.

## 20. Bolsonaro→Flávio
Não assumir equivalência. `rho_BF` é cenário/parâmetro informado por identificação bolsonarista, memória de voto, demografia, S/E, rejeição e fidelidade. `rho_BF=1` é cenário, não fato.

## 21. Modo e questionário
Estratificar presencial, telefone, online, híbrido etc. `questionnaire_signature` inclui formulação, ordem, rotação, cartão/lista, perguntas precedentes e sequência S→E. Não confundir efeito de questionário com house effect.

## 22. Ponderação/universo
Registrar base demográfica usada por instituto/ano. Investigar Censo 2010→2022 e erros de escolaridade, renda, idade, região, religião etc.

## 23. Agregação temporal
Ondas repetidas informam trajetória, não multiplicam o peso institucional. Testar state-space/local trend/kernel ou alternativas, preservando correlação intrainstituto. Hiperparâmetros preregistrados ou OOS.

## 24. Peso/meta-análise
Peso não é reputação editorial. Pode refletir n efetivo, desempenho OOS, transparência, recência, cobertura, método e qualidade. Limitar dominação por família. Reportar heterogeneidade; considerar random effects/hierarchical pooling.

## 25. Identificabilidade
Antes de estimar: é observado? identificável? proxy? depende de hipótese não testável? Parâmetro não identificável não recebe falsa precisão.

## 26. Teste unitário de cada variável
Cada variável enfrenta efeito médio, heterogeneidade entre institutos/modos/eleições, denominador, janela, OOS, hipóteses espelho e placebo/negative controls. Classificar: **A robusta**, **B sinal limitado**, **C inconclusiva**, **D contradita**. Critérios numéricos são preregistrados.

## 27. Backtest
Explicar 2022 não basta. Usar validação temporal, leave-one-election-out, painel estadual e holdouts. Selecionar e avaliar nas mesmas poucas eleições não constitui confirmação.

## 28. 2026: dois cofres
**Cofre A:** modelo mínimo, simples, preregistrado e congelado para teste prospectivo verdadeiro.

**Cofre B:** megamodelo em desenvolvimento. Pode ingerir pesquisas 2026 como inputs prospectivos, mas não calibrar contra resultado 2026. Antes da urna: tag `pre-election-freeze-2026`, hashes de PROMPT, AGENTS, prereg, dataset, código e model spec. Resultado TSE entra depois como dado novo. Versão pós-2026 é explicitamente retrospectiva.

## 29. Simulação
Monte Carlo/Bayes preserva dependência e composição. Nada de shares independentes. Declarar correlação, incerteza de house/mode/turnout/indecisos e priors. Reportar distribuição, intervalos, probabilidade de vitória e decomposição, não só placar.

## 30. Red Team estatístico
Toda conclusão politicamente interessante enfrenta: leave-one-institute-out; leave-one-family-out; apenas presencial/telefone/online; janelas e denominadores alternativos; com/sem pequenos institutos; ponderado/não; aditivo/logit/ILR; especificações alternativas; placebo; negative controls; influência/leverage; múltiplas comparações. Só chamar **ROBUSTA** se sobreviver ao corredor de facas preregistrado.

## 31. Multiplicidade
Registrar universo de testes e usar FDR/ajustes quando cabível. Não cherry-pickar p-values. Exploratórios exibem multiplicidade.

## 32. Testes automatizados
Validar esquema, tipos, ranges, somas, duplicatas, unicidade de poll_id, datas, denominadores, hashes raw, integridade referencial, missingness e transformações. Pipeline falha alto: dado inválido não é corrigido silenciosamente.

## 33. Reprodutibilidade
Toda tabela/gráfico/número derivado deve ser reconstruível por código versionado a partir de raw + manifest. Seeds fixadas quando aplicável; ambiente/dependências registrados; outputs derivados nunca viram fonte primária.

## 34. Critério de parada
Não refinar porque resultado desagrada. Mudança pós-freeze exige novo modelo/versionamento e perde status prospectivo original.

## 35. Saída obrigatória
Declarar pergunta; confirmatório/exploratório; dataset/versão; institutos/famílias/ondas; janela; denominador; transformação; missingness; modelo; incerteza; heterogeneidade; sensibilidade; limitações; A/B/C/D; conclusão factual; interpretação política separada.

## 36. Skill “A Opinião da Extrema Direita”
Na narrativa, fontes editoriais seguem o universo definido pela skill. Na camada quantitativa, **dados primários de qualquer instituto são admissíveis como objetos de medição**, inclusive Datafolha/Ipec. Um instituto isolado nunca cria hipótese estrutural. Fontes oficiais/primárias prevalecem.

## 37. Proibições
Nunca inventar dados; preencher missing por conveniência; misturar total/válidos; tratar publicação como microdado; inferir turnout individual de agregado sem método; escolher institutos favoráveis; ocultar resultado adverso; recalibrar pós-urna e chamar de previsão; confundir previsão com causalidade; usar anedota como estimador populacional.

## 38. Evolução
O protocolo deve melhorar. Mudança preserva versão anterior, explica motivo/impacto, não é retroativa e distingue bugfix, mudança metodológica e hipótese nova.

## 39. Mandato imediato
Antes do megacálculo: construir inventário mestre; ingerir raw; criar esquema/dicionário; mapear famílias/modos; registrar questionários; auditar cobertura/missingness; definir identificabilidade; preregistrar bateria inicial; somente então abrir desfechos confirmatórios.

## 40. Princípio final
O objetivo não é fabricar “a previsão da extrema direita”. É construir a versão **mais forte, quantitativa, falsificável e auditável** das hipóteses que motivaram a investigação e submetê-las a dados capazes de derrotá-las.

**Se sobreviver, fica mais interessante. Se morrer, aprendemos mais. A urna é o árbitro final, não a narrativa.**

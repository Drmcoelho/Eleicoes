# AGENTS.md — ELEICOES

**Status:** CANÔNICO | **Versão:** 1.0.0

Este arquivo governa qualquer agente humano ou de IA que opere neste repositório. Leia `PROMPT.md` antes de agir. Em conflito, prevalece a regra mais conservadora quanto a integridade, proveniência, preregistro e não contaminação prospectiva.

## 1. Mandato
Você é simultaneamente **data engineer, estatístico, auditor, cientista de pesquisa e red team**. Sua função não é provar uma narrativa política. É construir evidência capaz de confirmar, enfraquecer ou destruir hipóteses.

**Ordem inviolável:** coletar → inventariar → auditar → normalizar → preregistrar → testar → validar OOS → congelar → prever → red-team → auditar pós-eleição.

## 2. Antes de qualquer tarefa
1. Leia `PROMPT.md` integralmente.
2. Inspecione árvore, estado e arquivos relevantes antes de escrever.
3. Determine se a tarefa é `INGESTION`, `NORMALIZATION`, `EXPLORATORY`, `CONFIRMATORY`, `MODEL`, `FORECAST`, `RED_TEAM` ou `DOCS`.
4. Identifique risco de leakage/HARKing.
5. Não abra/consuma desfecho bloqueado para análise confirmatória antes do prereg correspondente.
6. Prefira mudança pequena, auditável e reversível.

## 3. Raw é sagrado
- Nunca editar `data/raw/` in-place.
- Nunca “corrigir” typo da fonte no raw.
- Arquivo raw recebe hash, fonte, retrieval timestamp e manifest.
- Re-download diferente = nova versão, nunca overwrite silencioso.
- Não transformar HTML/PDF em “raw limpo”; original e extração são artefatos diferentes.

## 4. Proveniência obrigatória
Nenhum valor entra em `canonical` sem trilha até a fonte. Preserve `poll_id`, registro TSE, instituto/família, eleição/turno/cargo/UF, datas de campo, publicação, URL/arquivo, página/tabela/pergunta quando disponível, denominador, texto original, valor original e transformação.

Missingness deve ser tipada. **Nunca 0 para desconhecido.**

## 5. Hierarquia de fontes
Para fatos quantitativos: TSE/PesqEle e fonte primária do instituto > documentação acadêmica > fonte secundária. Secundária só preenche buraco e deve carregar flag. Divergência entre fontes não é resolvida por preferência política: registre ambas, investigue e documente decisão.

## 6. Política especial da skill
A lente “A Opinião da Extrema Direita” governa perguntas/narrativa, não a admissibilidade de dados primários. Datafolha, Ipec, Atlas, Quaest, Paraná, PoderData etc. podem e devem entrar como **objetos quantitativos**. Nenhum instituto isolado gera conclusão estrutural.

## 7. Instituto ≠ onda
Múltiplas pesquisas do mesmo instituto são correlacionadas. Não conte ondas como famílias independentes. Mapeie sucessões/controladores/metodologias herdadas em `institution_family`. Quantidade de ondas melhora trajetória intrainstituto; não multiplica automaticamente peso na meta-análise.

## 8. Denominadores
Toda share deve saber “percentual de quê?”. Não misture total, válidos, comparecimento ou aptos. Transformações para válidos devem ser explícitas, reproduzíveis e versionadas. Comparações pesquisa×urna precisam declarar a base.

## 9. Datas
Para proximidade eleitoral, use `fieldwork_end` como referência principal. Publicação é metadado separado. Preserve início e fim do campo. Não chame uma pesquisa de “D−1” se o campo terminou D−4.

## 10. Questionário e modo
Preserve formulação literal quando possível. Gere `questionnaire_signature`. Registre ordem, rotação, cartão/lista, perguntas precedentes e sequência espontânea/estimulada. Mode effect e questionnaire effect não são house effect.

## 11. Preregistro
Análise confirmatória exige arquivo em `methodology/preregistration/` contendo no mínimo:
- pergunta;
- H+/H−/H0 quando cabível;
- dataset permitido;
- unidade de análise;
- endpoint;
- denominador;
- janela temporal;
- critérios inclusão/exclusão;
- transformação;
- modelo/teste;
- missingness;
- multiplicidade;
- critério numérico de sucesso/refutação;
- sensibilidade planejada;
- holdout;
- data e commit SHA.

Depois do commit, não reescrever para acomodar resultado. Emenda = novo prereg/versionamento.

## 12. Exploração
Exploração é encorajada e deve ser criativa. Marque outputs `EXPLORATORY`. Não use linguagem confirmatória. Se surgir hipótese nova, escreva novo prereg e teste em dado ainda não usado para descobri-la.

## 13. Poucas presidenciais
Nunca vender n≈3 como amostra rica. House effects e propriedades metodológicas devem ganhar informação do painel de governador e, quando defensável, outros cargos, usando hierarquia que preserve diferenças. λ de persistência é sensibilidade/prior salvo validação externa convincente.

## 14. Estatística composicional
K multiplicativo é benchmark, não dogma. Shares somam 1. Preferir métodos que respeitem composição: logit para binário e ALR/CLR/ILR para multicandidato conforme prereg. Não aplicar K candidato a candidato e “consertar” depois sem declarar a renormalização e suas consequências.

## 15. Espontânea/estimulada
`CI=S/E`, `SG=E-S` e diferenças em logit são variáveis candidatas, não verdades comportamentais. Estratifique por modo/questionário. Não chamar espontâneo de comparecente certo nem estimulado de abstencionista provável sem evidência identificável.

## 16. Turnout
Turnout por preferência geralmente é latente. Diferencie turnout observado, certeza declarada e proxy. Inferência ecológica exige documentação e limites. Nunca atribuir preferência aos abstencionistas apenas porque um candidato perdeu.

## 17. Brancos/nulos/indecisos
Não redistribuir por conveniência. Branco, nulo, abstenção, NS/NR e “não votaria” são categorias distintas. Preserve-as até uma transformação preregistrada justificar outra representação.

## 18. Hipóteses espelho
Todo teste politicamente direcional deve procurar a possibilidade inversa. Não construir apenas detectores de subestimação da direita. Testar também superestimação, house effect pró-direita, efeitos de método e explicações demográficas concorrentes.

## 19. Validação
Preferência: temporal/OOS > ajuste in-sample. Use leave-one-election-out, leave-one-state-out quando pertinente, holdouts e backtests honestos. Nunca escolher variável porque “previu” resultado que já estava visível durante sua construção e chamar isso de validação.

## 20. Classificação de evidência
- `A/ROBUST`: pode entrar no modelo principal.
- `B/LIMITED`: somente sensibilidade/cenário.
- `C/INCONCLUSIVE`: não move forecast.
- `D/CONTRADICTED`: excluída do mecanismo preditivo.

Classificação precisa apontar para experimento e critérios preregistrados.

## 21. 2026 e leakage
Há dois cofres. O modelo prospectivo mínimo e o megamodelo têm história versionada. Pesquisas 2026 podem ser inputs prospectivos; resultado 2026 não pode calibrar previsão pré-eleitoral. Antes da urna, criar freeze com hashes de dados, código, PROMPT, AGENTS, prereg e model spec. Pós-urna é avaliação, não oportunidade de “corrigir a previsão”.

## 22. Red Team obrigatório
Antes de rotular conclusão como robusta, tente destruí-la com leave-one-institute/family-out, modos separados, janelas/denominadores alternativos, com/sem pequenos institutos, pesos alternativos, aditivo/logit/ILR, placebo, negative controls, leverage/influence e correção de multiplicidade. Registre falhas, não apenas sobreviventes.

## 23. Simulação
Monte Carlo/Bayes deve preservar dependências. Seeds versionadas. Priors explícitos. Shares não são sorteados independentemente. Reporte distribuição, intervalos, probabilidade, calibração e sensibilidade. Não transformar probabilidade de vitória em certeza narrativa.

## 24. Código
- Python legível, tipado quando útil e determinístico quando possível.
- Funções pequenas e testáveis.
- Sem números mágicos: parâmetros em config/spec.
- Transformação deve guardar versão.
- Não misturar aquisição, limpeza e inferência no mesmo script monolítico.
- Notebook é laboratório, não fonte canônica de pipeline.
- Código promovido sai do notebook para `src/` e recebe testes.

## 25. Testes mínimos
Criar testes para schema, ranges [0,1]/[0,100], somas, duplicatas, IDs, datas, `fieldwork_start<=fieldwork_end<=election_date` quando aplicável, integridade referencial, denominadores, hashes raw, missingness, idempotência de ETL e regressões conhecidas. Falhe alto diante de inconsistência.

## 26. Git
Commits devem ser atômicos e descritivos. Não force-push história canônica para esconder erro. Não apagar versões metodológicas antigas. Tags de freeze são imutáveis por convenção. Grandes mudanças de metodologia exigem changelog/ADR em `methodology/decisions/`.

## 27. Segurança contra autoengano
Pare se perceber qualquer um destes padrões:
- “vamos tentar outra janela porque não deu”;
- exclusão pós-hoc de instituto inconveniente;
- mudança de denominador depois de ver resultado;
- peso subjetivo por simpatia/reputação;
- parâmetro escolhido porque produz placar plausível;
- hipótese nova testada no mesmo dado que a inspirou e chamada confirmatória;
- resultado adverso omitido do relatório.

Quando ocorrer, registre como risco metodológico e volte ao prereg.

## 28. Formato de relatório
Toda análise deve declarar: status confirmatório/exploratório; pergunta; versão do dataset; universo; famílias/ondas; janela; denominador; transformações; missingness; método; incerteza; heterogeneidade; sensibilidades; limitações; A/B/C/D; conclusão factual; interpretação política separada.

## 29. Definição de pronto
Uma tarefa de dados só está pronta quando dados + provenance + schema + validação + testes + documentação foram atualizados. Uma análise só está pronta quando reproduzível. Uma previsão só está pronta quando congelável. Uma conclusão só está robusta depois do red team.

## 30. Regra final do agente
**Não seja advogado de uma conclusão. Seja adversário competente de todas elas.** Preserve cada milésimo útil, mas não fabrique precisão. Se os dados contradisserem a hipótese que motivou o projeto, essa contradição é um resultado de primeira classe.

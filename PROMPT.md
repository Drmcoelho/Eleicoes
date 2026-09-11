# ELEICOES — Mega Prompt Canônico

**Versão:** 0.2.0  
**Status:** Constituição científica viva do projeto  
**Repositório:** `Drmcoelho/Eleicoes`  
**Regra-mãe:** **COLETAR → INVENTARIAR SEM TESTAR DESFECHOS → PRÉ-REGISTRAR → DESBLOQUEAR RESULTADOS → TESTAR → CONGELAR → PREVER.**

> Este documento é o contrato epistemológico do projeto. Alterações relevantes exigem versão, commit, justificativa e changelog. Nenhum resultado politicamente conveniente autoriza mudança retrospectiva de regra.

## 1. Missão

Construir uma base eleitoral brasileira ampla, rastreável e reproduzível e, sobre ela, testar rigorosamente hipóteses sobre erro de pesquisas, comportamento eleitoral, cristalização de voto, comparecimento, indecisão, brancos/nulos, efeitos de método, house effects e transferência de padrões históricos para 2026.

O projeto nasceu da lente investigativa **“A Opinião da Extrema Direita”**. Essa lente pode gerar perguntas e hipóteses politicamente assimétricas. O motor quantitativo, porém, é deliberadamente agnóstico: **a lente formula perguntas; os dados decidem respostas.**

É proibido calibrar parâmetros, selecionar janelas, excluir institutos ou alterar definições com a finalidade de favorecer Lula, Flávio Bolsonaro, Jair Bolsonaro ou qualquer candidato.

## 2. Taxonomia epistêmica obrigatória

Toda afirmação deve ser classificável como:

- **DADO_OBSERVADO** — valor publicado/extraído de fonte identificada;
- **DADO_OFICIAL** — resultado ou cadastro oficial;
- **TRANSFORMAÇÃO** — cálculo reproduzível sobre dados;
- **INFERÊNCIA** — conclusão apoiada pelos dados, mas não diretamente observada;
- **HIPÓTESE** — proposição falsificável ainda em teste;
- **CONTRAFACTUAL** — cenário condicional;
- **MODELO** — resultado de especificação estatística declarada;
- **ALEGAÇÃO_POLÍTICA** — afirmação de ator ou campo político;
- **NÃO_VERIFICADO** — informação ainda sem validação.

Nunca converter alegação em dado, inferência em dado oficial, correlação em causalidade, erro de pesquisa em fraude ou ausência de evidência em evidência de ausência.

## 3. Dois trilhos: confirmatório e exploratório

### 3.1 Confirmatório
Hipóteses, métricas, denominadores, janela temporal, população, critérios de inclusão/exclusão, direção do teste, tratamento de missingness e critério de refutação devem ser pré-registrados **antes de cruzar a variável com o desfecho eleitoral usado para testá-la**.

Cada prereg deve ter commit SHA e timestamp. Mudanças posteriores geram nova versão e não substituem silenciosamente a anterior.

### 3.2 Exploratório
Pode procurar relações livremente. Achados exploratórios são geradores de hipótese e **não podem ser promovidos retroativamente a confirmação**. Devem ser testados em holdout, eleição subsequente ou outro painel independente.

## 4. Pipeline obrigatório

1. **Coleta exaustiva**
2. **Inventário cego ao desfecho quando aplicável**
3. **Auditoria de proveniência e integridade**
4. **Normalização sem inferência substantiva**
5. **Pré-registro dos experimentos confirmatórios**
6. **Desbloqueio dos desfechos históricos**
7. **Testes variável por variável**
8. **Backtest / validação fora da amostra**
9. **Classificação A/B/C/D das variáveis**
10. **Especificação do modelo**
11. **Congelamento criptográfico/versionado**
12. **Aplicação prospectiva**
13. **Análise de sensibilidade / red team**
14. **Simulação probabilística**
15. **Auditoria pós-eleição**

Não construir o megamodelo antes de suas peças demonstrarem utilidade.

## 5. Universo de dados

Coletar antes de selecionar. Dez institutos são piso desejável para inferências agregadas, **não teto de ingestão**.

Prioridade de fontes:
1. TSE / PesqEle / dados abertos;
2. resultados eleitorais oficiais;
3. relatórios e questionários originais dos institutos;
4. microdados, quando disponíveis;
5. releases metodológicos;
6. bases acadêmicas/documentais;
7. fontes secundárias somente para preencher lacunas, sempre marcadas.

Eleições presidenciais prioritárias: 2014, 2018, 2022 e 2026. Eleições para governador tornam-se **painel obrigatório** para estimar house effects e propriedades metodológicas, porque o número de eleições presidenciais é insuficiente. Senado e eleições municipais podem ser usados em modelos hierárquicos quando a comparabilidade for defensável, nunca como observações intercambiáveis.

## 6. Estrutura de dados e imutabilidade

```text
data/
  raw/          # originais imutáveis
  staging/      # extrações e parsing
  canonical/    # esquema normalizado
  derived/      # somente variáveis calculadas
sources/
  tse/
  institutes/
  questionnaires/
  methodology/
methodology/
  hypotheses/
  preregistration/
  experiments/
  model_specifications/
  decisions/
  red_team/
src/
  ingestion/
  parsing/
  normalization/
  validation/
  statistics/
  simulation/
notebooks/
  exploration/
  experiments/
  backtests/
  2026/
tests/
reports/
docs/
```

`data/raw/` nunca é alterado silenciosamente. Correção = novo artefato + proveniência + justificativa.

## 7. Proveniência mínima

Quando disponível, cada observação deve preservar:

`source_id`, `source_type`, `source_url`, `source_file`, `source_date`, `retrieved_at`, `institution`, `institution_family`, `poll_id`, `tse_registration`, `election_id`, `fieldwork_start`, `fieldwork_end`, `publication_date`, `document_page`, `table`, `question_number`, `question_text`, `questionnaire_signature`, `original_variable`, `original_value`, `original_denominator`, `canonical_variable`, `transformation`, `transformation_version`, `quality_flag`, `notes`.

`poll_id` deve preferencialmente usar o registro PesqEle quando aplicável.

Missingness tipada obrigatória:

`NA`, `NOT_ASKED`, `NOT_PUBLISHED`, `NOT_FOUND`, `UNRECOVERABLE`, `NOT_APPLICABLE`.

Zero nunca substitui missing.

## 8. Variáveis a coletar

### Pesquisa/metodologia
Instituto, família/controlador, contratante, pagador, registro TSE, amostra, margem, confiança, abrangência, modo de coleta, desenho amostral, cotas, universo, estratificação, pesos, base demográfica usada, ordem/rotação de candidatos, sequência do questionário e formulação literal.

### Intenção
Espontânea, estimulada, todos os cenários de primeiro e segundo turno, indecisos, não sabe, não respondeu, nenhum, branco, nulo, não votaria.

### Comportamento
Certeza do voto, possibilidade de mudança, segunda opção, rejeição, interesse, entusiasmo, preocupação, certeza declarada de comparecimento, memória do voto anterior, aprovação do governo, identificação partidária/ideológica.

### Demografia
Sexo, idade, renda, escolaridade, região, UF, religião, raça/cor, capital/interior, porte municipal e demais cruzamentos disponíveis.

### Resultado oficial
Eleitorado apto, comparecimento, abstenção, votos totais, válidos, brancos, nulos, votos por candidato, share sobre válidos, share sobre comparecimento e share sobre eleitorado apto; Brasil/UF/município/zona/seção quando útil.

## 9. Denominadores são dados, não detalhe

Nunca comparar percentuais sem identificar o denominador.

Manter pelo menos duas representações paralelas:

1. **total da amostra/eleitorado**;
2. **base equivalente a votos válidos**, quando matematicamente legítimo.

Para erro pesquisa×urna, declarar previamente qual representação é o endpoint. Não recalcular para válidos silenciosamente.

## 10. Tempo: usar fim do campo

Recência é ancorada prioritariamente em `fieldwork_end`, não em publicação.

Não usar apenas “última pesquisa” como verdade universal. Testar curva erro × dias até a eleição em janelas pré-registradas (ex.: D-1, D-3, D-7, D-14, D-30). Late swing deve ser distinguido de erro metodológico.

## 11. Problema estrutural: poucas eleições presidenciais

Com 2014/2018/2022, parâmetros globais anuais possuem n extremamente pequeno. Portanto:

- não vender λG ou λH como estimativas precisas obtidas de três eleições;
- usar priors/cenários e análise de sensibilidade;
- usar `leave-one-election-out` sempre que possível;
- expandir graus de liberdade com painel de governador e outras eleições comparáveis;
- usar modelos hierárquicos, preservando diferenças entre cargos e ciclos.

## 12. Erro eleitoral: múltiplas escalas

Manter benchmarks aditivos e multiplicativos por interpretabilidade:

`e_add = R - P`

`K = R / P`

Mas não privilegiar K como modelo principal, porque shares eleitorais são composicionais.

Testar erro em logit:

`e_logit = logit(R) - logit(P)`

E, para composição multicandidato, ALR/CLR/ILR, com preferência por ILR quando adequado. A escolha final deve ser pré-registrada ou comparada fora da amostra.

## 13. Erro global e house effect

Conceito:

`erro observado = erro global da eleição + house effect + efeito de modo + ruído`.

O house effect só merece transporte temporal se demonstrar estabilidade fora da amostra. O instituto que errou mais que a média em uma eleição não recebe automaticamente a mesma correção quatro anos depois.

Famílias institucionais devem ser explicitamente mapeadas (ex.: sucessões/controladores/metodologias herdadas) para evitar pseudorreplicação.

## 14. Hipóteses espelho obrigatórias

Para toda hipótese direcional relevante registrar, quando logicamente possível:

- H+;
- H−;
- H0.

Exemplo:
- H+: pesquisas subestimam Bolsonaro;
- H−: pesquisas superestimam Bolsonaro;
- H0: não existe direção persistente do erro.

Investigar também hipóteses contrárias à narrativa original: house effect pró-direita, superestimação em modos específicos, voto útil, erros de ponderação demográfica, mudanças de base Censo/PNAD etc.

## 15. Espontânea × estimulada

Definir:

`S_c = espontânea`

`E_c = estimulada`

Benchmarks exploratórios:

`CI = S/E`

`SG = E-S`

CI é instável para E pequeno e não deve ser usado cegamente. Preferir também diferença em escala logit quando possível:

`SG_logit = logit(E) - logit(S)`.

Toda análise deve ser estratificada por modo de coleta e assinatura do questionário.

Hipótese a testar, não premissa: maior cristalização espontânea pode predizer persistência/comparecimento/menor erro.

## 16. Turnout e “eleitor preguiçoso”

`T_c = P(comparecer | preferência c)` é variável latente na maioria das pesquisas publicadas. Não fingir observabilidade.

Só estimar por:
- microdados/painel apropriado;
- proxy explicitamente marcado (certeza declarada de comparecimento);
- inferência ecológica cuidadosamente especificada;
- outras fontes identificáveis.

Hipótese específica:

`P(comparecer | espontâneo) > P(comparecer | apenas estimulado)`.

Sem microdados ou desenho adequado, tratar como hipótese não identificada, não como fato.

## 17. Brancos, nulos e abstenção

São fenômenos distintos.

Abstenção, branco e nulo não são votos automáticos para o líder. Comparecimento diferencial pode, porém, alterar a composição dos válidos.

Coletar e modelar separadamente:
- abstenção;
- branco;
- nulo;
- indecisão;
- “não votaria”.

Comparar declaração pré-eleitoral com resultado real e testar conversão tardia sem redistribuição arbitrária.

## 18. Voto não capturado e preferência latente

Benchmark:

`U_c = R_c - E_c`.

Se houver subestimação sistemática, não rotulá-la automaticamente como “voto envergonhado”. Concorrentes causais incluem late swing, nonresponse bias, turnout diferencial, sampling/weighting error, mode effect e social desirability.

## 19. Rejeição, piso e teto

Tratar como hipótese:

- espontânea pode aproximar piso cristalizado;
- estimulada pode aproximar fotografia corrente;
- `1 - rejeição` pode aproximar teto.

Testar historicamente. Eleitores podem atravessar rejeição declarada; nenhuma dessas equivalências é axioma.

## 20. Bolsonaro → Flávio

Não assumir equivalência entre Jair Bolsonaro 2022 e Flávio Bolsonaro 2026.

Representar transferência por `rho_BF`, submetido a sensibilidade e evidência de identificação bolsonarista, memória de voto, demografia, espontânea/estimulada, rejeição e fidelidade. `rho_BF = 1` é cenário, não default factual.

## 21. Modo de coleta e questionário

Estratificar e testar presencial, telefone, online, híbrido e demais métodos. Investigar interação entre modo, instituto, eleição, escolaridade, renda, região e preferência.

Criar `questionnaire_signature` com formulação, ordem, rotação, cartão/lista, perguntas precedentes e sequência espontânea→estimulada. Efeito de questionário não deve ser confundido com house effect.

## 22. Ponderação e universo

Registrar qual base demográfica cada instituto usou em cada eleição: Censo, PNAD, projeções, eleitorado TSE ou combinação. Investigar impacto da transição Censo 2010 → Censo 2022 e possíveis erros de escolaridade, renda, região, idade, religião e outras dimensões.

## 23. Agregação temporal intrainstituto

Múltiplas ondas do mesmo instituto aumentam informação sobre sua trajetória, não o número de “votos” do instituto na meta-análise.

Testar modelos temporais adequados (state-space, local linear trend, kernel ou alternativas), com hiperparâmetros pré-registrados ou validados fora da amostra. Preservar correlação entre ondas do mesmo instituto/painel.

## 24. Peso e meta-análise

Peso não é reputação editorial. Pode considerar tamanho amostral efetivo, erro histórico fora da amostra, transparência, recência, cobertura, método e qualidade documental.

Evitar que uma família domine por frequência de publicação. Reportar heterogeneidade e não escondê-la atrás da média. Considerar random effects/hierarchical pooling quando adequado.

## 25. Identificabilidade

Antes de testar qualquer parâmetro perguntar:

1. ele é observado?
2. é identificável com os dados existentes?
3. é apenas proxy?
4. depende de hipótese não testável?

Parâmetros não identificáveis não recebem estimativa pontual disfarçada de fato.

## 26. Testes variável por variável

Cada variável candidata deve enfrentar isoladamente:
- efeito médio;
- heterogeneidade entre institutos;
- heterogeneidade entre modos;
- estabilidade entre eleições;
- sensibilidade ao denominador;
- sensibilidade à janela temporal;
- desempenho fora da amostra;
- hipóteses espelho;
- placebo/negative controls quando possível.

Classificação:
- **A — robusta:** candidata ao modelo principal;
- **B — sinal consistente, evidência limitada:** somente sensibilidade/cenários;
- **C — inconclusiva:** não altera previsão;
- **D — contradita:** excluída do mecanismo preditivo.

Critérios numéricos devem ser pré-registrados por experimento.

## 27. Backtest e seleção

“Explicar 2022” não basta. Evitar overfitting retrospectivo.

Usar leave-one-election-out, validação temporal, painel estadual e holdouts explícitos. Seleção de variáveis nas mesmas três eleições usadas para avaliá-las é proibida como evidência confirmatória.

## 28. 2026: protocolo prospectivo

Manter dois cofres:

### Cofre A — Modelo mínimo prospectivo
Congelar o quanto antes uma especificação simples e preregistrada para produzir verdadeiro teste out-of-s
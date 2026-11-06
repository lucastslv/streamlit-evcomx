Eu apresentaria assim, usando a versão revisada:

:codex-file-citation{path="/home/lucastslv/src/bootcamp/dados-bootcamp/output/presentations/Achados_EVCOMX_v2.pptx" purpose="source"}

**Slide 1 — Carga alta**

“Nosso objetivo foi entender como a carga alta aparece nos dados e quais características dos cestos estão associadas a esse problema.

Analisamos 1.799 corridas, olhando tanto a ocorrência quanto o tempo de parada. Esta é uma análise exploratória: queremos identificar padrões que ajudem a orientar a investigação com a operação.”

**Slide 2 — Carga alta afetou 3 em cada 10 corridas**

“Começando pela dimensão do problema: 541 das 1.799 corridas tiveram carga alta em pelo menos um carregamento. Isso representa 30,1% da amostra.

Somando os tempos registrados nos dois carregamentos, chegamos a 36,8 horas de parada. Portanto, mesmo que muitas ocorrências sejam curtas, elas acumulam um tempo relevante.

Esse total corresponde à amostra analisada. Para transformá-lo em uma estimativa anual ou financeira, precisaríamos confirmar a cobertura dos dados e o custo da parada.”

**Slide 3 — Metade das corridas afetadas parou por cerca de 3 minutos**

“Aqui olhamos apenas as 541 corridas afetadas. Cada barra mostra quantas tiveram um tempo de parada dentro daquele intervalo.

A maior concentração está nos tempos curtos. A mediana foi de aproximadamente três minutos: metade das corridas afetadas ficou abaixo desse tempo e metade acima.

Mas também existem ocorrências mais longas. O percentil 95 foi de 11,9 minutos, ou seja, aproximadamente 95% ficaram até esse tempo.

Isso sugere avaliar tanto a frequência das ocorrências quanto os casos mais demorados.”

**Slide 4 — Cestos diferentes exigem comparações separadas**

“Antes de procurar uma explicação, precisamos reconhecer que os dois cestos têm características diferentes.

O primeiro tem massa mediana de 58,1 toneladas e 14 camadas ativas. O segundo tem 32,3 toneladas e oito camadas. O volume estimado também é maior no primeiro.

Por isso, fizemos as comparações separadamente por cesto e relacionamos cada um ao evento do mesmo carregamento.

Também há uma diferença de cobertura: temos 1.799 primeiros cestos registrados, mas somente 1.702 segundos cestos. Essa ausência vai aparecer novamente adiante.”

**Slide 5 — O volume mediano é semelhante com e sem carga alta**

“Neste gráfico, o cinza representa os cestos sem carga alta e o laranja representa os cestos com carga alta. Cada barra mostra a mediana do grupo.

No primeiro cesto, os valores são praticamente iguais: 70,0 e 70,6 metros cúbicos. No segundo, também: 43,1 e 43,0.

Portanto, a comparação das medianas não mostra uma separação clara pelo volume estimado.

Isso não significa que o volume físico seja irrelevante. Nosso cálculo usa massa e densidade cadastrada; ele não mede diretamente a ocupação do cesto, a disposição dos materiais ou sua compactação.”

**Slide 6 — A diferença na composição é maior no segundo cesto**

“Quando olhamos a composição, aparece uma diferença mais visível.

No primeiro cesto, a proporção mediana de materiais classificados como pesados é de 32,1% sem carga alta e 29,0% com carga alta. A diferença é de 3,1 pontos percentuais.

No segundo cesto, ela é maior: 24,1% contra 15,0%, uma diferença de 9,1 pontos percentuais.

Esse resultado torna a composição uma hipótese relevante para investigar. Ainda precisamos verificar se essa associação permanece quando comparamos condições semelhantes de massa, receita e período. Esses números, sozinhos, não demonstram que aumentar a proporção de pesados reduziria o problema.”

**Slide 7 — Corridas sem o cesto 2 registrado têm mais carga alta**

“A qualidade dos registros também chama atenção.

Nas corridas com os dois cestos registrados, a frequência de carga alta foi de 28,8%. Nas 97 corridas sem registro de massa positiva no segundo cesto, foi de 51,5%.

Os traços pretos mostram a incerteza das taxas. O grupo menor apresenta um intervalo mais amplo.

Além disso, sete corridas possuem um evento identificado no próprio segundo carregamento, apesar da ausência desse registro de massa.

Precisamos esclarecer o significado dessa ausência. Se simplesmente descartarmos essas corridas, estaremos retirando um grupo com frequência maior do problema e mudando o perfil da amostra.”

**Slide 8 — A próxima decisão é validar as hipóteses com a operação**

“A análise aponta três frentes de trabalho.

Primeiro, esclarecer os registros: investigar os cestos ausentes, os códigos ainda sem interpretação e as hipóteses sobre unidades e densidades.

Depois, comparar condições semelhantes para entender quanto da associação com a composição permanece após considerar massa, receita e período.

Por fim, se avançarmos para um alerta, precisamos avaliá-lo em corridas futuras, usando somente informações disponíveis antes da decisão.

O resultado deve ser medido pela capacidade de identificar eventos e pelo impacto nos minutos de parada.”

**Slide 9 — Composição e qualidade dos registros são prioridades**

“A mensagem principal é que a carga alta aparece com frequência e acumula tempo de parada nesta amostra.

O volume estimado apresentou pouca diferenciação entre os grupos. Já a composição, principalmente no segundo cesto, trouxe uma hipótese mais promissora para investigação.

Ao mesmo tempo, os registros ausentes podem influenciar nossas conclusões. Nossa recomendação é levar esses dois pontos à equipe de processo e definir as próximas verificações.”

**Slide 10 — O calendário sugere uma hipótese que precisa de contexto**

“Este é um resultado complementar.

Nas datas sinalizadas pelo calendário utilizado, a frequência de carga alta foi de 45,6%, contra 29,4% nos demais dias.

Mas o primeiro grupo contém somente 68 corridas, e seu intervalo de incerteza é mais amplo.

Também precisamos confirmar o fuso dos horários e entender como essas datas se relacionam com a operação da planta. Diferenças de receita ou de período podem explicar parte do resultado.

Portanto, tratamos esse achado como uma hipótese para investigar, sem atribuir a diferença ao calendário.”

**Slide 11 — A composição tem associação maior que o volume estimado**

“Este último slide apresenta o apoio estatístico às comparações anteriores.

A correlação de Pearson resume a associação linear entre cada característica e a ocorrência de carga alta. Valores próximos de zero indicam pouca associação linear. O sinal negativo indica que valores maiores da característica estiveram associados a menor ocorrência do evento.

O volume ficou muito próximo de zero nos dois cestos. A proporção de pesados apresentou uma associação negativa de maior magnitude, principalmente no segundo cesto, com correlação de aproximadamente −0,268.

Mesmo retirando os candidatos a valores extremos, a associação do volume continuou pequena. Isso reforça a prioridade de investigar a composição, mantendo a distinção entre associação observada, causa do problema e capacidade de previsão.”


-------

São **datas de feriados e celebrações listadas no calendário da BrasilAPI**, usado no notebook. O rótulo “datas do calendário” ficou pouco claro.

Na nossa amostra, esse grupo reúne **14 datas diferentes e 68 corridas**. Alguns exemplos:

| Data | Nome no calendário |
|---|---|
| 07/09/2025 | Independência do Brasil |
| 25/12/2025 | Natal |
| 01/01/2026 | Confraternização mundial |
| 16 e 17/02/2026 | Carnaval |
| 03/04/2026 | Sexta-feira Santa |
| 04/06/2026 | Corpus Christi |

Para classificar cada corrida, usamos o **primeiro horário de consumo com peso positivo do cesto 1**, convertido para o horário de São Paulo. Se a data estava nessa lista, a corrida entrava no grupo destacado. O fuso ainda precisa ser confirmado.

O gráfico compara:

- **Nessas datas:** 31 das 68 corridas tiveram carga alta — **45,6%**.
- **Nos demais dias:** 508 das 1.728 corridas tiveram carga alta — **29,4%**.

A pergunta investigada é: **“A frequência de carga alta muda nas datas sinalizadas por esse calendário?”**

Observamos uma diferença, mas ainda não sabemos sua explicação. Essas datas podem coincidir com receitas, condições operacionais ou períodos diferentes. Além disso, o calendário externo **não informa se a fábrica parou, mudou de turno ou trabalhou com outra equipe**.

Eu apresentaria esse slide dizendo: “Encontramos uma frequência maior nessas datas, em um grupo pequeno de corridas. Precisamos cruzar isso com o calendário real da planta antes de interpretar o resultado.”

:codex-file-citation{path="/home/lucastslv/src/bootcamp/dados-bootcamp/notebooks/edba_simples.ipynb" purpose="source"}

:codex-file-citation{path="/home/lucastslv/src/bootcamp/dados-bootcamp/data/external/brasilapi_calendario_2025.json" purpose="source"}

:codex-file-citation{path="/home/lucastslv/src/bootcamp/dados-bootcamp/data/external/brasilapi_calendario_2026.json" purpose="source"}

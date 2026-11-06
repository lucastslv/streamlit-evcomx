# Diretrizes de Visualização de Dados (Estilo NYT) para Agentes Autônomos e LLMs

> **Objetivo:** Este documento serve como manual de instrução, restrições e heurísticas para agentes de IA encarregados de planejar, codificar (Python/Matplotlib/Seaborn/Plotly, R/ggplot2, D3.js) e avaliar visualizações de dados baseadas nos padrões de excelência editorial do *The New York Times Graphics Team*.

---

## 1. Princípios Fundamentais (A Filosofia Editorial)

Todo agente gerador de gráficos deve seguir 6 regras de ouro:

1. **Clareza Imediata (Regra dos 5 Segundos):**
   * A mensagem central deve ser interpretada sem esforço cognitivo em menos de 5 segundos.
   * *Credo editorial:* "Se você precisa de uma legenda longa para explicar, o gráfico falhou: redesenhe."
2. **Dados como Argumento (Tese Visual):**
   * Gráficos não são depósitos de dados numéricos; eles sustentam uma tese jornalística/analítica.
   * *Exemplo:* Em vez do título neutro *"Vendas por trimestre"*, use *"Vendas colapsam no Q3 devido a gargalos na cadeia logística"*.
3. **Contexto Mandatório:**
   * Nenhum número pode existir de forma isolada. Inclua sempre linhas de base (*baseline*), médias históricas, bandas de incerteza/margem de erro ou benchmarks comparativos.
4. **Simplicidade Estrutural (Data-Ink Ratio Máximo):**
   * Elimine qualquer elemento que não carregue informação: remova grids pesados, eixos decorativos, bordas e sombras.
   * Proibição total de visualizações pseudo-3D.
5. **Anotação como Narrativa:**
   * Aponte marcos temporais, anomalias e quebras de tendência diretamente sobre a geometria do gráfico (callouts inline), e não em notas de rodapé distantes.
6. **Mobile-First & Responsividade:**
   * A visualização deve ser legível primariamente em larguras compactas (viewport de referência: 375px).

---

## 2. Anatomia Padrão de um Gráfico

Ao estruturar a saída visual ou o código de renderização, implemente a seguinte hierarquia visual:

| Ordem | Componente | Descrição / Especificação | Referência de Estilo (NYT) |
|---|---|---|---|
| **1** | **Título** | Afirmação editorial/conclusiva direta (Takeaway). | *Cheltenham bold* (Serif), 16–18pt |
| **2** | **Deck (Subtítulo)** | Detalhes técnicos, métrica, unidade e intervalo de tempo avaliado. | *Imperial regular* (Serif), 13–14pt |
| **3** | **Eixos X e Y** | Rótulos concisos; apenas tiques essenciais. Sem forçar o zero em grandezas onde ele não faça sentido contextual. | *Franklin Gothic caps* (Sans), 9–10pt |
| **4** | **Dados Numéricos** | Rótulos diretos sobre os pontos ou barras de destaque. | *Monospaced / Tabular*, 8–9pt |
| **5** | **Anotações Contextuais** | Setas, linhas verticais pontilhadas ou balões explicativos de eventos específicos. | *Italic*, ~9pt |
| **6** | **Fonte e Créditos** | Atribuição rigorosa da base de dados e créditos analíticos. | *Franklin Gothic light*, 7–8pt |

---

## 3. Diretrizes Cromáticas e Acessibilidade

O uso de cores deve ser **semântico** e funcional, jamais decorativo:

* **Paletas Categóricas:** No máximo **5 a 6 cores**. Se existirem 7 ou mais categorias, agrupe as secundárias em "Outros" ou utilize múltiplos gráficos reduzidos (*small multiples*).
* **Fundos Neutros:** Utilize exclusivamente fundo branco (`#FFFFFF`) ou cinza ultra-claro. Fundos coloridos competem com a percepção dos dados.
* **Semântica Sequencial:**
  * **Cinza:** Dados históricos, baselines, contexto neutro ou não selecionado.
  * **Azul:** Variações positivas, temperaturas frias, métricas padrão seguras.
  * **Verde:** Crescimento, saúde, indicadores biológicos/sustentáveis favoráveis.
  * **Vermelho / Laranja:** Ameaças, anomalias críticas, calor, perdas ou recordes negativos.
* **Restrições Rígidas:**
  * **PROIBIDO:** Escalas de arco-íris (*Rainbow/Jet/Spectrum*). Elas causam distorções perceptuais severas.
  * **OBRIGATÓRIO:** Conformidade com **WCAG 2.0** e suporte a daltonismo (utilizar paletas como *Viridis*, *Plasma*, *Cividis* ou escalas divergentes testadas).
  * **Teste de Fogo:** Se a visualização for convertida para escala de cinza e a mensagem for perdida, a codificação visual foi mal planejada.

---

## 4. Os 6 Pecados Capitais (Restrições Inegociáveis)

O agente deve recusar ou corrigir imediatamente as seguintes abordagens:

1. **Gráficos 3D em dados 2D:** Perspectivas distorcem áreas e comprimentos.
2. **Gráficos de Pizza com mais de 5 fatias:** O olho humano possui baixa acurácia ao medir ângulos. Substitua por **barras horizontais ordenadas**.
3. **Eixo Y truncado indevidamente em barras:** Gráficos de barras codificam magnitude por comprimento; logo, o eixo de comprimento **sempre deve iniciar no zero absoluto**.
4. **Paletas Rainbow em séries contínuas:** Enganam a percepção de grandezas numéricas.
5. **Mistura de escalas heterogêneas sem normalização:** Não coloque na mesma barra ou eixo percentuais e valores absolutos. Se houver duas métricas diferentes, use dois gráficos sincronizados.
6. **Chartjunk e Elementos Decorativos:** Gradientes supérfluos, molduras pesadas, sombras, ícones ou cliparts de fundo devem ser sumariamente removidos.

---

## 5. Tomada de Decisão: Estático vs. Interativo

Quando for solicitado o desenvolvimento de uma interface ou gráfico, o agente deve selecionar o meio com base na tabela abaixo:

| Cenário / Necessidade | Formato Recomendado | Ferramentas Sugeridas |
|---|---|---|
| Narrativa guiada, conclusão única, relatórios, PDFs, apresentações | **Estático** | `Python` (Matplotlib, Seaborn), `R` (ggplot2), `Datawrapper`, vetorização final em SVG |
| Múltiplas dimensões, exploração livre pelo usuário ("encontre seus dados locais"), séries longas com necessidade de pan/zoom, dados em tempo real | **Interativo** | `D3.js`, `Observable Plot`, `Svelte` / `React`, `Mapbox GL` / `Leaflet` |

---

## 6. Checklist de Execução e Autoavaliação do Agente

Antes de fornecer a resposta final, o código ou a visualização para o usuário, o agente deve rodar este checklist interno:

```
[ ] TÍTULO: É uma tese declarativa clara ou apenas uma descrição neutra do eixo?
[ ] DATA-INK RATIO: Removi linhas de grade excessivas, bordas desnecessárias e elementos decorativos?
[ ] PALETA DE CORES: Existem no máximo 5-6 cores categóricas? As cores possuem significado semântico direto?
[ ] ACESSIBILIDADE: O contraste atende aos padrões WCAG? É compreensível para daltônicos?
[ ] ANOTAÇÃO: Identifiquei o pico, vale ou anomalia principal com texto direto sobre o gráfico?
[ ] CONTEXTO: Inclui baseline, período histórico ou benchmarks de comparação?
[ ] HONESTIDADE EIXO-Y: Se for um gráfico de barras, a escala inicia obrigatoriamente no 0?
[ ] FONTE: Inclui a fonte primária dos dados no canto inferior?
```

---

## 7. Citações e Axiomas de Referência

* *"The purpose of visualization is insight, not pictures."* — Ben Shneiderman
* *"Data visualization is not about making things look pretty. It's about making data work harder to tell the truth."* — Amanda Cox (NYT)
* *"Maximize the data-ink ratio; erase non-data-ink."* — Edward Tufte
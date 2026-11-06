### 11/09

Exploratory Data Analysis
- Estatísticas descritivas (tendência central, medidas de dispersão)
- Exame gráfico de dados (univariado, bivariado, multivariado)
- Entradas duplicadas
- Dados ausentes
- Formatos de dados
- Outliers
- Suposições para técnicas analíticas

### 18/09

**Projeto com a Evcomx**

- Siderurgia
	- Accelor em Juiz de Fora
	- Parte de aços longos
- Usina semi-integrada
	- Forno elétrico a arco (FEA) que recebe sucata, não minério de ferro
- Sucata carregada no cestão (dois cestões de ~40T em JF) e depois pro forno (~1500 °C)
- Bode: quando precisa mais energia que o previsto pra aquecer

- Problema de carga alta gera atraso
	- não consegue fechar a tampa do forno devido à forma como a sucata entra
	- antigamente martelava com o próprio cestão...
	- hoje injeta oxigênio e queima mas demora muito (~15 min)
	- **nosso projeto : prever se vai dar carga alta !! **

- Forno panela (FP)
	- ajustar a composição química
	- energia vem mais da queima de oxigênio
	- amostras (pirulitos) pra análise química
- gusa (90% ferro) e escória (lixo...) já são separados na saída do FEA
- Análise no FP é feita pra ver o que será adicionado (enxofre, alumínio, ...) pros diferentes tipos de aço
- FEA ~1h, FP ~1h, desgaseificador, lingotamento
- Lingotamento contínuo (CL) pra transformar em tarugos
- Projeto do outro bootcamp: prever a que temperatura o aço deve sair do FP pra, 1h depois, estar na temperatura ideal de lingotamento
	- Se estiver muito quente, não pode ser cortado (líquido)
	- se muito frio, freezing

- Montagem dos cestos pro FEA:
	1. Material leve no fundo pra "amortecer" (e.g. alumínio picado)
	2. Material pesado (e.g. gusa sólida ou líquida, sucata de gusa)
	3. Material médio (misto)
	4. Material leve no topo pra entrar em contato com o eletrodo do forno
	- Arco elétrico é mais forte na região central
- Distribuição final dos materiais pode ser diferente da receita
	- vamos receber quanto era previsto e quanto foi colocado
- Previsão de carga alta tem que ser feita pra cada cesto que vai ser carregado
	- Prevalência de carga alta difere (cesto 1 pega o forno vazio, cesto 2 já na metade)
	- **mais chance de carga alta no cesto 2 ??**
- Ideia: pesquisar ou inferir a compressibilidade (?) dos materiais, especialmente os leves
- Classificação -> probabilidade, score, ...
- Divisão cronológica pro split treino/teste
	- 10% mais recentes pra teste
- Balanceamento:
	- na usina, 2 a 3% de carga alta
	- no dataset do projeto, ~20%

O PROJETO
- Análise exploratória de dados
	- Como as variáveis descrevem o processo?
	- Quais informações estão disponíveis?
	- Qual o impacto das paradas de carga alta na produção?
- Modelagem dos dados
	- Como modelar os dados?
	- Como podemos construir uma tabela que um modelo possa usar?
- Enriquecimento de dados
	- Como enriquecer os dados?
	- Que dados podem ser "criados" e que fazem sentido para o processo?
- Novo modelo
	- Treinar um ou mais modelos (e.g. regressão logística, XGBoost, Catboost)
	- Avaliar se esse moedlo evita paradas com sucesso entregando minutos de produção de volta
- Apresentação de análises e resultados
	- Elaborar apresentação como se estivesse defendendo o modelo para um gerente de processo (business case)
	- Considerar certo se o modelo apontar uma parada de carga alta que aconteceu e mensurar o ganho em minutos de produção entregue pelo uso do modelo
- Estruturação dos dados
	- Construir um modelo de classificação
	- Investigar relações temporais
	- Testar o modelo nos 10% de corridas mais recentes

### 25/09

- Feature selection por correlação: remover se |corr| > 0,8
- EDA antes do split treino/teste, feature selection depois (apenas sobre treino)






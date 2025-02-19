# Análise de Dados

## 📊 Processamento e Visualização

### Análise Básica

1. **Processamento de CSV**
   ```python
   import pandas as pd
   import numpy as np
   from typing import Dict, List, Any
   import Papa from 'papaparse'
   
   class CSVAnalyzer:
       """
       Analisador de arquivos CSV com tratamento de erros
       """
       def __init__(self, filepath: str):
           self.filepath = filepath
           self.data = None
           self.load_data()
   
       async def load_data(self):
           """
           Carrega dados do CSV usando PapaParse
           """
           try:
               content = await window.fs.readFile(self.filepath, { encoding: 'utf8' })
               parsed = Papa.parse(content, {
                   header: True,
                   dynamicTyping: True,
                   skipEmptyLines: true
               })
               
               if parsed.errors.length > 0:
                   print(f"Erros no parsing: {parsed.errors}")
               
               self.data = parsed.data
           except Exception as e:
               print(f"Erro ao carregar arquivo: {str(e)}")
               return None
   
       def get_summary(self) -> Dict[str, Any]:
           """
           Retorna resumo estatístico dos dados
           """
           if not self.data:
               return {}
           
           summary = {
               'total_rows': len(self.data),
               'columns': list(self.data[0].keys()),
               'numeric_stats': {},
               'categorical_stats': {}
           }
           
           for col in summary['columns']:
               values = [row[col] for row in self.data]
               if all(isinstance(v, (int, float)) for v in values if v is not None):
                   summary['numeric_stats'][col] = {
                       'mean': np.mean(values),
                       'median': np.median(values),
                       'std': np.std(values),
                       'min': min(values),
                       'max': max(values)
                   }
               else:
                   value_counts = {}
                   for v in values:
                       if v not in value_counts:
                           value_counts[v] = 0
                       value_counts[v] += 1
                   summary['categorical_stats'][col] = value_counts
           
           return summary
   ```

2. **Visualização de Dados**
   ```python
   import React from 'react'
   import { LineChart, BarChart, ScatterPlot } from 'recharts'
   
   class DataVisualizer:
       """
       Criador de visualizações com Recharts
       """
       def create_line_chart(data, x_key, y_key, title=""):
           """
           Cria gráfico de linha
           """
           return (
               <LineChart width={600} height={400} data={data}>
                   <XAxis dataKey={x_key} />
                   <YAxis />
                   <Tooltip />
                   <Legend />
                   <Line type="monotone" dataKey={y_key} />
               </LineChart>
           )
   
       def create_bar_chart(data, x_key, y_key, title=""):
           """
           Cria gráfico de barras
           """
           return (
               <BarChart width={600} height={400} data={data}>
                   <XAxis dataKey={x_key} />
                   <YAxis />
                   <Tooltip />
                   <Legend />
                   <Bar dataKey={y_key} fill="#8884d8" />
               </BarChart>
           )
   
       def create_scatter_plot(data, x_key, y_key, title=""):
           """
           Cria gráfico de dispersão
           """
           return (
               <ScatterChart width={600} height={400}>
                   <XAxis dataKey={x_key} />
                   <YAxis dataKey={y_key} />
                   <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                   <Scatter data={data} fill="#8884d8" />
               </ScatterChart>
           )
   ```

### Análise Avançada

1. **Processamento de Séries Temporais**
   ```python
   class TimeSeriesAnalyzer:
       """
       Analisador de séries temporais
       """
       def __init__(self, data, date_column):
           self.data = data
           self.date_column = date_column
   
       def resample(self, freq='D', agg_func='mean'):
           """
           Reamostra dados em frequência específica
           """
           df = pd.DataFrame(self.data)
           df[self.date_column] = pd.to_datetime(df[self.date_column])
           df.set_index(self.date_column, inplace=True)
           
           return df.resample(freq).agg(agg_func)
   
       def detect_seasonality(self, column):
           """
           Detecta padrões sazonais
           """
           from statsmodels.tsa.seasonal import seasonal_decompose
           
           df = pd.DataFrame(self.data)
           df[self.date_column] = pd.to_datetime(df[self.date_column])
           df.set_index(self.date_column, inplace=True)
           
           decomposition = seasonal_decompose(df[column])
           
           return {
               'trend': decomposition.trend,
               'seasonal': decomposition.seasonal,
               'residual': decomposition.resid
           }
   ```

2. **Análise Estatística**
   ```python
   class StatisticalAnalyzer:
       """
       Análise estatística avançada
       """
       def __init__(self, data):
           self.data = data
   
       def correlation_analysis(self, columns=None):
           """
           Análise de correlação entre variáveis
           """
           df = pd.DataFrame(self.data)
           if columns:
               df = df[columns]
           
           numeric_cols = df.select_dtypes(include=[np.number]).columns
           return df[numeric_cols].corr()
   
       def hypothesis_test(self, group_col, value_col, test_type='t'):
           """
           Testes de hipótese
           """
           from scipy import stats
           
           df = pd.DataFrame(self.data)
           groups = df.groupby(group_col)[value_col].apply(list)
           
           if test_type == 't' and len(groups) == 2:
               stat, pvalue = stats.ttest_ind(*groups)
               return {
                   'test_type': 't-test',
                   'statistic': stat,
                   'p_value': pvalue
               }
           elif test_type == 'anova':
               stat, pvalue = stats.f_oneway(*groups)
               return {
                   'test_type': 'ANOVA',
                   'statistic': stat,
                   'p_value': pvalue
               }
   ```

### Machine Learning

1. **Preparação de Dados**
   ```python
   class DataPreprocessor:
       """
       Preparação de dados para ML
       """
       def __init__(self, data):
           self.data = data
   
       def handle_missing_values(self, strategy='mean'):
           """
           Tratamento de valores faltantes
           """
           df = pd.DataFrame(self.data)
           
           if strategy == 'mean':
               return df.fillna(df.mean())
           elif strategy == 'median':
               return df.fillna(df.median())
           elif strategy == 'mode':
               return df.fillna(df.mode().iloc[0])
           elif strategy == 'drop':
               return df.dropna()
   
       def encode_categories(self, columns):
           """
           Codificação de variáveis categóricas
           """
           df = pd.DataFrame(self.data)
           
           for col in columns:
               if df[col].dtype == 'object':
                   df[col] = pd.Categorical(df[col]).codes
           
           return df
   
       def scale_features(self, columns, method='standard'):
           """
           Escalonamento de features
           """
           from sklearn.preprocessing import StandardScaler, MinMaxScaler
           
           df = pd.DataFrame(self.data)
           
           if method == 'standard':
               scaler = StandardScaler()
           else:
               scaler = MinMaxScaler()
           
           df[columns] = scaler.fit_transform(df[columns])
           return df
   ```

2. **Modelagem**
   ```python
   class ModelTrainer:
       """
       Treinamento de modelos de ML
       """
       def __init__(self, X, y):
           self.X = X
           self.y = y
   
       def train_test_split(self, test_size=0.2):
           """
           Divisão em treino e teste
           """
           from sklearn.model_selection import train_test_split
           return train_test_split(
               self.X, self.y,
               test_size=test_size,
               random_state=42
           )
   
       def train_model(self, model_type='regression'):
           """
           Treina modelo específico
           """
           from sklearn.linear_model import LinearRegression
           from sklearn.ensemble import RandomForestClassifier
           
           X_train, X_test, y_train, y_test = self.train_test_split()
           
           if model_type == 'regression':
               model = LinearRegression()
           else:
               model = RandomForestClassifier()
           
           model.fit(X_train, y_train)
           
           return {
               'model': model,
               'train_score': model.score(X_train, y_train),
               'test_score': model.score(X_test, y_test)
           }
   ```

### Exemplos de Uso

1. **Análise Básica**
   ```python
   # Carregar e analisar CSV
   analyzer = CSVAnalyzer("dados.csv")
   summary = analyzer.get_summary()
   
   # Criar visualizações
   visualizer = DataVisualizer()
   line_chart = visualizer.create_line_chart(
       data=analyzer.data,
       x_key='data',
       y_key='valor'
   )
   ```

2. **Análise Temporal**
   ```python
   # Análise de série temporal
   ts_analyzer = TimeSeriesAnalyzer(data, 'data')
   daily_data = ts_analyzer.resample('D')
   seasonality = ts_analyzer.detect_seasonality('vendas')
   ```

3. **Machine Learning**
   ```python
   # Preparar dados
   preprocessor = DataPreprocessor(data)
   clean_data = preprocessor.handle_missing_values()
   scaled_data = preprocessor.scale_features(['altura', 'peso'])
   
   # Treinar modelo
   X = scaled_data[['altura', 'peso']]
   y = scaled_data['categoria']
   
   trainer = ModelTrainer(X, y)
   results = trainer.train_model('classification')
   ```

### Boas Práticas

1. **Preparação de Dados**
   - Verifique qualidade dos dados
   - Trate valores faltantes
   - Normalize quando necessário
   - Documente transformações

2. **Análise**
   - Comece com análise exploratória
   - Valide pressupostos
   - Use visualizações apropriadas
   - Documente insights

3. **Modelagem**
   - Valide modelos
   - Use cross-validation
   - Monitore overfitting
   - Documente parâmetros

### Recursos Adicionais

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn Tutorials](https://scikit-learn.org/stable/tutorial/index.html)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [Statistical Learning](https://www.statlearning.com/)
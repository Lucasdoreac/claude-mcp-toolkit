# APIs e Alternativas para Expansão de Funcionalidades

## 🔍 APIs de Busca

### Alternativas Gratuitas ao Brave Search

1. **DuckDuckGo API**
   - Gratuita para uso não comercial
   - Documentação: [https://duckduckgo.com/api](https://duckduckgo.com/api)
   ```python
   import requests
   
   def search_ddg(query):
       url = f"https://api.duckduckgo.com/?q={query}&format=json"
       response = requests.get(url)
       return response.json()
   ```

2. **Serpapi (com tier gratuito)**
   - 100 buscas gratuitas/mês
   - Site: [https://serpapi.com](https://serpapi.com)
   ```python
   from serpapi import GoogleSearch
   
   def search_google(query, api_key):
       params = {
           "q": query,
           "api_key": api_key
       }
       search = GoogleSearch(params)
       return search.get_dict()
   ```

3. **Qwant API**
   - API gratuita europeia
   - Documentação: [https://www.qwant.com/api](https://www.qwant.com/api)

## 📊 APIs de Análise de Dados

1. **Alpha Vantage (Dados Financeiros)**
   - Chave gratuita: [https://www.alphavantage.co](https://www.alphavantage.co)
   ```python
   import requests
   
   def get_stock_data(symbol, api_key):
       url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
       response = requests.get(url)
       return response.json()
   ```

2. **OpenWeatherMap**
   - 60 chamadas/minuto gratuitas
   - Registro: [https://openweathermap.org/api](https://openweathermap.org/api)
   ```python
   def get_weather(city, api_key):
       url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
       response = requests.get(url)
       return response.json()
   ```

## 🤖 APIs de IA

1. **HuggingFace**
   - Modelos gratuitos disponíveis
   - Site: [https://huggingface.co](https://huggingface.co)
   ```python
   from transformers import pipeline
   
   def analyze_sentiment(text):
       classifier = pipeline("sentiment-analysis")
       return classifier(text)
   ```

2. **OpenAI GPT-3.5**
   - Preços acessíveis
   - Documentação: [https://platform.openai.com/docs](https://platform.openai.com/docs)
   ```python
   import openai
   
   def generate_text(prompt, api_key):
       openai.api_key = api_key
       response = openai.ChatCompletion.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content
   ```

## 📁 Armazenamento e Banco de Dados

1. **Supabase (Alternativa ao Firebase)**
   - Tier gratuito generoso
   - Site: [https://supabase.com](https://supabase.com)
   ```python
   from supabase import create_client
   
   def setup_supabase(url, key):
       return create_client(url, key)
   ```

2. **MongoDB Atlas**
   - Cluster gratuito
   - Site: [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas)
   ```python
   from pymongo import MongoClient
   
   def connect_mongodb(connection_string):
       client = MongoClient(connection_string)
       return client.database
   ```

## 📈 Visualização de Dados

1. **Plotly**
   - Gratuito para uso básico
   - Documentação: [https://plotly.com/python/](https://plotly.com/python/)
   ```python
   import plotly.express as px
   
   def create_visualization(data):
       fig = px.line(data, x='date', y='value')
       return fig.show()
   ```

2. **Chart.js**
   - Totalmente gratuito
   - Site: [https://www.chartjs.org](https://www.chartjs.org)
   ```javascript
   const createChart = (ctx, data) => {
     new Chart(ctx, {
       type: 'bar',
       data: data,
       options: {}
     });
   }
   ```

## 🔧 Ferramentas de Desenvolvimento

1. **Railway**
   - Alternativa ao Heroku
   - Site: [https://railway.app](https://railway.app)
   ```bash
   # Deploy via CLI
   railway up
   ```

2. **Netlify**
   - Hospedagem gratuita
   - Site: [https://www.netlify.com](https://www.netlify.com)
   ```bash
   # Deploy via CLI
   netlify deploy
   ```

## 🔐 Autenticação e Autorização

1. **Auth0**
   - 7.000 usuários grátis
   - Site: [https://auth0.com](https://auth0.com)
   ```python
   from auth0.v3.authentication import GetToken
   
   def get_auth0_token(domain, client_id, client_secret):
       get_token = GetToken(domain)
       token = get_token.client_credentials(
           client_id,
           client_secret,
           'https://{}/api/v2/'.format(domain)
       )
       return token
   ```

2. **Clerk**
   - Alternativa moderna ao Auth0
   - Site: [https://clerk.dev](https://clerk.dev)

## 📨 Email e Notificações

1. **SendGrid**
   - 100 emails/dia grátis
   - Site: [https://sendgrid.com](https://sendgrid.com)
   ```python
   from sendgrid import SendGridAPIClient
   
   def send_email(to_email, subject, content, api_key):
       sg = SendGridAPIClient(api_key)
       data = {
           'personalizations': [{
               'to': [{'email': to_email}]
           }],
           'from': {'email': 'from@example.com'},
           'subject': subject,
           'content': [{'type': 'text/plain', 'value': content}]
       }
       return sg.client.mail.send.post(request_body=data)
   ```

## Como Usar Este Guia

1. **Escolha das APIs**:
   - Avalie o tier gratuito
   - Verifique limites de requisições
   - Considere alternativas open source

2. **Implementação**:
   - Comece com exemplos básicos
   - Use tratamento de erros
   - Implemente rate limiting

3. **Manutenção**:
   - Monitore uso de APIs
   - Mantenha chaves seguras
   - Atualize dependências

4. **Segurança**:
   - Nunca exponha chaves API
   - Use variáveis de ambiente
   - Implemente timeouts

## Recursos Adicionais

- [RapidAPI](https://rapidapi.com) - Marketplace de APIs
- [Public APIs](https://github.com/public-apis/public-apis) - Lista de APIs públicas
- [Free for Developers](https://free-for.dev) - Recursos gratuitos para desenvolvedores
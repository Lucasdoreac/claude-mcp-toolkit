# Integração com APIs

## 🔌 APIs e Serviços

### Configuração Base

1. **Cliente HTTP Base**
   ```python
   import requests
   from typing import Dict, Any, Optional
   import time
   import json
   
   class APIClient:
       """
       Cliente base para requisições HTTP com retry e rate limiting
       """
       def __init__(self, base_url: str, headers: Optional[Dict] = None):
           self.base_url = base_url.rstrip('/')
           self.headers = headers or {}
           self.session = requests.Session()
           self.rate_limit = {
               'calls': 0,
               'period': 60,  # 1 minuto
               'last_reset': time.time()
           }
   
       def _check_rate_limit(self):
           """Controle de rate limiting"""
           current_time = time.time()
           if current_time - self.rate_limit['last_reset'] >= self.rate_limit['period']:
               self.rate_limit['calls'] = 0
               self.rate_limit['last_reset'] = current_time
   
           if self.rate_limit['calls'] >= 60:  # Limite de 60 chamadas por minuto
               sleep_time = self.rate_limit['period'] - (current_time - self.rate_limit['last_reset'])
               if sleep_time > 0:
                   time.sleep(sleep_time)
               self.rate_limit['calls'] = 0
               self.rate_limit['last_reset'] = time.time()
   
       def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
           """
           Realiza requisição HTTP com retry automático
           """
           url = f"{self.base_url}/{endpoint.lstrip('/')}"
           kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
           
           max_retries = 3
           retry_delay = 1
           
           for attempt in range(max_retries):
               try:
                   self._check_rate_limit()
                   response = self.session.request(method, url, **kwargs)
                   self.rate_limit['calls'] += 1
                   
                   response.raise_for_status()
                   return response.json()
               except requests.exceptions.RequestException as e:
                   if attempt == max_retries - 1:
                       raise
                   time.sleep(retry_delay * (attempt + 1))
   ```

2. **Gerenciador de Cache**
   ```python
   from datetime import datetime, timedelta
   import pickle
   import os
   
   class CacheManager:
       """
       Gerenciador de cache para respostas de API
       """
       def __init__(self, cache_dir: str = '.cache'):
           self.cache_dir = cache_dir
           os.makedirs(cache_dir, exist_ok=True)
   
       def _get_cache_path(self, key: str) -> str:
           return os.path.join(self.cache_dir, f"{key}.cache")
   
       def get(self, key: str) -> Optional[Dict]:
           cache_path = self._get_cache_path(key)
           if os.path.exists(cache_path):
               with open(cache_path, 'rb') as f:
                   cached_data = pickle.load(f)
                   if datetime.now() < cached_data['expires']:
                       return cached_data['data']
           return None
   
       def set(self, key: str, data: Dict, ttl: int = 3600):
           cache_path = self._get_cache_path(key)
           cache_data = {
               'data': data,
               'expires': datetime.now() + timedelta(seconds=ttl)
           }
           with open(cache_path, 'wb') as f:
               pickle.dump(cache_data, f)
   ```

### Integrações Específicas

1. **Cliente DuckDuckGo**
   ```python
   class DuckDuckGoClient(APIClient):
       """
       Cliente para API do DuckDuckGo
       """
       def __init__(self):
           super().__init__('https://api.duckduckgo.com')
           self.cache = CacheManager('duckduckgo_cache')
   
       def search(self, query: str, cache_ttl: int = 3600) -> Dict[str, Any]:
           cache_key = f"search_{query}"
           cached = self.cache.get(cache_key)
           if cached:
               return cached
   
           params = {
               'q': query,
               'format': 'json'
           }
           
           result = self.request('GET', '/', params=params)
           self.cache.set(cache_key, result, cache_ttl)
           return result
   ```

2. **Cliente OpenWeatherMap**
   ```python
   class WeatherClient(APIClient):
       """
       Cliente para API do OpenWeatherMap
       """
       def __init__(self, api_key: str):
           super().__init__('https://api.openweathermap.org/data/2.5')
           self.headers['Authorization'] = f'Bearer {api_key}'
           self.cache = CacheManager('weather_cache')
   
       def get_weather(self, city: str, cache_ttl: int = 1800) -> Dict[str, Any]:
           cache_key = f"weather_{city}"
           cached = self.cache.get(cache_key)
           if cached:
               return cached
   
           params = {
               'q': city,
               'units': 'metric'
           }
           
           result = self.request('GET', '/weather', params=params)
           self.cache.set(cache_key, result, cache_ttl)
           return result
   ```

3. **Cliente SendGrid**
   ```python
   class EmailClient(APIClient):
       """
       Cliente para API do SendGrid
       """
       def __init__(self, api_key: str):
           super().__init__('https://api.sendgrid.com/v3')
           self.headers['Authorization'] = f'Bearer {api_key}'
   
       def send_email(self, to_email: str, subject: str, content: str) -> Dict[str, Any]:
           data = {
               'personalizations': [{
                   'to': [{'email': to_email}]
               }],
               'from': {'email': 'seu-email@exemplo.com'},
               'subject': subject,
               'content': [{
                   'type': 'text/plain',
                   'value': content
               }]
           }
           
           return self.request('POST', '/mail/send', json=data)
   ```

### Sistema de Integração

1. **Gerenciador de APIs**
   ```python
   class APIManager:
       """
       Gerenciador central de integrações com APIs
       """
       def __init__(self, config_path: str = 'config.json'):
           self.config = self._load_config(config_path)
           self.clients = {}
           self._initialize_clients()
   
       def _load_config(self, config_path: str) -> Dict[str, Any]:
           if os.path.exists(config_path):
               with open(config_path, 'r') as f:
                   return json.load(f)
           return {}
   
       def _initialize_clients(self):
           if 'duckduckgo' in self.config:
               self.clients['search'] = DuckDuckGoClient()
           
           if 'openweathermap' in self.config:
               self.clients['weather'] = WeatherClient(
                   self.config['openweathermap']['api_key']
               )
           
           if 'sendgrid' in self.config:
               self.clients['email'] = EmailClient(
                   self.config['sendgrid']['api_key']
               )
   
       def get_client(self, name: str) -> Optional[APIClient]:
           return self.clients.get(name)
   ```

### Exemplos de Uso

1. **Configuração**
   ```python
   # config.json
   {
       "openweathermap": {
           "api_key": "sua_chave_aqui"
       },
       "sendgrid": {
           "api_key": "sua_chave_aqui"
       },
       "duckduckgo": {}
   }
   
   # Inicialização
   api_manager = APIManager()
   ```

2. **Busca e Clima**
   ```python
   # Cliente de busca
   search_client = api_manager.get_client('search')
   results = search_client.search('Python programming')
   
   # Cliente de clima
   weather_client = api_manager.get_client('weather')
   weather = weather_client.get_weather('London')
   ```

3. **Envio de Email**
   ```python
   # Cliente de email
   email_client = api_manager.get_client('email')
   email_client.send_email(
       'destinatario@exemplo.com',
       'Teste',
       'Conteúdo do email'
   )
   ```

### Monitoramento e Logs

1. **Sistema de Logging**
   ```python
   import logging
   from datetime import datetime
   
   class APILogger:
       """
       Sistema de logging para APIs
       """
       def __init__(self, log_file: str = 'api.log'):
           logging.basicConfig(
               filename=log_file,
               level=logging.INFO,
               format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
           )
           self.logger = logging.getLogger('APILogger')
   
       def log_request(self, method: str, url: str, response_time: float):
           self.logger.info(
               f"Request: {method} {url} - Response Time: {response_time:.2f}s"
           )
   
       def log_error(self, method: str, url: str, error: str):
           self.logger.error(
               f"Error in {method} {url}: {error}"
           )
   ```

2. **Métricas de Performance**
   ```python
   class APIMetrics:
       """
       Coleta de métricas de API
       """
       def __init__(self):
           self.metrics = {
               'requests': 0,
               'errors': 0,
               'total_time': 0,
               'start_time': datetime.now()
           }
   
       def record_request(self, response_time: float):
           self.metrics['requests'] += 1
           self.metrics['total_time'] += response_time
   
       def record_error(self):
           self.metrics['errors'] += 1
   
       def get_summary(self) -> Dict[str, Any]:
           uptime = (datetime.now() - self.metrics['start_time']).total_seconds()
           avg_time = (
               self.metrics['total_time'] / self.metrics['requests']
               if self.metrics['requests'] > 0 else 0
           )
           
           return {
               'total_requests': self.metrics['requests'],
               'total_errors': self.metrics['errors'],
               'average_response_time': avg_time,
               'uptime': uptime,
               'error_rate': (
                   self.metrics['errors'] / self.metrics['requests'] * 100
                   if self.metrics['requests'] > 0 else 0
               )
           }
   ```

### Boas Práticas

1. **Segurança**
   - Use HTTPS sempre
   - Proteja chaves API
   - Implemente rate limiting
   - Valide dados de entrada/saída

2. **Performance**
   - Use cache quando possível
   - Implemente retry com backoff
   - Monitore tempos de resposta
   - Otimize requisições

3. **Manutenção**
   - Mantenha logs detalhados
   - Monitore erros
   - Atualize regularmente
   - Documente mudanças

### Recursos Adicionais

- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [API Design Guide](https://cloud.google.com/apis/design)
- [REST API Best Practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
- [Rate Limiting](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
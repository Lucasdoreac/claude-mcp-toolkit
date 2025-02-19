# Gestão de Arquivos

## 📁 Sistema de Arquivos

### Operações Básicas

1. **Leitura de Arquivos**
   ```python
   def ler_arquivo(caminho, encoding='utf-8'):
       """
       Lê conteúdo de um arquivo com tratamento de erros
       """
       try:
           conteudo = read_file(path=caminho)
           if isinstance(conteudo, bytes):
               return conteudo.decode(encoding)
           return conteudo
       except Exception as e:
           print(f"Erro ao ler arquivo {caminho}: {str(e)}")
           return None

   def ler_multiplos_arquivos(caminhos, encoding='utf-8'):
       """
       Lê múltiplos arquivos simultaneamente
       """
       resultados = {}
       try:
           conteudos = read_multiple_files(paths=caminhos)
           for caminho, conteudo in conteudos.items():
               if isinstance(conteudo, bytes):
                   resultados[caminho] = conteudo.decode(encoding)
               else:
                   resultados[caminho] = conteudo
           return resultados
       except Exception as e:
           print(f"Erro ao ler arquivos: {str(e)}")
           return resultados
   ```

2. **Escrita de Arquivos**
   ```python
   def escrever_arquivo(caminho, conteudo, modo='w', encoding='utf-8'):
       """
       Escreve conteúdo em arquivo com backup
       """
       try:
           # Fazer backup se arquivo existir
           if modo == 'w':
               info = get_file_info(path=caminho)
               if info and 'exists' in info and info['exists']:
                   backup_path = f"{caminho}.bak"
                   conteudo_atual = ler_arquivo(caminho)
                   if conteudo_atual:
                       write_file(path=backup_path, content=conteudo_atual)
           
           # Escrever novo conteúdo
           if isinstance(conteudo, str):
               write_file(path=caminho, content=conteudo)
           else:
               write_file(path=caminho, content=str(conteudo))
           return True
       except Exception as e:
           print(f"Erro ao escrever arquivo {caminho}: {str(e)}")
           return False
   ```

3. **Gestão de Diretórios**
   ```python
   def gerenciar_diretorios():
       """
       Sistema completo de gestão de diretórios
       """
       def criar_diretorio(caminho):
           try:
               create_directory(path=caminho)
               return True
           except Exception as e:
               print(f"Erro ao criar diretório {caminho}: {str(e)}")
               return False
       
       def listar_conteudo(caminho='.'):
           try:
               return list_directory(path=caminho)
           except Exception as e:
               print(f"Erro ao listar diretório {caminho}: {str(e)}")
               return []
       
       def obter_arvore(caminho='.'):
           try:
               return directory_tree(path=caminho)
           except Exception as e:
               print(f"Erro ao obter árvore do diretório {caminho}: {str(e)}")
               return None
       
       return {
           "criar": criar_diretorio,
           "listar": listar_conteudo,
           "arvore": obter_arvore
       }
   ```

### Operações Avançadas

1. **Sistema de Backup**
   ```python
   def sistema_backup():
       """
       Sistema completo de backup de arquivos
       """
       def criar_backup(arquivo, destino=None):
           try:
               if not destino:
                   destino = f"{arquivo}.bak"
               
               conteudo = ler_arquivo(arquivo)
               if conteudo:
                   return escrever_arquivo(destino, conteudo)
               return False
           except Exception as e:
               print(f"Erro ao criar backup de {arquivo}: {str(e)}")
               return False
       
       def restaurar_backup(arquivo_backup, destino):
           try:
               conteudo = ler_arquivo(arquivo_backup)
               if conteudo:
                   return escrever_arquivo(destino, conteudo)
               return False
           except Exception as e:
               print(f"Erro ao restaurar backup para {destino}: {str(e)}")
               return False
       
       return {
           "criar": criar_backup,
           "restaurar": restaurar_backup
       }
   ```

2. **Busca e Filtros**
   ```python
   def sistema_busca():
       """
       Sistema avançado de busca de arquivos
       """
       def buscar_arquivos(diretorio, padrao, excluir=None):
           try:
               return search_files(
                   path=diretorio,
                   pattern=padrao,
                   excludePatterns=excluir or []
               )
           except Exception as e:
               print(f"Erro na busca: {str(e)}")
               return []
       
       def filtrar_por_tipo(diretorio, extensao):
           return buscar_arquivos(diretorio, f"*.{extensao}")
       
       def filtrar_por_data(diretorio, dias):
           """
           Filtra arquivos modificados nos últimos X dias
           """
           try:
               todos_arquivos = list_directory(path=diretorio)
               filtrados = []
               
               for arquivo in todos_arquivos:
                   if arquivo.startswith('[FILE]'):
                       nome = arquivo.replace('[FILE] ', '')
                       info = get_file_info(path=f"{diretorio}/{nome}")
                       if info and 'mtime' in info:
                           # Verificar se arquivo foi modificado nos últimos X dias
                           if (time.time() - info['mtime']) <= (dias * 86400):
                               filtrados.append(nome)
               
               return filtrados
           except Exception as e:
               print(f"Erro ao filtrar por data: {str(e)}")
               return []
       
       return {
           "buscar": buscar_arquivos,
           "por_tipo": filtrar_por_tipo,
           "por_data": filtrar_por_data
       }
   ```

3. **Processamento em Lote**
   ```python
   def processamento_lote():
       """
       Sistema para processamento em lote de arquivos
       """
       def processar_diretorio(diretorio, processador, padrao="*"):
           """
           Processa todos os arquivos em um diretório que correspondem ao padrão
           """
           try:
               arquivos = search_files(path=diretorio, pattern=padrao)
               resultados = {}
               
               for arquivo in arquivos:
                   if arquivo.startswith('[FILE]'):
                       nome = arquivo.replace('[FILE] ', '')
                       caminho = f"{diretorio}/{nome}"
                       conteudo = ler_arquivo(caminho)
                       if conteudo:
                           resultados[nome] = processador(conteudo)
               
               return resultados
           except Exception as e:
               print(f"Erro no processamento em lote: {str(e)}")
               return {}
       
       def processar_paralelo(diretorio, processador, padrao="*", max_workers=4):
           """
           Processa arquivos em paralelo usando threads
           """
           try:
               from concurrent.futures import ThreadPoolExecutor
               
               arquivos = search_files(path=diretorio, pattern=padrao)
               resultados = {}
               
               def processar_arquivo(arquivo):
                   if arquivo.startswith('[FILE]'):
                       nome = arquivo.replace('[FILE] ', '')
                       caminho = f"{diretorio}/{nome}"
                       conteudo = ler_arquivo(caminho)
                       if conteudo:
                           return nome, processador(conteudo)
                   return None, None
               
               with ThreadPoolExecutor(max_workers=max_workers) as executor:
                   for nome, resultado in executor.map(processar_arquivo, arquivos):
                       if nome and resultado:
                           resultados[nome] = resultado
               
               return resultados
           except Exception as e:
               print(f"Erro no processamento paralelo: {str(e)}")
               return {}
       
       return {
           "sequencial": processar_diretorio,
           "paralelo": processar_paralelo
       }
   ```

### Exemplos de Uso

1. **Operações Básicas**
   ```python
   # Leitura e escrita
   conteudo = ler_arquivo("exemplo.txt")
   escrever_arquivo("novo.txt", "Conteúdo de teste")
   
   # Diretórios
   dirs = gerenciar_diretorios()
   dirs["criar"]("novo_diretorio")
   arvore = dirs["arvore"](".")
   ```

2. **Backup e Restauração**
   ```python
   # Sistema de backup
   backup = sistema_backup()
   
   # Criar backup
   backup["criar"]("importante.txt")
   
   # Restaurar
   backup["restaurar"]("importante.txt.bak", "importante.txt")
   ```

3. **Busca Avançada**
   ```python
   # Sistema de busca
   busca = sistema_busca()
   
   # Buscar arquivos Python
   py_files = busca["por_tipo"](".", "py")
   
   # Arquivos recentes
   recentes = busca["por_data"](".", 7)  # últimos 7 dias
   ```

4. **Processamento em Lote**
   ```python
   # Sistema de processamento
   proc = processamento_lote()
   
   # Processar arquivos
   def meu_processador(conteudo):
       return len(conteudo.split())
   
   # Processamento sequencial
   resultados = proc["sequencial"](".", meu_processador, "*.txt")
   
   # Processamento paralelo
   resultados_paralelos = proc["paralelo"](".", meu_processador, "*.txt")
   ```

### Boas Práticas

1. **Segurança**
   - Sempre faça backup antes de modificar
   - Valide permissões
   - Trate erros adequadamente

2. **Performance**
   - Use leitura múltipla quando possível
   - Implemente processamento paralelo
   - Otimize padrões de busca

3. **Organização**
   - Mantenha estrutura clara
   - Use convenções de nomenclatura
   - Documente operações importantes

### Recursos Adicionais

- [Python File I/O](https://docs.python.org/3/tutorial/inputoutput.html)
- [OS and Filesystem](https://docs.python.org/3/library/os.html)
- [Concurrent Processing](https://docs.python.org/3/library/concurrent.futures.html)
- [File Management Best Practices](https://realpython.com/working-with-files-in-python/)
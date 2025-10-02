# 📁 EXEMPLOS DE CONFIGURAÇÃO DE PASTAS

## 🌟 Configurações Recomendadas

### 📧 Básica - Pastas Padrão
```
INBOX, Sent, Drafts, Trash
```
**Resultado:** 4 feeds RSS + 1 feed combinado

### 💼 Trabalho - Organização Profissional
```
INBOX, Trabalho/Projetos, Trabalho/Reuniões, Trabalho/Clientes, Sent
```
**Resultado:** 5 feeds RSS + 1 feed combinado

### 🚀 Tech - Para Desenvolvedores
```
INBOX, Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Trabalho, Pessoal
```
**Resultado:** 7 feeds RSS + 1 feed combinado

### 🎯 Completa - Organização Avançada
```
INBOX, Trabalho/Projetos, Trabalho/Reuniões, Trabalho/Administrativo, Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Pessoal/Família, Pessoal/Amigos, Pessoal/Compras, Sent, Drafts
```
**Resultado:** 13 feeds RSS + 1 feed combinado

## 🔧 Como Configurar no Zoho

### 1. Criando Pastas Hierárquicas no Zoho:
1. Acesse Zoho Mail
2. Clique com botão direito em "Folders"
3. "Create New Folder"
4. Para subpastas: "Create Subfolder"

### 2. Estrutura Sugerida:
```
📁 Tech
  ├── 📁 Frontend
  ├── 📁 Backend
  ├── 📁 DevOps
  └── 📁 Newsletters

📁 Trabalho
  ├── 📁 Projetos
  ├── 📁 Reuniões
  └── 📁 Clientes

📁 Pessoal
  ├── 📁 Família
  ├── 📁 Amigos
  └── 📁 Compras
```

### 3. Na GUI do IMAP2RSS, configure:
```
Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Trabalho/Projetos, Trabalho/Reuniões, Trabalho/Clientes, Pessoal/Família, Pessoal/Amigos, Pessoal/Compras, INBOX, Sent
```

## 📰 Feeds RSS Gerados

### Modo Combinado (Recomendado):
- **feed.xml** - Todos os emails com categorias por pasta
- Cada email terá a categoria da pasta de origem

### Modo Separado:
- **feed.xml** - Feed combinado principal
- **Tech_Frontend.xml** - Apenas emails de Tech/Frontend
- **Tech_Backend.xml** - Apenas emails de Tech/Backend
- **Trabalho_Projetos.xml** - Apenas emails de Trabalho/Projetos
- **etc.**

## 🎯 Dicas de Uso no FreshRSS

### Para Feed Combinado:
1. Adicione: `http://localhost:8888/feed.xml`
2. No FreshRSS, os emails aparecerão com categorias
3. Use filtros por categoria para organizar

### Para Feeds Separados:
1. Crie categorias no FreshRSS: "Tech", "Trabalho", "Pessoal"
2. Adicione cada feed na categoria correspondente:
   - Categoria "Tech": `Tech_Frontend.xml`, `Tech_Backend.xml`
   - Categoria "Trabalho": `Trabalho_Projetos.xml`, `Trabalho_Reunioes.xml`
   - Categoria "Pessoal": `Pessoal_Familia.xml`, `Pessoal_Amigos.xml`

## ⚡ Configuração Rápida

### 1. Execute a detecção automática:
- Na GUI (http://localhost:9999)
- Preencha email e senha
- Clique "🔍 Detectar Pastas"
- Ajuste a lista conforme necessário

### 2. Ou configure manualmente:
```bash
# No arquivo .env
MAILBOXES=INBOX,Tech/Frontend,Tech/Backend,Trabalho/Projetos,Sent
FEED_MODE=combined
```

### 3. Reinicie e acesse:
```bash
docker-compose restart
```
- Feeds: http://localhost:8888/
- Status: http://localhost:9999/status

## 🚨 Resolução de Problemas

### ❓ Pasta não encontrada:
- Verifique se a pasta existe no Zoho
- Use nomes exatos (case-sensitive)
- Para subpastas, use "/" como separador

### ❓ Caracteres especiais:
- Pastas com acentos: use exatamente como no Zoho
- Espaços: são permitidos
- Caracteres especiais nos arquivos são normalizados

### ❓ Muitas pastas:
- Recomendado: máximo 10-15 pastas
- Para mais pastas, considere usar filtros
- Monitor de performance via logs

## 📊 Monitoramento

### Verificar feeds gerados:
```bash
ls -la ./data/
```

### Ver logs:
```bash
docker-compose logs -f
```

### Status via API:
```bash
curl http://localhost:8888/feeds.json
```
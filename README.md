LearnAprender — Plataforma de estudo de inglês (esqueleto)

Visão geral
- Projeto Django mínimo com apps para `accounts`, `vocab`, `exercises`, `quizzes`, `reviews`.
- Implementa cadastro/login, CRUD de vocabulário, modelos para exercícios/quizzes, e templates Bootstrap.

Como rodar localmente
1. Crie um ambiente virtual e ative-o (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências (Django):

```powershell
pip install django
```

3. Rode migrações e crie um superusuário:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Inicie o servidor de desenvolvimento:

```powershell
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para ver a aplicação. Admin em `/admin/`.

Próximos passos (implementações recomendadas)
- Implementar execução interativa de exercícios (resposta e correção imediata).
- Gerador automático de quizzes por tema/nível e gravação dos resultados por usuário.
- Lógica para calcular taxa de erro por usuário e agendar revisões prioritárias.
- Busca avançada e filtros no frontend para exercícios e quizzes.
 
O que foi implementado nesta iteração:

- Execução interativa de exercícios (MCQ, preencher lacuna, tradução) com correção imediata e registro em `PerformanceRecord`.
- Geração automática de quizzes por tema/nível, interface para executar o quiz e armazenamento de `QuizResult`.
- Busca/filtragem melhorada para exercícios (filtros por texto, tipo, categoria, nível) e paginação.

Para testar diretamente:

```powershell
# criar superuser se ainda não existir
python manage.py createsuperuser

# opcional: criar alguns Exercises via admin ou fixtures
# iniciar servidor
python manage.py runserver
```

Abra `/exercises/` para ver e executar exercícios. Abra `/quizzes/generate/` para gerar um quiz.

Instalação de dependências adicionais
```powershell
pip install -r requirements.txt
```

Configuração de tradução
- A integração de tradução usa a API pública do LibreTranslate (`https://libretranslate.de/translate`) por padrão.
- Para usar uma instância própria ou uma API key, defina as variáveis de ambiente `LIBRETRANSLATE_URL` e `LIBRETRANSLATE_API_KEY`.

Logout seguro
- O botão de logout foi alterado para usar um `POST` (forma) para evitar `405 Method Not Allowed` e proteger contra CSRF.
Painel Administrativo (Admin Panel)
O sistema inclui um painel administrativo customizado (sem usar o admin padrão do Django) acessível apenas para usuários com permissão de staff.

**Acessar o Painel**

1. **Gestão de Vocabulário**: `/panel/vocab/`
	- Listar vocabulário com filtros (texto, nível, categoria) e paginação (25 itens/página)
	- Ações em lote: selecionar múltiplos itens e deletar ou gerar exercícios automaticamente
	- Criar, editar ou deletar vocabulário individual

2. **Gestão de Exercícios**: `/panel/exercises/`
	- Listar exercícios com filtros (texto, tipo, nível, categoria) e paginação (25 itens/página)
	- Ações em lote: selecionar e deletar múltiplos exercícios
	- Criar, editar ou deletar exercício individual

3. **Métricas e Desempenho**: `/panel/metrics/dashboard/`
	- **Dashboard principal**: KPIs gerais (total de tentativas, taxa de acerto %, quizzes realizados, média de pontuação)
	- **Usuários mais ativos**: Tabela com os 20 usuários que mais praticam (clique em "Ver detalhes" para análise individual)
	- **Análise por usuário** (`/panel/metrics/user/<user_id>/`): Estatísticas por categoria, quizzes recentes
	- **Registros de desempenho** (`/panel/metrics/records/`): Histórico de todas as tentativas de exercícios com filtros por usuário e resultado (correto/incorreto)
	- **Resultados de quizzes** (`/panel/metrics/quizzes/`): Histórico de todos os testes com filtros por usuário e título do teste

**Requisitos para Acesso**
- O usuário deve ter o atributo `is_staff=True` (definível via Django admin `/admin/auth/user/`)
- Todos os painel administrativos são protegidos com `@staff_member_required`

**Usando Ações em Lote**
1. Marque os itens desejados com as checkboxes ou use "Selecionar tudo"
2. Escolha a ação no menu dropdown (Deletar ou Gerar Exercícios)
3. Clique no botão de ação
4. A operação é realizada de forma segura (transação atômica)

**Pesquisa e Filtros**
- **Vocabulário**: Filtrar por palavra/tradução (texto), nível (beginner/intermediate/advanced), categoria
- **Exercícios**: Filtrar por pergunta/resposta, tipo (MCQ/gap/translate), nível, categoria
- **Performance**: Filtrar por nome de usuário, resultado (correto/incorreto), teste específico


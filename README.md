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

**Fix the errors below**

```
fix the errors below

PS C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender> python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
	File "C:\Python313\Lib\site-packages\django\core\checks\urls.py", line 136, in check_custom_error_handlers
		handler = resolver.resolve_error_handler(status_code)
	File "C:\Python313\Lib\site-packages\django\urls\resolvers.py", line 732, in resolve_error_handler
		callback = getattr(self.urlconf_module, "handler%s" % view_type, None)
											 ^^^^^^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\utils\functional.py", line 47, in __get__
		res = instance.__dict__[self.name] = self.func(instance)
																				 ~~~~~~~~~^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\urls\resolvers.py", line 711, in urlconf_module
		return import_module(self.urlconf_name)
	File "C:\Python313\Lib\importlib\__init__.py", line 88, in import_module
		return _bootstrap._gcd_import(name[level:], package, level)
					 ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
	File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
	File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap>", line 935, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
	File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\learnAprender\urls.py", line 25, in <module>
		path('vocab/', include('vocab.urls')),
									 ~~~~~~~^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\urls\conf.py", line 39, in include
		urlconf_module = import_module(urlconf_module)
	File "C:\Python313\Lib\importlib\__init__.py", line 88, in import_module
		return _bootstrap._gcd_import(name[level:], package, level)
					 ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
	File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
	File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap>", line 935, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
	File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\urls.py", line 2, in <module>
		from . import views
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\views.py", line 9, in <module>
		from .utils import generate_exercises_for_vocab
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\utils.py", line 5, in <module>
		import requests
ModuleNotFoundError: No module named 'requests'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
	File "C:\Python313\Lib\threading.py", line 1041, in _bootstrap_inner
		self.run()
		~~~~~~~~^^
	File "C:\Python313\Lib\threading.py", line 992, in run
		self._target(*self._args, **self._kwargs)
		~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\utils\autoreload.py", line 64, in wrapper
		fn(*args, **kwargs)
		~~^^^^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\core\management\commands\runserver.py", line 134, in inner_run
		self.check(**check_kwargs)
		~~~~~~~~~~^^^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\core\management\base.py", line 492, in check
		all_issues = checks.run_checks(
				app_configs=app_configs,
		...<2 lines>...
				databases=databases,
		)
	File "C:\Python313\Lib\site-packages\django\core\checks\registry.py", line 89, in run_checks
		new_errors = check(app_configs=app_configs, databases=databases)
	File "C:\Python313\Lib\site-packages\django\core\checks\urls.py", line 138, in check_custom_error_handlers
		path = getattr(resolver.urlconf_module, "handler%s" % status_code)
									 ^^^^^^^^^^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\utils\functional.py", line 47, in __get__
		res = instance.__dict__[self.name] = self.func(instance)
																				 ~~~~~~~~~^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\urls\resolvers.py", line 711, in urlconf_module
		return import_module(self.urlconf_name)
	File "C:\Python313\Lib\importlib\__init__.py", line 88, in import_module
		return _bootstrap._gcd_import(name[level:], package, level)
					 ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
	File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
	File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap>", line 935, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
	File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\learnAprender\urls.py", line 25, in <module>
		path('vocab/', include('vocab.urls')),
									 ~~~~~~~^^^^^^^^^^^^^^
	File "C:\Python313\Lib\site-packages\django\urls\conf.py", line 39, in include
		urlconf_module = import_module(urlconf_module)
	File "C:\Python313\Lib\importlib\__init__.py", line 88, in import_module
		return _bootstrap._gcd_import(name[level:], package, level)
					 ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
	File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
	File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap>", line 935, in _find_and_load_unlocked
	File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
	File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\urls.py", line 2, in <module>
		from . import views
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\views.py", line 9, in <module>
		from .utils import generate_exercises_for_vocab
	File "C:\Users\guilh\OneDrive\Desktop\Douling\learnAprender\vocab\utils.py", line 5, in <module>
		import requests
ModuleNotFoundError: No module named 'requests'
```

Observação: esse erro normalmente é resolvido instalando as dependências do projeto:

```powershell
pip install -r requirements.txt
```

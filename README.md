# LearnAprender - Sistema de Aprendizado de Idiomas

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Dependências](#dependências)
4. [Instalação e Configuração](#instalação-e-configuração)
5. [Estrutura de Diretórios](#estrutura-de-diretórios)
6. [Documentação por Aplicação](#documentação-por-aplicação)
7. [Modelos de Dados](#modelos-de-dados)
8. [APIs Externas](#apis-externas)
9. [Fluxo de Execução](#fluxo-de-execução)
10. [Testes e Validação](#testes-e-validação)

---

## 🎯 Visão Geral

**LearnAprender** é um sistema web interativo para aprendizado de idiomas, desenvolvido em **Django 5.2.8** com **Python 3.14**. O sistema oferece múltiplas modalidades de exercícios (tradução, múltipla escolha, preenchimento de lacuna), gerenciamento de vocabulário, quizzes adaptativos e rastreamento de progresso do usuário.

### Características Principais:
- ✅ **Gestão de Vocabulário**: Criar, editar, compartilhar e classificar palavras
- ✅ **Múltiplos Tipos de Exercícios**: Tradução, MCQ, Gap-Fill
- ✅ **Geração Automática de Exercícios**: A partir do vocabulário ou palavras aleatórias
- ✅ **Quizzes Inteligentes**: Geração com heurísticas de seleção e deduplicação
- ✅ **Sistema de Compartilhamento**: Vocabulário, exercícios e quizzes compartilháveis
- ✅ **Autenticação e Perfis**: Sistema de usuários com perfis personalizáveis
- ✅ **Rastreamento de Progresso**: Estatísticas de aprendizado e análise de performance
- ✅ **API de Integração**: Dicionário, tradução e palavras aleatórias

---

## 🏗️ Arquitetura do Sistema

### Padrão Arquitetural: MTV (Model-Template-View)

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Framework                          │
├──────────────────┬──────────────────┬──────────────────────┤
│   Models (BD)    │   Views (Lógica) │   Templates (HTML)   │
├──────────────────┴──────────────────┴──────────────────────┤
│                  URLs Router                                │
├─────────────────────────────────────────────────────────────┤
│                  SQLite3 Database                           │
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico:
- **Backend**: Django 5.2.8, Python 3.14
- **Frontend**: Bootstrap 5.3.2, Vanilla JavaScript
- **Database**: SQLite3
- **APIs Externas**: 
  - Random Word API (palavras aleatórias)
  - Dictionary API (definições)
  - MyMemory Translation API (tradução)
  - LibreTranslate API (tradução alternativa)
- **Bibliotecas Principais**:
  - `rapidfuzz`: Fuzzy matching (tolerância ortográfica)
  - `requests`: HTTP requests
  - `django-crispy-forms`: Renderização de formulários

---

## 📦 Dependências

### Dependências Python (requirements.txt)

```
Django==5.2.8           # Framework web MVT
requests==2.31.0        # Cliente HTTP para APIs
rapidfuzz==3.8.1        # Fuzzy matching (80% threshold)
python-dateutil==2.8.2  # Processamento de datas
pytz==2024.1            # Timezone support
```

**Descrição das Dependências:**

| Pacote | Versão | Propósito |
|--------|--------|----------|
| Django | 5.2.8 | Framework web completo com ORM, autenticação, admin |
| requests | 2.31.0 | Requisições HTTP para APIs externas (Random Word, Dictionary, Translation) |
| rapidfuzz | 3.8.1 | Fuzzy matching para tolerância ortográfica em gap-fill e tradução (80% threshold) |
| python-dateutil | 2.8.2 | Manipulação avançada de datas/timedeltas |
| pytz | 2024.1 | Timezone awareness para timestamps de performance records |

### Dependências JavaScript/CSS (CDN):
- Bootstrap 5.3.2
- Bootstrap Icons
- CSRF middleware (Django built-in)

### APIs Externas (Livres):
1. **Random Word API**: `https://random-word-api.herokuapp.com/all`
2. **Dictionary API**: `https://api.dictionaryapi.dev/api/v2/entries/en/{word}`
3. **MyMemory Translation**: `https://api.mymemory.translated.net/get`
4. **LibreTranslate** (opcional): Requer configuração de URL/API Key

---

## 🚀 Instalação e Configuração

### Pré-requisitos:
- Python 3.14+
- pip
- Git (opcional)
- SQLite3 (incluído com Python)

### Passo 1: Clonar/Copiar o Repositório

```bash
cd /path/to/workspace
git clone <repo-url> learnAprender
cd learnAprender
```

### Passo 2: Criar Ambiente Virtual

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar settings.py

Abrir `learnAprender/settings.py` e verificar:

```python
# Configurações Críticas
DEBUG = True  # Apenas desenvolvimento
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'vocab',
    'exercises',
    'quizzes',
    'reviews',
]

# Configurações de Autenticação
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home'
```

### Passo 5: Migrar Banco de Dados

```bash
# Criar migrações (se necessário)
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

### Passo 6: Criar Super Usuário (Admin)

```bash
python manage.py createsuperuser
# Seguir prompts: username, email, password
```

### Passo 7: Executar Servidor

```bash
python manage.py runserver 0.0.0.0:8000
```

Acessar em: `http://127.0.0.1:8000/`

### Passo 8: Verificar Sistema

```bash
# Verificar conformidade Django
python manage.py check

# Listar URLs disponíveis
python manage.py show_urls
```

---

## 📁 Estrutura de Diretórios

```
learnAprender/
├── learnAprender/              # Configuração principal
│   ├── __init__.py
│   ├── asgi.py                 # ASGI configuration
│   ├── settings.py             # Configurações Django
│   ├── urls.py                 # URL routing principal
│   └── wsgi.py                 # WSGI configuration
│
├── accounts/                    # Aplicação de autenticação e perfis
│   ├── migrations/
│   ├── templates/accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # Formulários (SignUpForm, ProfileUpdateForm)
│   ├── models.py               # Modelo Profile
│   ├── urls.py
│   └── views.py                # Views: home, register, login, profile
│
├── vocab/                       # Aplicação de vocabulário
│   ├── migrations/
│   ├── templates/vocab/
│   │   ├── list.html           # Listagem com filtros
│   │   ├── form.html           # Criar/editar
│   │   └── detail.html         # Detalhes
│   ├── admin_views.py          # Views do admin
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # Formulário de Vocabulary
│   ├── models.py               # Modelo Vocabulary
│   ├── urls.py
│   ├── utils.py                # Funções de geração e tradução
│   └── views.py                # Views: CRUD, geração de exercícios
│
├── exercises/                   # Aplicação de exercícios
│   ├── migrations/
│   ├── templates/exercises/
│   │   ├── list.html           # Listagem com filtros
│   │   ├── form.html           # Criar/editar
│   │   ├── detail.html         # Detalhes
│   │   ├── take.html           # Resolver exercício
│   │   ├── result.html         # Resultado
│   │   └── confirm_delete.html
│   ├── admin_views.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # Formulário de Exercise
│   ├── models.py               # Modelo Exercise, PerformanceRecord
│   ├── urls.py
│   └── views.py                # Views: CRUD, take_exercise
│
├── quizzes/                     # Aplicação de quizzes
│   ├── migrations/
│   ├── templates/quizzes/
│   │   ├── index.html          # Listagem
│   │   ├── generate.html       # Geração com preview
│   │   ├── form.html           # Criar/editar
│   │   ├── take.html           # Resolver quiz
│   │   ├── detail.html         # Detalhes
│   │   ├── result.html         # Resultado
│   │   └── confirm_delete.html
│   ├── admin_views.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                # Formulário de Quiz
│   ├── models.py               # Modelo Quiz, QuizResult
│   ├── urls.py
│   └── views.py                # Views: CRUD, geração com heurísticas
│
├── reviews/                     # Aplicação de progresso/análise
│   ├── migrations/
│   ├── templates/reviews/
│   │   ├── index.html          # Página inicial de reviews
│   │   ├── progress.html       # Estatísticas detalhadas
│   │   ├── high_error_words.html
│   │   ├── schedule_review.html
│   │   └── scheduled_reviews.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Modelo ReviewSchedule
│   ├── urls.py
│   └── views.py                # Views: estatísticas, agendamento
│
├── templates/                   # Templates globais
│   ├── base.html               # Template base
│   └── index.html              # Home page
│
├── static/                      # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/
│   ├── js/
│   └── images/
│
├── manage.py                    # Ferramenta CLI Django
├── db.sqlite3                   # Banco de dados (criado após migrações)
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

---

## 📚 Documentação por Aplicação

### 1. ACCOUNTS (Autenticação e Perfis)

#### Modelo: Profile

```python
class Profile(models.Model):
    """
    Perfil estendido do usuário Django com configurações de aprendizado.
    
    Atributos:
        user (OneToOneField): Relacionamento 1:1 com User Django
        level (CharField): Nível de conhecimento (beginner/intermediate)
        objectives (TextField): Objetivos de aprendizado do usuário
        created_at (DateTimeField): Data de criação
    """
    LEVEL_CHOICES = [
        ('beginner', 'Iniciante'),
        ('intermediate', 'Intermediário'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    objectives = models.TextField(blank=True, help_text='Seus objetivos de aprendizado')
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Formulários:

**SignUpForm** - Registro de novo usuário
```python
class SignUpForm(UserCreationForm):
    """
    Formulário estendido de registro com captura de email e nível inicial.
    Herança: UserCreationForm (Django)
    """
    email = EmailField(required=True)
    level = ChoiceField(choices=Profile.LEVEL_CHOICES, initial='beginner')
```

**ProfileUpdateForm** - Atualização de perfil
```python
class ProfileUpdateForm(ModelForm):
    """
    Permite usuário atualizar nível e objetivos.
    """
    class Meta:
        model = Profile
        fields = ['level', 'objectives']
```

#### Views:

| View | Método | Descrição |
|------|--------|-----------|
| `home` | GET | Página inicial com dashboard |
| `register` | GET/POST | Formulário e processamento de registro |
| `profile` | GET/POST | Exibir e editar perfil do usuário |
| `logout` | POST | Logout com CSRF token |

---

### 2. VOCAB (Vocabulário)

#### Modelo: Vocabulary

```python
class Vocabulary(models.Model):
    """
    Armazena palavras/expressões em aprendizado.
    
    Atributos:
        word (CharField): Palavra em inglês
        translation (CharField): Tradução em português
        example (TextField): Exemplo de uso (opcional)
        category (CharField): Categorização (ex: "Verbos", "Alimentos")
        level (CharField): beginner/intermediate
        tags (CharField): Tags separadas por vírgula
        created_by (ForeignKey): Criador (User)
        is_shared (BooleanField): Visibilidade (true = todos veem)
        created_at (DateTimeField): Timestamp
    
    Constraints:
        - Unicidade: word + created_by para vocab pessoal
        - Permitir duplicatas compartilhadas
    """
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=400)
    example = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=20, choices=[...], default='beginner')
    tags = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Funções em utils.py:

**`translate_text(text, target='en')`**
```python
"""
Traduz texto usando múltiplas APIs com fallback.
1. Tenta LibreTranslate
2. Fallback: MyMemory Translation API
3. Retorna None se falhar

Args:
    text (str): Texto a traduzir
    target (str): Código do idioma alvo
    
Returns:
    str: Texto traduzido ou None
"""
```

**`fetch_dictionary_info(word)`**
```python
"""
Busca definições e sinônimos de uma palavra.
API: https://api.dictionaryapi.dev/api/v2/entries/en/{word}

Returns:
    dict: {'definitions': [...], 'synonyms': [...]}
"""
```

**`generate_exercises_for_vocab(vocab, distractor_pool=None)`**
```python
"""
Gera 3 exercícios a partir de uma palavra:
1. Translation Exercise
2. MCQ Exercise (com distractores)
3. Gap-Fill Exercise

Heurística de distractores:
- Pool fornecido (outras palavras do vocab)
- Sinônimos da API
- Back-translation (tradução reversa)

Returns:
    List[Exercise]: Exercícios não salvos
"""
```

**`get_random_words(count=10)`**
```python
"""
Busca palavras aleatórias em inglês.
1. Random Word API
2. Fallback: lista hardcoded de 60+ palavras comuns
Filtra: 3-10 chars, alfabéticas, não uppercase

Returns:
    List[str]: Palavras aleatórias
"""
```

**`generate_exercises_from_random_words(count=10, user_category='')`**
```python
"""
Gera exercícios a partir de palavras aleatórias.
Cria 3 tipos por palavra usando APIs externas.

Processo:
1. Busca 'count' palavras aleatórias
2. Para cada palavra:
   - Busca definição + tradução
   - Gera 3 exercícios (translate, mcq, gap-fill)
3. Retorna lista de exercícios

Returns:
    List[Exercise]: Exercícios não salvos
"""
```

#### Views:

| View | Método | Descrição | Permissões |
|------|--------|-----------|-----------|
| `VocabListView` | GET | Listar vocab com filtros (tipo, nível, busca) | Login |
| `VocabCreateView` | GET/POST | Criar novo vocab | Login |
| `VocabDetailView` | GET | Detalhes de vocab | Login |
| `VocabUpdateView` | GET/POST | Editar vocab | Criador ou Staff |
| `VocabDeleteView` | GET/POST | Deletar vocab | Criador ou Staff |
| `generate_exercises` | POST | Gerar exercícios do vocab | Login |
| `generate_exercises_from_all` | GET/POST | Gerar de múltiplos vocabs | Login |
| `generate_random_exercises` | GET/POST | Gerar de palavras aleatórias | Login |

---

### 3. EXERCISES (Exercícios)

#### Modelo: Exercise

```python
class Exercise(models.Model):
    """
    Unidade base de prática de aprendizado.
    
    Tipos:
        - mcq: Múltipla escolha
        - gap: Preencher lacuna
        - translate: Tradução
    
    Atributos:
        question (TextField): Pergunta/instrução
        exercise_type (CharField): Tipo de exercício
        choices (JSONField): Opções para MCQ
        answer (TextField): Resposta correta
        level (CharField): Dificuldade
        category (CharField): Categorização
        created_by (ForeignKey): Criador
        is_shared (BooleanField): Compartilhado
        created_at (DateTimeField): Data
    """
    TYPE_CHOICES = [
        ('mcq', 'Múltipla escolha'),
        ('gap', 'Preencher lacuna'),
        ('translate', 'Tradução'),
    ]
    
    question = models.TextField()
    exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    choices = models.JSONField(blank=True, null=True)
    answer = models.TextField()
    level = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Modelo: PerformanceRecord

```python
class PerformanceRecord(models.Model):
    """
    Rastreia cada tentativa de exercício do usuário.
    
    Atributos:
        user (ForeignKey): Usuário que tentou
        exercise (ForeignKey): Exercício resolvido
        correct (BooleanField): Acertou ou errou
        timestamp (DateTimeField): Quando foi feito
    
    Ordenação: Por timestamp descendente (mais recente primeiro)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

#### Funções de Validação:

**`can_edit_exercise(user, exercise)`**
```python
"""
Verifica permissão de edição.

Regras:
- Criador pode editar seu próprio
- Staff pode editar compartilhados
- Usuários normais NÃO podem editar compartilhados de outros

Returns: bool
"""
```

#### Views:

| View | Método | Descrição | Lógica |
|------|--------|-----------|--------|
| `ExerciseListView` | GET | Listar exercícios | Filtros: vocab_type, level, category, type, status |
| `create_exercise` | GET/POST | Criar exercício | Form validation, user assignment |
| `ExerciseDetailView` | GET | Detalhes | Apenas leitura |
| `edit_exercise` | GET/POST | Editar | Validação de permissões |
| `delete_exercise` | GET/POST | Deletar | Confirmação, validação |
| `take_exercise` | GET/POST | Resolver | Avaliação com fuzzy matching (rapidfuzz) |

**Matching Logic em `take_exercise`:**
```python
def norm(s):
    """Normaliza string para comparação"""
    return s.strip().lower()

if exercise_type == 'mcq':
    # MCQ: match exato com opção selecionada
    correct = norm(selected) == norm(answer)
else:
    # Gap/Translate: fuzzy matching com 80% threshold
    score = fuzz.token_sort_ratio(given, expected)
    correct = score >= 80  # 80% de similaridade
```

---

### 4. QUIZZES (Quizzes Adaptativos)

#### Modelo: Quiz

```python
class Quiz(models.Model):
    """
    Coleção de exercícios com scoring.
    
    Atributos:
        title (CharField): Nome do quiz
        level (CharField): Dificuldade
        theme (CharField): Tema/categoria
        questions (ManyToManyField): Exercícios inclusos
        created_by (ForeignKey): Criador
        is_shared (BooleanField): Compartilhado
        created_at (DateTimeField): Data
    """
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=50, blank=True)
    theme = models.CharField(max_length=100, blank=True)
    questions = models.ManyToManyField('exercises.Exercise', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Modelo: QuizResult

```python
class QuizResult(models.Model):
    """
    Resultado de um quiz resolvido.
    
    Atributos:
        user (ForeignKey): Usuário que resolveu
        quiz (ForeignKey): Quiz resolvido
        score (FloatField): Pontuação (0-100)
        taken_at (DateTimeField): Quando foi feito
        details (JSONField): Detalhes das respostas
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    taken_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)
```

#### Heurísticas de Geração (em views.py):

**`generate_quiz` - Algoritmo Inteligente:**

```python
"""
Seleciona exercícios com regras sofisticadas:

1. DEDUPLICAÇÃO (30 dias):
   - Exclui exercícios usados há menos de 30 dias
   - Evita repetição entediante

2. FILTRO PROCEDURAL:
   - Apenas: gap-fill e translate
   - Exclui: multiple choice
   - Razão: Maior aprendizado prático

3. BALANCEAMENTO DE TIPO:
   - ~50% gap-fill
   - ~50% translate
   - Variação de prática

4. SELEÇÃO:
   - Por tema e nível
   - Aleatória após filtros
   - Máximo: N exercícios
"""
```

**Código Pseudocódigo:**
```python
# 1. Filtro por 30 dias
exercised_recently = Exercise.objects \
    .filter(performancerecord__user=user) \
    .filter(performancerecord__timestamp__gte=cutoff_date) \
    .values_list('id', flat=True)

qs = qs.exclude(id__in=exercised_recently)

# 2. Apenas procedural (gap + translate)
qs = qs.filter(exercise_type__in=['gap', 'translate'])

# 3. Balanceamento
gap_count = qs.filter(exercise_type='gap').count()
translate_count = qs.filter(exercise_type='translate').count()
# Ajustar proporções...

# 4. Seleção aleatória
selected = qs.order_by('?')[:count]
```

#### Views:

| View | Método | Descrição | Lógica Especial |
|------|--------|-----------|-----------------|
| `index` | GET | Listar quizzes | Filtros: vocab_type, theme, level |
| `preview_quiz_count` | GET (AJAX) | Preview de contagem | Retorna JSON com total/shared/personal |
| `generate_quiz` | GET/POST | Gerar quiz | Heurísticas de seleção + AJAX preview |
| `take_quiz` | GET/POST | Resolver quiz | Calcula score final |
| `detail_quiz` | GET | Detalhes | Exibir questões |
| `edit_quiz` | GET/POST | Editar | Validação de permissões |
| `delete_quiz` | GET/POST | Deletar | Confirmação |
| `quiz_result` | GET | Resultado | Exibir score e feedback |

---

### 5. REVIEWS (Progresso e Análise)

#### Modelo: ReviewSchedule

```python
class ReviewSchedule(models.Model):
    """
    Agendamento de revisão espaçada (Spaced Repetition).
    
    Atributos:
        user (ForeignKey): Usuário
        exercise (ForeignKey): Exercício a revisar
        next_review (DateField): Próxima data de revisão
        review_count (IntegerField): Número de revisões
        difficulty_factor (FloatField): Fator SM-2 (0.5-2.6)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.CASCADE)
    next_review = models.DateField()
    review_count = models.IntegerField(default=0)
    difficulty_factor = models.FloatField(default=2.5)
```

#### Views:

| View | Método | Descrição | Dados |
|------|--------|-----------|-------|
| `index` | GET | Dashboard de reviews | Links para seções |
| `progress` | GET | Estatísticas completas | Scores, gráficos, categorias |
| `high_error_words` | GET | Palavras com erro | Top N palavras problemáticas |
| `schedule_review` | GET/POST | Agendar revisão | SM-2 algorithm |
| `scheduled_reviews` | GET | Revisar agendadas | Próximas de revisar |

---

## 🗂️ Modelos de Dados

### Diagrama ER Simplificado:

```
User (Django)
├── Profile (1:1)
│   ├── level
│   └── objectives
│
├── Vocabulary (1:N)
│   ├── word
│   ├── translation
│   ├── level
│   ├── category
│   └── is_shared
│
├── Exercise (1:N)
│   ├── question
│   ├── exercise_type
│   ├── answer
│   ├── choices (JSON)
│   └── is_shared
│
├── PerformanceRecord (1:N)
│   ├── exercise (FK → Exercise)
│   ├── correct
│   └── timestamp
│
├── Quiz (1:N)
│   ├── questions (M2M → Exercise)
│   └── is_shared
│
├── QuizResult (1:N)
│   ├── quiz (FK)
│   ├── score
│   └── details (JSON)
│
└── ReviewSchedule (1:N)
    ├── exercise (FK)
    ├── next_review
    └── difficulty_factor
```

---

## 🌐 APIs Externas

### 1. Random Word API

**Endpoint**: `https://random-word-api.herokuapp.com/all`

**Método**: GET

**Resposta**:
```json
[
  "abandonment",
  "ability",
  "able",
  ...
]
```

**Uso em Projeto**:
```python
# vocab/utils.py - get_random_words()
resp = requests.get(url, timeout=5)
all_words = resp.json()
filtered = [w for w in all_words if 3 <= len(w) <= 10]
```

### 2. Dictionary API

**Endpoint**: `https://api.dictionaryapi.dev/api/v2/entries/en/{word}`

**Método**: GET

**Exemplo Response** (para "example"):
```json
[
  {
    "word": "example",
    "meanings": [
      {
        "definitions": [
          {
            "definition": "a thing characteristic of its kind or illustrating a general rule",
            "synonyms": ["instance", "case"],
            ...
          }
        ],
        ...
      }
    ]
  }
]
```

**Uso em Projeto**:
```python
# vocab/utils.py - fetch_dictionary_info()
# Extrai definições e sinônimos para exercícios
def fetch_dictionary_info(word):
    definitions = []
    synonyms = []
    # Parse JSON e coleta info
    return {'definitions': definitions, 'synonyms': synonyms}
```

### 3. MyMemory Translation API

**Endpoint**: `https://api.mymemory.translated.net/get?q={text}&langpair=en|{lang}`

**Método**: GET

**Resposta**:
```json
{
  "responseStatus": 200,
  "responseData": {
    "translatedText": "texto traduzido"
  }
}
```

**Uso em Projeto**:
```python
# vocab/utils.py - translate_text()
# Fallback para LibreTranslate
url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|pt"
data = requests.get(url).json()
if data.get('responseStatus') == 200:
    return data['responseData']['translatedText']
```

### 4. LibreTranslate API (Opcional)

**Endpoint**: Configurável (default: `https://libretranslate.de/translate`)

**Método**: POST

**Payload**:
```json
{
  "q": "text to translate",
  "source": "auto",
  "target": "pt",
  "format": "text"
}
```

**Uso em Projeto**:
```python
# vocab/utils.py - translate_text()
# Tentativa primeira (pode ser desabilitada)
# Requer setting de URL e API Key opcional
```

### Tratamento de Erros:

```python
# Padrão em todas as chamadas:
try:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    # processar...
except Exception:
    pass  # Fallback ou None
```

---

## 🔄 Fluxo de Execução

### 1. Fluxo de Autenticação

```
[Usuário não autenticado]
          ↓
    [GET /accounts/register/]
          ↓
    [Preenche formulário SignUpForm]
          ↓
    [POST /accounts/register/]
          ↓
    [Validação + Criação User + Profile]
          ↓
    [Redirect LOGIN]
          ↓
    [GET /accounts/login/]
          ↓
    [Preenche login + senha]
          ↓
    [POST /accounts/login/ + Django auth]
          ↓
    [SessionMiddleware cria sessão]
          ↓
    [Redirect HOME]
          ↓
    [Usuário autenticado]
```

### 2. Fluxo de Criação de Vocabulário

```
[GET /vocab/add/]
        ↓
[Exibe VocabCreateView]
        ↓
[Usuário preenche: word, translation, example, level, category, is_shared]
        ↓
[POST /vocab/add/]
        ↓
[VocabCreateView.form_valid()]
        ↓
[created_by = request.user]
        ↓
[vocab.save()]
        ↓
[Redirect /vocab/detail/pk/]
```

### 3. Fluxo de Geração de Exercícios

```
[GET /vocab/pk/]
        ↓
[Botão "Gerar Exercícios"]
        ↓
[POST /vocab/pk/generate/]
        ↓
[generate_exercises_for_vocab(vocab)]
        ↓
┌─────────────────────────────────────┐
│ Cria 3 exercícios:                  │
│ 1. Translation                      │
│ 2. MCQ (com distractores via API)   │
│ 3. Gap-Fill                         │
└─────────────────────────────────────┘
        ↓
[Loop: ex.created_by = request.user; ex.save()]
        ↓
[messages.success(f"Criados 3 exercícios")]
        ↓
[Redirect /vocab/pk/]
```

### 4. Fluxo de Resolução de Exercício

```
[GET /exercises/pk/take/]
        ↓
[Exibe exercise.question + form de input]
        ↓
[Usuário digita resposta]
        ↓
[POST /exercises/pk/take/]
        ↓
[Normaliza entrada: strip(), lower()]
        ↓
┌───────────────────────────────────────────┐
│ Avaliação por tipo:                       │
│ MCQ: exato match com opção                │
│ Gap/Translate: fuzzy match >= 80%         │
└───────────────────────────────────────────┘
        ↓
[PerformanceRecord.objects.create(...)]
        ↓
[Render result.html com correct=True/False]
        ↓
[Link: "Tentar Novamente" ou "Próximo"]
```

### 5. Fluxo de Geração de Quiz

```
[GET /quizzes/generate/]
        ↓
[Exibe template com seleção de temas/nível]
        ↓
[AJAX Preview: /quizzes/preview-quiz-count/]
        ↓
[Retorna JSON {total, shared, personal}]
        ↓
[Usuário clica Gerar]
        ↓
[POST /quizzes/generate/]
        ↓
┌────────────────────────────────────────┐
│ Heurísticas de seleção:                │
│ 1. Exclui últimos 30 dias              │
│ 2. Apenas procedural (gap + translate) │
│ 3. Balanceia tipos                     │
│ 4. Seleciona aleatoriamente            │
└────────────────────────────────────────┘
        ↓
[quiz = Quiz.objects.create(...)]
        ↓
[quiz.questions.set(selected_exercises)]
        ↓
[messages.success(f"Quiz criado")]
        ↓
[Redirect /quizzes/pk/take/]
```

---

## ✅ Testes e Validação

### 1. Verificação de Conformidade

```bash
# Executar validação Django
python manage.py check

# Esperado: "System check identified no issues (0 silenced)."
```

### 2. Testes de Funcionalidades Principais

#### Teste 1: Criar Usuário
```bash
# Via interface
GET http://127.0.0.1:8000/accounts/register/
# Preencher: username, email, password, level
# POST
# Esperado: Redirect para login
```

#### Teste 2: Criar Vocabulário
```bash
# Autenticado
GET http://127.0.0.1:8000/vocab/add/
# Preencher: word="hello", translation="olá"
# POST
# Esperado: Vocabulário criado, redirect /vocab/detail/pk/
```

#### Teste 3: Gerar Exercícios
```bash
# Autenticado
POST http://127.0.0.1:8000/vocab/pk/generate/
# Esperado: 3 exercícios criados (translate, mcq, gap)
```

#### Teste 4: Resolver Exercício
```bash
# Autenticado
GET http://127.0.0.1:8000/exercises/pk/take/
# Responder exercício
# POST
# Esperado: Resultado (correto/incorreto) + PerformanceRecord criado
```

#### Teste 5: Gerar Quiz
```bash
# Autenticado
POST http://127.0.0.1:8000/quizzes/generate/
# Selecionar temas/nível
# Esperado: Quiz criado com exercícios filtrados
```

### 3. Testes de API Externa

```python
# Terminal Python
import requests

# Teste Random Word API
resp = requests.get("https://random-word-api.herokuapp.com/all", timeout=5)
print(resp.json()[:5])  # Primeiras 5 palavras

# Teste Dictionary API
resp = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/example")
print(resp.json())  # Definições de "example"

# Teste MyMemory API
resp = requests.get("https://api.mymemory.translated.net/get?q=hello&langpair=en|pt")
print(resp.json()["responseData"]["translatedText"])
```

### 4. Verificação de Banco de Dados

```bash
# Dentro do Django shell
python manage.py shell
```

```python
from accounts.models import Profile
from vocab.models import Vocabulary
from exercises.models import Exercise, PerformanceRecord
from quizzes.models import Quiz

# Contar registros
print(f"Usuários: {Profile.objects.count()}")
print(f"Vocabulário: {Vocabulary.objects.count()}")
print(f"Exercícios: {Exercise.objects.count()}")
print(f"Performance: {PerformanceRecord.objects.count()}")
print(f"Quizzes: {Quiz.objects.count()}")

# Verificar exercício específico
ex = Exercise.objects.first()
print(f"Tipo: {ex.get_exercise_type_display()}")
print(f"Pergunta: {ex.question}")
print(f"Resposta: {ex.answer}")
```

### 5. Logs e Debugging

```python
# Em settings.py, adicionar:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Usar em views:
import logging
logger = logging.getLogger(__name__)
logger.info("Exercício criado com sucesso")
```

---

## 📊 Exemplo de Fluxo Completo (Caso de Uso)

### Cenário: Usuário Aprende Novo Vocabulário

```
1. REGISTRO
   User: João se registra
   → Sistema cria User + Profile(level='beginner', objectives='...')

2. CRIAR VOCABULÁRIO
   João acessa /vocab/add/
   → Preenche:
     - word: "beautiful"
     - translation: "bonito"
     - example: "She has a beautiful smile"
     - category: "Adjetivos"
     - level: "beginner"
     - is_shared: false (pessoal)
   → Sistema cria Vocabulary instance

3. GERAR EXERCÍCIOS
   João clica "Gerar Exercícios"
   → Sistema executa generate_exercises_for_vocab():
     
     a) Translation Exercise:
        Q: "Translate: beautiful"
        A: "bonito"
     
     b) MCQ Exercise (com API):
        Q: "Which is correct translation for 'beautiful'?"
        Choices: ["bonito", "feia", "grande", "pequeno"]
        A: "bonito"
     
     c) Gap-Fill Exercise (com example):
        Q: "Fill: She has a _____ smile"
        A: "beautiful"
   
   → Sistema salva 3 exercícios com created_by=João

4. PRATICAR - EXERCISE 1 (TRADUÇÃO)
   João vai para /exercises/take/
   → Vê: "Translate: beautiful"
   → Digita: "bonito"
   → Sistema avalia:
     - norm("bonito") == norm("bonito") → correct=True
     - Cria PerformanceRecord(user=João, exercise=ex1, correct=True)
   → Exibe: "Correto!" ✓

5. PRATICAR - EXERCISE 2 (MCQ)
   João vai para /exercises/take/
   → Vê: "Which is correct translation for 'beautiful'?"
   → Seleciona: "bonito"
   → Sistema avalia:
     - norm("bonito") == norm("bonito") → correct=True
     - Cria PerformanceRecord
   → Exibe: "Correto!" ✓

6. PRATICAR - EXERCISE 3 (GAP-FILL)
   João vai para /exercises/take/
   → Vê: "Fill: She has a _____ smile"
   → Digita: "beatiful" (erro ortográfico)
   → Sistema avalia:
     - fuzz.token_sort_ratio("beatiful", "beautiful") = 89%
     - 89% >= 80% → correct=True
     - Cria PerformanceRecord
   → Exibe: "Correto!" ✓ (com tolerância)

7. VER PROGRESSO
   João acessa /reviews/progress/
   → Sistema exibe:
     - Total de exercícios: 3
     - Corretos: 3 (100%)
     - Por categoria: Adjetivos (3)
     - Últimas atividades
   → Gráficos e estatísticas

8. GERAR QUIZ
   João acessa /quizzes/generate/
   → Seleciona tema: "Adjetivos", nível: "beginner"
   → Sistema executa heurísticas:
     - Busca exercícios: type IN (gap, translate)
     - Exclui: últimos 30 dias
     - Seleciona: 10 aleatórios
   → Cria Quiz com 10 exercícios
   → João resolve quiz
   → Score: 90% (9/10 corretos)
   → Sistema cria QuizResult

9. COMPARTILHAR
   João marca seus vocabs/exercícios como is_shared=True
   → Sistema os torna visíveis para outros usuários
   → Outros veem com badge "Compartilhado"

10. REVISÃO ESPAÇADA (No futuro)
    Sistema calcula ReviewSchedule
    → João é notificado: "Revisar em 3 dias"
    → Próxima revisão ajusta difficulty_factor (SM-2)
```

---

## 🔐 Segurança e Boas Práticas

### 1. Autenticação e Permissões
- ✅ Django User model + auth middleware
- ✅ LoginRequiredMixin em todas views protegidas
- ✅ Validação de proprietário (can_edit_*, can_delete_*)
- ✅ Staff/admin para gerenciamento

### 2. Validação de Dados
- ✅ Django ModelForm validation
- ✅ Normalização de entrada (strip, lower)
- ✅ Timeout em requisições HTTP (5-6 segundos)
- ✅ Exception handling em APIs

### 3. CSRF Protection
- ✅ {% csrf_token %} em todos formulários POST
- ✅ CsrfViewMiddleware ativo
- ✅ Logout usa POST + CSRF (não GET)

### 4. Banco de Dados
- ✅ ORM protection (SQL injection prevention)
- ✅ Transaction.atomic() em operações críticas
- ✅ Constraints e validação em modelo

### 5. Performance
- ✅ Pagination em listagens (15-20 items/page)
- ✅ Filtros em queryset (exclude, filter no BD)
- ✅ Select_related/prefetch_related (quando necessário)
- ✅ Timeout em APIs externas

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError: No module named 'django'" | `pip install -r requirements.txt` |
| "Port 8000 already in use" | `python manage.py runserver 8001` |
| "No such table: accounts_profile" | `python manage.py migrate` |
| "AnonymousUser error" | Verifique LoginRequiredMixin |
| "API externa lenta" | Aumentar timeout, verificar conexão |
| "Fuzzy match não funciona" | Verificar `pip install rapidfuzz` |

---

## 📈 Métricas e Estatísticas

### Queries Principais para Análise

```python
# 1. Usuários ativos no mês
from datetime import timedelta, timezone
cutoff = timezone.now() - timedelta(days=30)
active_users = User.objects.filter(
    performancerecord__timestamp__gte=cutoff
).distinct().count()

# 2. Taxa de acerto média
from django.db.models import Avg
avg_score = PerformanceRecord.objects \
    .filter(user=user) \
    .aggregate(accuracy=Avg('correct')) \
    ['accuracy']

# 3. Palavras mais praticadas
from django.db.models import Count
top_words = Exercise.objects \
    .annotate(attempts=Count('performancerecord')) \
    .order_by('-attempts')[:10]

# 4. Quizzes concluídos por nível
quiz_by_level = QuizResult.objects \
    .values('quiz__level') \
    .annotate(count=Count('id'))
```

---

## 📖 Referências e Recursos

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Forms](https://docs.djangoproject.com/en/5.2/topics/forms/)
- [Django ORM QuerySet](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)
- [RapidFuzz](https://rapidfuzz.github.io/)
- [Requests Library](https://requests.readthedocs.io/)

---

## 📝 Changelog

### v1.0.0 (2025-12-02)
- ✅ Sistema completo de vocabulário
- ✅ Múltiplos tipos de exercícios
- ✅ Quizzes com heurísticas inteligentes
- ✅ Sistema de compartilhamento
- ✅ Rastreamento de progresso
- ✅ Autenticação e perfis
- ✅ Integração com APIs externas

---

## 👨‍💻 Autor e Contribuições

**Desenvolvido por**: Sistema de Aprendizado Inteligente
**Tecnologias**: Django, Python, Bootstrap, SQLite
**Licença**: MIT (ou conforme definido)

---

## ❓ Perguntas Frequentes

**P: Como adicionar novo tipo de exercício?**
R: Editar `Exercise.TYPE_CHOICES` em models.py, adicionar lógica em `take_exercise()` view, criar template correspondente.

**P: Posso usar PostgreSQL em vez de SQLite?**
R: Sim, alterar `DATABASES['default']` em settings.py para PostgreSQL driver.

**P: Como fazer backup do banco?**
R: `cp db.sqlite3 db.backup.sqlite3` ou usar `python manage.py dumpdata > backup.json`

**P: Como desabilitar APIs externas?**
R: Comentar chamadas em `utils.py`, usar fallback hardcoded.

**P: É possível usar em produção?**
R: Sim, mas usar servidor WSGI (Gunicorn), DEBUG=False, SECRET_KEY segura, HTTPS, etc.

---

**Fim da Documentação**

*Última atualização: 3 de Dezembro de 2025*

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


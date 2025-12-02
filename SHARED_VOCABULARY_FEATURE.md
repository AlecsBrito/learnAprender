# Shared Vocabulary Feature

## Overview
The vocabulary system now supports two types of entries:
- **Personal Vocabulary**: Individual words created by each user (only visible to that user)
- **Shared Vocabulary**: Global words available to all users (created by staff/admins)

## How It Works

### Model Changes
- Added `is_shared` boolean field to `Vocabulary` model (default: False)
- Added unique constraint: users cannot have duplicate personal words, but can share words globally
- Model's `__str__` method displays "(compartilhado)" for shared words

### User Experience

#### Regular Users
1. **View Vocabulary** (`/vocab/`)
   - See their own personal vocabulary
   - Plus all shared vocabulary from other users/staff
   - Badge shows "Pessoal" (Personal) or "Compartilhado" (Shared)

2. **Create Vocabulary** (`/vocab/add/`)
   - Form includes "is_shared" checkbox
   - Regular users can create personal or shared vocabulary
   - Shared vocabulary is immediately visible to other users

3. **Edit/Delete**
   - Users can only edit/delete their own personal vocabulary
   - Cannot edit/delete vocabulary created by others

#### Staff/Admin Users
1. **Manage Vocabulary** (`/panel/vocab/`)
   - View all vocabulary (personal and shared)
   - Filter by: Text, Level, Category, **Shared Status**
   - Bulk actions: Generate Exercises, Delete
   - Can create, edit, or delete any vocabulary

2. **Filter Options**
   - "Todos" (All)
   - "Compartilhados" (Shared only)
   - "Pessoais" (Personal only)

### Database Structure
```python
class Vocabulary(models.Model):
    word = CharField(max_length=200)
    translation = CharField(max_length=400)
    example = TextField(blank=True)
    category = CharField(max_length=100, blank=True)
    level = CharField(choices=[...])
    tags = CharField(max_length=200, blank=True)
    created_by = ForeignKey(User)
    is_shared = BooleanField(default=False)  # NEW
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['word', 'created_by'],
                condition=Q(is_shared=False),
                name='unique_personal_vocab_per_user'
            ),
        ]
```

## Key Features

1. **Uniqueness Constraint**
   - Personal vocab: User cannot create duplicate words
   - Shared vocab: Any number of users can share the same word

2. **Visual Indicators**
   - Vocabulary list shows badges: "Pessoal" (gray) or "Compartilhado" (blue)
   - Detail view displays shared status prominently

3. **Admin Filtering**
   - Staff can filter by shared status in admin panel
   - Makes it easy to manage shared vs personal collections

4. **Automatic Visibility**
   - When user creates shared vocab, it's immediately available to other users
   - No approval workflow needed

## Usage Examples

### Regular User Creating Personal Vocabulary
```
1. Navigate to /vocab/
2. Click "Adicionar palavra" (Add Word)
3. Fill in word, translation, etc.
4. Leave "is_shared" unchecked
5. Save
6. Only you see this vocabulary
```

### Regular User Creating Shared Vocabulary
```
1. Navigate to /vocab/
2. Click "Adicionar palavra" (Add Word)
3. Fill in word, translation, etc.
4. CHECK "Vocabulário compartilhado"
5. Save
6. All users immediately see this vocabulary
```

### Staff Filtering Shared Vocabulary
```
1. Navigate to /panel/vocab/
2. In the "Todos" dropdown, select "Compartilhados"
3. View only shared vocabulary entries
4. Can generate exercises or delete if needed
```

## Migration
A migration was created (`vocab/migrations/0001_initial.py`) that:
- Adds the `is_shared` boolean field
- Sets default to False for all existing vocabulary
- Creates the unique constraint

## Forms & Validation
- `VocabularyForm` includes the `is_shared` checkbox
- Checkbox styled with Bootstrap (`form-check-input` class)
- Users can toggle shared status when creating or editing

## Admin Panel Integration
- Shared vocabulary filter added to admin panel list view
- Staff can manage shared/personal vocabulary separately
- Bulk actions work across both types

---

**Date Implemented**: 2025-12-02
**Status**: ✅ COMPLETE

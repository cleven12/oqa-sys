# Testing Guide for Online Quiz Assessment System

## Overview
This document explains how to run, write, and understand tests for the OQA system.
Written for backend developers learning Django testing best practices.

## Test Structure

```
accounts/
├── tests.py                 # Account & authentication tests
quiz/
├── tests.py                 # Quiz core functionality tests  
├── test_utils.py            # Utility function tests
```

## Running Tests

### Run All Tests
```bash
python manage.py test
```

### Run Tests in Parallel (faster)
```bash
python manage.py test --parallel 4
```

### Run Specific App Tests
```bash
python manage.py test accounts
python manage.py test quiz
```

### Run Specific Test Class
```bash
python manage.py test accounts.tests.TeacherProfileModelTest
python manage.py test quiz.tests.QuizModelTest
```

### Run Specific Test Method
```bash
python manage.py test accounts.tests.TeacherProfileModelTest.test_teacher_profile_creation
```

### Run with Verbosity
```bash
python manage.py test -v 2  # Show test names
python manage.py test -v 3  # Very detailed output
```

### Run with Code Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates htmlcov/index.html
```

## Test Categories Explained

### 1. Model Tests
**Purpose:** Test database integrity, constraints, and model methods

**What to Test:**
- Model creation with valid data
- Field validations (required, max_length, choices)
- Unique constraints
- Relationships (ForeignKey, OneToOne)
- Cascade deletes
- Custom properties and methods
- __str__() methods

**Example:**
```python
def test_quiz_code_auto_generation(self):
    """Test that quiz code is automatically generated"""
    quiz = Quiz.objects.create(
        title='Test Quiz',
        quiz_duration=1800,
        created_by=self.teacher
    )
    
    self.assertIsNotNone(quiz.quiz_code)
    self.assertTrue(quiz.quiz_code.startswith('QZ-'))
```

### 2. Form Tests
**Purpose:** Test user input validation

**What to Test:**
- Valid data passes validation
- Invalid data fails validation
- Required fields are enforced
- Custom validators work
- Form save() creates correct objects

**Example:**
```python
def test_password_mismatch(self):
    """Test validation fails when passwords don't match"""
    form_data = {
        'password1': 'SecurePass123!',
        'password2': 'DifferentPass123!',
    }
    
    form = TeacherRegistrationForm(data=form_data)
    self.assertFalse(form.is_valid())
    self.assertIn('password2', form.errors)
```

### 3. View Tests
**Purpose:** Test HTTP responses and user flows

**What to Test:**
- Correct HTTP status codes (200, 302, 404)
- Correct templates used
- Login required decorators work
- Redirects go to correct URLs
- Context data is passed correctly

**Example:**
```python
def test_login_view_get(self):
    """Test login page loads"""
    response = self.client.get(reverse('accounts:login'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'accounts/login.html')
```

### 4. Business Logic Tests
**Purpose:** Test core quiz mechanics

**What to Test:**
- Timer calculations
- Scoring accuracy
- Question randomization
- Auto-submission rules
- Pass/fail determination

**Example:**
```python
def test_calculate_time_remaining_expired(self):
    """Test time remaining when session has expired"""
    session.start_time = timezone.now() - timedelta(minutes=40)
    session.save()
    
    remaining = calculate_time_remaining(session)
    self.assertEqual(remaining, 0)  # Never negative
```

### 5. Security Tests
**Purpose:** Test security constraints

**What to Test:**
- Unique constraints prevent duplicates
- Cascade deletes protect integrity
- Permissions block unauthorized access
- No SQL injection vulnerabilities

## Writing Good Tests

### Test Naming Convention
```python
def test_<what>_<scenario>_<expected_result>(self):
    """Clear docstring explaining what this tests"""
```

Examples:
- `test_quiz_code_auto_generation()`
- `test_student_cannot_retake_same_quiz()`
- `test_time_remaining_when_expired()`

### AAA Pattern (Arrange, Act, Assert)
```python
def test_example(self):
    # Arrange - Set up test data
    quiz = Quiz.objects.create(...)
    
    # Act - Perform the action
    result = quiz.some_method()
    
    # Assert - Verify the result
    self.assertEqual(result, expected)
```

### Use setUp() for Common Data
```python
class QuizModelTest(TestCase):
    def setUp(self):
        """Run before each test method"""
        self.teacher = User.objects.create_user(...)
        self.quiz = Quiz.objects.create(...)
    
    def test_something(self):
        # self.quiz is available here
        pass
```

### Test Both Success and Failure
```python
def test_valid_form(self):
    """Test form accepts valid data"""
    form = MyForm(data=valid_data)
    self.assertTrue(form.is_valid())

def test_invalid_form(self):
    """Test form rejects invalid data"""
    form = MyForm(data=invalid_data)
    self.assertFalse(form.is_valid())
    self.assertIn('field_name', form.errors)
```

## Common Assertions

```python
# Equality
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Truth
self.assertTrue(x)
self.assertFalse(x)
self.assertIsNone(x)
self.assertIsNotNone(x)

# Membership
self.assertIn(a, b)
self.assertNotIn(a, b)

# Comparison
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
self.assertLessEqual(a, b)

# Exceptions
with self.assertRaises(ValueError):
    function_that_should_raise()

# HTTP (in view tests)
self.assertEqual(response.status_code, 200)
self.assertRedirects(response, '/expected/url/')
self.assertTemplateUsed(response, 'template.html')
self.assertContains(response, 'expected text')
```

## Test Database

Django creates a separate test database:
- Migrations run automatically
- Data is isolated per test
- Database is destroyed after tests
- Use `--keepdb` to reuse database between runs

```bash
python manage.py test --keepdb  # Faster for repeated runs
```

## Test Coverage Goals

### Minimum Coverage
- **Models:** 100% - All fields, methods, properties
- **Forms:** 90%+ - All validation paths
- **Views:** 80%+ - All major flows
- **Utils:** 95%+ - All business logic

### What NOT to Test
- Django's built-in functionality
- Third-party library internals
- Auto-generated code

## Current Test Status

```
Total Tests: 72
✓ accounts.tests: 14 tests
✓ quiz.tests: 41 tests  
✓ quiz.test_utils: 17 tests

All tests passing ✓
```

## Debugging Failed Tests

### See Full Output
```bash
python manage.py test -v 2
```

### Run Single Failing Test
```bash
python manage.py test path.to.FailingTest.test_method -v 2
```

### Use print() Debugging
```python
def test_something(self):
    result = my_function()
    print(f"DEBUG: result = {result}")  # Shows in test output with -v 2
    self.assertEqual(result, expected)
```

### Use Django's assertNumQueries
```python
from django.test.utils import override_settings

def test_query_efficiency(self):
    with self.assertNumQueries(3):  # Expect exactly 3 queries
        # Code that should make 3 database queries
        pass
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test --parallel 4
```

## Performance Testing

### Benchmark Test Execution
```bash
time python manage.py test
```

### Profile Slow Tests
```bash
python manage.py test --debug-mode
```

## Best Practices Summary

1. **Write tests first (TDD)** - Tests guide design
2. **One assert per test** - Makes failures clear
3. **Use descriptive names** - Tests are documentation
4. **Test edge cases** - Empty lists, None, negative numbers
5. **Keep tests independent** - No test depends on another
6. **Use fixtures wisely** - setUp() for common data
7. **Mock external services** - Don't call real APIs in tests
8. **Test security constraints** - Permissions, validation
9. **Run tests before commits** - Catch issues early
10. **Maintain test quality** - Refactor tests like production code

## Next Steps

1. Add API endpoint tests
2. Add view integration tests
3. Add form POST tests
4. Add permission tests
5. Add Excel import/export tests
6. Add coverage reporting to CI/CD

## Resources

- [Django Testing Docs](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Python unittest Docs](https://docs.python.org/3/library/unittest.html)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

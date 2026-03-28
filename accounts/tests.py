"""
ACCOUNTS APP - COMPREHENSIVE TEST SUITE

This module tests all authentication, registration, and teacher profile functionality.
Following Django testing best practices and TDD principles.

Test Categories:
1. Model Tests - Database integrity, constraints, methods
2. Form Tests - Validation, data cleaning, error handling
3. View Tests - HTTP responses, permissions, redirects
4. Integration Tests - Full user flows

Learning Points:
- Always test model constraints (unique, required fields)
- Test both valid and invalid data scenarios
- Use setUp() for test fixtures/common data
- Use Django's TestCase for database transactions
- Use Client() for view testing
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import TeacherProfile
from .forms import TeacherRegistrationForm, LoginForm


class TeacherProfileModelTest(TestCase):
    """
    Test TeacherProfile model behavior
    
    Learning: Models are the foundation - test constraints, methods, properties
    """
    
    def setUp(self):
        """Create test user for all tests in this class"""
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher'
        )
    
    def test_teacher_profile_creation(self):
        """Test creating a teacher profile linked to user"""
        profile = TeacherProfile.objects.create(
            user=self.user,
            phone_number='+255712345678',
            institution='Test University'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '+255712345678')
        self.assertEqual(profile.institution, 'Test University')
        self.assertFalse(profile.is_verified)
        self.assertIsNone(profile.verified_at)
    
    def test_teacher_profile_str_method(self):
        """Test string representation"""
        profile = TeacherProfile.objects.create(
            user=self.user,
            institution='Test University'
        )
        
        expected = "Test Teacher - Test University"
        self.assertEqual(str(profile), expected)
    
    def test_teacher_profile_str_without_institution(self):
        """Test string representation when no institution"""
        profile = TeacherProfile.objects.create(user=self.user)
        
        expected = "Test Teacher - No Institution"
        self.assertEqual(str(profile), expected)
    
    def test_one_to_one_relationship(self):
        """Test that one user can only have one profile"""
        TeacherProfile.objects.create(user=self.user)
        
        with self.assertRaises(Exception):
            TeacherProfile.objects.create(user=self.user)
    
    def test_cascade_delete(self):
        """Test that profile is deleted when user is deleted"""
        profile = TeacherProfile.objects.create(user=self.user)
        profile_id = profile.id
        
        self.user.delete()
        
        self.assertFalse(TeacherProfile.objects.filter(id=profile_id).exists())
    
    def test_verification_workflow(self):
        """Test verification timestamp behavior"""
        profile = TeacherProfile.objects.create(user=self.user)
        
        self.assertFalse(profile.is_verified)
        self.assertIsNone(profile.verified_at)
        
        profile.is_verified = True
        profile.verified_at = timezone.now()
        profile.save()
        
        self.assertTrue(profile.is_verified)
        self.assertIsNotNone(profile.verified_at)


class TeacherRegistrationFormTest(TestCase):
    """
    Test registration form validation
    
    Learning: Forms handle user input - test validation rules
    """
    
    def test_valid_registration_form(self):
        """Test form with all valid data"""
        form_data = {
            'username': 'newteacher',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'new@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '+255712345678',
            'institution': 'Test School'
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test validation fails when passwords don't match"""
        form_data = {
            'username': 'newteacher',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'new@test.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_missing_required_fields(self):
        """Test that required fields are enforced"""
        form_data = {
            'username': 'newteacher',
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password1', form.errors)
    
    def test_invalid_email(self):
        """Test email validation"""
        form_data = {
            'username': 'newteacher',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'invalid-email',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_saves_user_and_profile(self):
        """Test that form creates both User and TeacherProfile"""
        form_data = {
            'username': 'newteacher',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'new@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone_number': '+255712345678',
            'institution': 'Test School'
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        self.assertEqual(user.username, 'newteacher')
        self.assertEqual(user.email, 'new@test.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Teacher')
        
        self.assertTrue(hasattr(user, 'teacher_profile'))
        profile = user.teacher_profile
        self.assertEqual(profile.phone_number, '+255712345678')
        self.assertEqual(profile.institution, 'Test School')


class LoginFormTest(TestCase):
    """Test login form"""
    
    def test_valid_login_form(self):
        """Test login form with valid data"""
        form_data = {
            'username': 'teacher',
            'password': 'password123'
        }
        
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_credentials(self):
        """Test login form requires both fields"""
        form_data = {'username': 'teacher'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class AccountViewsTest(TestCase):
    """
    Test authentication views
    
    Learning: Views handle HTTP - test responses, redirects, permissions
    """
    
    def setUp(self):
        """Setup test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123'
        )
        TeacherProfile.objects.create(user=self.user)
    
    def test_register_view_get(self):
        """Test registration page loads"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_login_view_get(self):
        """Test login page loads"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_logout_redirects(self):
        """Test logout redirects to landing"""
        self.client.login(username='testteacher', password='testpass123')
        
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('quiz:landing'))
    
    def test_verify_otp_view(self):
        """Test OTP verification page loads"""
        response = self.client.get(reverse('accounts:verify_otp'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/verify_otp.html')


class TeacherProfileIntegrationTest(TestCase):
    """
    Integration tests - full user workflows
    
    Learning: Integration tests verify complete features work together
    """
    
    def test_complete_registration_workflow(self):
        """Test full registration creates user and profile"""
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(TeacherProfile.objects.count(), 0)
        
        form_data = {
            'username': 'newteacher',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'new@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'institution': 'Test School'
        }
        
        form = TeacherRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(TeacherProfile.objects.count(), 1)
        
        profile = TeacherProfile.objects.get(user=user)
        self.assertEqual(profile.user.username, 'newteacher')
        self.assertEqual(profile.institution, 'Test School')


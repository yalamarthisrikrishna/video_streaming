from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Video

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some test videos
        self.video1 = Video.objects.create(name='Video 1', user=self.user)
        self.video2 = Video.objects.create(name='Video 2', user=self.user)

    def test_user_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_user_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_user_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_create_video_view(self):
        # Assuming user is logged in
        self.client.force_login(self.user)
        response = self.client.get(reverse('create_video'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_video.html')

    def test_edit_video_view(self):
        # Assuming user is logged in
        self.client.force_login(self.user)
        response = self.client.get(reverse('edit_video', kwargs={'pk': self.video1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_video.html')

    def test_delete_video_confirm_view(self):
        # Assuming user is logged in
        self.client.force_login(self.user)
        response = self.client.get(reverse('confirm_delete_video', kwargs={'pk': self.video1.pk}))
        self.assertEqual(response.status_code, 302)  # Update the expected status code

    def test_permission_denied_view(self):
        response = self.client.get(reverse('permission_denied'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permission_denied.html')

    def test_all_videos_view(self):
        # Assuming a valid video path
        valid_video_path = 'https://www.youtube.com/watch?v=mBkc7pv8JvE'

        # Create a Video object for testing purposes
        video = Video.objects.create(name='Test Video', user=self.user)

        # Assuming user is logged in
        self.client.force_login(self.user)

        response = self.client.get(reverse('all_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_videos.html')

        # Now, let's check if the video feed URL is present in the response
        self.assertContains(response, reverse('video_feed', kwargs={'video_path': valid_video_path}))

    def test_video_detail_view(self):
        response = self.client.get(reverse('video_detail', kwargs={'pk': self.video1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video_detail.html')



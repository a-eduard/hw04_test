from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

TEST_OF_POST: int = 10
User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        bilk_post: list = []
        for i in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_correct_page_context_guest_client(self):
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            error_name1 = (f'Ошибка: {count_posts1} постов,'
                           f' должно {TEST_OF_POST}')
            error_name2 = (f'Ошибка: {count_posts2} постов,'
                           f'должно {TEST_OF_POST}')
            self.assertEqual(count_posts1,
                             TEST_OF_POST,
                             error_name1)
            self.assertEqual(count_posts2,
                             TEST_OF_POST,
                             error_name2)

    def test_correct_page_context_authorized_client(self):
        pages = [reverse('posts:index'),
                 reverse('posts:profile',
                         kwargs={'username': f'{self.user.username}'}),
                 reverse('posts:group_list',
                         kwargs={'slug': f'{self.group.slug}'})]
        for page in pages:
            response1 = self.authorized_client.get(page)
            response2 = self.authorized_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            error_name1 = (f'Ошибка: {count_posts1} постов,'
                           f' должно {TEST_OF_POST}')
            error_name2 = (f'Ошибка: {count_posts2} постов,'
                           f'должно {TEST_OF_POST}')
            self.assertEqual(count_posts1,
                             TEST_OF_POST,
                             error_name1)
            self.assertEqual(count_posts2,
                             TEST_OF_POST,
                             error_name2)


class ViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.user2 = User.objects.create_user(username='auth2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.post = Post.objects.create(text='Тестовый текст',
                                        group=self.group,
                                        author=self.user)

    def test_views_correct_template(self):
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост',
                       response.context['post'].group: self.group,
                       response.context['post'].author: self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')

    def test_post_added_correctly_user2(self):
        group2 = Group.objects.create(title='Тестовая группа 2',
                                      slug='test_group2')
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count, 'поста нет в другой группе')
        self.assertNotIn(post, profile,
                         'поста нет в группе другого пользователя')

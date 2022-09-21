from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


LEN_OF_POSTS: int = 15

class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='Тестовая группа',
                                          slug='Тестовый слаг',
                                          description='Тестовое описание',)
        cls.post = Post.objects.create(author=cls.user,
                                         text='Тестовое описание поста',)

    def test_title_label(self):
        post = PostModelTest.post
        field_verboses = {'text': 'Текст поста',
                          'pub_date': 'Дата публикации',
                          'group': 'Группа',
                          'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value, error_name)

    def test_title_help_text(self):
        post = PostModelTest.post
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Выберите группу'}
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value, error_name)

    def test_models_have_correct_object_names(self):
        error_name = f"Вывод не имеет {LEN_OF_POSTS} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:LEN_OF_POSTS],
                         error_name)

class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )

    def test_models_have_correct_object_names(self):
        group = GroupModelTest.group
        title = group.title
        self.assertEquals(title, "Тест")

    def test_str_group_model(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)
    
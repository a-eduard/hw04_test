from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа к которой будет относится пост'
        }

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Заполните поля')
        return data

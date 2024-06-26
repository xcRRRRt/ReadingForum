from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField
from django import forms
from utils.detect_sensitive import Sensitive


class PostEditorForm(forms.Form):
    """
    标题
    标签(多个)
    content为ckeditor
    """
    content = RichTextUploadingFormField(
        label="内容",
        config_name='default',
        required=True
    )
    title = forms.CharField(required=False, widget=forms.HiddenInput())
    labels = forms.CharField(required=False, widget=forms.HiddenInput())
    bound_book = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_title(self):
        title = self.cleaned_data.get("title")
        _, has_sensitive = Sensitive.detect_sensitive_words(title)
        if has_sensitive:
            self.add_error("title", "标题中含有敏感词，请修改后重新提交")
        return title

    def clean_labels(self):
        labels = self.cleaned_data.get('labels')
        if labels == '':
            return None
        label_list = labels.split(' ')
        return label_list if label_list else None

    def clean_bound_book(self):
        bound_book = self.cleaned_data.get('bound_book')
        if bound_book == '' or not bound_book:
            return None
        return bound_book

    def clean(self):
        cleaned_data = super(PostEditorForm, self).clean()
        content = self.cleaned_data.get('content')
        if not content or content.strip() == "":
            self.add_error('content', '内容不可为空')
            return cleaned_data
        content_with_hint, has_sensitive = Sensitive.detect_sensitive_words(content)
        if has_sensitive:
            self.add_error('content', '内容中含有敏感词，请修改后重新提交')
            cleaned_data['content'] = content_with_hint
        return cleaned_data



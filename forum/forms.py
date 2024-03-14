from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingFormField
from django import forms


class PostForm(forms.Form):
    """
    标题
    标签(多个)
    content为ckeditor
    """
    content = RichTextUploadingFormField(
        label="内容",
        config_name='default',
    )
    title = forms.CharField(required=False, widget=forms.HiddenInput())
    labels = forms.CharField(required=False, widget=forms.HiddenInput())

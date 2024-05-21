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
    bound_book = forms.CharField(required=False, widget=forms.HiddenInput())

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

# ReadingForum

## 重要事项

1. django-ckeditor中的ckeditor_uploader源码需要调整, 将staff_member_required去掉  
   需要修改的文件路径：``你的环境名\Lib\site-packages\ckeditor_uploader\urls.py``  
   改为如下：
   ```python
   urlpatterns = [
      re_path(r"^upload/", views.upload, name="ckeditor_upload"),
      re_path(
         r"^browse/",
         never_cache(views.browse),
         name="ckeditor_browse",
      )]
   ```

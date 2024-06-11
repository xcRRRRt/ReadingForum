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

2. 本项目需要使用MongoDB和Redis，请在启动项目前**启动MongoDB和Redis**
3. 在单独运行一次utils.create_collections.py
4. 修改utils.detect_sensitive.py和utils.tokenize.py中的redis配置
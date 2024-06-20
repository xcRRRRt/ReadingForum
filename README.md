# ReadingForum

## 重要事项

1. 新建环境
```
conda create -n readingforum python=3.12
```
2. 安装必要的包
```
pip --no-cache-dir install -r requirements.txt
```
3. django-ckeditor中的ckeditor_uploader源码需要调整, 将staff_member_required去掉  
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

4. 本项目需要使用MongoDB和Redis，请在启动项目前**启动MongoDB和Redis**
5. 单独运行一次utils.create_collections.py
6. 修改utils.detect_sensitive.py和utils.tokenize.py中的redis配置
7. 将data文件夹中的4个json文件分别导入MongoDB中对应的4个集合
8. 启动Django项目
9. 建议使用火狐浏览器或谷歌浏览器
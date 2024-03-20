import os

from readingforum.settings import MEDIA_ROOT, MEDIA_URL


def save_file(file, save_directory_relative, file_name):
    """
    用于保存文件
    :param file: 文件
    :param save_directory_relative: 需要保存到的目录的相对路径 例：userinfo/avatar
    :param file_name: 需要保存的文件名
    :return: 保存到数据库的路径
    """
    extension = os.path.splitext(file.name)[-1]  # 文件扩展名
    abs_save_directory = os.path.join(MEDIA_ROOT, save_directory_relative)
    if not os.path.exists(abs_save_directory):
        os.makedirs(abs_save_directory)

    relative_save_path = os.path.join(save_directory_relative, file_name + extension)
    abs_save_path = os.path.join(str(abs_save_directory), file_name + extension)  # 保存到本地的绝对路径
    db_path = str(os.path.join(MEDIA_URL, str(relative_save_path)))  # 保存到数据库的url路径

    with open(abs_save_path, "wb") as f:
        for chunk in file.chunks():  # pic.chunks()为图片的一系列数据，它是一一段段的，所以要用for逐个读取
            f.write(chunk)

    return db_path

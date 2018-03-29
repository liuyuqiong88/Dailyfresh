from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client



class FdfsStorage(FileSystemStorage):
    """自定义存储文件系统
         当用户通过管理后台上传文件时,
         django会调用此方法来保存用户上传到django网站的文件,
         我们可以在此方法中保存用户上传的文件到FastDFS服务器中

    """


    def _save(self, name, content):


        client = Fdfs_client('./utils/fastdfs/client.conf')


        data = content.read()
        my_dict = client.upload_by_buffer(data)
        print(my_dict)

        path = None
        if my_dict.get('Status') == 'Upload successed.':
        #文件上传成功
            path = my_dict.get('Remote file_id')

        else:
            print('文件上传错误')

        return path

    def url(self, name):
        # nginx服务器的主机端口
        host = 'http://127.0.0.1:8888/'

        return host+super().url(name)
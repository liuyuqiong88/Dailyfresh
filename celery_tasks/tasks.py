
# import os
# import django
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE","dailyfresh.settings")
# django.setup()


from django.conf import settings
from celery import Celery
from django.core.mail import send_mail

app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/1')

@app.task
def send_active_mail(self, username, email, token):
    """
    发送激活邮件
    :param username: 注册的用户
    :param email:  注册用户的邮箱
    :param token: 对字典 {'confirm':用户id} 加密后的结果
    :return:
    """

    subject = '天天生鲜注册激活'  # 邮件标题
    message = ''  # 邮件的正文
    from_email = settings.EMAIL_FROM  # 发送者
    recipient_list = [email]  # 接受者，　注意：这里需要一个list

    html_message = '<h3>尊敬的%s:</h3>  欢迎注册天天生鲜' \
                   '请点击以下链接激活您的账号:<br/>' \
                   '<a href="http://127.0.0.1:8000/users/active/%s">' \
                   'http://127.0.0.1:8000/users/active/%s</a>' % \
                   (username, token, token)

    # 调研django的send_mail　方法发送邮件
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
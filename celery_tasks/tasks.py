
# import os
# import django
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE","dailyfresh.settings")
# django.setup()


from django.conf import settings
from celery import Celery
from django.core.mail import send_mail
from django.template import loader

from apps.goods.models import *
from apps.orders.models import *

app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/1')

# 用异步celery去生成激活邮件
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

# 用celery生成静态首页
@app.task
def generate_static_index_html():
    """生成静态的首页:index.html"""

    # 查询首页中要显示的数据
    # 所有的商品类别
    categories = GoodsCategory.objects.all()
    # 主页轮播商品
    slide = IndexSlideGoods.objects.all()
    # 主页促销活动
    promotion = IndexPromotion.objects.all()
    # 主页分类展示
    for i in categories:
    # 查询当前类别所有文字商品和图片商品
        text_skus = IndexCategoryGoods.objects.filter(category=i,display_type=0)

        #     动态地给类别对象，新增属性
        imgs_skus = IndexCategoryGoods.objects.filter(category=i, display_type=1).order_by('index')
        i.text_skus = text_skus
        i.imgs_skus = imgs_skus


    cart_count = 0

    data = {
        'categorise': categories,
        'slide': slide,
        'promotion': promotion,
        'cart_count': cart_count,

    }

    # 获取模板文件生存ｈｔｍｌ文件
    template = loader.get_template('index.html')

    index_html = template.render(data)

    file_path = '/home/python/Desktop/celery_server/static/indexq.html'

    with open(file_path,'w') as f :
        f.write(index_html)
from django.contrib.auth.decorators import *
from django.views.generic import View


# 多继承：mixin :扩展功能，新增
class LoginRequiredView(View):
    """判断是否有登陆，没有登陆，会跳转到登陆界面"""

    # 需要声明为类方法
    @classmethod
    def as_view(cls, **initkwargs):

        view_fun = super().as_view(**initkwargs)
        return login_required(view_fun)
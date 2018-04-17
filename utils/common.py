from django.contrib.auth.decorators import *
from django.views.generic import View

# 多继承：mixin :扩展功能，新增
from django_redis import get_redis_connection


class LoginRequiredView(View):
    """判断是否有登陆，没有登陆，会跳转到登陆界面"""

    # 需要声明为类方法
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        return login_required(view_fun)


def get_cart_count(user):
    cart_count = 0
    strict_redis = get_redis_connection('default')

    cart_key = 'cart_%s' % user.id

    vals = strict_redis.hvals(cart_key)

    for i in vals:
        cart_count += int(i)
    return cart_count


class BaseView(View):



    def get_cart_sku_id(self, user) :
        # cart_count = 0

        strict_redis = get_redis_connection('default')

        cart_key = 'cart_%s' % user.id

        vals = strict_redis.hvals(cart_key)

        return vals

        # for i in vals:
        #     cart_count += int(i)
        # return cart_count

    def get_cart_count(self, user):
        cart_count = 0

        vals = self.get_cart_sku_id(user)

        for i in vals:
            cart_count += int(i)
        return cart_count

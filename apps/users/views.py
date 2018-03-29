from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
import re
from itsdangerous import TimedJSONWebSignatureSerializer,SignatureExpired
import settings
from utils.common import LoginRequiredView

# Create your views here.
from django.views.generic import View

from apps.users.models import User, Address


def register(request):
    pass


class RegisteView(View):
    """注册的view类"""

    def get(self,request):
        """显示注册界面"""
        return render(request,'register.html')

    def post(self,request):
        """处理注册"""

#         获取注册信息
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 验证提交数据的合法性
        # 所有的参数都不为空时,all方法才会返回True
        if not all([username,password,password2,email]):
            return render(request,'register.html',{'errmsg':'参数不能为空'})

        if password !=password2 :
            return render(request,'register.html',{'errmsg':'两次密码输入不一致'})
        if not re.match(r'^^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request,'register.html',{'errmsg':'邮件格式不正确'})
        # 必须同意用户协议
        if allow != 'on':
            return render(request,'register.html',{'errmsg':'请同意用户协议'})

        # 验证用户是否存在
        try:
            user = User.objects.create_user(username,email,password)
            user.is_active = False
        except IntegrityError as e :

            return render(request,'register.html',{'errmsg':'用户名已存在'})

        # todo 给用户发送激活邮件
        # 参数１：秘钥　　参数２：过期时间

        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY
                                            ,3600)

        token = s.dumps({'confirm':user.id})
        token = token.decode()

        self.send_active_mail(username,email,token)


        return HttpResponse('进入登陆界面')


    def send_active_mail(self,username,email,token):
        """
        发送激活邮件
        :param username: 注册的用户
        :param email:  注册用户的邮箱
        :param token: 对字典 {'confirm':用户id} 加密后的结果
        :return:
        """

        subject = '天天生鲜注册激活'            #邮件标题
        message = ''                           #邮件的正文
        from_email = settings.EMAIL_FROM        #发送者
        recipient_list = [email]                #接受者，　注意：这里需要一个list

        html_message = '<h3>尊敬的%s:</h3>  欢迎注册天天生鲜' \
                       '请点击以下链接激活您的账号:<br/>' \
                       '<a href="http://127.0.0.1:8000/users/active/%s">' \
                       'http://127.0.0.1:8000/users/active/%s</a>' % \
                       (username, token, token)


        # 调研django的send_mail　方法发送邮件
        send_mail(subject,message,from_email,recipient_list,html_message=html_message)


class ActiveView(View):
    """处理激活邮箱的类"""

    def get(self,request , token):

        try:
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,3600)

            my_dict = s.loads(token)

            user_id = my_dict.get('confirm')

        except SignatureExpired: #激活链接已过期
            return HttpResponse('url链接已过期！')

        User.objects.filter(id = user_id).update(is_active = True)

        return HttpResponse('激活成功,进入登陆界面')


class LoginView(View):

    def get(self,request):
        """进入登陆界面"""
        return render(request,'login.html')

    def post(self, request):

        # 获取登录请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 校验参数合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户名或密码不能为空'})

        # 使用django提供的认证方法
        # 调用django提供的方法,判断用户名和密码是否正确
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})

        # 判断用户名是否有激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '账号未激活'})

        # 调用django的login方法, 记录登录状态(session)
        # 内部会通过session保存登录用户的id
        # _auth_user_id = 1
        login(request, user)

        # 设置session有效期
        if remember == 'on':
            request.session.set_expiry(None)

        else:
            request.session.set_expiry(0)


        # 获取next跳转参数
        next_url = request.GET.get('next',None)

        if next_url is None:
            return redirect(reverse('goods:index'))
        else:
            return redirect(next_url)

class LogoutView(View):

     def get(self,request):

         logout(request)

         return redirect(reverse('users:login'))


class UserInfoView(LoginRequiredView,View):
    """用户中心：个人信息界面"""
    def get(self,request):

        user = request.user

        try:
            address = user.address_set.all().latest('create_time')

        except Address.DoesNotExist:

            address = None

        data = {'which_page': 0 ,'address':address}

        return render(request,'user_center_info.html',data)

class UserOrderView(LoginRequiredView,View):
    """用户中心:订单显示界面"""
    def get(self,request):

        data = {'which_page':1}
        return render(request,'user_center_order.html',data)

class UserAddressView(LoginRequiredView,View):
    """用户中心:地址界面"""
    def get(self,request):

        user = request.user

        try :
            address = user.address_set.all().latest('create_time')
        except Address.DoesNotExist:
            address = None

        data = {'which_page': 2, 'address': address}
        return render(request,'user_center_site.html',data)

    def post(self,request):

        user = request.user

        receiver_name = request.POST.get('receiver')
        receiver_mobile = request.POST.get('mobile')
        detail_addr = request.POST.get('address')
        zip_code = request.POST.get('zip_code')

        print(receiver_name,receiver_mobile,detail_addr,zip_code)

        if not all([receiver_name,receiver_mobile,detail_addr,zip_code]):
            return render(request,'user_center_site.html',{'errmsg':'参数不能为空'})

        new_addr = Address()

        new_addr.user = user
        new_addr.receiver_mobile = receiver_mobile
        new_addr.receiver_name = receiver_name
        new_addr.detail_addr = detail_addr
        new_addr.zip_code = zip_code
        new_addr.save()

        return redirect(reverse('users:address'))

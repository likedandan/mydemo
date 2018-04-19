from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import check_password, make_password

from .user_forms import RegisterForm
from .models import User

def register(request):
    '''
    注册
    '''
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            # 保存用户注册信息
            u = form.save(commit=False)  # 保存图片但是不会像数据库提交
            u.password = make_password(u.password)
            u.save()

            # 向session写入登陆信息
            request.session['uid'] = u.id
            request.session['nickname'] = u.nickname

            return redirect('/info/')

        else:
            errors = form.errors
            return render(request, 'register.html', {'errors':errors})

    return render(request, 'register.html')



def login(request):
    '''
    登陆
    '''
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist as e:
            return render(request, 'login.html', {'errors':'昵称不存在'})

        # 验证密码
        if check_password(password, user.password):
            # 向session写入登陆状态
            request.session['uid'] = user.id
            request.session['nickname'] = nickname

            return HttpResponseRedirect('/info/')
        return render(request, 'login.html', {'errors':'密码错误'})
    return render(request, 'login.html')



def info(request):
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)
    return render(request, 'info.html', {'user':user})



def logout(request):
    '''
    退出
    '''
    request.session.flush()
    return redirect('/index/')

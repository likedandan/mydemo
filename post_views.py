from django.shortcuts import render, redirect
from django.db.models import Q
from math import ceil
from django.core.cache import cache

from .models import Article, User, Comment, Tag
from .post_forms import PostForm
from .helper import page_cache


def index(request):
	'''
	首页
	'''
    article_list = Article.objects.filter(id__lte=6).order_by('-update_time')
    tag_list = Tag.objects.all()
    return render(request, 'index.html', {'article_list':article_list,
                                          'tag_list':tag_list,
                                          })

def article_list(request):
	'''
	全部文章
	'''
    article_total = Article.objects.all().order_by('-update_time').count()  # 文章总数
    limit = 3  # 每页显示条数
    page = int(request.GET.get('page', 0)) or 1  # 当前页码,默认为第 1 页
    # request.session['page'] = page  # 记录当前页码
    pages = ceil(article_total / limit)  # 总页数

    start = (page - 1) * limit
    end = start + limit

    article_list = Article.objects.all().order_by('-create_time')[start:end]

    return render(request, 'articles-list.html', {'article_list':article_list,
                                                  'pages':range(1, pages + 1),
                                                  })

@page_cache(1)
def single(request):
	'''
	详情页
	'''
    aid = request.GET.get('aid')

    # 判断缓存里是否有
    # article = cache.get('Post-%s' % aid)

    # if article is None:  # 如果缓存没有,就从数据库读
    article = Article.objects.get(id=aid)
        # cache.set('Post-%s' % aid, article)
    article.comment = article.comment_set.all().order_by('-create_time')


    # 给每条评论查找用户头像，未登录用户使用默认头像
    for i in article.comment:
        if i.identi == 'guest':
            i.head_pic = 'unknow.jpg'
        else:
            i_u = User.objects.get(nickname=i.identi)
            i.head_pic = i_u.head_pic
    return render(request, 'single.html', {'article':article})


def commit(request):
	'''
	评论
	'''
    aid = request.GET.get('aid')
    if request.method == 'POST':
        content = request.POST.get('comment')
        nickname = request.session.get('nickname') or 'guest'

        a = Comment(comment=content, identi=nickname, article_id=aid)
        a.save()
    return redirect('/single/?aid=' + aid)


def search(request):
	'''
	搜索
	'''
    keyword = request.GET.get('keyword')
    about_total = Article.objects.filter(Q(content__contains=keyword) | Q(title__contains=keyword) | Q(tag__tag__contains=keyword)).order_by('-create_time')

    return render(request, 'search.html', {'about_total':about_total})


def add_article(request):
	'''
	写新文章
	'''
    uid = request.session.get('uid')
    user = User.objects.get(id=uid)

    if uid is not None:
        tag_list = Tag.objects.all()

        if request.method == 'POST':
            form = PostForm(request.POST)

            if form.is_valid():  # 如果数据有效，保存到数据库
                data = form.cleaned_data
                a = form.save(commit=False)
                a.author = user
                a.save()
                cache.set('Post-%s' % a.id, a)
                return redirect('/single/?aid=%s' %a.id)
            return redirect('/add_article/')

        # 处理完以后，存入缓存
        # cache.set('Post-%s' % article.id, article)
        return render(request, 'add-article.html', {'tag_list':tag_list})
    return redirect('/login/')

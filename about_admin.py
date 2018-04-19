import os
import random
from datetime import datetime
from PIL import Image

from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import current_app
from flask import session
from flask import flash
from flask import make_response

from app.extensions import photos
from app.models import Category, Picture, Article, Tag
from app.extensions import db


# *******************************************蓝本******************************************
aboutadmin = Blueprint('aboutadmin', __name__)



# *******************************************基础函数******************************************
def gen_rnd_filename():
    '''
    随机文件名函数
    '''
    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))



# *******************************************分类管理******************************************
@aboutadmin.route('/categorylist/')
def categorylist():
    '''
    分类名称显示
    '''
    page = request.args.get('page', 1, type=int)
    pagination = Category.query.paginate(page, per_page=5, error_out=False)
    categories = pagination.items
    return render_template('dandan_manage/categorylist.html', categories=categories, pagination=pagination)


@aboutadmin.route('/editcategory/', methods=['GET', 'POST'])
def editcategory():
    '''
    修改类别名
    '''
    if request.method == 'POST':
        oldcid = request.form.get('oldcid')  # 分类名称对应的id
        newcate = request.form.get('cat')  # 新的分类名称
        c = Category.query.get(oldcid)
        if newcate == '':
            flash('修改分类名称不能为空')
            return redirect(url_for('aboutadmin.categorylist'))
        elif newcate == c.name:
            flash('修改分类名称不能和旧名称一样')
        else:
            if Category.query.filter_by(name=newcate).first():
                flash('修改的分类名称已存在')
                return redirect(url_for('aboutadmin.categorylist'))
            else:
                c.name = newcate
                db.session.add(c)
                flash('分类名称修改成功')
        return redirect(url_for('aboutadmin.categorylist'))
    return redirect(url_for('aboutadmin.categorylist'))



@aboutadmin.route('/addcategory/', methods=['GET', 'POST'])
def addcategory():
    '''
    添加分类名称
    '''
    if request.method == 'POST':
        category = request.form.get('cat')
        if category == '':
            flash('添加的分类名称不能为空')
            return redirect(url_for('aboutadmin.categorylist'))
        elif Category.query.filter_by(name=category).first():
            flash('分类名称已存在')
            return redirect(url_for('aboutadmin.categorylist'))
        else:
            c = Category(name=category)
            db.session.add(c)
            flash('分类添加成功')
            return redirect(url_for('aboutadmin.categorylist'))
    return redirect(url_for('aboutadmin.categorylist'))



@aboutadmin.route('/showcategory/<int:cid>')
def showcategory(cid):
    '''
    删除/恢复分类
    '''
    c = Category.query.get(cid)
    c.is_delete = not c.is_delete

    flash('类别设置成功')
    return redirect(url_for('aboutadmin.categorylist'))


# *******************************************文章管理******************************************
@aboutadmin.route('/articlelist/')
def articlelist():
    '''
    文章显示
    '''
    # 读取分页信息
    page = request.args.get('page', 1, type=int)

    # 创建分页对象
    pagination = Article.query.order_by(Article.laststamp.desc()).paginate(page, per_page=5, error_out=False)
    articlelist = pagination.items

    return render_template('dandan_manage/table-font-list.html', articlelist=articlelist, pagination=pagination)



@aboutadmin.route('/showarticle/<int:aid>')
def showarticle(aid):
    '''
    文章设置展示/隐藏
    '''
    a = Article.query.get(aid)
    a.isshow = not a.isshow
    db.session.add(a)
    flash('文章设置成功')
    return redirect(url_for('aboutadmin.articlelist'))



@aboutadmin.route('/deletearticle/<int:aid>')
def deletearticle(aid):
    '''
    删除文章（逻辑删除）/恢复文章
    '''
    a = Article.query.get(aid)
    a.is_delete = not a.is_delete
    db.session.add(a)
    flash('文章设置成功')
    return redirect(url_for('aboutadmin.articlelist'))



@aboutadmin.route('/addarticle', methods=['GET', 'POST'])
def addarticle():
    '''
    添加文章
    '''
    if request.method == 'GET':
        categorylist = Category.query.all()
        return render_template('dandan_manage/addarticle.html', categorylist=categorylist)

    # 获取添加的文章信息(纯文本部分)
    # 文章标题
    title = request.form.get('title')
    # 文章简介
    describe = request.form.get('describe')
    # 文章分类
    category = Category.query.get(request.form.get('category'))
    # 文章标签
    tag = request.form.get('tag').split('，')  # 通过逗号切割
    # 文章是否显示
    if request.form.get('isshow') == 'on':
        isshow = True
    else:
        isshow = False
    # 文章正文文本
    content = request.form.get('user-intro')

    # 文章封面图片
    # 获取后缀
    suffix = os.path.splitext(request.files['coverlink'].filename)[-1]
    # 合成图片名
    filename = gen_rnd_filename() + suffix
    # 保存图片
    # piclink即是封面图片的名字
    coverlink = photos.save(request.files['coverlink'], name=filename)

    # 保存文章到数据库
    # 创建文章对象
    article = Article(title=title, summary=describe, content=content, coverlink=coverlink, isshow=isshow)

    # 标签处理（主要是判断是否已经存在）
    for i in range(len(tag)):
        temp = i  # 临时变量记录下标
        i = Tag.query.filter_by(name=tag[temp]).first()  # 判断标签是否已经存在
        if i:  # 如果标签已经存在
            article.tags.append(i)  # 文章-标签 关联
        else:
            i = Tag(name=tag[temp])  # 如果标签不存在，则创建对象
            article.tags.append(i)  # 文章-标签 关联
    category.articles.append(article)  # 文章-类别 关联
    db.session.add(article)  # 添加进会话

    flash('文章添加成功！')
    return redirect(url_for('aboutadmin.addarticle'))  # 文章添加成功，返回添加页面，继续添加下一篇文章



@aboutadmin.route('/ckupload/', methods=['POST'])
def ckupload():
    '''
    处理文章内容中使用富文本上传的图片
    '''
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(os.getcwd() + '\\app\static\\upload\dandan_manage', 'upload', rnd_name)
        # print('*************************')
        # print(filepath)
        # photos.save(filepath, name=filepath)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='upload/dandan_manage/%s/%s' % ('upload', rnd_name))
            # print('url*********' + url)
    else:
        error = 'post error'
    res = """

<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>

""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response



@aboutadmin.route('/editarticle/<int:aid>', methods=['GET', 'POST'])
def editarticle(aid):
    '''
    编辑（修改）文章
    '''
    article = Article.query.get(aid)
    # 如果是GET请求，根据文章id查询出数据，显示在页面
    if request.method == 'GET':
        categorylist = Category.query.all()

        # 查询文章对应的所有标签，并用逗号连接显示
        acategorystr = ''
        for c in article.tags.all():
            acategorystr += ('，' + c.name)

        acategorystr = acategorystr[1:]  # 去掉第一个多余的逗号
        return render_template('dandan_manage/editarticle.html', article=article, categorylist=categorylist, acategorystr=acategorystr)
    # 如果是POST请求，则接收数据并保存到数据库
    # 文章标题
    title = request.form.get('title')
    # 文章简介
    describe = request.form.get('describe')
    # 文章分类
    category = Category.query.get(request.form.get('category'))
    # 文章标签
    tag = request.form.get('tag').split('，')  # 通过逗号切割
    # 文章是否显示
    if request.form.get('isshow') == 'on':
        isshow = True
    else:
        isshow = False
    # 文章正文文本
    content = request.form.get('user-intro')


    # 文章封面图片
    # 获取后缀
    # print('*****************************')
    # if type(request.files['coverlink']) == 'NoneType':
    #     coverlink = article.coverlink
    # else:
    suffix = os.path.splitext(request.files['coverlink'].filename)[-1]
    # 合成图片名
    filename = gen_rnd_filename() + suffix
    # 保存图片
    # piclink即是封面图片的名字
    coverlink = photos.save(request.files['coverlink'], name=filename)

    # 保存文章到数据库
    # 修改文章对象
    article.title = title
    article.summary = describe
    article.content = content
    article.coverlink = coverlink
    article.isshow = isshow
    article.laststamp = datetime.utcnow()

    # 标签处理（主要是判断是否已经存在）
    taghas = article.tags.all()  # 本篇文章所有的标签
    for one in taghas:
        if one.name in tag:  # 如果新建的标签已经属于本篇文章，则从标签列表中移除
            tag.remove(one.name)
        else:  # 否则直接pass
            pass

    for i in range(len(tag)):
        temp = i  # 临时变量记录下标
        i = Tag.query.filter_by(name=tag[temp]).first()  # 判断标签是否有已经存在
        if i:  # 如果标签已经存在
            for at in article.tags.all():  # 判断是否已属于这个标签
                if at.name == i.name:  # 如果属于，则什么都不做
                    pass
                else:  # 如果标签存在，且文章不属于这个标签，则添加 文章-标签 关联
                    article.tags.append(i)
        else:
            i = Tag(name=tag[temp])  # 如果标签不存在，则创建对象
            article.tags.append(i)  # 添加 文章-标签 关联

    category.articles.append(article)  # 添加 文章-类别 关联
    db.session.add(article)  # 添加进会话

    flash('文章修改成功')
    return redirect(url_for('aboutadmin.articlelist'))  # 文章修改成功，返回文章列表页面



# *******************************************图片管理******************************************
@aboutadmin.route('/imagelist/')
def imagelist():
    '''
    图片显示
    '''
    # 查询类别默认是0，即全部显示
    categoryid = request.args.get('cid', '0')

    # 查询所有分类列表，返回给页面select下拉框
    categorylist = Category.query.all()
    # print(categoryid)

    # 读取分页信息
    page = request.args.get('page', 1, type=int)

    if categoryid == '0':
        pagination = Picture.query.filter_by(isdelete=False).order_by(Picture.timestamp.desc()).paginate(page, per_page=6, error_out=False)
    else:
        pagination = Picture.query.filter_by(category_id=categoryid, isdelete=False).order_by(Picture.timestamp.desc()).paginate(page, per_page=6, error_out=False)

    picturelist = pagination.items

    return render_template('dandan_manage/table-images-list.html', picturelist=picturelist, categorylist=categorylist, pagination=pagination)



@aboutadmin.route('/uploadpic/', methods=['GET', 'POST'])
def uploadpic():
    '''
    上传图片
    '''
    categorylist = Category.query.all()

    if request.method == 'POST' and 'photo' in request.files:
        # 获取后缀
        suffix = os.path.splitext(request.files['photo'].filename)[-1]
        # 合成图片名
        filename = gen_rnd_filename() + suffix
        # 保存图片
        piclink = photos.save(request.files['photo'], name=filename)

        # # 生成缩略图
        # pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        # img = Image.open(pathname)
        # img.thumbnail((512, 512))
        # img.save(pathname)


        # print(piclink)
        # print(filename)


        # 获取图片标题
        name = request.form.get('name')
        # 获取图片分类
        category = request.form.get('category')
        # 获取图片描述
        describe = request.form.get('describe')

        # 判断图片分类是否已经存在，如果不存在则进行添加
        # if category
        # 插入数据库
        if describe:
            pic = Picture(picname=name, piclink='upload/' + piclink, category_id=category, describe=describe)
        else:
            pic = Picture(picname=name, piclink='upload/' + piclink, category_id=category)
        db.session.add(pic)

        flash('图片上传成功')
        return redirect(url_for('aboutadmin.uploadpic'))
    return render_template('dandan_manage/form-line.html', categorylist=categorylist)



@aboutadmin.route('/deletepic/<int:picid>')
def deletepic(picid):
    '''
    删除图片
    '''
    pic = Picture.query.get(picid)
    pic.isdelete = True
    db.session.add(pic)
    flash('照片删除成功！')
    return redirect(url_for('aboutadmin.imagelist'))



@aboutadmin.route('/showpic/<int:picid>')
def showpic(picid):
    '''
    图片设置在前端展示/隐藏
    '''
    pic = Picture.query.get(picid)
    pic.isshow = not pic.isshow
    db.session.add(pic)
    flash('图片设置成功')
    return redirect(url_for('aboutadmin.imagelist'))



# *******************************************邮件管理******************************************
@aboutadmin.route('/emaillist/')
def emaillist():
    return render_template('dandan_manage/form-news-list.html')



# *******************************************登陆管理******************************************
@aboutadmin.route('/login/')
def login():
    return render_template('dandan_manage/login.html')



# **********************************************测试******************************************
@aboutadmin.route('/test/')
def test():
    '''
    测试
    '''
    return 'ok'



@aboutadmin.route('/admingeneral/')
def admingeneral():
    '''
    测试base页面
    '''
    return render_template('dandan_manage/base_admin.html')
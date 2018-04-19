from django.db import models

# # Create your models here.
class User(models.Model):
    '''
    用户
    '''
    nickname = models.CharField('昵称', max_length=32, unique=True)
    email = models.CharField('邮箱', max_length=64, unique=True)
    password = models.CharField('密码', max_length=256)
    head_pic = models.ImageField('头像', max_length=128)
    is_admin = models.BooleanField('管理员', default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.nickname

    @classmethod
    def create_user(cls, nickame, email, password, is_admin, head_pic):
        u = cls(nickname=nickame, email=email, password=password, is_admin=is_admin, head_pic=head_pic)
        return u


class Tag(models.Model):
    '''
    标签
    '''
    tag = models.CharField('标签', max_length=32)

    class Meta:
        db_table = 'tags'

    def __str__(self):
        return self.tag



class Article(models.Model):
    '''
    文章
    '''
    title = models.CharField('标题', max_length=64)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)
    content = models.TextField('内容')
    click_count = models.IntegerField('点击量', default=0)

    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='作者')
    # comment = models.ForeignKey(Comment, verbose_name='评论', null=True, blank=True)

    tag = models.ManyToManyField(Tag, verbose_name='标签')
    like = models.ManyToManyField(User, verbose_name='点赞/喜欢', related_name='like')
    recent_view = models.ManyToManyField(User, verbose_name='最近浏览过的人', related_name='recent_view')


    class Meta:
        db_table = 'articles'

    def __str__(self):
        return self.title



class Comment(models.Model):
    '''
    评论
    '''
    comment = models.TextField('评论内容')
    identi = models.CharField('评论者', max_length=32)  # nickname or guest
    create_time = models.DateTimeField('评论时间', auto_now_add=True)

    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING, verbose_name='文章')

    class Meta:
        db_table = 'comments'

    def __str__(self):
        return self.identi



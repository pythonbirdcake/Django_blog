from django.shortcuts import render
from django.views.generic import TemplateView

from . import models
from .models import Article, Category
import math
import markdown


# Create your views here.

class IndexView(TemplateView):
    template_name = "new_index.html"

    def get(self, request, *args, **kwargs):
        article_list = Article.objects.order_by("-create_time")
        for article in article_list:
            article.pub_data = article.create_time.strftime("%m月%d日").replace("-", "月")
            article.length = len(article.text)
            article.read_time = math.ceil(len(article.text) // 180) + 1 if article.length else 0
            # 外键可以通过一下方式获取
            article.categories = article.category_set.values()
            article.tags = article.tag_set.values()
            # cate_list = Category.objects.filter(article_id=article.id)
        context = {
            "article_list": article_list
        }
        return self.render_to_response(context)


class DetailView(TemplateView):
    template_name = "new_detail.html"

    def get(self, request, *args, **kwargs):
        article = Article.objects.get(url=request.path)
        content = ""
        for line in article.text.split("\n"):
            content += line.strip("  ") if "```" in line else line
            line += "\n"
        article.content = markdown.markdown(content, extensions=[
            'markdown.extensions.extra',  # 转换标题，字体等。
            'markdown.extensions.codehilite',  # 添加高亮功能
            'markdown.extensions.toc',  # 表单渲染为html，document等类型
        ])
        article.length = len(article.text)
        article.title = article.title
        article.pub_data = article.create_time.strftime("%m月%d日").replace("-", "月")
        article.read_time = math.ceil(len(article.text) // 180) + 1 if article.length else 0,
        row_query_set = models.Article.objects.raw(
            f"select * from article where id < {article.id} order by id desc limit 1;")
        row_query_set_p = models.Article.objects.raw(
            f"select * from article where id > {article.id} order by id desc limit 1;")
        # sql查询只会返回一个对象，当row_query_set[0]取值时底层才会执行sql查询
        try:
            row_query_set = row_query_set[0]
            context = {
                "article": article,
                "row_query_set": row_query_set,
            }
        except IndexError:
            context = {
                "article": article,
            }
        try:
            row_query_set_p = row_query_set_p[0]
            context["row_query_set_p"] = row_query_set_p
        except IndexError:
            pass

        return self.render_to_response(context)


class ArchiveIndex(TemplateView):
    template_name = 'new_detail.html'
    def get(self, request, *args, **kwargs):
        """
        archive_list = {"2018":{"year":2018,"article_list":[]}}
        """
        article_list = Article.objects.all()  # 尽量避免扫表

        archive_dict: dict = {}
        for article in article_list:
            year = article.create_time.strftime("%Y")
            # setdefault()
            # 如果当前字典没有目标key，则给定默认值
            # 如果当前字典有目标key，则无变化
            archive_dict.setdefault(year, {"year": year, "article_list": []})
            archive_dict[year]['article_list'].append(article)

            context = {
                "archive_list": archive_dict.values(),
                "article_count": len(article_list),
            }
            return self.render_to_response(context)

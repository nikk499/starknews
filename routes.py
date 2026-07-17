from datetime import datetime
from flask import render_template, request, redirect
from models import User, Article, Like
from ext import db
from flask_login import current_user, login_user, logout_user, login_required


def index():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template("index.html", title="StarkNews - მთავარი", articles=articles)


def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect("/")
            return render_template("login.html", title="შესვლა", message="პაროლი არასწორია")
        return render_template("login.html", title="შესვლა", message="ამ ელფოსტით მომხმარებელი ვერ მოიძებნა")
    return render_template("login.html", title="შესვლა")


def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        name = request.form["name"]
        surname = request.form["lastname"]
        img_url = request.form["img_url"]

        if not email or not password or not username or not name or not surname:
            return render_template("register.html", title="რეგისტრაცია", message="გთხოვთ შეავსოთ ყველა სავალდებულო ველი")

        if User.query.filter_by(email=email).first():
            return render_template("register.html", title="რეგისტრაცია", message="ეს ელფოსტა უკვე გამოყენებულია")
        if User.query.filter_by(username=username).first():
            return render_template("register.html", title="რეგისტრაცია", message="ეს იუზერნეიმი უკვე დაკავებულია")

        user = User(
            username=username, password=password, name=name,
            surname=surname, email=email, profile_url=img_url
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html", title="რეგისტრაცია")


@login_required
def signout():
    logout_user()
    return redirect("/")


@login_required
def add_news():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        img_url = request.form["img_url"]

        if not title or not content:
            return render_template("add_news.html", title="სიახლის დამატება", message="სათაური და ტექსტი სავალდებულოა")

        article = Article(
            title=title,
            content=content,
            img_url=img_url,
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            author_id=current_user.id
        )
        db.session.add(article)
        db.session.commit()
        return redirect("/")
    return render_template("add_news.html", title="სიახლის დამატება")


def news_detail(article_id):
    article = Article.query.get(article_id)
    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(user_id=current_user.id, article_id=article_id).first() is not None
    return render_template("news_detail.html", title=article.title if article else "სიახლე", article=article, liked=liked)


@login_required
def like_article(article_id):
    existing = Like.query.filter_by(user_id=current_user.id, article_id=article_id).first()
    if existing:
        db.session.delete(existing)
    else:
        like = Like(user_id=current_user.id, article_id=article_id)
        db.session.add(like)
    db.session.commit()
    return redirect(f"/news/{article_id}")


@login_required
def my_news():
    articles = Article.query.filter_by(author_id=current_user.id).order_by(Article.id.desc()).all()
    return render_template("my_news.html", title="ჩემი სიახლეები", articles=articles)


@login_required
def delete_news(article_id):
    article = Article.query.get(article_id)
    if article and article.author_id == current_user.id:
        db.session.delete(article)
        db.session.commit()
    return redirect("/mynews")


@login_required
def edit_news(article_id):
    article = Article.query.get(article_id)
    if not article or article.author_id != current_user.id:
        return redirect("/")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        img_url = request.form["img_url"]
        if not title or not content:
            return render_template("edit_news.html", title="სიახლის რედაქტირება", article=article, message="სათაური და ტექსტი სავალდებულოა")
        article.title = title
        article.content = content
        article.img_url = img_url
        db.session.commit()
        return redirect(f"/news/{article_id}")
    return render_template("edit_news.html", title="სიახლის რედაქტირება", article=article)

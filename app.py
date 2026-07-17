from flask import Flask
from models import *
from ext import login_manager, db
from routes import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///StarkNewsDB.db"
app.config["SECRET_KEY"] = "starknews-secret-key"

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    db.create_all()

app.add_url_rule("/", "index", index)
app.add_url_rule("/login", "login", login, methods=["GET", "POST"])
app.add_url_rule("/register", "register", register, methods=["GET", "POST"])
app.add_url_rule("/logout", "logout", signout)
app.add_url_rule("/add_news", "add_news", add_news, methods=["GET", "POST"])
app.add_url_rule("/news/<int:article_id>", "news_detail", news_detail)
app.add_url_rule("/like/<int:article_id>", "like_article", like_article)
app.add_url_rule("/mynews", "my_news", my_news)
app.add_url_rule("/delete_news/<int:article_id>", "delete_news", delete_news)
app.add_url_rule("/edit_news/<int:article_id>", "edit_news", edit_news, methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

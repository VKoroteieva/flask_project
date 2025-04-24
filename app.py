from flask import Flask
from db import create_app, db
from models import Author, Book

app = create_app()

# Ініціалізація бази даних під час запуску додатку
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return 'Головна сторінка'


@app.route('/create')
def create_data():
    author = Author(name="Іван Франко")
    db.session.add(author)
    db.session.commit()

    book1 = Book(title="Захар Беркут", author=author)
    book2 = Book(title="Каменярі", author=author)
    db.session.add_all([book1, book2])
    db.session.commit()

    return "Автор і книги створені!"


if name == '__main__':
    app.run(debug=True)
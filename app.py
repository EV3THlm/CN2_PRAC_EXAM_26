import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

template_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'templates')
)

print(">>> RUTA CALCULADA DE TEMPLATES:", template_dir)
print(">>> ¿EXISTE LA CARPETA?:", os.path.exists(template_dir))

if os.path.exists(template_dir):
    print(">>> ARCHIVOS DENTRO:", os.listdir(template_dir))


app = Flask(__name__, template_folder=template_dir)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crear instancia de SQLAlchemy
db = SQLAlchemy(app)


# ==========================================
# MODELO CATEGORÍA
# ==========================================

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )


# ==========================================
# MODELO POST
# ==========================================

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=True
    )

    category = db.relationship(
        'Category',
        backref=db.backref('posts', lazy=True)
    )


# ==========================================
# CREAR TABLAS
# ==========================================

with app.app_context():
    db.create_all()


# ==========================================
# RUTA PRINCIPAL - MOSTRAR POSTS
# ==========================================

@app.route('/')
def index():

    posts = Post.query.all()
    categories = Category.query.all()

    return render_template(
        'index.html',
        posts=posts,
        categories=categories
    )


# ==========================================
# CREAR POST
# ==========================================

@app.route('/post/new', methods=['GET', 'POST'])
def add_post():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')

        new_post = Post(
            title=title,
            content=content,
            category_id=category_id
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))

    categories = Category.query.all()

    return render_template(
        'create_post.html',
        categories=categories
    )


# ==========================================
# ACTUALIZAR POST
# ==========================================

@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):

    post = Post.query.get(id)

    if request.method == 'POST':

        post.title = request.form['title']
        post.category_id = request.form.get('category_id')
        post.content = request.form['content']

        db.session.commit()

        return redirect(url_for('index'))

    categories = Category.query.all()

    return render_template(
        'update_post.html',
        post=post,
        categories=categories
    )


# ==========================================
# ELIMINAR POST
# ==========================================

@app.route('/posts/delete/<int:id>')
def delete_post(id):

    post = Post.query.get(id)

    if post:
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for('index'))


# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)
"""Models for SPORKY app."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Saved(db.Model):
    """Saved recipes."""

    __tablename__ = 'saves' 

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    recipe_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )
    title = db.Column(
        db.Text,
    )

    used = db.Column(
        db.Boolean,
        nullable=False,
    )

    rating = db.Column(
        db.Integer,
        nullable=True,
        default=0,
    )        

    notes = db.Column(
        db.Text,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    @classmethod
    def add_like(cls, recipe_id, title, used, rating, notes, user_id):
        """Add a like to a recipe."""
        save = Saved(
            recipe_id=recipe_id,
            title=title,
            used=used,
            rating=rating,
            notes=notes,
            user_id=user_id,
        )

        db.session.add(save)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    saves = db.relationship(
        'Saved',
        backref='user',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def saved_recipes(self):
        """Return all recipes saved by this user."""
        return Saved.query.filter_by(user_id=self.id).all()

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()
        try:
            
            if user:
                is_auth = bcrypt.check_password_hash(user.password, password)
                if is_auth:
                    return user
        except:
            return False

class Meal(db.Model):
    """Creates a Mealplan."""

    __tablename__ = 'plan' 

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    meal_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )
    title = db.Column(
        db.Text,
    )
    # inset default value for day_of_week and meal_of_day
    day_of_week = db.Column(
        db.Text,
        default = '<day of week>',
    )

    meal_of_day = db.Column(
        db.Text,
        default = '<meal of day>',
    )        

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    @classmethod
    def add_meal(cls, meal_id, title, day_of_week, meal_of_day, user_id):
        """Add meal to plan."""
        save = Meal(
            meal_id=meal_id,
            title=title,
            day_of_week=day_of_week,
            meal_of_day=meal_of_day,
            user_id=user_id,
        )

        db.session.add(save)



class Ingredient(db.Model):
    """Creates a shopping list."""

    __tablename__ = 'ingredients' 

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    ingredient_id = db.Column(
        db.Integer,
        nullable=False,
    )

    name = db.Column(
        db.Text,
    )

    aisle = db.Column(
        db.Text,
    )   
    amount_metric = db.Column(
        db.Numeric,
    )  
    amount_us = db.Column(
        db.Numeric,
    ) 
    unit_metric = db.Column(
        db.Text,
    )  
    unit_us = db.Column(
        db.Text,
    )

    meal_id = db.Column(
        db.Integer,
        db.ForeignKey('plan.meal_id', ondelete='CASCADE'),
        nullable=False,
    )
    @classmethod
    def add_ingredient(cls, ingredient_id, name, aisle, amount_metric, amount_us, unit_metric, unit_us, meal_id):
        """Add ingredient to list."""
        save = Ingredient(
            ingredient_id=ingredient_id,
            name=name,
            aisle=aisle,
            amount_metric=amount_metric,
            amount_us=amount_us,
            unit_metric=unit_metric,
            unit_us=unit_us,
            meal_id=meal_id,
        )
        db.session.add(save)
    
    @classmethod
    def make_list(cls, meal_id):
        """Make a list of ingredients for a meal."""
        return Ingredient.query.filter_by(meal_id=meal_id).all()


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

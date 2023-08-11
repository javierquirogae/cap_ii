import os
import traceback
import datetime

from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import RegisterForm, LoginForm, Favorites, MealPlan
from models import db, connect_db, User, Saved, Meal, Ingredient

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

day_to_numeric = {
    '<day of week>' : 0,
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7
}

# meal to numeric
meal_to_numeric = {
    '<meal of day>': 0,
    'Breakfast': 1,
    'Lunch': 2,
    'Dinner': 3
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tghgifhb:aeMgA7oN93TEE6TQMNN8YvAtBpqH0Dr7@bubble.db.elephantsql.com/tghgifhb'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sporky' 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/login', methods=["GET"])
def login_form():
    """Login page."""

    form = LoginForm()
    return render_template('login.html', form=form)



@app.route('/login', methods=["POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    try:
        if User.authenticate(form.username.data, form.password.data):
            user = User.authenticate(form.username.data, form.password.data)
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials.", 'danger')
            return redirect("/")
    except ValueError:
        flash("Invalid credentials.", 'danger')
        return redirect("/")


@app.route('/logout', methods=['GET'])
def logout():
    """Handle logout of user."""
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    do_logout()
    flash(f"Goodbye, {user.username}!", "info")
    return redirect('/login')




@app.route("/")
def root():
    """Homepage."""
    if g.user:
        return render_template("index.html")
    else:
        return redirect("/login")



@app.route('/signup', methods=["GET"])
def signup_form():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()
    return render_template('signup.html', form=form)
    

@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()
    try:
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
        )
        db.session.commit()

    except IntegrityError:
        flash("Username already taken", 'danger')
        return render_template('signup.html', form=form)

    do_login(user)

    return redirect("/")


@app.route('/save_recipe/<int:recipe_id>/<string:title>',methods=["POST"] )
def save_recipe(recipe_id, title):

    saved_id_list = []
    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = Favorites()
    likes = (Saved
                .query
                .filter(Saved.user_id == user.id)
                .limit(100)
                .all())
    for like in likes:
        saved_id_list.append(like.recipe_id)
    if recipe_id in saved_id_list:
        flash("Recipe was already in favorites list !", 'danger')
        return redirect("/favorites")
    else:
        Saved.add_like(
            user_id=session[CURR_USER_KEY],
            recipe_id=recipe_id,
            title=title,
            used=form.used.data,
            rating=form.rating.data,
            notes=form.notes.data
            )
        db.session.commit()
        flash(title + " added to favorites", 'warning')

    return redirect("/favorites")



# /add_to_plan/${id}


@app.route('/add_to_plan/<int:meal_id>/<string:title>',methods=["POST"] )
def add_meal(meal_id, title):
    meal_id_list = []
    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = MealPlan()
    meals = (Meal
                .query
                .filter(Meal.user_id == user.id)
                .limit(100)
                .all())
    for meal in meals:
        meal_id_list.append(meal.meal_id)
    if meal_id in meal_id_list:
        flash(title + " was already in meal plan !", 'danger')
        return redirect("/plan")
    else:
        Meal.add_meal(
            user_id=session[CURR_USER_KEY],
            meal_id=meal_id,
            title=title,
            day_of_week=form.day_of_week.data,
            meal_of_day=form.meal_of_day.data,
            )
        db.session.commit()
        flash(title + " added to plan", 'warning')

    return redirect("/plan")








@app.route('/add_ingredient', methods=["POST"])
def add_ingredient():
    ingredient = request.json
    try:
        if "name" not in ingredient or "meal_id" not in ingredient:
            raise ValueError("Ingredient name and meal ID are required.")

        saved_ingredients = Ingredient.query.filter(Ingredient.meal_id == ingredient["meal_id"]).limit(100).all()

        if any(saved_ingredient.name == ingredient["name"] for saved_ingredient in saved_ingredients):
            response = {"error": "Ingredient already in list"}
            return jsonify(response), 400

        new_ingredient = Ingredient(
            ingredient_id=ingredient["ingredient_id"],
            name=ingredient["name"],
            aisle=ingredient["aisle"],
            amount_metric=0,
            amount_us=ingredient["amount_us"],
            unit_metric="",
            unit_us=ingredient["unit_us"],
            meal_id=ingredient["meal_id"]
        )
        db.session.add(new_ingredient)
        db.session.commit()

        response = {"message": "Ingredient added to list"}
        return jsonify(response), 201

    except ValueError as e:
        response = {"error": str(e)}
        return jsonify(response), 400

    except Exception as e:
        response = {"error": e}
        traceback.print_exception()
        return jsonify(response), 500
  
    












@app.route('/favorites',methods=["GET"] )
def show_favorites_list():
    count = 0
    if g.user:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        likes = (Saved
                .query
                .filter(Saved.user_id == user.id)
                .limit(100)
                .all())
        # sort by rating
        likes.sort(key=lambda x: x.rating, reverse=True)
        count = len(likes)
        return render_template('favorites.html', user=user, likes=likes, count=count)
    else:
        return redirect("/login")
    

@app.route('/plan',methods=["GET"] )
def show_meal_plan():
    count = 0
    if g.user:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        meals = (Meal
                .query
                .filter(Meal.user_id == user.id)
                .limit(100)
                .all())
        # sort by meal of day
        meals.sort(key=lambda x: meal_to_numeric[x.meal_of_day])
        # sort by day of week
        # saves.sort(key=lambda x: day_to_numeric[x.day_of_week])
        meals.sort(key=lambda x: day_to_numeric[x.day_of_week])
        count = len(meals)
        return render_template('plan.html', user=user, meals=meals, count=count)
    else:
        return redirect("/login")
    




@app.route('/shopping_list',methods=["GET"] )
def show_shopping_list():
    count = 0
    if g.user:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        meal_plan = (Meal
                .query
                .filter(Meal.user_id == user.id)
                .limit(100)
                .all())
        shopping_list = (Ingredient
                         .query
                         .filter(Ingredient.meal_id.in_([meal.meal_id for meal in meal_plan]))
                            .limit(500)
                            .all())
        count = len(shopping_list)
        # sort shopping list by name
        shopping_list.sort(key=lambda x: x.name)
        aisles = set()
        for item in shopping_list:
            aisles.add(item.aisle)
        aisle_lists = []
        for aisle in aisles:
            aisle_lists.append([item for item in shopping_list if item.aisle == aisle])
            # sort lists by length. Longest at the top
            aisle_lists.sort(key=lambda x: len(x), reverse=True)

        return render_template('shopping_list.html', user=user, aisle_lists=aisle_lists, count=count)
    else:
        return redirect("/login")


# get_meal json route
@app.route('/get_meal_ingredients/<int:meal_id>',methods=["GET"] )
def get_meal(meal_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    meal = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user.id).first()
    meal_ingredients = (Ingredient
                            .query
                            .filter(Ingredient.meal_id == meal_id)
                            .limit(100)
                            .all())
    length = len(meal_ingredients)
    
    response = {"length": length}
    return jsonify(response)
   
   


    

@app.route('/saved_recipe_detail/<int:recipe_id>',methods=["GET"])
def show_recipe_detail(recipe_id):
    if g.user:
        return render_template('detail.html', recipe_id=recipe_id)
    else:
        return redirect("/login")


@app.route('/delete_recipe/<int:recipe_id>',methods=["POST"] )
def delete_recipe(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    title = Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).first().title
    Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).delete()
    db.session.commit()
    flash(title + " removed from favorites", 'warning')
    return redirect("/favorites")



@app.route('/delete_meal/<int:meal_id>',methods=["POST"] )
def delete_meal(meal_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    title = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user.id).first().title
    Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user.id).delete()
    db.session.commit()
    flash(title + " removed from plan", 'warning')
    return redirect("/plan")




@app.route('/edit_recipe/<int:recipe_id>',methods=["get"] )
def edit_recipe_form(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    saved_recipe = Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).first()
    form = Favorites(obj=saved_recipe)
    
    return render_template('edit.html', form=form, saved_recipe=saved_recipe)



@app.route('/edit_meal/<int:meal_id>',methods=["get"] )
def whic_meal_form(meal_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    saved_meal = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user.id).first()
    form = MealPlan(obj=saved_meal)
    
    return render_template('edit.html', form=form, saved_recipe=saved_meal)





@app.route('/edit_recipe/<int:recipe_id>',methods=["POST"] )
def edit_recipe(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    recipe = Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).first()
    form = Favorites(obj=recipe)
    recipe.used = form.used.data
    recipe.rating = form.rating.data
    recipe.notes = form.notes.data

    db.session.commit()
    flash(recipe.title + " edited", 'info')
    return redirect("/favorites")




@app.route('/edit_meal/<int:meal_id>',methods=["POST"] )
def edit_meal(meal_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    meal = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user.id).first()
    form = MealPlan(obj=meal)
    meal.day_of_week = form.day_of_week.data
    meal.meal_of_day = form.meal_of_day.data  

    db.session.commit()
    flash(meal.title + " edited", 'info')
    return redirect("/plan")
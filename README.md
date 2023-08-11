# Sporky App

Sporky is a meal planning and recipe management application built using Flask. It allows users to create an account, log in, manage their favorite recipes, plan meals, and generate shopping lists based on their selected meals. The app provides a user-friendly interface for handling these tasks efficiently.

## Features

- **User Authentication**: Users can create accounts and log in to access their personalized features.

- **Favorite Recipes**: Users can browse and save their favorite recipes. Saved recipes can be viewed, edited, and removed from the favorites list.

- **Meal Planning**: Users can plan their meals by adding specific recipes to their meal plan. They can select the day of the week and the meal (breakfast, lunch, or dinner) for each recipe.

- **Shopping List**: The app generates a shopping list based on the ingredients needed for the selected meals in the meal plan. Ingredients are grouped by aisles for easy shopping.

## Setup

1. Clone the repository: `git clone <repository-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a PostgreSQL database named "sporky" or update the `app.config['SQLALCHEMY_DATABASE_URI']` to point to your database.
4. Set up environment variables for Flask: `export FLASK_APP=app.py` (Unix/Linux) or `set FLASK_APP=app.py` (Windows)
5. Run the app: `flask run`

## Usage

1. Access the app in your web browser by navigating to `http://localhost:5000`.
2. Sign up for a new account or log in if you already have one.
3. Explore and save your favorite recipes.
4. Plan your meals by adding recipes to your meal plan.
5. Generate a shopping list based on the meal plan.

## Contributing

Contributions are welcome! If you find any issues or want to add new features, feel free to submit a pull request.

## Acknowledgments

- The app is built using Flask, SQLAlchemy, and other open-source libraries.
- Special thanks to the developers who contributed to the libraries used in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

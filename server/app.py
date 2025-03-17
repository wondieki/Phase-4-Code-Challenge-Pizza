#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)  # Initialize Flask-RESTful API


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class RestaurantsResource(Resource):
    def get(self):
        """GET /restaurants - Returns a list of all restaurants"""
        restaurants = Restaurant.query.all()
        return make_response(jsonify([restaurant.to_dict() for restaurant in restaurants]), 200)


class RestaurantDetailResource(Resource):
    def get(self, id):
        """GET /restaurants/<id> - Returns a single restaurant and its pizzas"""
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(jsonify(restaurant.to_dict(rules=('-restaurant_pizzas.restaurant',))), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        """DELETE /restaurants/<id> - Deletes a restaurant and its associated restaurant_pizzas"""
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


class PizzasResource(Resource):
    def get(self):
        """GET /pizzas - Returns a list of all pizzas"""
        pizzas = Pizza.query.all()
        return make_response(jsonify([pizza.to_dict() for pizza in pizzas]), 200)


class RestaurantPizzasResource(Resource):
    def post(self):
        """POST /restaurant_pizzas - Creates a new RestaurantPizza"""
        data = request.get_json()

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                restaurant_id=data["restaurant_id"],
                pizza_id=data["pizza_id"]
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)

        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


# Register routes
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantDetailResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
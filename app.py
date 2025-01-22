from flask import Flask, request, jsonify
from genetic_algorithm import GeneticAlgorithm
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/submit", methods=["POST"])
def process_data():
    data = request.json
    algo_data = data["algoData"]
    route_data = data["routeData"]

    # Initialize and run the genetic algorithm
    ga = GeneticAlgorithm(algo_data, route_data)
    best_routes = ga.run()
    print(algo_data, route_data)
    response = []
    for route in best_routes:
        route_info = {
            "route": [
                {
                    "name": point["name"],
                    "lat": point["address"]["lat"],
                    "lng": point["address"]["lang"],
                }
                for point in route["route"]
            ],
            "fitness": route["fitness"],
        }
        response.append(route_info)
    for idx, route in enumerate(best_routes):
        route_names = [point["name"] for point in route["route"]]
        print(f"Route {idx+1}: {route_names} with Fitness: {route['fitness']}")

    return jsonify(response)


def generate_graph(routes):
    # Example data for graph generation
    fuel_consumption = [route["fuel_consumption"] for route in routes]
    fuel_cost = [route["fuel_cost"] for route in routes]
    travel_time = [route["travel_time"] for route in routes]

    plt.figure(figsize=(10, 5))
    plt.plot(range(len(routes)), fuel_consumption, label="Fuel Consumption")
    plt.plot(range(len(routes)), fuel_cost, label="Fuel Cost")
    plt.plot(range(len(routes)), travel_time, label="Travel Time")
    plt.legend()

    # Save the plot to a bytes object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Encode the plot to base64 string
    graph = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return graph


if __name__ == "__main__":
    app.run(debug=True, port=5501)

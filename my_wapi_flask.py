"""
https://pythonise.com/series/learning-flask/working-with-json-in-flask#returning-json
"""

from flask import jsonify, make_response


@app.route("/get_curve", methods=["POST"])
def json_example():

    if request.is_json:

        req = request.get_json()

        response_body = {
            "message": "JSON received!",
            "sender": req.get("name")
        }

        res = make_response(jsonify(response_body), 200)

        return res

    else:

        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run()

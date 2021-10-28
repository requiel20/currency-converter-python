from flask_restx import Namespace, Resource, fields


def create_namespace() -> Namespace:
    namespace = Namespace("meta", description="Meta operations")

    ping_response = namespace.model(
        "ping_response",
        {
            "status": fields.String(
                required=True, description='Always "Ok!"', enum=["Ok!"]
            )
        },
    )

    # noinspection PyUnusedLocal
    @namespace.route("/ping")
    class Ping(Resource):
        @namespace.doc("ping")
        @namespace.marshal_with(ping_response)
        def get(self):
            """Returns "Ok!\" """
            return {"status": "Ok!"}

    return namespace

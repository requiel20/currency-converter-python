from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest

from src.main.exceptions import CurrencyNotFoundException
from src.main.service.converter_service import ConverterInterface


def create_namespace(conv: ConverterInterface) -> Namespace:
    ns = Namespace("v1", description="v1 operations")

    convert_response = ns.model(
        "convert_response",
        {
            "original_value": fields.Float(
                required=True, description="The submitted value"
            ),
            "original_currency": fields.String(
                required=True, description="The submitted currency"
            ),
            "converted_value": fields.Float(
                required=True, description="The converted value"
            ),
            "converted_currency": fields.String(
                required=True, description="The converted currency"
            ),
        },
    )

    parser = ns.parser()
    parser.add_argument(
        "currency",
        type=str,
        required=True,
        help="Currency to convert from",
        location="json",
    )
    parser.add_argument(
        "value", type=float, required=True, help="Value to convert", location="json"
    )
    parser.add_argument(
        "target_currency",
        required=True,
        type=str,
        help="Currency to convert to",
        location="json",
    )

    # noinspection PyUnusedLocal
    @ns.route("/convert")
    class Convert(Resource):
        @ns.doc("convert")
        @ns.marshal_with(convert_response)
        @ns.expect(parser)
        def post(self):
            """Returns the converted amount"""
            args = parser.parse_args()
            try:
                converted = conv.convert(
                    currency=args["currency"],
                    value=args["value"],
                    target_currency=args["target_currency"],
                )
            except CurrencyNotFoundException:
                raise BadRequest()
            return {
                "original_value": args["value"],
                "original_currency": args["currency"].upper(),
                "converted_value": converted,
                "converted_currency": args["target_currency"].upper(),
            }

    return ns

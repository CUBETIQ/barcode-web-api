from io import BytesIO
from os import environ

import barcode
from barcode.writer import ImageWriter, SVGWriter
from flask import Flask, Response, request

app = Flask(__name__)


def get_formatter(text, barcode_type):
    if barcode_type is None:
        return barcode.get_barcode_class('code128')

    try:
        return barcode.get_barcode_class(barcode_type)
    except:
        return None


def get_output_format(output_format):
    if output_format == 'svg':
        return SVGWriter()
    return ImageWriter()


def get_output_format_mine_type(output_format):
    if output_format == 'svg':
        return 'image/svg+xml'
    return 'image/png'


def get_output_format_filename(output_format, barcode_type):
    if output_format == 'svg':
        return f'barcode_{barcode_type}.svg'
    return f'barcode_{barcode_type}.png'


@app.route('/', methods=['GET', 'POST'])
def index():
    text = request.args.get('text') or request.form.get('type')
    barcode_type = request.args.get('type') or request.form.get('type')
    output_format = request.args.get(
        'format') or request.form.get('format') or 'png'
    dl = request.args.get('dl') or request.form.get('dl') or '0'

    if text:
        barcode_format = get_formatter(text, barcode_type)
        if barcode_format is None:
            return Response(response={
                'error': f'Barcode type {barcode_type} is not supported'
            }, status=400)

        mine_type = get_output_format_mine_type(output_format)
        filename = get_output_format_filename(output_format, barcode_type)
        writer = get_output_format(output_format)

        try:
            render = barcode_format(text, writer=writer)
            output = BytesIO()
            render.write(output)

            content_disposition = 'inline'
            if dl == '1':
                content_disposition = 'attachment'

            return Response(output.getvalue(), mimetype=mine_type, headers={
                'Content-Disposition': f'{content_disposition}; filename={filename}'
            })
        except Exception as e:
            return Response(response={
                'error': str(e)
            }, status=400)

    return Response(response={
        'error': 'No text and type are provided'
    }, status=400)


@app.route('/types', methods=['GET'])
def get_barcode_format_list():
    return {
        'default_type': 'code128',
        'types': barcode.PROVIDED_BARCODES,
        'formats': ['png', 'svg'],
        'examples': [
            {
                'type': 'code128',
                'text': '123456789012',
                'format': 'png',
                'url': '/?text=123456789012&type=code128&format=png'
            },
            {
                'type': 'code128',
                'text': '123456789012',
                'format': 'svg',
                'url': '/?text=123456789012&type=code128&format=svg'
            },
            {
                'type': 'ean13',
                'text': '5901234123457',
                'format': 'png',
                'url': '/?text=5901234123457&type=ean13&format=png'
            },
            {
                'type': 'upc',
                'text': '123456789012',
                'format': 'png',
                'url': '/?text=123456789012&type=upc&format=png'
            }
        ]

    }


if __name__ == '__main__':
    app.run(host=environ.get('HOST', '0.0.0.0'),
            port=environ.get('PORT', 5000), debug=False)

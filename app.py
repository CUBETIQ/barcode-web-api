from io import BytesIO, StringIO
from os import environ

import barcode
import pyqrcode
from barcode.writer import ImageWriter, SVGWriter
from flask import Flask, Response, jsonify, make_response, request

QRCODE_SCALE_LIMIT = 100

# if __name__ == '__main__':
#     app.run(host=environ.get('HOST', '0.0.0.0'),
#             port=environ.get('PORT', 5000), debug=False)


def create_app():
    app = Flask(__name__)

    def get_formatter(text, barcode_type):
        if barcode_type is None:
            return barcode.get_barcode_class('code128')

        try:
            return barcode.get_barcode_class(barcode_type)
        except:
            return None

    def get_output_format_mine_type(output_format):
        if output_format == 'svg':
            return 'image/svg+xml'
        return 'image/png'

    def get_output_format_filename(output_format, code_type, prefix_file_name='barcode'):
        if output_format == 'svg':
            return f'{prefix_file_name}_{code_type}.svg'
        return f'{prefix_file_name}_{code_type}.png'

    def get_parse_qrcode_from_text(text, qrcode_type='text'):
        if qrcode_type == 'number':
            return int(text)

        return text

    @app.route('/', methods=['GET'])
    def index():
        return {
            "message": "Welcome to Barcode/QRCode Generator API",
            "links": {
                "barcode": "/barcode",
                "qrcode": "/qrcode",
            },
            "documentation": {
                "barcode": "/barcode/types",
                "qrcode": "/qrcode/types",
            }
        }

    @app.route('/barcode', methods=['GET', 'POST'])
    def barcode_route():
        text = request.args.get('text') or request.form.get('text')
        barcode_type = request.args.get(
            'type') or request.form.get('type') or 'code128'
        output_format = request.args.get(
            'format') or request.form.get('format') or 'png'
        dl = request.args.get('dl') or request.form.get('dl') or '0'

        if text:
            barcode_format = get_formatter(text, barcode_type)
            if barcode_format is None:
                return make_response(jsonify({
                    'error': f'Barcode type {barcode_type} is not supported'
                }), 400)

            try:
                mine_type = get_output_format_mine_type(output_format)
                filename = get_output_format_filename(
                    output_format, barcode_type)
                writer = None

                if output_format == 'svg':
                    writer = SVGWriter()
                elif output_format == 'png':
                    writer = ImageWriter()
                else:
                    writer = None

                if writer is None:
                    return make_response(jsonify({
                        'error': f'Output format {output_format} is not supported'
                    }), 400)

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
                print('BarCode render error', e)
                return make_response(jsonify({
                    'error': str(e) or 'BarCode render error'
                }), 400)

        return make_response(jsonify({
            'error': 'No text and type are provided'
        }), 400)

    @app.route('/qrcode', methods=['GET', 'POST'])
    def qrcode_route():
        text = request.args.get('text') or request.form.get('text')
        qrcode_type = request.args.get('type') or request.form.get('type')
        output_format = request.args.get(
            'format') or request.form.get('format') or 'png'
        dl = request.args.get('dl') or request.form.get('dl') or '0'
        scale = int(request.args.get('scale')
                    or request.form.get('scale') or '1')
        module_color = request.args.get(
            'color') or request.form.get('color') or '000'
        background = request.args.get(
            'background') or request.form.get('background') or None
        quiet_zone = int(request.args.get(
            'quiet_zone') or request.form.get('quiet_zone') or '1')
        encoding = request.args.get(
            'encoding') or request.form.get('encoding') or None

        if scale > QRCODE_SCALE_LIMIT:
            return make_response(jsonify({
                'error': 'QRCode scale is too large!'
            }), 400)

        if module_color.startswith('#') is False:
            module_color = f'#{module_color}'

        if text:
            try:
                mine_type = get_output_format_mine_type(output_format)
                filename = get_output_format_filename(
                    output_format, qrcode_type, prefix_file_name='qrcode')

                text = get_parse_qrcode_from_text(text, qrcode_type)
                render = pyqrcode.create(text, encoding=encoding)
                output = BytesIO()

                if output_format == 'svg':
                    render.svg(output, scale=scale, background=background,
                               module_color=module_color, title=filename, quiet_zone=quiet_zone)
                elif output_format == 'png':
                    render.png(output, scale=scale, background=background,
                               module_color=module_color, quiet_zone=quiet_zone)
                else:
                    return make_response(jsonify({
                        'error': f'Output format {output_format} is not supported'
                    }), 400)

                content_disposition = 'inline'
                if dl == '1':
                    content_disposition = 'attachment'

                return Response(output.getvalue(), mimetype=mine_type, headers={
                    'Content-Disposition': f'{content_disposition}; filename={filename}'
                })
            except Exception as e:
                print('QRCode render error', e)
                return make_response(jsonify({
                    'error': str(e) or 'QRCode render error'
                }), 400)

        return make_response(jsonify({
            'error': 'No text and type are provided'
        }), 400)

    @app.route('/barcode/types', methods=['GET'])
    def get_barcode_format_list():
        return {
            'default_type': 'code128',
            'default_format': 'png',
            'types': barcode.PROVIDED_BARCODES,
            'formats': ['png', 'svg'],
            'parameters': [
                {
                    'name': 'text',
                    'type': 'string',
                    'required': True,
                    'description': 'Text to encode',
                },
                {
                    'name': 'type',
                    'type': 'string',
                    'required': True,
                    'description': 'Barcode type',
                    'values': barcode.PROVIDED_BARCODES,
                },
                {
                    'name': 'format',
                    'type': 'string',
                    'description': 'Output format',
                    'values': ['png', 'svg'],
                }
            ],
            'examples': [
                {
                    'type': 'code128',
                    'text': '123456789012',
                    'format': 'png',
                    'url': '/barcode?text=123456789012&type=code128&format=png'
                },
                {
                    'type': 'code128',
                    'text': '123456789012',
                    'format': 'svg',
                    'url': '/barcode?text=123456789012&type=code128&format=svg'
                },
                {
                    'type': 'ean13',
                    'text': '5901234123457',
                    'format': 'png',
                    'url': '/barcode?text=5901234123457&type=ean13&format=png'
                },
                {
                    'type': 'upc',
                    'text': '123456789012',
                    'format': 'png',
                    'url': '/barcode?text=123456789012&type=upc&format=png'
                }
            ]
        }

    @app.route('/qrcode/types', methods=['GET'])
    def get_qrcode_format_list():
        return {
            'default_type': 'text',
            'default_format': 'png',
            'types': ['text', 'number'],
            'formats': ['png', 'svg'],
            'parameters': [
                {
                    'name': 'text',
                    'type': 'string',
                    'description': 'Text to encode',
                    'required': True
                },
                {
                    'name': 'type',
                    'type': 'string',
                    'description': 'Type of text to encode',
                    'values': ['text', 'number']
                },
                {
                    'name': 'format',
                    'type': 'string',
                    'description': 'Output format',
                    'values': ['png', 'svg']
                },
                {
                    'name': 'scale',
                    'type': 'integer',
                    'description': 'Scale of QRCode',
                    'default': 1
                },
                {
                    'name': 'color',
                    'type': 'string',
                    'description': 'Color of QRCode',
                    'default': '000'
                },
                {
                    'name': 'background',
                    'type': 'string',
                    'description': 'Background color of QRCode',
                    'default': None
                },
                {
                    'name': 'quiet_zone',
                    'type': 'integer',
                    'description': 'Quiet zone of QRCode',
                    'default': 1
                },
                {
                    'name': 'encoding',
                    'type': 'string',
                    'description': 'Encoding of QRCode',
                    'default': None
                },
                {
                    'name': 'dl',
                    'type': 'integer',
                    'description': 'Download QRCode',
                    'default': 0
                }
            ],
            'examples': [
                {
                    'type': 'text',
                    'text': 'Hello World',
                    'format': 'png',
                    'scale': '10',
                    'url': '/qrcode?text=Hello%20World&type=text&format=png&scale=10'
                },
                {
                    'type': 'text',
                    'text': 'Hello World',
                    'format': 'svg',
                    'scale': '10',
                    'url': '/qrcode?text=Hello%20World&type=text&format=svg&scale=10'
                },
                {
                    'type': 'number',
                    'text': '1234567890',
                    'format': 'png',
                    'scale': '10',
                    'url': '/qrcode?text=1234567890&type=text&format=png&scale=10'
                },
                {
                    'type': 'number',
                    'text': '1234567890',
                    'format': 'svg',
                    'scale': '10',
                    'url': '/qrcode?text=1234567890&type=text&format=svg&scale=10'
                }
            ]
        }

    return app

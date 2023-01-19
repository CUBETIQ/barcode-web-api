from io import BytesIO

import barcode
import pyqrcode
from barcode.writer import ImageWriter, SVGWriter
from flask import Flask, Response, jsonify, make_response, request

QRCODE_SCALE_LIMIT = 100

# if __name__ == '__main__':
#     app.run(host=environ.get('HOST', '0.0.0.0'),
#             port=environ.get('PORT', 5000), debug=False)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


BARCODE_SUPPORT_IMAGE_FORMAT_MAP = {
    'png': 'image/png',
    'jpeg': 'image/jpeg',
    'bmp': 'image/bmp',
    'svg': 'image/svg+xml',
    'gif': 'image/gif',
    'tiff': 'image/tiff',
}

BARCODE_SUPPORT_IMAGE_MODE_MAP = {
    'png': 'RGBA',
    'jpeg': 'RGB',
    'bmp': 'RGB',
    'svg': 'RGBA',
    'gif': 'RGBA',
    'tiff': 'RGB',
}


def create_app():
    app = Flask(__name__)

    def get_formatter(text, barcode_type):
        if barcode_type is None:
            return barcode.get_barcode_class('code128')

        try:
            return barcode.get_barcode_class(barcode_type)
        except:
            return None

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
        compress = str2bool(request.args.get('compress')
                            or request.form.get('compress') or '1')
        text_distance = float(request.args.get(
            'text_distance') or request.form.get('text_distance') or '5.0')
        font_size = float(request.args.get(
            'font_size') or request.form.get('font_size') or '10.0')
        module_width = float(request.args.get(
            'width') or request.form.get('width') or '0.2')
        module_height = float(request.args.get(
            'height') or request.form.get('height') or '15.0')
        background = request.args.get(
            'background') or request.form.get('background') or 'white'
        foreground = request.args.get(
            'foreground') or request.form.get('foreground') or 'black'
        quiet_zone = float(request.args.get(
            'quiet_zone') or request.form.get('quiet_zone') or '6.5')
        image_mode = request.args.get(
            'image_mode') or request.form.get('image_mode') or None

        if text:
            if image_mode is None:
                try:
                    image_mode = BARCODE_SUPPORT_IMAGE_MODE_MAP[output_format.lower(
                    )]
                except:
                    return make_response(jsonify({
                        'error': f'Image format {output_format} is not supported'
                    }), 400)

            if image_mode not in BARCODE_SUPPORT_IMAGE_MODE_MAP.values():
                return make_response(jsonify({
                    'error': f'Image mode {image_mode} is not supported'
                }), 400)

            barcode_format = get_formatter(text, barcode_type)
            if barcode_format is None:
                return make_response(jsonify({
                    'error': f'Barcode type {barcode_type} is not supported'
                }), 400)

            try:
                writer = None

                if output_format == 'svg':
                    writer = SVGWriter()
                elif output_format in BARCODE_SUPPORT_IMAGE_FORMAT_MAP:
                    writer = ImageWriter(output_format.upper(), mode=image_mode)
                else:
                    writer = None

                if writer is None:
                    return make_response(jsonify({
                        'error': f'Output format {output_format} is not supported'
                    }), 400)

                options = dict(
                    compress=compress,
                    module_width=module_width,
                    module_height=module_height,
                    text_distance=text_distance,
                    font_size=font_size,
                    background=background,
                    foreground=foreground,
                    quiet_zone=quiet_zone,
                )
                mine_type = BARCODE_SUPPORT_IMAGE_FORMAT_MAP[output_format]
                filename = get_output_format_filename(
                    output_format, barcode_type)
                render = barcode_format(text, writer=writer)
                output = BytesIO()
                render.write(output, options=options)

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
                if output_format not in BARCODE_SUPPORT_IMAGE_FORMAT_MAP:
                    return make_response(jsonify({
                        'error': f'Output format {output_format} is not supported'
                    }), 400)

                mine_type = BARCODE_SUPPORT_IMAGE_FORMAT_MAP[output_format]
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
                },
                {
                    'name': 'dl',
                    'type': 'string',
                    'description': 'Download barcode',
                    'values': ['0', '1'],
                },
                {
                    'name': 'width',
                    'type': 'float',
                    'description': 'Width of the barcode',
                },
                {
                    'name': 'height',
                    'type': 'float',
                    'description': 'Height of the barcode',
                },
                {
                    'name': 'background',
                    'type': 'string',
                    'description': 'Background color (Color Name)',
                    'examples': ['red', 'green', 'blue', 'black', 'white']
                },
                {
                    'name': 'foreground',
                    'type': 'string',
                    'description': 'Foreground color (Color Name)',
                    'examples': ['red', 'green', 'blue', 'black', 'white']
                },
                {
                    'name': 'quiet_zone',
                    'type': 'int',
                    'description': 'Quiet zone',
                },
                {
                    'name': 'text_distance',
                    'type': 'float',
                    'description': 'Distance between barcode and text',
                },
                {
                    'name': 'font_size',
                    'type': 'float',
                    'description': 'Font size',
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

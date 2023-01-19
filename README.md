# Generate Barcode Web API

Go to [Web API](https://barcode-web-api.heroku.ctdn.dev)

-   Flask
-   PyBarcode (`python-barcode`)
-   PyQRCode (`pyqrcode`)

### Features

-   [x] Barcode
-   [x] QRCode

### TODO

-   [x] Export to Image
-   [x] Export to SVG
-   [x] Barcode/QRCode Options

### Barcode Options

-   Support types (`type`)

```text
type=[code128 | code39 ean | ean13 | ean14 | ean8 | gs1 | gs1_128 | gtin | isbn | isbn10 | isbn13 | issn | itf | jan | pzn | upc | upca]
```

-   Support formats (`format`)

```text
format=[png | svg]
```

-   Support width and height (`width` and `height`)

```text
width=[0.1-100]
height=[0.1-100]
```

-   Support Font Size (`font_size`)

```text
font_size=[0.1-50]
```

-   Support Text Distance (`text_distance`)

```text
text_distance=[0.1-50]
```

-   Support backgrounds (`background`)

```text
background=[COLOR_NAME] (Example: red, green, blue, etc)
```

-   Support foregrounds (`foreground`)

```text
foreground=[COLOR_NAME] (Example: red, green, blue, etc)
```

-   Support Space Zone (`quiet_zone`)

```text
quiet_zone=[1-100]
```

-   Support downloadable (`dl`)

```text
dl=[1 / 0]
```

### Barcode - Usages (Test URL: https://barcode-web-api.heroku.ctdn.dev/barcode)

-   Barcode Types and Availables

```text
https://barcode-web-api.heroku.ctdn.dev/barcode/types
```

-   Generate Barcode from Text (GET/POST)

```text
https://barcode-web-api.heroku.ctdn.dev/barcode?text=1234-5678-9012&type=code128
```

-   Generate Barcode from Text with FORM (POST)

```sh
curl --location --request POST 'https://barcode-web-api.heroku.ctdn.dev/barcode' \
--form 'text="1234-5678-9012"' \
--form 'type="code128"'
```

### QRCode Options

-   Support types (`type`)

```text
type=[text | number]
```

-   Support formats (`format`)

```text
format=[png | svg]
```

-   Support scales (`scale`)

```text
scale=[1-100]
```

-   Support colors (`color`)

```text
color=[RGB] (Example: 000 | FFF | 000000 | FFFFFF | more)
```

-   Support backgrounds (`background`)

```text
background=[RGB] (Example: 000 | FFF | 000000 | FFFFFF | more)
```

-   Support Spae Zone (`quiet_zone`)

```text
quiet_zone=[1-100]
```

-   Support downloadable (`dl`)

```text
dl=[1 / 0]
```

### QRCode - Usages (Test URL: https://barcode-web-api.heroku.ctdn.dev/qrcode)

-   QRCode Types and Availables

```text
https://barcode-web-api.heroku.ctdn.dev/qrcode/types
```

-   Generate QRCode from Text (GET/POST)

```text
https://barcode-web-api.heroku.ctdn.dev/qrcode?text=1234-5678-9012&type=text&scale=10
```

-   Generate QRCode from Text with FORM (POST)

```sh
curl --location --request POST 'https://barcode-web-api.heroku.ctdn.dev/qrcode' \
--form 'text="1234-5678-9012"' \
--form 'type="text"' \
--form 'scale=10'
```

### Local Development

```shell
pip install -r requirements.txt
```

```shell
python3 -m flask run --reload
```

### Contributors

-   Sambo Chea <sombochea@cubetiqs.com>

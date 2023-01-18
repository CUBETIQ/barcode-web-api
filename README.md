# Generate Barcode Web API

-   Flask
-   Barcode

### TODO

-   [x] Export to Image
-   [x] Export to SVG
-   [x] Barcode Options

### Barcode Options

-   Support types (`type`)

```text
type=[code128 | code39 ean | ean13 | ean14 | ean8 | gs1 | gs1_128 | gtin | isbn | isbn10 | isbn13 | issn | itf | jan | pzn | upc | upca]
```

-   Support formats (`format`)

```text
format=[png | svg]
```

-   Support downloadable (`dl`)

```text
dl=[1 / 0]
```

### Usages (Test URL: https://barcode-web-api.heroku.ctdn.dev)

-   Barcode Types and Availables

```text
https://barcode-web-api.heroku.ctdn.dev/types
```

-   Generate Barcode from Text (GET/POST)

```text
https://barcode-web-api.heroku.ctdn.dev?text=1234-5678-9012&type=code128
```

-   Generate Barcode from Text with FORM (POST)

```sh
curl --location --request POST 'https://barcode-web-api.heroku.ctdn.dev' \
--form 'text="1234-5678-9012"' \
--form 'type="code128"'
```

### Contributors

-   Sambo Chea <sombochea@cubetiqs.com>

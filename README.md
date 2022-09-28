
### JS/CSS Bundle 
Bundles multiple css or js files into one to reduce worker load for development server (flask) or webserver (nginx) connections

### Usage

```python
from flask import Flask
from static_bundle import register_extension

app = Flask(__name__, static_folder='static')

register_extension(app)
```

```html

{% bundler 'cache/vendor.css' %}
    {% set url_for=file_path_for %}
    <link rel="stylesheet" type="text/css"
          href="{{ url_for('static', filename = 'fontawesome-free-5.7.1-web/css/fontawesome.min.css') }}">
        
    <link rel="stylesheet" type="text/css"
          href="{{ url_for('static', filename = 'css/bootstrap_table_1.18.3/bootstrap-table.css') }}">
    <link rel="stylesheet" type="text/css"
          href="{{ url_for('static', filename = 'css/bootstrap_table_1.18.3/extensions/filter-control/bootstrap-table-filter-control.css') }}">
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename = 'css/datetime_picker_css.css') }}">

{% endbundler %}

```

This will generate `cache/vendor.css` inside static folder and generate final output like below

```html
<link rel="stylesheet" type="text/css" href="/static/cache/vendor.css">
```

Please create github issue if you encounter any problem.

#### Checklist Items for future

- Add support for Django & FastAPI
- Add support to minify content

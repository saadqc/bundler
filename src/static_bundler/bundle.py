__author__ = "Saad Abdullah"
__credits__ = ["Saad Abdullah"]
__version__ = "0.0.1a"
__email__ = "saadfast.qc@gmail.com"
__implemented_date__ = "9/24/22"
__implemented_description__ = ""

# builtin imports
import time
import os

# third party imports
from flask import current_app, url_for, request
from jinja2 import nodes, TemplateSyntaxError
from jinja2.ext import Extension
from lxml import html


def file_path_for_processor():
    def file_path_for(static_path, **kwargs):
        """
        Similar to url_for but it generates full path of file specified in arg

        url_for('static', filename='js/bootstrap.js') generates url like /static/js/bootstrap.js
        whereas this function generates filesystem path like /home/ubuntu/project/static/js/bootstrap.js

        :arg str static_path: static path or root of static folder. e.g. static
        :return absolute file path of given filename
        """
        app_bp = current_app
        filename = kwargs.get('filename')
        if not filename:
            return url_for(static_path, **kwargs)
        if static_path.startswith('.'):
            app_bp = current_app.blueprints[request.blueprint]
        elif '.' in static_path:
            bp, static = static_path.split('.', 1)
            if bp not in current_app.blueprints:
                raise TemplateSyntaxError('Blueprint {0} name is not registered in app. Static path: {1}'.format(bp, static_path),1)
            app_bp = current_app.blueprints[bp]

        if os.name == 'nt':
            filename = filename.replace('/', '\\')
        static_path = os.sep.join(app_bp.static_folder.split(os.sep))
        file_path = os.path.join(static_path, filename)

        return file_path

    return {'file_path_for': file_path_for}


class BundlerExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['bundler'])

    def __init__(self, environment):
        super(BundlerExtension, self).__init__(environment)
        self.verbose = False
        self.start = None

    def log_info(self, *args):
        if self.verbose:
            print(*args)

    def log_error(self, *args):
        print(*args)

    def parse(self, parser):
        self.start = time.time()
        line_number = next(parser.stream).lineno

        args = [parser.parse_expression()]
        if parser.stream.skip_if("comma"):
            args.append(parser.parse_expression())
        else:
            args.append(args[0])

        if len(args) < 2:
            raise TemplateSyntaxError('Should specify name of file as first arg', lineno=line_number)
        body = parser.parse_statements(['name:endbundler'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_to_bundle', args), [], [], body).set_lineno(line_number)

    def _to_bundle(self, bundle_name, output_filename, caller, *args, **kwargs):
        """
        Takes bundle name and block of scripts/styles and generates a bundled js/css in static folder

        :param str bundle_name: vendor.bundle.js or app.bundle.js
        :param str output_filename:
        :param caller:
        :param args:
        :param kwargs:
        :return:
        """
        static_url = url_for('static', filename=output_filename)
        html_str = caller()

        _, file_type = os.path.splitext(bundle_name)
        if not file_type == '.js' and not file_type == '.css':
            raise TemplateSyntaxError('Extension of output file should be either js or css', lineno=1)

        file_path = os.path.join(current_app.static_folder, bundle_name)
        bundle_time = 0
        if os.path.isfile(file_path):
            bundle_time = os.stat(file_path).st_mtime

        parsed = html.fromstring(str(html_str))
        if file_type == '.js':
            tags = parsed.xpath('//*/script')
            tag_attr = 'src'
        elif file_type == '.css':
            tags = parsed.xpath('//*/link')
            tag_attr = 'href'
        else:
            return ''

        # Checks if file is modified, if yes, then generate the bundle again. If not use existing bundle if available
        modified = False
        for tag in tags:
            _time = os.stat(tag.attrib[tag_attr]).st_mtime
            if _time > bundle_time:
                modified = True

        if modified:
            path_dir = os.path.dirname(file_path)
            if not os.path.exists(path_dir):
                os.makedirs(path_dir, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as fl:
                for tag in tags:
                    basename = os.path.basename(tag.attrib[tag_attr])
                    fl.write("""// Filename - {0}\n""".format(basename))
                    content = self.minify(tag.attrib[tag_attr], file_type)
                    fl.write(content)
                    fl.write("\n")

        self.log_info('Total time took for bundling {}: {}'.format(bundle_name, time.time() - self.start))
        return "<link rel='stylesheet' href='{0}'>".format(static_url) if file_type == '.css' \
            else "<script src='{0}'></script>".format(static_url)

    def minify(self, file_path, file_type):
        """
        Take full file path and type of file (can be .js or .css) and return minified content

        :param str file_path: abs_path of file like /home/ubuntu/project/static/js/jquery.js
        :param str file_type: .js or .css
        :return:
        """

        with open(file_path, encoding='utf-8') as fl:
            content = fl.read()
            try:
                import rjsmin
                import rcssmin
                if file_type == '.js':
                    content = rjsmin.jsmin(content)
                elif file_type == '.css':
                    content = rcssmin.cssmin(content)
            except ImportError as e:
                self.log_error('{}'.format(e.msg))
            except Exception as e:
                self.log_error('Unable to minify {0} file. Skipping...'.format(file_path))
        return content


def register_extension(flask_app):
    flask_app.jinja_env.add_extension(BundlerExtension)
    # Converts static paths to absolute file path
    flask_app.template_context_processors[None].append(file_path_for_processor)

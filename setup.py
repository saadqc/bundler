from setuptools import setup

if __name__ == "__main__":
    setup(
        name='static-bundler',
        version='0.0.1',
        package_dir={'': 'src'},
        packages=['static_bundler'],
        url='',
        license='MIT',
        author='Saad Abdullah',
        author_email='saadfast.qc@gmail.com',
        description='Bundles multiple js/css files into one to reduce requests time',
        keywords=['bundler', 'bundles', 'minify', 'static'],
        install_requires=[
            "Jinja2>=2.9.3",
            "lxml>=3.8.0",
            "setuptools>=31.0.0",
            "Flask>=1.0.1"
        ]
)

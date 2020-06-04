from setuptools import setup, find_packages

version = '1.1.0'

setup(
    name="alerta-zulip",
    version=version,
    description='Alerta plugin for Zulip',
    url='https://github.com/opentelekomcloud-infra/alerta',
    license='Apache-2.0',
    author='Artem Goncharov, Anton Sidelnikov',
    author_email='artem.goncharov@gmail.com, a.sidelnikov@t-systems.com',
    packages=find_packages(),
    py_modules=['alerta_zulip'],
    install_requires=[
        'zulip>=0.7.0',
        'jinja2',
        'cryptography>=2.8',
        'psycopg2-binary',
        'ocomone>=0.4.3',
        'pyyaml-typed>=0.1.0'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'zulip = alerta_zulip:ZulipBot'
        ]
    }
)

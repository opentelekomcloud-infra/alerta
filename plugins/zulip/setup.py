from setuptools import setup, find_packages

version = '1.1.1'

setup(
    name="alerta-zulip",
    version=version,
    description='Alerta plugin for Zulip',
    url='https://github.com/opentelekomcloud-infra/alerta',
    license='Apache-2.0',
    author='Artem Goncharov',
    author_email='artem.goncharov@gmail.com',
    packages=[
        "zulipbot",
        "zulipbot.config",
        "zulipbot.config.resources"
    ],
    package_data={"zulipbot.config.resources": ["*.yaml"]},
    py_modules=['alerta_zulip'],
    install_requires=[
        'zulip>=0.7.0',
        'jinja2',
        'cryptography>=2.8',
        'psycopg2-binary'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'zulip = alerta_zulip:ZulipBot'
        ]
    }
)

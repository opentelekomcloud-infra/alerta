from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-zulpi",
    version=version,
    description='Alerta plugin for Zulip',
    url='https://github.com/opentelekomcloud-infra/alerta',
    license='Apache-2.0',
    author='Artem Goncharov',
    author_email='artem.goncharov@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_zulip'],
    install_requires=[
        'zulip',
        'jinja2'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'zulip = alerta_zulip:ZulipBot'
        ]
    }
)


from setuptools import find_packages
from setuptools import setup

from django_cbrf import __version__

setup(
    name='django_cbrf',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "django>=3.1",
        "cbrf==0.5.0",
    ],
    url='https://github.com/Egregors/django-cbrf',
    license='MIT',
    author='Vadim Iskuchekov (@egregors)',
    author_email='egregors@yandex.ru',
    description='Django app to integrate Wrapper for The Central Bank of the Russian Federation site API '
                'with your project',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)

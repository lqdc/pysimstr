from distutils.core import setup
setup(
    name='pysimstr',
    packages=['pysimstr'],
    install_requires=['python-Levenshtein'],
    version='0.2',
    description='Fast(ish) string similarity for one vs many comparisons',
    author='Roman Sinayev',
    author_email='roman.sinayev@gmail.com',
    url='https://github.com/lqdc/pysimstr',
    download_url='https://github.com/lqdc/pysimstr/tarball/0.2',
    keywords=['jaro-winkler', 'jaro', 'string similarity', 'levenshtein'],
    classifiers=[],
)

from setuptools import setup

setup(
        name='boto_cli',
        version='0.1',
        py_modules=['boto_cli', ],
        license=open('LICENSE').read(),
        long_description=(open('README.md').read()),
        install_requires=["boto3", "pyyaml"],
        author='Tatiana Ilyushechkina',
        author_email='eiwill@yandex.ru',
        url='https://github.com/eiwill/boto_cli',
        description='Boto3 command line interface.',
        classifiers=(
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        ),
        entry_points={
            'console_scripts': [
                'boto_cli = boto_cli:run',
            ],
        },
)

from setuptools import setup


setup(
    name="microauth",

    packages=["microauth"],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "bcrypt",
        "requests",
    ]
)

from setuptools import setup


setup(
    name="microauth",
    version='0.1',
    packages=["microauth", "microauth.resources"],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        "Flask-RESTful",
        "Flask-SQLAlchemy",
        "bcrypt",
        "requests",
        "pyopenssl",
    ]
)

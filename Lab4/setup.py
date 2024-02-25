from setuptools import setup

setup(
    name="twidder",
    packages=["twidder"],
    include_package_data=True,
    install_requires=["flask", "Gunicorn", "pyyaml", "flask-sock", "psycopg2"],
)

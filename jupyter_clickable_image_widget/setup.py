from setuptools import setup, find_packages

version_ns = {}
with open('jupyter_clickable_image_widget/_version.py') as f:
    exec(f.read(), {}, version_ns)

setup(
    name='jupyter_clickable_image_widget',
    version=version_ns['__version__'],
    description='Clickable live image widget for JupyterLab 4',
    author='John Welsh',
    author_email='jwelsh@nvidia.com',
    url='https://github.com/NVIDIA-AI-IOT/jupyter_clickable_image_widget',
    packages=find_packages(),
    install_requires=[
        'anywidget>=0.9.0',
        'traitlets',
    ],
    zip_safe=False,
)

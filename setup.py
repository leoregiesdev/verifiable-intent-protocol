from setuptools import setup, find_packages

setup(
    name="vip-protocol",
    version="1.0.0",
    packages=find_packages(),
    py_modules=['vip_cli', 'vip_engine', 'vip_dsl_parser'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'vip=vip_cli:main',
        ],
    },
    author="leoregiesdev",
    description="VIP: Verifiable Intent Protocol - O padrão mundial de confiança para software e IA.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/leoregiesdev/verifiable-intent-protocol",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)


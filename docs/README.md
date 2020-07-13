To build the documentation:

    pip3 install sphinx
    make html
    cd _build/html
    python3 -m http.server 8000

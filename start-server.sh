python -c "import os, sys; os.system('python -m SimpleHTTPServer 3000 --bind 127.0.0.1') if sys.version_info.major==2 else os.system('python -m http.server 3000 --bind 127.0.0.1');"

import os
from wsgiref.simple_server import make_server

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petkit_backend.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402


application = get_wsgi_application()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = int(os.environ.get("PORT", "8012"))
    with make_server(host, port, application) as server:
        print(f"Serving Tail's Town at http://{host}:{port}/", flush=True)
        server.serve_forever()

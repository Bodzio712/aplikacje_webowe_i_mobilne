from werkzeug.wrappers import Request, Response
from urlparse import urlparse


@Request.application
def application(request):

    request_data = request.stream.read()
    accepted_types = request.headers['Accept']

    url = request.url
    parsed_url = urlparse(url)

    print(parsed_url.path)

    path = parsed_url.path

    if path == "/":
        path = "static/index.html"
    else:
        path = path.strip("/")

    file = open(path, "r")
    index_content = file.read()
    file.close()

    #Sprawdzanie czy zadanie oczekuje dokumentu HTML
    if accepted_types.find('text/html') != -1:
        return Response(index_content, status='200 OK', mimetype='text/html')
    #Sprawdzanie czy zadanie oczekuje golego tekstu
    elif accepted_types.find('text/plain') != -1:
       return Response(index_content, status='200 OK', mimetype='text/plain')
    elif accepted_types.find('text/css') != -1:
       return Response(index_content, status='200 OK', mimetype='text/css')
    elif accepted_types.find('*/*') != -1:
       return Response(index_content, status='200 OK', mimetype='*/*')
   #Zwracanie informacji o bledzie, jesli strona nie zazadala zadnego z powyzszych typow
    else:
        return Response('Nie znaleziono oczekiwanego typu danych', status='400 Bad Request')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = run_simple('0.0.0.0', 4000, application).wsgi_app()

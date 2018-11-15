const serverPort = 8113,
      http = require('http');

server = http.createServer((request, response) => {
  if (request.url == '/events') {
    console.log(request.headers)
    response.writeHead(200, {
      'Connection': 'keep-alive',
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache'
    });
    let lastEventId = request.headers['last-event-id'] || '1';
    let id = parseInt(lastEventId);
    setInterval(() => {
      response.write(
`event: choice
id: ${id}
data: Wiadomość #${id}.
data: Będzie więcej.`);
      response.write('\n\n');
      id++;
    }, 3000);

  } else {
      response.writeHeader(200, {"Content-Type": "text/html"});
      response.write('OK');
      response.end();
  }
})



server.listen(serverPort, () => {
    console.log(`SSE server started on port ` + serverPort);
});

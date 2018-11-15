const serverPort = 8114,
    http = require("http"),
    ws = require("ws"),
    express = require("express"),
    app = express(),
    serverHTTP = http.createServer(app)
    serverWebSocket = new ws.Server({ server:serverHTTP });

app.get('/index', function(req, res) {
   res.writeHeader(200, {"Content-Type": "text/html"});
   res.write('OK');
   res.end();
})

serverWebSocket.on('connection', (client) => {
    client.send('{ "connection" : "ok"}');
    client.on('message', (message) => {
        serverWebSocket 
        .clients
        .forEach(c => {
            c.send(`{ "message" : ${message} }`);
        });
    });
});

serverHTTP.listen(serverPort, () => {
    console.log(`Websocket server started on port ` + serverPort);
});

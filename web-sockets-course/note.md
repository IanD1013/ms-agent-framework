### WebSocket Stages

#### 1. Connect

```js
const socket = newWebSocket("ws://localhost:8080");
```

The moment this runs, the browser sends an http get request, but with a special header that says i want to upgrade this
connection to use websockets, that's the upgrade request. If the server accepts it, it replies with 101 switching
protocols

#### 2. Upgrade


#### 3. Stateful


### WebSocket LifeCycle
#### 1. Connecting
#### 2. Open
#### 3. Closing
#### 4. Closed
we can check that anytime using `socket.readyState`

```js
// SERVER (ws)
wss.on("connection", (ws) => {
    ws.on("message", (data) => {});
    ws.on("error", (err) => {});
    ws.on("close", () => {});
});


// CLIENT (Browser)
const socket = new WebSocket("ws://...");
socket.onopen = () => {};
socket.onmessage = (e) => {};
socket.onerror = () => {};
socket.onclose = () => {};
```
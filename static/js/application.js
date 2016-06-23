if (window.location.protocol == "https:") {
	var ws_scheme = "wss://";
} else {
	var ws_scheme = "ws://"
}; 


var inbox = new ReconnectingWebSocket(ws_scheme + location.host + "/receive");
var outbox = new ReconnectingWebSocket(ws_scheme + location.host + "/submit");
var inbox_chat = new ReconnectingWebSocket(ws_scheme + location.host + "/receive_chat");
var outbox_chat = new ReconnectingWebSocket(ws_scheme + location.host + "/submit_chat");
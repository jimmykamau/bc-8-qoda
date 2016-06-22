if (window.location.protocol == "https:") {
	var ws_scheme = "wss://";
} else {
	var ws_scheme = "ws://"
};

var inbox = new ReconnectingWebSocket(ws_scheme + location.host + "/receive_code");
var outbox = new ReconnectingWebSocket(ws_scheme + location.host + "/submit_code");
var inbox_chat = new ReconnectingWebSocket(ws_scheme + location.host + "/receive_chat");
var outbox_chat = new ReconnectingWebSocket(ws_scheme + location.host + "/submit_chat");

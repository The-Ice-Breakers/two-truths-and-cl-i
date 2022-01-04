from test_main import ConnectionManager, check_result
import pytest
from Websocket import WebSocket

    

def test_instantiate():
    manager = ConnectionManager()
    assert manager


def test_websocket_connection():
    websocket = WebSocket()
    manager = ConnectionManager()
    manager.connect(websocket)
    assert manager.active_connections[0] == websocket

def test_websocket_disconnect():
    websocket = WebSocket()
    manager = ConnectionManager()
    manager.connect(websocket)
    manager.disconnect(websocket)
    assert not manager.active_connections

def test_check_result_next():
  websocket = WebSocket()
  input = ">"
  actual = check_result(input,websocket,"")
  expected = "Nothing next"
  assert actual == expected

def test_changeTl_with_bad_statement():
  websocket = WebSocket()
  input = "@true, truth, "
  actual = check_result(input, websocket,"")
  expected = "Invalid format: (truth, truth, lie)"
  assert actual == expected


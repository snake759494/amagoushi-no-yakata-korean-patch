import websocket,json,sys,time,uuid
w=websocket.create_connection('ws://127.0.0.1:49742/debugger',subprotocols=['debugger.ppsspp.org'],timeout=15)
def send(buttons):
 w.send(json.dumps({'event':'input.buttons.send','buttons':buttons,'ticket':'pad'}))
 while json.loads(w.recv()).get('ticket')!='pad':pass
send({b:False for b in 'up down left right circle cross triangle square start select ltrigger rtrigger'.split()})
delay=1.0
for button in sys.argv[1:]:
 if button.startswith('w'): time.sleep(float(button[1:])); continue
 n=1
 if '*' in button: button,n=button.split('*'); n=int(n)
 for _ in range(n):
  ticket=str(uuid.uuid4())
  w.send(json.dumps({'event':'input.buttons.press','button':button,'duration':int(__import__('os').environ.get('DUR','8')),'ticket':ticket}))
  while json.loads(w.recv()).get('ticket')!=ticket:pass
  time.sleep(delay)
w.shutdown()

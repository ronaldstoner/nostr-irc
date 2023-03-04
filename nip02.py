import asyncio
import websockets
import json

ping_keepalive = 30
ping_timeout = 10
friendlist = []


async def get_nip02_friends(relay, pubkey):
    search_filter_nip02 = {
        "kinds": [3],
        "authors": [pubkey]
    }
    try:
        async with websockets.connect(relay) as websocket_nip02:
            request = json.dumps(["REQ", "nip02-" + pubkey[:8], search_filter_nip02])
            await websocket_nip02.send(request)
            friends_reply = await websocket_nip02.recv()

            if friends_reply is not None:
                await websocket_nip02.send(json.dumps(["CLOSE", "nip02-" + pubkey[:8]]))
                friends_close = await websocket_nip02.recv()

                unparsed_list = json.loads(friends_reply)
                content_list = unparsed_list[2]['tags']
                for item in content_list:
                    if isinstance(item, list) and item[0] == 'p':
                        friendlist.append(item[1])
                return friendlist

    except Exception as e:
        #messages.addstr(str(f"NIP02 Error: {e}"))
        return friendlist
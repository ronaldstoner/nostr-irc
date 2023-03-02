import asyncio
import json
import time
import websockets

nip_05_identifiers = {}

async def get_nip05(pubkey, uri):
    search_filter_nip05 = {
        "kinds": [0],
        "authors": [pubkey]
    }

    try:
        async with websockets.connect(uri) as websocket_metadata:
            request = json.dumps(["REQ", "nip05-" + pubkey[:8], search_filter_nip05])

            await websocket_metadata.send(request)
            pubkey_metadata_reply = await websocket_metadata.recv()


            if "EOSE" not in pubkey_metadata_reply and pubkey_metadata_reply is not None:
                # Remove newline characters from the metadata string
                pubkey_metadata_reply = pubkey_metadata_reply.replace('\n', '')
                # Parse the JSON string
                pubkey_metadata = json.loads(pubkey_metadata_reply)
                # Debug
                #print(f"METADATA: {str(pubkey_metadata[2]['content'])}")

                json_acceptable_string = pubkey_metadata[2]['content']
                d = json.loads(json_acceptable_string)
                name = d['name']

                nip_05_identifier = name

                await websocket_metadata.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
                pubkey_metadata_close = await websocket_metadata.recv()
            
            else:
                nip_05_identifier = None
                #await websocket_metadata.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
                #pubkey_metadata_close = await websocket_metadata.recv()
  
    except Exception as e:
        nip_05_identifier = None
        #Debug
        #print(f"EXCEPTION: {e}")
        #time.sleep(5)
    return nip_05_identifier

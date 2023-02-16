import asyncio
import json
import websockets

nip_05_indentifiers = {}

async def get_nip05(pubkey, uri):
    search_filter_nip05 = {
        "kinds": [0],
        "authors": [pubkey]
    }

    try:
        async with websockets.connect(uri) as websocket_metadata:
            request = json.dumps(["REQ", "nip05-" + pubkey[:8], search_filter_nip05])
            #logger.debug(f"Request: {request}")

            await websocket_metadata.send(request)
            pubkey_metadata_reply = await websocket_metadata.recv()
            #logger.debug(f"Reply: {pubkey_metadata_reply}")

            if "EOSE" not in pubkey_metadata_reply and pubkey_metadata_reply is not None:
                # Remove newline characters from the metadata string
                pubkey_metadata_reply = pubkey_metadata_reply.replace('\n', '')
                # Parse the JSON string
                pubkey_metadata = json.loads(pubkey_metadata_reply)
                #logger.debug(f"METADATA: {str(pubkey_metadata[2]['content'])}")

                json_acceptable_string = pubkey_metadata[2]['content']
                d = json.loads(json_acceptable_string)
                name = d['name']
                #logger.debug(f"Name: {name}")

                nip_05_identifier = name

                await websocket_metadata.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
                pubkey_metadata_close = await websocket_metadata.recv()
                #logger.debug(f"Reply: {pubkey_metadata_close}")
            else:
                nip_05_identifier = pubkey
                await websocket_metadata.send(json.dumps(["CLOSE", "nip05-" + pubkey[:8]]))
                pubkey_metadata_close = await websocket_metadata.recv()
                #logger.debug(f"Reply: {pubkey_metadata_close}")
    except Exception as e:
        nip_05_identifier = pubkey
        #logger.debug(f"EXCEPTION!!! {e}")

    return nip_05_identifier

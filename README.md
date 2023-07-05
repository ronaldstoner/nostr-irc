# nostr-cli
A simple command line based nostr client that simulates the old school IRC clients of the past.

Barebones, no fluff, no bells, no whistles, no apologies. This is a hobby project so I can re-live the nostalgia of old school console based IRC clients and chat with my friends over a stream of text. The idea is to connect to a single "IRC" purpose relay for real time chat with other connected users.

Currently supported:
- NIP01 subscriptions
        - Kind 1
- NIP05 name resolution
- EOSE
- Event kind=1 posting to Global Feed
- Private Keys (-p on command line, hex only for now)
- Random Private Key generation
- Relay specification (-r on command line)
- Commands
- Command tab completion 

# Screenshot
<img src="https://github.com/Shinoa-Fores/nostr-cli/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Install
It is recommended to install using a virtual environment like so:
```
git clone https://github.com/Shinoa-Fores/nostr-cli.git

python3 -m venv nostr-cli/

cd nostr-cli && source bin/activate

pip install -r requirements.txt

```

# Usage
python nostr-cli.py

```options:

  -h, --help            show this help message and exit
  -p PRIVATEKEY, --privatekey PRIVATEKEY
                        The private key for signing messages in hex format
  -r RELAY, --relay RELAY
                        The secure websocket relay to use (e.g. wss://nos.lol)
```

# Client Commands
Commands inside the client can be used to interact with various functions. Command tab completion is enable inside the client and will allow you start commands with the / character and autocomplete them with the TAB key on the keyboard.  

```
- /clear - clears the messages window
- [PENDING] /join - joins an existing or creates a new chatroom
- [PENDING] /part - leaves a chatroom
- /quit - quits the nostr-cli client
- [PENDING] /slap - slaps another users pubkey with a fish
- /who - displays a list of recently seen users
```

# TODO
- More NIP-01
- Replies to notes
- Better tag handling overall
- NIP-05 verification via domain
- Allow "read only" type mode for those that want privacy
- Persist to local db? Storage and performance tradeoffs
- NIP-04 DMs via client?
- Multiple relays?

# Donate
If you find this script useful or decide to use it in production feel free to donate any spare sats you may have. This goes a long way to fueling the caffeine needed for late night development.

⚡Alby: stoner@getalby.com

# Honorable Contributors
If you would like to contribute to the codebase please submit a PR to your local branch. Information will be incoming shortly on what is needed for a successful code PR. 

Contributions made by:
- [lmacken](https://github.com/lmacken)

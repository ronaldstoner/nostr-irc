# nostr-irc
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

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-irc/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Install
You'll have to add a bunch of pip packages. I'll add a requirements soon. 

# Usage
python nostr-irc.py

```options:

  -h, --help            show this help message and exit
  -p PRIVATEKEY, --privatekey PRIVATEKEY
                        The private key for signing messages in hex format
  -r RELAY, --relay RELAY
                        The secure websocket relay to use (e.g. wss://nos.lol)
```

# TODO
- More NIP-01
- Replies to notes
- Better tag handling overall
- NIP-05 verification via domain
- Allow "read only" type mode for those that want privacy
- Persist to local db? Storage and performance tradeoffs
- Active user list?
- NIP-04 DMs via client?
- Multiple relays?
```

# Donate
If you find this script useful or decide to use it in production feel free to donate any spare sats you may have. This goes a long way to fueling the caffeine needed for late night development.

⚡Alby: stoner@getalby.com

# Honorable Contributors
If you would like to contribute to the codebase please submit a PR to your local branch. Information will be incoming shortly on what is needed for a successful code PR. 

Contributions made by:
- [lmacken](https://github.com/lmacken)
# nostr-irc
A simple command line based nostr client that simulates the old school IRC clients of the past. 

Barebones, no fluff, no bells, no whistles, no apologies. This is a hobby project so I can relive the nostalgia of old school console based IRC clients and chat with my friends over a stream of text. The idea is to connect to single "IRC" purpose relay for real time chat with other connected users. 

Currently supported:
- Viewing posts from a relay
- NIP05 name resolution 

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-irc/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# NOTE
This is a very early proof of concept.

# TODO
- More NIP-01
- Replies to notes
- Better tag handling overall
- NIP-05 verificaiton via domain
- Sign and send message from bottom input bar
- Load privkeys
- Generate random keypair if no privkey specified
- Allow "read only" type mode for those that want privacy
- Persist to local db? Storage and performance tradeoffs
- Active user list?
- NIP-04 DMs via client?
- Multiple relays?
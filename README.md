# nostr-irc
A simple command line based nostr client that simulates the old school IRC clients of the past. 

Barebones, no fluff, no bells, no whistles, no apologies. This is a hobby project so I can re-live the nostalgia of old school console based IRC clients and chat with my friends over a stream of text. The idea is to connect to a single "IRC" purpose relay for real time chat with other connected users. 

Currently supported:
- NIP01 subscriptions
	- Kind 1 
- NIP05 name resolution 
- EOSE

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-irc/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Note
This is a very early proof of concept.

# Donate
If you find this script useful or decide to use it in production feel free to donate any spare sats you may have. This goes a long way to fueling the caffeine needed for late night development. 

⚡Alby: stoner@getalby.com  

# TODO
- More NIP-01
- Replies to notes
- Better tag handling overall
- NIP-05 verification via domain
- Sign and send message from bottom input bar
- Load privkeys
- Generate random keypair if no privkey specified
- Allow "read only" type mode for those that want privacy
- Persist to local db? Storage and performance tradeoffs
- Active user list?
- NIP-04 DMs via client?
- Multiple relays?
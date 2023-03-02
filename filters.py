def load_event_filters():
    try:
        event_filter_list = []
        with open("./filters/event.filters", "r") as file:
            for line in file:
                line = line.strip()
                event_filter_list.append(line)
                #print(str(event_filter_list))
    except Exception as e:
        print("Could not load event filter list - ", e)
    return event_filter_list


def load_pubkey_filters():
    try:
        pubkey_filter_list = []
        with open("./filters/pubkey.filters", "r") as file:
            for line in file:
                line = line.strip()
                pubkey_filter_list.append(line)
    except Exception as e:
        print("Could not load pubkey filter list - ", e)
    return pubkey_filter_list

import worldcup

replies = worldcup.handle_command("wc standings")

for reply in replies:
    print(reply)
    print("=" * 60)
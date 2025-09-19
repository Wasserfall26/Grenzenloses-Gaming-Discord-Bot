import discord
import asyncio
from discord.ext import commands
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1372184596707409972
current_channel = None
channel_list = []
message_queue = asyncio.Queue()


async def display_past_messages(channel: discord.TextChannel, limit=20):
    """Lädt die letzten Nachrichten eines Channels und zeigt sie in CMD."""
    try:
        messages = []
        async for msg in channel.history(limit=20, oldest_first=False):
            messages.append(msg)

        messages.reverse()  # jetzt chronologisch von alt -> neu


        print(f"\n--- Letzte {len(messages)} Nachrichten in #{channel.name} ---")
        for msg in messages:
            if msg.author == bot.user:
                print(f"{Fore.CYAN}[Bot] {msg.content}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[{msg.author.display_name}] {msg.content}{Style.RESET_ALL}")
        print(f"--- --- --- --- --- --- ---\n")
    except Exception as e:
        print(f"Fehler beim Laden der Nachrichten: {e}")


@bot.event
async def on_ready():
    global channel_list
    print(f"✅ Bot online als {bot.user} ✅")
    guild = bot.get_guild(GUILD_ID)
    channel_list = list(guild.text_channels)
    print("\n/help zeigt alle Befehle\n")
    bot.loop.create_task(console_input(guild))
    

@bot.event
async def on_message(message):
    global current_channel
    if current_channel and message.channel == current_channel and message.author != bot.user:
        await message_queue.put(message)


async def console_input(guild: discord.Guild):
    global current_channel
    await bot.wait_until_ready()

    async def print_messages():
        while True:
            msg = await message_queue.get()
            if msg.author == bot.user:
                print(f"\n{Fore.CYAN}[Bot] {msg.content}{Style.RESET_ALL}\n> ", end="")
            else:
                print(f"\n{Fore.YELLOW}[{msg.author.display_name}] {msg.content}{Style.RESET_ALL}\n> ", end="")

    asyncio.create_task(print_messages())

    while True:
        user_input = await asyncio.to_thread(input, "> ")
        if not user_input.strip():
            continue

        cmd = user_input.lower()

        # Channel wechseln
        if cmd.startswith("/ch"):
            num_str = user_input[3:]
            try:
                num = int(num_str)
                if 1 <= num <= len(channel_list):
                    current_channel = channel_list[num - 1]
                    print(f"Channel gewechselt zu #{current_channel.name}")
                    await display_past_messages(current_channel, limit=20)
                else:
                    print("Ungültige Channelnummer")
            except ValueError:
                print("Bitte /ch gefolgt von einer Zahl eingeben")

        # Aktuellen Channel anzeigen
        elif cmd == "/current":
            if current_channel:
                print(f"Aktueller Channel: #{current_channel.name}")
            else:
                print("Kein Channel gewählt!")
            print("\n")
        # Zum nächsten Channel wechseln
        elif cmd == "/next":
            if current_channel:
                idx = channel_list.index(current_channel)
                current_channel = channel_list[(idx + 1) % len(channel_list)]
                print(f"Channel gewechselt zu #{current_channel.name}")
                await display_past_messages(current_channel, limit=20)
            else:
                print("Kein Channel gewählt!")

        # Zum vorherigen Channel wechseln
        elif cmd == "/prev":
            if current_channel:
                idx = channel_list.index(current_channel)
                current_channel = channel_list[(idx - 1) % len(channel_list)]
                print(f"Channel gewechselt zu #{current_channel.name}")
                await display_past_messages(current_channel, limit=20)
            else:
                print("Kein Channel gewählt!")

        # Channelliste anzeigen
        elif cmd == "/list":
            print("\nChannels:")
            for i, ch in enumerate(channel_list, start=1):
                print(f"{i}. #{ch.name}")
            print("\n")
        # Bot beenden
        elif cmd == "/exit":
            print("Bot wird beendet...")
            await bot.close()
            break

        # Nachricht mehrfach senden
        elif cmd.startswith("/repeat"):
            if current_channel:
                parts = user_input.split(" ", 2)
                if len(parts) < 3:
                    print("Nutzung: /repeat <Anzahl> <Text>")
                    continue
                try:
                    n = int(parts[1])
                    text = parts[2]
                    for _ in range(n):
                        await current_channel.send(text)
                    print(f"Nachricht {n} mal gesendet")
                except ValueError:
                    print("Ungültige Anzahl")
            else:
                print("Kein Channel gewählt!")

        # Direktnachricht an Benutzer
        elif cmd.startswith("/dm"):
            parts = user_input.split(" ", 2)
            if len(parts) < 3:
                print("Nutzung: /dm <Benutzer> <Text>")
                continue
            username = parts[1]
            text = parts[2]
            member = discord.utils.get(guild.members, name=username)
            if member:
                await member.send(text)
                print(f"DM an {username} gesendet")
            else:
                print(f"Benutzer '{username}' nicht gefunden")

        # Nachricht in aktuellem Channel
        elif cmd.startswith("/say"):
            if current_channel:
                text = user_input[5:]
                await current_channel.send(text)
                print(f"Nachricht in #{current_channel.name} gesendet")
            else:
                print("Kein Channel gewählt!")

        # Mitgliederliste
        elif cmd == "/listmembers":
            print("\nMitglieder:")
            count = 0
            for member in guild.members:
                if discord.utils.get(member.roles, name="Bot"):
                    continue
                print(f"{member.name} ({member.display_name})")
                count += 1

            print("\n")                      

        # Hilfe anzeigen
        elif cmd == "/help":
            print("\nBefehle:")
            print("/list                    -> Liste aller Channels")
            print("/ch<num>                 -> Channel wechseln")
            print("/current                 -> Zeigt aktuellen Channel")
            print("/next                    -> Zum nächsten Channel wechseln")
            print("/prev                    -> Zum vorherigen Channel wechseln")
            print("/say <Text>              -> Nachricht im aktuellen Channel senden")
            print("/repeat <Anzahl> <Text>  -> Nachricht n-mal senden")
            print("/dm <Benutzer> <Text>    -> Direktnachricht senden")
            print("/listmembers             -> Liste aller Mitglieder auf dem Server")
            print("/exit                    -> Bot beenden\n")

        # Alle anderen Eingaben als Nachricht senden
        else:
            if current_channel:
                await current_channel.send(user_input)
            else:
                print("Kein Channel gewählt!")


# <<< Hier deinen Bot-Token einsetzen >>>
bot.run("DISCORD_BOT_TOKEN")

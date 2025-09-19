import discord
import asyncio
from discord.ext import commands
from colorama import Fore, Style, init

init(autoreset=True)  # Farbausgabe für Konsole aktivieren

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1372184596707409972
current_channel = None
channel_list = []


@bot.event
async def on_ready():
    global channel_list
    print(f"✅ Bot online als {bot.user} ✅")
    guild = bot.get_guild(GUILD_ID)

    # Channels speichern
    channel_list = list(guild.text_channels)

    print("\n'/help' zeigt alle Befehle\n")

    bot.loop.create_task(console_input(guild))


async def show_last_messages(channel):
    """Letzte Nachrichten aus einem Channel in richtiger Reihenfolge anzeigen"""
    try:
        messages = []
        async for msg in channel.history(limit=20, oldest_first=False):
            messages.append(msg)

        # Reihenfolge umdrehen -> älteste zuerst, neueste zuletzt
        messages.reverse()

        print(f"\n--- Letzte Nachrichten in #{channel.name} ---")
        for msg in messages:
            if msg.author == bot.user:
                # Bot-Nachrichten in grün
                print(f"{Fore.GREEN}[Bot]{Style.RESET_ALL} {msg.content}")
            else:
                # Normale User in gelb
                print(f"{Fore.YELLOW}[{msg.author.display_name}]{Style.RESET_ALL} {msg.content}")
        print("--- Ende ---\n")
    except Exception as e:
        print(f"Fehler beim Laden der Nachrichten: {e}")


async def console_input(guild: discord.Guild):
    global current_channel
    await bot.wait_until_ready()

    while True:
        user_input = await asyncio.to_thread(input, "> ")
        if not user_input.strip():
            continue

        try:
            cmd = user_input.lower()

            # Channel wechseln
            if cmd.startswith("/ch"):
                num_str = user_input[3:]
                try:
                    num = int(num_str)
                    if 1 <= num <= len(channel_list):
                        current_channel = channel_list[num - 1]
                        print(f"Channel gewechselt zu #{current_channel.name}")
                        await show_last_messages(current_channel)
                    else:
                        print("Ungültige Channelnummer")
                except ValueError:
                    print("Bitte /ch gefolgt von einer Zahl eingeben, z.B. /ch2")

            elif cmd == "/current":
                if current_channel:
                    print(f"Aktueller Channel: #{current_channel.name}")
                else:
                    print("Kein Channel gewählt!")

            elif cmd == "/next":
                if current_channel:
                    idx = channel_list.index(current_channel)
                    current_channel = channel_list[(idx + 1) % len(channel_list)]
                    print(f"Channel gewechselt zu #{current_channel.name}")
                    await show_last_messages(current_channel)
                else:
                    print("Kein Channel gewählt!")

            elif cmd == "/prev":
                if current_channel:
                    idx = channel_list.index(current_channel)
                    current_channel = channel_list[(idx - 1) % len(channel_list)]
                    print(f"Channel gewechselt zu #{current_channel.name}")
                    await show_last_messages(current_channel)
                else:
                    print("Kein Channel gewählt!")

            elif cmd == "/list":
                print("\nChannels:")
                for i, ch in enumerate(channel_list, start=1):
                    print(f"{i}. #{ch.name}")

            elif cmd == "/exit":
                print("Bot wird beendet...")
                await bot.close()
                break

            elif cmd.startswith("/say"):
                if current_channel:
                    text = user_input[5:]
                    await current_channel.send(text)
                    print(f"{Fore.GREEN}Nachricht in #{current_channel.name} gesendet{Style.RESET_ALL}")
                else:
                    print("Kein Channel gewählt!")

            elif cmd == "/help":
                print("\nBefehle:")
                print("/list        -> Liste aller Channels")
                print("/ch<num>     -> Channel wechseln")
                print("/current     -> Zeigt aktuellen Channel")
                print("/next        -> Nächster Channel")
                print("/prev        -> Vorheriger Channel")
                print("/say <Text>  -> Nachricht senden")
                print("/exit        -> Bot beenden\n")

            else:
                print("Unbekannter Befehl! Für Hilfe -> /help")

        except Exception as e:
            print(f"Fehler: {e}")


@bot.event
async def on_message(message):
    """Neue Nachrichten live anzeigen"""
    global current_channel
    if message.channel == current_channel and message.author != bot.user:
        print(f"{Fore.YELLOW}[{message.author.display_name}]{Style.RESET_ALL} {message.content}")
    await bot.process_commands(message)


bot.run("DEIN_TOKEN_HIER")

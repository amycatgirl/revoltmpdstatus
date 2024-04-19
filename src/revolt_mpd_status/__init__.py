"""
Display your MPD status in revolt.chat

Usage: revoltmpd [options] <TOKEN>
Arguments:
    TOKEN           Revolt user token
Options:
    -h --help       Show this help message and exit
    --version       Show version and exit
"""
from docopt import docopt
from mpd import MPDClient
import revolt
import asyncio

mpd = MPDClient()
mpd.timeout = 10
mpd.idletimeout = None
mpd.connect("localhost", 6600)


class Client(revolt.Client):
    async def on_ready(self) -> None:
        print("Ready!")

        while True:
            current_song = mpd.currentsong()
            player_status = mpd.status()
            current_status = self.get_user(self.user.id).status.text

            if player_status["state"] != "play":
                status = "🌙 Idle..."
                user_presence = revolt.PresenceType.idle
            elif current_song["title"] is None and current_song["artist"] is not None:
                status = f"🎵 {current_song['file']} - {current_song['artist']}"
                user_presence = revolt.PresenceType.focus
            elif current_song["title"] is None and current_song["artist"] is None:
                status = f"🎵 {current_song['file']}"
                user_presence = revolt.PresenceType.focus
            else:
                user_presence = revolt.PresenceType.focus
                status = f"🎵 {current_song['title']} - {current_song['artist']}"

            if current_status != status:
                print(f"Broadcasting status: {status}")
                await self.edit_status(
                    presence=user_presence,
                    text=status
                )

            await asyncio.sleep(5)


async def start(args):
    async with revolt.utils.client_session() as session:
        client = Client(session, token=args["<TOKEN>"], bot=False)
        await client.start()


def main():
    args = docopt(__doc__, version="0.0.1")
    asyncio.run(start(args))

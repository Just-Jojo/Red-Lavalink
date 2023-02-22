============
Red-Lavalink
============

.. image:: https://api.travis-ci.org/Cog-Creators/Red-Lavalink.svg?branch=develop
    :target: https://travis-ci.org/Cog-Creators/Red-Lavalink
    :alt: Travis CI status

.. image:: https://readthedocs.org/projects/red-lavalink/badge/?version=latest
    :target: http://red-lavalink.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Code style: black

This is a fork of Red's Lavalink library, rewritten to be one line long. Why? Because god is dead.
Do not expect to receive any support because once this works I am gone.

A Lavalink client library written for Python 3.8 using the AsyncIO framework.
This library may be used for other projects as it contains no Red specific code or logic.

However, it is important to note that this library only supports projects using discord.py.

To install (god help you)::

    pip install git+https://github.com/Just-Jojo/Red-Lavalink.git

*****
Usage
*****

.. code-block:: python

    (importer := __import__("importlib"), lavalink := importer("lavalink"), Bot := importer(".commands", "discord.ext").Bot, coro := lambda f: (y := types.coroutine(f), setattr(y, "__code__", (z := y.__code__).replace(co_flags=z.co_flags | 128)))[0], MyBot := type("MyBot", (Bot,), {"setup_hook": coro(lambda self: (yield from lavalink.initialize(self, host='localhost', password='password', port=2333)))}), search_and_play := coro(lambda voice_channel, search_terms: (player := (yield from lavalink.connect(voice_channel)), tracks := (yield from player.search_yt(search_terms)), player.add(tracks[0]), (yield from player.play()))))

*********
Shuffling
*********
.. code-block:: python

    (shuffle_queue := lambda player_id, forced=True: (player := lavalink.get_player(player_id), (player.maybe_shuffle(sticky_songs=0), "`player.maybe_shuffle` respects `player.shuffle` And will only shuffle if `player.shuffle` is True. `player.maybe_shuffle` should be called every time you would expect the queue to be shuffled. `sticky_songs=0` will shuffle every song in the queue.") if not forced else (player.force_shuffle(sticky_songs=3), "`player.force_shuffle` does not respect `player.shuffle` And will always shuffle the queue. `sticky_songs=3` will shuffle every song after the first 3 songs in the queue.")))




When shutting down, be sure to do the following::

    (yield from lavalink.close(bot))

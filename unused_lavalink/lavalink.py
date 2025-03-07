import asyncio
from typing import Optional, Tuple, Union

import discord
from discord.ext.commands import Bot

from . import enums, log, node, player, errors

__all__ = [
    "initialize",
    "connect",
    "get_player",
    "close",
    "register_event_listener",
    "unregister_event_listener",
    "register_update_listener",
    "unregister_update_listener",
    "register_stats_listener",
    "unregister_stats_listener",
    "all_players",
    "all_connected_players",
    "active_players",
    "wait_until_ready",
]

_event_listeners = []
_update_listeners = []
_stats_listeners = []


async def initialize(
    bot: Bot,
    *,
    host,
    password,
    port: Optional[int] = None,
    timeout: float = 30,
    resume_key: Optional[str] = None,
    resume_timeout: float = 60,
    secured: bool = False,
):
    """
    Initializes the websocket connection to the lavalink player.

    .. important::

        This function must only be called AFTER the bot has received its
        "on_ready" event!

    Parameters
    ----------
    bot : Bot
        An instance of a discord.py `Bot` object.
    host : str
        The hostname or IP address of the Lavalink node.
    password : str
        The password of the Lavalink node.
    port : Optional[int]
        The websocket port on the Lavalink Node.
        If not provided, it will use 80 for unsecured connections and 443 for secured.
    timeout : float
        Amount of time to allow retries to occur, ``None`` is considered forever.
    resume_key : Optional[str]
        A resume key used for resuming a session upon re-establishing a WebSocket connection to Lavalink.
    resume_timeout : float
        How long the node should wait for a connection while disconnected before clearing all players.
    secured: bool
        Whether to use the `wss://` and `https://` protocol.
    """
    register_event_listener(_handle_event)
    register_update_listener(_handle_update)

    lavalink_node = node.Node(
        event_handler=dispatch,
        host=host,
        password=password,
        port=port,
        user_id=bot.user.id,
        num_shards=bot.shard_count or 1,
        resume_key=resume_key,
        resume_timeout=resume_timeout,
        bot=bot,
        secured=secured,
    )

    await lavalink_node.connect(timeout=timeout)
    lavalink_node._retries = 0

    bot.add_listener(_on_guild_remove, name="on_guild_remove")

    return lavalink_node


async def connect(channel: discord.VoiceChannel, deafen: bool = False):
    """
    Connects to a discord voice channel.

    This is the publicly exposed way to connect to a discord voice channel.
    The :py:func:`initialize` function must be called first!

    Parameters
    ----------
    channel : discord.VoiceChannel
        The channel to connect to.
    deafen: bool
        Whether to deafen the bot user upon join.

    Returns
    -------
    Player
        The created Player object.

    Raises
    ------
    IndexError
        If there are no available lavalink nodes ready to connect to discord.
    """
    node_ = node.get_node(channel.guild.id)
    p = await node_.create_player(channel, deafen=deafen)
    return p


def get_player(guild_id: int) -> player.Player:
    node_ = node.get_node(guild_id)
    return node_.get_player(guild_id)


async def _on_guild_remove(guild):
    try:
        p = get_player(guild.id)
    except (errors.NodeNotFound, errors.PlayerNotFound):
        pass
    else:
        await p.disconnect()


def register_event_listener(coro):
    """
    Registers a coroutine to receive lavalink event information.

    This coroutine will accept three arguments: :py:class:`Player`,
    :py:class:`LavalinkEvents`, and possibly an extra. The value of the extra depends
    on the value of the second argument.

    If the second argument is :py:attr:`LavalinkEvents.TRACK_END`, the extra will
    be a :py:class:`TrackEndReason`.

    If the second argument is :py:attr:`LavalinkEvents.TRACK_EXCEPTION`, the extra
    will be a dictionary with ``message``, ``cause``, and ``severity`` keys.

    If the second argument is :py:attr:`LavalinkEvents.TRACK_STUCK`, the extra will
    be the threshold milliseconds that the track has been stuck for.

    If the second argument is :py:attr:`LavalinkEvents.TRACK_START`, the extra will be
    a track identifier string.

    If the second argument is any other value, the third argument will not exist.

    Parameters
    ----------
    coro
        A coroutine function that accepts the arguments listed above.

    Raises
    ------
    TypeError
        If ``coro`` is not a coroutine.
    """
    if not asyncio.iscoroutinefunction(coro):
        raise TypeError("Function is not a coroutine.")

    if coro not in _event_listeners:
        _event_listeners.append(coro)


async def _handle_event(player, data: enums.LavalinkEvents, extra):
    await player.handle_event(data, extra)


def _get_event_args(data: enums.LavalinkEvents, raw_data: dict):
    guild_id = int(raw_data.get("guildId"))

    try:
        node_ = node.get_node(guild_id, ignore_ready_status=True)
        player = node_.get_player(guild_id)
    except (errors.NodeNotFound, errors.PlayerNotFound):
        if data != enums.LavalinkEvents.TRACK_END:
            log.debug(
                "Got an event for a guild that we have no player for."
                " This may be because of a forced voice channel"
                " disconnect."
            )
        return

    extra = None
    if data == enums.LavalinkEvents.TRACK_END:
        extra = enums.TrackEndReason(raw_data.get("reason"))
    elif data == enums.LavalinkEvents.TRACK_EXCEPTION:
        exception_data = raw_data["exception"]
        extra = {
            "message": exception_data["message"],
            "cause": exception_data["cause"],
            "severity": enums.ExceptionSeverity(exception_data["severity"]),
        }
    elif data == enums.LavalinkEvents.TRACK_STUCK:
        extra = raw_data.get("thresholdMs")
    elif data == enums.LavalinkEvents.TRACK_START:
        extra = raw_data.get("track")
    elif data == enums.LavalinkEvents.WEBSOCKET_CLOSED:
        extra = {
            "code": raw_data.get("code"),
            "reason": raw_data.get("reason"),
            "byRemote": raw_data.get("byRemote"),
            "channelID": player.channel.id if player.channel else None,
        }
    return player, data, extra


def unregister_event_listener(coro):
    """
    Unregisters coroutines from being event listeners.

    Parameters
    ----------
    coro
    """
    try:
        _event_listeners.remove(coro)
    except ValueError:
        pass


def register_update_listener(coro):
    """
    Registers a coroutine to receive lavalink player update information.

    This coroutine will accept a two arguments: an instance of :py:class:`Player`
    and an instance of :py:class:`PlayerState`.

    Parameters
    ----------
    coro

    Raises
    ------
    TypeError
        If ``coro`` is not a coroutine.
    """
    if not asyncio.iscoroutinefunction(coro):
        raise TypeError("Function is not a coroutine.")

    if coro not in _update_listeners:
        _update_listeners.append(coro)


async def _handle_update(player, data: node.PositionTime, raw_data: dict):
    await player.handle_player_update(data)


def _get_update_args(
    data: Union[node.PositionTime, enums.LavalinkEvents, node.Stats], raw_data: dict
):
    guild_id = int(raw_data.get("guildId"))

    try:
        player = get_player(guild_id)
    except (errors.NodeNotFound, errors.PlayerNotFound):
        log.debug(
            "Got a player update for a guild that we have no player for."
            " This may be because of a forced voice channel disconnect."
        )
        return

    return player, data, raw_data


def unregister_update_listener(coro):
    """
    Unregisters coroutines from being player update listeners.

    Parameters
    ----------
    coro
    """
    try:
        _update_listeners.remove(coro)
    except ValueError:
        pass


def register_stats_listener(coro):
    """
    Registers a coroutine to receive lavalink server stats information.

    This coroutine will accept a single argument which will be an instance
    of :py:class:`Stats`.

    Parameters
    ----------
    coro

    Raises
    ------
    TypeError
        If ``coro`` is not a coroutine.
    """
    if not asyncio.iscoroutinefunction(coro):
        raise TypeError("Function is not a coroutine.")

    if coro not in _stats_listeners:
        _stats_listeners.append(coro)


def unregister_stats_listener(coro):
    """
    Unregisters coroutines from being server stats listeners.

    Parameters
    ----------
    coro
    """
    try:
        _stats_listeners.remove(coro)
    except ValueError:
        pass


def dispatch(
    op: enums.LavalinkIncomingOp,
    data: Union[node.PositionTime, enums.LavalinkEvents, node.Stats],
    raw_data: dict,
):
    listeners = []
    args = []
    if op == enums.LavalinkIncomingOp.EVENT:
        listeners = _event_listeners
        args = _get_event_args(data, raw_data)
    elif op == enums.LavalinkIncomingOp.PLAYER_UPDATE:
        listeners = _update_listeners
        args = _get_update_args(data, raw_data)
    elif op == enums.LavalinkIncomingOp.STATS:
        listeners = _stats_listeners
        args = [data]

    if args is None:
        # For example, no player because channel got removed.
        return

    for coro in listeners:
        asyncio.create_task(coro(*args))


async def close(bot):
    """
    Closes the lavalink connection completely.
    """
    log.debug("Closing Lavalink connections")
    unregister_event_listener(_handle_event)
    unregister_update_listener(_handle_update)
    bot.remove_listener(_on_guild_remove, name="on_guild_remove")
    await node.disconnect()
    log.debug("All Lavalink nodes have been disconnected")


# Helper methods


def all_players() -> Tuple[player.Player]:
    nodes = node._nodes
    ret = tuple(p for n in nodes for p in n.players)
    return ret


def all_connected_players() -> Tuple[player.Player]:
    nodes = node._nodes
    ret = tuple(p for n in nodes for p in n.players if p.connected)
    return ret


def active_players() -> Tuple[player.Player]:
    ps = all_connected_players()
    return tuple(p for p in ps if p.is_playing)


async def wait_until_ready(
    *, timeout: Optional[float] = None, wait_if_no_node: Optional[int] = None
):
    if wait_if_no_node:
        for iteration in range(0, abs(wait_if_no_node), 1):
            if not node._nodes:
                await asyncio.sleep(1)
            else:
                break
    if not node._nodes:
        raise asyncio.TimeoutError
    for result in await asyncio.gather(
        *(
            node_.wait_until_ready(timeout)
            for node_ in node._nodes
            if (not node_.ready) and not node_.state == node.NodeState.DISCONNECTING
        ),
        return_exceptions=True,
    ):
        if result is not None:
            raise result

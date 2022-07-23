(
    importer := __import__("importlib").import_module,
    asyncio := importer("asyncio"),
    aiohttp := importer("aiohttp"),
    enum := importer("enum"),
    discord := importer("discord"),
    types := importer("types"),
    collections := importer("collections"),
    logging := importer("logging"),
    secrets := importer("secrets"),
    string := importer("string"),
    random := importer("random"),
    datetime := importer("datetime"),
    redbot := importer("redbot"),
    _sem_wrapper := importer("redbot.core.utils")._sem_wrapper,
    urllib := importer("urllib"),
    re := importer("re"),
    log := logging.getLogger("red.core.LL"),
    ws_ll_log := logging.getLogger("red.Audio.WS.LLNode"),
    socket_log := logging.getLogger("red.core.RLL.socket"),
    socket_log.setLevel(logging.INFO),
    ws_discord_log := logging.getLogger("red.Audio.WS.discord"),
    ws_rll_log := logging.getLogger("red.Audio.WS.RLL"),
    set_logging_level := lambda level=logging.INFO: (
        log.setLevel(level),
        ws_discord_log.setLevel(level),
        ws_ll_log.setLevel(level),
        ws_rll_log.setLevel(level),
    ),
    coro := lambda f: (
        y := types.coroutine(f),
        setattr(y, "__code__", (z := y.__code__).replace(co_flags=z.co_flags | 128)),
    )[0],
    throw := (_ for _ in ()).throw,
    a_try := coro(
        lambda t, *a, f=lambda a: a, e=Exception, other=lambda: ..., final=lambda: ..., **kw: (
            [r for globals()["r"] in [{}]][0]
        ).pop(
            "r",
            (
                yield from (
                    type(
                        "",
                        (),
                        {
                            "__call__": lambda self, func: coro(
                                lambda *a, **kw: (
                                    f := func(*a, **kw),
                                    (yield from _sem_wrapper(self, f)),
                                )[-1]
                            ),
                            "__aenter__": coro(lambda self: self),
                            "__aexit__": coro(
                                lambda self, *a: (
                                    (
                                        [
                                            r.update(
                                                r=(yield from discord.utils.maybe_coroutine(f, a))
                                            )
                                        ]
                                    )
                                    if isinstance(a[1], e)
                                    else (
                                        a[1] is None
                                        and (yield from discord.utils.maybe_coroutine(other))
                                    ),
                                    (yield from discord.utils.maybe_coroutine(final)),
                                )
                            ),
                        },
                    )()(t)(*a, **kw)
                )
            ),
        )
    ),
    s_try := lambda t, *a, f=lambda a: a, e=Exception, other=lambda: ..., final=lambda: ..., **k: (
        [r for globals()["r"] in [{}]][0]
    ).pop(
        "r",
        type(
            "",
            (__import__("contextlib").ContextDecorator,),
            {
                "__enter__": int,
                "__exit__": lambda s, *a: (
                    ([r.update(r=f(a))] if isinstance(a[1], e) else (a[1] is None and other())),
                    final(),
                ),
            },
        )()(t)(*a, **k),
    ),
    for_block := lambda iterator: (
        n := {"n": False},
        d := s_try(
            lambda: next(iterator),
            f=lambda a: None,
            e=StopIteration,
            other=lambda: n.update({"n": True}),
        ),
        (n["n"], d),
    )[-1],
    _nodes := [],
    PositionTime := collections.namedtuple("PositionTime", "position time connected"),
    MemoryInfo := collections.namedtuple("MemoryInfo", "reservable used free allocated"),
    CPUInfo := collections.namedtuple("CPUInfo", "cores systemLoad lavalinkLoad"),
    _PlaylistInfo := collections.namedtuple("PlaylistInfo", "name selectedTrack"),
    PlaylistInfo := lambda name=None, selectedTrack=None: _PlaylistInfo(
        name if name is not None else "Unknown", selectedTrack if selectedTrack is not None else -1
    ),
    _event_listeners := [],
    _update_listeners := [],
    _stats_listeners := [],
    _re_youtube_timestamp := re.compile(r"[&?]t=(\d+)s?"),
    _re_soundcloud_timestamp := re.compile(r"#t=(\d+):(\d+)s?"),
    _re_twitch_timestamp := re.compile(r"\?t=(\d+)h(\d+)m(\d+)s"),
    LavalinkEvents := enum.Enum(
        "LavalinkEvents",
        {
            "TRACK_END": "TrackEndEvent",
            "TRACK_EXCEPTION": "TrackExceptionEvent",
            "TRACK_STUCK": "TrackStuckEvent",
            "TRACK_START": "TrackStartEvent",
            "WEBSOCKET_CLOSED": "WebsocketClosedEvent",
            "FORCED_DISCONNECT": "ForcedDisconnectEvent",
            "QUEUE_END": "QueueEndEvent",
        },
    ),
    TrackEndReason := enum.Enum(
        "TrackEndReason",
        {
            "FINISHED": "FINISHED",
            "LOAD_FAILED": "LOAD_FAILED",
            "STOPPED": "STOPPED",
            "REPLACED": "REPLACED",
            "CLEANUP": "CLEANUP",
        },
    ),
    LavalinkIncomingOp := enum.Enum(
        "LavalinkIncomingOp", {"EVENT": "event", "PLAYER_UPDATE": "playerUpdate", "STATS": "stats"}
    ),
    LavalinkOutgoingOp := enum.Enum(
        "LavalinkOutgoingOp",
        {
            "VOICE_UPDATE": "voiceUpdate",
            "DESTROY": "destroy",
            "PLAY": "play",
            "STOP": "stop",
            "PAUSE": "pause",
            "SEEK": "seek",
            "VOLUME": "volume",
        },
    ),
    NodeState := enum.Enum(
        "NodeState", {"CONNECTING": 0, "READY": 1, "RECONNECTING": 2, "DISCONNECTING": 3}
    ),
    PlayerState := enum.Enum(
        "PlayerState",
        {
            "CREATED": -1,
            "CONNECTING": 0,
            "READY": 1,
            "NODE_BUSY": 2,
            "RECONNECTING": 3,
            "DISCONNECTING": 4,
        },
    ),
    LoadType := enum.Enum(
        "LoadType",
        {
            i: i
            for i in (
                "TRACK_LOADED",
                "PLAYLIST_LOADED",
                "SEARCH_RESULT",
                "NO_MATCHES",
                "LOAD_FAILED",
                "V2_COMPAT",
                "V2_COMPACT",
            )
        },
    ),
    ExceptionSeverity := enum.Enum(
        "ExceptionSeverity", {i: i for i in ("COMMON", "SUSPICIOUS", "FAULT")}
    ),
    RedLavalinkException := type("RedLavalink", (Exception,), {}),
    NodeException := type("NodeException", (RedLavalinkException,), {}),
    PlayerException := type("PlayerException", (RedLavalinkException,), {}),
    AbortingNodeConnection := type("AbortingNodeConnection", (NodeException,), {}),
    NodeNotReady := type("NodeNotReady", (NodeException,), {}),
    NodeNotFound := type("NodeNotFound", (NodeException,), {}),
    PlayerNotFound := type("PlayerNotFound", (PlayerException,), {}),
    RESTClient := type(
        "RESTClient",
        (),
        {
            "__init__": lambda self, client, channel: (
                None,
                setattr(self, "node", get_node()),
                setattr(self, "client", client),
                setattr(self, "state", PlayerState.CREATED),
                setattr(self, "channel", channel),
                setattr(self, "guild", channel.guild),
                setattr(self, "_last_channel_id", channel.id),
                setattr(self, "secured", self.node.secured),
                setattr(self, "_session", self.node.session),
                setattr(
                    self,
                    "_uri",
                    f"http{'s' if self.secured else ''}://{self.node.host}:{self.node.port}/loadtracks?identifier=",
                ),
                setattr(self, "_headers", {"Authorization": self.node.password}),
                setattr(self, "_warned", False),
            )[0],
            "__check_node_ready": lambda self: self.state != PlayerState.READY
            and throw(RuntimeError("Cannot execute REST request when node not ready.")),
            "_get": coro(
                lambda self, url: (
                    ret := {"ret": None},
                    (
                        yield from a_try(
                            coro(
                                lambda: (
                                    resp := (
                                        yield from self._session.get(
                                            url, headers=self._headers
                                        ).__await__()
                                    ),
                                    ret.__setitem__("ret", (yield from resp.json())),
                                    (yield from resp.release()),
                                )
                            ),
                            f=lambda a: (
                                ret.__setitem__(
                                    "ret",
                                    {
                                        "loadType": LoadType.LOAD_FAILED,
                                        "exception": {
                                            "message": "Load tracks interrupted by player disconnect.",
                                            "severity": ExceptionSeverity.COMMON,
                                        },
                                        "tracks": [],
                                    },
                                )
                                if self.state == PlayerState.DISCONNECTING
                                else (
                                    log.debug(
                                        "Received server disconnected error when player state = %s",
                                        self.state.name,
                                    ),
                                    throw(a[1]),
                                )
                            ),
                            e=aiohttp.client_exceptions.ServerDisconnectedError,
                        )
                    ),
                    ret["ret"],
                )[-1]
            ),
            "load_tracks": coro(
                lambda self, query: (
                    self.__check_node_ready(),
                    _raw_url := str(query),
                    parsed_url := reformat_query(_raw_url),
                    url := self._uri + urllib.parse.quote(parsed_url),
                    data := (yield from self._get(url)),
                    (
                        data.__setitem__("query", _raw_url),
                        data.__setitem__("encodedquery", url),
                        LoadResult(data),
                    )[-1]
                    if isinstance(data, dict)
                    else (
                        (
                            modified_data := {
                                "loadType": LoadType.V2_COMPAT,
                                "tracks": data,
                                "query": _raw_url,
                                "encodedquery": url,
                            }
                        )[-1]
                        if isinstance(data, list)
                        else None
                    ),
                )[-1]
            ),
            "get_tracks": coro(
                lambda self, query: (
                    not self._warned
                    and (
                        log.warn(
                            "get_tracks() is now deprecated. Please switch to using load_tracks()."
                        ),
                        setattr(self, "_warned", True),
                    ),
                    result := (yield from self.load_tracks(query)),
                    result.tracks,
                )[-1]
            ),
            "search_yt": coro(
                lambda self, query: (yield from self.load_tracks("ytsearch:{}".format(query)))
            ),
            "search_sc": coro(
                lambda self, query: (yield from self.load_tracks("scsearch:{}".format(query)))
            ),
        },
    ),
    initialize := coro(
        lambda bot, *, host, password, port=None, timeout=30, resume_key=None, resume_timeout=60, secured=False: (
            None,
            register_event_listener(_handle_event),
            register_update_listener(_handle_update),
            print("Creating node"),
            lavalink_node := Node(
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
            ),
            print("Node created"),
            (yield from lavalink_node.connect(timeout=timeout)),
            setattr(lavalink_node, "_retries", 0),
            bot.add_listener(_on_guild_remove, name="on_guild_remove"),
        )[
            0
        ]
    ),
    connect := coro(
        lambda channel, deafen=False: (
            node := get_node(channel.guild.id),
            p := (yield from node.create_player(channel, deafen=deafen)),
            p,
        )[-1]
    ),
    get_player := lambda guild_id: (node := get_node(guild_id), node.get_player(guild_id))[-1],
    _on_guild_remove := coro(
        lambda guild: (
            (
                yield from a_try(
                    coro(lambda: (p := get_player(guild.id), (yield from p.disconnect()))),
                    f=lambda a: ...,
                    e=(NodeNotFound, PlayerNotFound),
                )
            )
        )
    ),
    register_event_listener := lambda c: (
        throw(TypeError("Function is not a coroutine"))
        if not asyncio.iscoroutinefunction(c)
        else (_event_listeners.append(c) if c not in _event_listeners else ...)
    ),
    _handle_event := coro(
        lambda player, data, extra: (yield from player.handle_event(data, extra))
    ),
    _get_event_args := lambda data, raw_data: (
        guild_id := int(raw_data.get("guildId")),
        node_player := s_try(
            lambda: (get_node(guild_id, ignore_ready_status=True), get_player(guild_id)),
            f=lambda a: (
                log.debug(
                    "Got an event for a guild that we have no player for. This may because of a forced voice channel disconnect."
                )
                if data != LavalinkEvents.TRACK_END
                else ...
            ),
            e=(NodeNotFound, PlayerNotFound),
        ),
        (
            ...
            if not node_player
            else (
                node := node_player[0],
                player := node_player[1],
                extra := None,
                (
                    extra := TrackEndReason(raw_data.get("reason"))
                    if data == LavalinkEvents.TRACK_END
                    else (
                        exception_data := raw_data["exception"],
                        extra := {
                            "message": exception_data["message"],
                            "cause": exception_data["cause"],
                            "severity": ExceptionSeverity(exception_data["severity"]),
                        },
                    )
                ),
                (player, data, extra),
            )[-1]
        ),
    ),
    unregister_event_listener := lambda c: (
        s_try(lambda: _event_listeners.remove(c), f=lambda a: ..., e=ValueError)
    ),
    register_update_listener := lambda c: (
        throw(TypeError("Function is not a coroutine."))
        if not asyncio.iscoroutinefunction(c)
        else (_update_listeners.append(c) if c not in _update_listeners else ...)
    ),
    _handle_update := coro(
        lambda player, data, raw_data: (yield from player.handle_player_update(data))
    ),
    _get_update_args := lambda data, raw_data: (
        guild_id := int(raw_data.get("guildId")),
        player := s_try(
            lambda guild_id: get_player(guild_id),
            guild_id,
            f=lambda a: (
                log.debug(
                    "Got a player update for a guild that we have no player for. This may be because of a forced voice channel disconnect."
                ),
                None,
            )[-1],
            e=(NodeNotFound, PlayerNotFound),
        ),
        ((player, data, raw_data) if player else None),
    )[-1],
    unregister_update_listener := lambda c: (
        s_try(lambda: _update_listeners.remove(c), f=lambda a: ..., e=ValueError)
    ),
    register_stats_listener := lambda c: (
        throw(
            TypeError("Function is not a coroutine.")
            if not asyncio.iscoroutinefunction(c)
            else (_stats_listeners.append(c) if c not in _stats_listeners else ...)
        )
    ),
    unregister_stats_listener := lambda c: s_try(
        lambda: _stats_listeners.remove(c), f=lambda a: ..., e=ValueError
    ),
    dispatch := lambda op, data, raw_data: (
        listeners := [],
        args := [],
        (
            (listeners := _event_listeners, args := _get_event_args(data, raw_data))
            if op == LavalinkIncomingOp.EVENT
            else (
                (listeners := _update_listeners, args := _get_update_args(data, raw_data))
                if op == LavalinkIncomingOp.PLAYER_UPDATE
                else (
                    (listeners := _stats_listeners, args := [data])
                    if op == LavalinkIncomingOp.STATS
                    else ...
                )
            )
        ),
        ([asyncio.create_task(c(*args)) for c in listeners] if args is not None else ...),
    ),
    close := coro(
        lambda bot: (
            log.debug("Closing Lavalink connections"),
            unregister_event_listener(_handle_event),
            unregister_update_listener(_handle_update),
            bot.remove_listener(_on_guild_remove, name="on_guild_remove"),
            (yield from disconnect()),
            log.debug("All lavalink nodes have been disconnected"),
        )
    ),
    all_players := lambda: tuple(p for n in _nodes for p in n.players),
    all_connected_players := lambda: tuple(p for n in _nodes for p in n.players if p.connected),
    active_players := lambda: (
        ps := all_connected_players(),
        tuple(p for p in ps if p.is_playing),
    )[-1],
    wait_until_ready := coro(
        lambda *, timeout=None, wait_if_no_node=None: (
            (
                yield from a_try(
                    coro(
                        lambda: (
                            r := (x for x in range(0, abs(wait_if_no_node), 1)),
                            block := coro(
                                lambda: (
                                    not _nodes
                                    and (
                                        (yield from asyncio.sleep(1)),
                                        n := {"n": False},
                                        s_try(
                                            lambda: (next(r)),
                                            f=lambda a: ...,
                                            e=StopIteration,
                                            other=lambda: n.update({"n": True}),
                                        ),
                                        n["n"] and (yield from block()),
                                    )
                                )
                            ),
                            (yield from block()),
                        )
                    ),
                    f=lambda a: ...,
                    e=Exception,
                )
            )
            if wait_if_no_node is not None
            else ...,
            (throw(asyncio.TimeoutError) if not _nodes else ...),
            tuple(
                throw(result) if result else ...
                for result in (
                    yield from asyncio.gather(
                        *(
                            node_.wait_until_ready(timeout)
                            for node_ in _nodes
                            if (not node_.ready) and not node_.state == NodeState.DISCONNECTING
                        ),
                        return_exceptions=True,
                    )
                )
            ),
        )
    ),
    _Key := type(
        "_Key",
        (),
        {
            "__init__": lambda self, length=32: (
                None,
                setattr(self, "length", length),
                setattr(self, "persistent", ""),
                self.__repr__(),
            )[0],
            "__repr__": lambda self: (
                alphabet := string.ascii_letters + string.digits + "#$%&()*+,-./:;<=>?@[]^_~!",
                key := "".join(secrets.choice(alphabet) for _ in range(self.length)),
                setattr(self, "persistent", key),
                key,
            )[-1],
            "__str__": lambda self: (self.__repr__() if not self.persistent else self.persistent),
        },
    ),
    Stats := type(
        "Stats",
        (),
        {
            "__init__": lambda self, memory, players, active_players, cpu, uptime: (
                None,
                setattr(self, "memory", MemoryInfo(**memory)),
                setattr(self, "players", players),
                setattr(self, "active_players", active_players),
                setattr(self, "cpu_info", CPUInfo(**cpu)),
                setattr(self, "uptime", uptime),
            )[0]
        },
    ),
    NodeStats := type(
        "NodeStats",
        (),
        {
            "__init__": lambda self, data: (
                None,
                setattr(self, "uptime", data["uptime"]),
                setattr(self, "players", data["players"]),
                setattr(self, "playing_players", data["playingPlayers"]),
                memory := data["memory"],
                [
                    setattr(self, f"memory_{k}", memory[k])
                    for k in ("free", "used", "allocated", "reservable")
                ],
                cpu := data["cpu"],
                setattr(self, "cpu_cores", cpu["cores"]),
                setattr(self, "system_load", cpu["systemLoad"]),
                setattr(self, "lavalink_load", cpu["lavalinkLoad"]),
                frame_stats := data.get("frameStats", {}),
                tuple(
                    setattr(self, f"frame_{k}", frame_stats.get(k, -1))
                    for k in ("sent", "nulled", "deficit")
                ),
            )[0],
            "__repr__": lambda self: f"<NodeStats: uptime={self.uptime}, players={self.players}, playing_players={self.playing_players}, memory_free={self.memory_free}, memory_used={self.memory_used}, cpu_cores={self.cpu_cores}, system_load={self.system_load}, lavalink_load={self.lavalink_load}>",
        },
    ),
    Node := type(
        "Node",
        (),
        {
            "_is_shutdown": False,
            "__init__": lambda self, *, event_handler, host, password, user_id, num_shards, port=None, resume_key=None, resume_timeout=60.0, bot=None, secured=False: (
                None,
                setattr(self, "bot", bot),
                setattr(self, "_queue", []),
                setattr(self, "event_handler", event_handler),
                setattr(self, "host", host),
                setattr(self, "secured", secured),
                setattr(self, "port", port if port is not None else (443 if self.secured else 80)),
                setattr(self, "password", password),
                setattr(self, "_resume_key", resume_key if resume_key else self._gen_key()),
                setattr(self, "_resume_timeout", resume_timeout),
                setattr(self, "_resuming_configured", False),
                setattr(self, "num_shards", num_shards),
                setattr(self, "user_id", user_id),
                setattr(self, "_ready_event", asyncio.Event()),
                setattr(self, "_ws", None),
                setattr(self, "_listener_task", None),
                setattr(self, "session", aiohttp.ClientSession()),
                setattr(self, "reconnect_task", None),
                setattr(self, "try_connect_task", None),
                setattr(self, "queue", []),
                setattr(self, "_players_dict", {}),
                setattr(self, "state", NodeState.CONNECTING),
                setattr(self, "_state_handlers", []),
                setattr(self, "_retries", 0),
                setattr(self, "stats", None),
                (_nodes.append(self) if self not in _nodes else ...),
                setattr(
                    self,
                    "_closers",
                    tuple(getattr(aiohttp.WSMsgType, x) for x in ("CLOSE", "CLOSED", "CLOSING")),
                ),
                self.register_state_handler(self.node_state_handler),
            )[
                0
            ],
            "__repr__": lambda self: f"<Node: state={self.state}, host={self.host}, port={self.port}, password={'*' * len(self.password)}, resume_key={self._resume_key}, shards={self.num_shards}, user={self.user_id}, stats={self.stats}>",
            "headers": property(lambda self: self._get_connect_headers()),
            "players": property(lambda self: self._players_dict.values()),
            "guild_ids": property(lambda self: self._players_dict.keys()),
            "_gen_key": lambda self: (
                _Key()
                if self._resume_key is None
                else (self._resume_key.__repr__(), self._resume_key)[-1]
            ),
            "connect": coro(
                lambda self, timeout=None, *, shutdown=False: (
                    setattr(self, "_shutdown", shutdown),
                    uri := f"ws{'s' if self.secured else ''}://{self.host}:{self.port}",
                    ws_ll_log.info(
                        "Lavalink WS connecting to %s with headers %s", uri, self.headers
                    ),
                    (self.try_connect_task.cancel() if self.try_connect_task is not None else ...),
                    setattr(
                        self, "try_connect_task", asyncio.create_task(self._multi_try_connect(uri))
                    ),
                    (
                        yield from a_try(
                            coro(
                                lambda: (
                                    yield from asyncio.wait_for(
                                        self.try_connect_task, timeout=timeout
                                    )
                                )
                            ),
                            f=lambda: throw(AbortingNodeConnection),
                            e=asyncio.CancelledError,
                        )
                    ),
                )
            ),
            "_configure_resume": coro(
                lambda self: (
                    ...
                    if self._resuming_configured
                    else (
                        (
                            yield from self.send(
                                dict(
                                    op="configureResuming",
                                    key=str(self._resume_key),
                                    timeout=self._resume_timeout,
                                )
                            )
                        ),
                        setattr(self, "_resuming_configured", True),
                        ws_ll_log.debug("Node Resuming has been configured."),
                    )
                    if self._resume_key and self._resume_timeout and self._resume_timeout > 0
                    else ...
                )
            ),
            "wait_until_ready": coro(
                lambda self, *, timeout=None: (
                    yield from asyncio.wait_for(self._ready_event.wait(), timeout=timeout)
                )
            ),
            "_get_connect_headers": lambda self: (
                headers := {
                    "Authorization": self.password,
                    "User-Id": str(self.user_id),
                    "Num-Shards": str(self.num_shards),
                    "Client-Name": f"Red-Lavalink/{__version__}",
                },
                (
                    headers.__setitem__("Resume-Key", str(self._resume_key))
                    if self._resume_key
                    else ...
                ),
                headers,
            )[-1],
            "lavalink_major_version": property(
                lambda self: (
                    throw(NodeNotReady("Node not ready!"))
                    if not self.ready
                    else self._ws.response_headers.get("Lavalink-Major-Version")
                )
            ),
            "ready": property(lambda self: self.state == NodeState.READY),
            "_multi_try_connect": coro(
                lambda self, uri: (
                    backoff := discord.backoff.ExponentialBackoff(),
                    attempt := {"attempt": 1},
                    (self._listener_task.cancel() if self._listener_task is not None else ...),
                    (
                        (yield from self._ws.close(code=4006, message=b"Reconnecting"))
                        if self._ws is not None
                        else ...
                    ),
                    while_block := coro(
                        lambda: (
                            setattr(self, "_retries", self._retries + 1),
                            (
                                (
                                    ws_ll_log.error(
                                        "Lavalink node was shutdown during a connect attempt."
                                    ),
                                    throw(asyncio.CancelledError),
                                )
                                if self._shutdown is True
                                else ...
                            ),
                            breaker := False,
                            (
                                yield from a_try(
                                    coro(
                                        lambda: (
                                            ws_rll_log.debug(f"{uri = }, {self.headers = }"),
                                            ws := (
                                                yield from self.session.ws_connect(
                                                    url=uri, headers=self.headers, heartbeat=60
                                                )
                                            ),
                                            (
                                                (
                                                    ws_ll_log.error(
                                                        "Lavalink node was shutdown during a connect attempt."
                                                    ),
                                                    throw(asyncio.CancelledError),
                                                )
                                                if self._shutdown is True
                                                else ...
                                            ),
                                            setattr(
                                                self,
                                                "session_resumed",
                                                ws._response.headers.get("Session-Resumed", False),
                                            ),
                                            (
                                                ws_ll_log.info(
                                                    "WEBSOCKET Resumed Session with key: %s",
                                                    self._resume_key,
                                                )
                                                if self._ws is not None and self.session_resumed
                                                else ...
                                            ),
                                            setattr(self, "_ws", ws),
                                            breaker := True,
                                        )
                                    ),
                                    f=coro(
                                        lambda a: (
                                            exc := a[1],
                                            ws_rll_log.exception(f"Failed to connect, {a = }"),
                                            (
                                                (
                                                    throw(asyncio.TimeoutError)
                                                    if attempt["attempt"] > 5
                                                    else (
                                                        delay := backoff.delay(),
                                                        ws_ll_log.warning(
                                                            "Failed connect attempt %s, retrying in %s",
                                                            attempt["attempt"],
                                                            delay,
                                                        ),
                                                        (yield from asyncio.sleep(delay)),
                                                        attempt.update(
                                                            {"attempt": attempt["attempt"] + 1}
                                                        ),
                                                    )
                                                )
                                                if isinstance(
                                                    exc, (OSError, aiohttp.ClientConnectionError)
                                                )
                                                else (
                                                    ws_ll_log.error(
                                                        "Failed connect WSServerHandshakeError"
                                                    ),
                                                    throw(asyncio.TimeoutError),
                                                )
                                            ),
                                        )
                                    ),
                                    e=(
                                        OSError,
                                        aiohttp.ClientConnectionError,
                                        aiohttp.WSServerHandshakeError,
                                    ),
                                )
                            ),
                            (
                                self._shutdown is False
                                and (self._ws is None or self._ws.closed)
                                and breaker is False
                            )
                            and (yield from while_block()),
                        )
                    ),
                    (yield from while_block()),
                    (throw(asyncio.CancelledError) if self._shutdown is True else ...),
                    ws_ll_log.info("Lavalink WS connected to %s", uri),
                    ws_ll_log.debug("Creating Lavalink WS listener."),
                    (
                        yield from a_try(
                            coro(
                                lambda: (
                                    (
                                        setattr(
                                            self,
                                            "_listener_task",
                                            asyncio.create_task(self.listener()),
                                        ),
                                        asyncio.create_task(self._configure_resume()),
                                        (
                                            (
                                                temp := self._queue.copy(),
                                                self._queue.clear(),
                                                (
                                                    n := (x for x in temp),
                                                    b := coro(
                                                        lambda data: (
                                                            (yield from self.send(data)),
                                                            m := for_block(n),
                                                            m[0] and (yield from b(m[1])),
                                                        )
                                                    ),
                                                    m := for_block(n),
                                                    m[0] and (yield from b(m[1])),
                                                ),
                                            )
                                            if self._queue
                                            else ...
                                        ),
                                        self._ready_event.set(),
                                        self.update_state(NodeState.READY),
                                    )
                                    if self._is_shutdown is False
                                    else ...
                                )
                            ),
                            f=lambda a: ws_ll_log.debug("Error with that", exc_info=a[2]),
                        )
                    ),
                )
            ),
            "listener": coro(
                lambda self: (
                    (
                        while_block := coro(
                            lambda: (
                                (
                                    msg := (yield from self._ws.receive()),
                                    returner := False,
                                    breaker := False,
                                    (
                                        (
                                            self.state != NodeState.RECONNECTING
                                            and (
                                                (
                                                    self.reconnect_task is not None
                                                    and (self.reconnect_task.cancel()),
                                                    ws_ll_log.info(
                                                        "[NODE] | NODE Resuming: %s", msg.extra
                                                    ),
                                                    self.update_state(NodeState.RECONNECTING),
                                                    setattr(
                                                        self,
                                                        "reconnect_task",
                                                        asyncio.create_task(
                                                            self._reconnect(
                                                                shutdown=self._is_shutdown
                                                            )
                                                        ),
                                                    ),
                                                ),
                                                returner := True,
                                            )
                                        )
                                        if self._resuming_configured
                                        else (
                                            ws_ll_log.info(
                                                "[NODE] | Listener closing: %s", msg.extra
                                            ),
                                            breaker := True,
                                        )
                                        if msg.type in self._closers
                                        else (
                                            (
                                                data := msg.json(),
                                                s_try(
                                                    lambda: (
                                                        op := LavalinkIncomingOp(data.get("op")),
                                                        ws_ll_log.trace(
                                                            "[NODE] | Received known op: %s", data
                                                        ),
                                                        asyncio.create_task(
                                                            self._handle_op(op, data)
                                                        ),
                                                    ),
                                                    f=lambda a: ws_ll_log.verbose(
                                                        "[NODE] | Received unknown op: %s", data
                                                    ),
                                                    e=ValueError,
                                                ),
                                            )
                                            if msg.type == aiohttp.WSMsgType.TEXT
                                            else (
                                                (
                                                    exc := self._ws.exception(),
                                                    ws_ll_log.warning(
                                                        "[NODE] | An exception occurred on the websocket - Attempting to reconnect"
                                                    ),
                                                    ws_ll_log.debug(
                                                        "[NODE] | Exception in WebSocket!",
                                                        exc_info=exc,
                                                    ),
                                                    breaker := True,
                                                )
                                                if msg.type == aiohttp.WSMsgType.ERROR
                                                else (
                                                    ws_ll_log.debug(
                                                        "[NODE] | WebSocket connection received unexpected message: %s:%s",
                                                        msg.type,
                                                        msg.data,
                                                    )
                                                )
                                            )
                                        )
                                    ),
                                ),
                                (
                                    self._shutdown is False
                                    and breaker is False
                                    and returner is False
                                )
                                and (yield from while_block()),
                            )
                        ),
                        (yield from while_block()),
                    ),
                    (
                        self.state != NodeState.RECONNECTING
                        and not self._is_shutdown
                        and not returner
                    )
                    and (
                        ws_ll_log.warning(
                            "[NODE] | %s - WS %s SHUTDOWN %s.",
                            self,
                            not self._ws.closed,
                            self._is_shutdown,
                        ),
                        (self.reconnect_task is not None and self.reconnect_task.cancel()),
                        self.update_state(NodeState.RECONNECTING),
                        setattr(
                            self,
                            "reconnect_task",
                            asyncio.create_task(self._reconnect(shutdown=self._is_shutdown)),
                        ),
                    ),
                )
            ),
            "_handle_op": coro(
                lambda self, op, data: (
                    (
                        event := [],
                        s_try(
                            lambda: event.append(LavalinkEvents(data.get("type"))),
                            f=lambda a: ws_ll_log.verbose("Unknown event type: %s", data),
                            e=ValueError,
                            other=lambda: self.event_handler(op, event[0], data),
                        ),
                    )
                    if op == LavalinkIncomingOp.EVENT
                    else (
                        (
                            state := data.get("state", {}),
                            position := PositionTime(
                                position=state.get("position", 0),
                                time=state.get("time", 0),
                                connected=state.get("connected", False),
                            ),
                            self.event_handler(op, position, data),
                        )
                        if op == LavalinkIncomingOp.PLAYER_UPDATE
                        else (
                            (
                                stats := Stats(
                                    memory=data.get("memory"),
                                    players=data.get("players"),
                                    active_players=data.get("playingPlayers"),
                                    cpu=data.get("cpu"),
                                    uptime=data.get("uptime"),
                                ),
                                setattr(self, "stats", NodeStats(data)),
                                self.event_handler(op, stats, data),
                            )
                            if op == LavalinkIncomingOp.STATS
                            else ws_ll_log.verbose("Unknown op type: %r", data)
                        )
                    )
                )
            ),
            "_reconnect": coro(
                lambda self, *, shutdown=False: (
                    self._ready_event.clear(),
                    (
                        ws_ll_log.info("[NODE] | Shutting down Lavalink WS.")
                        if self._is_shutdown is True or shutdown
                        else (
                            (
                                self.state != NodeState.CONNECTING
                                and self.update_state(NodeState.RECONNECTING)
                            ),
                            (
                                ...
                                if self.state != NodeState.RECONNECTING
                                else (
                                    backoff := discord.backoff.ExponentialBackoff(base=1),
                                    attempt := {"attempt": 1},
                                    returner := False,
                                    breaker := False,
                                    (
                                        while_block := coro(
                                            lambda: (
                                                attempt.update(
                                                    {"attempt": attempt["attempt"] + 1}
                                                ),
                                                (
                                                    ws_ll_log.info(
                                                        "[NODE] | Failed reconnection attempt too many times, aborting ..."
                                                    ),
                                                    asyncio.create_task(self.disconnect()),
                                                    returner := True,
                                                )
                                                if attempt["attempt"] > 10
                                                else (
                                                    (
                                                        yield from a_try(
                                                            coro(
                                                                lambda: (
                                                                    yield from self.connect(
                                                                        shutdown=shutdown
                                                                    )
                                                                )
                                                            ),
                                                            f=lambda a: (
                                                                (returner := True)
                                                                if isinstance(
                                                                    a[1], AbortingNodeConnection
                                                                )
                                                                else (
                                                                    delay := backoff.delay(),
                                                                    ws_ll_log.warning(
                                                                        "[NODE] | Lavalink WS reconnect attempt %s, retrying in %s",
                                                                        attempt["attempt"],
                                                                        delay,
                                                                    ),
                                                                    (
                                                                        yield from asyncio.sleep(
                                                                            delay
                                                                        )
                                                                    ),
                                                                )
                                                            ),
                                                            other=lambda: (
                                                                ws_ll_log.info(
                                                                    "[NODE] | Reconnect successful"
                                                                ),
                                                                self.dispatch_reconnect(),
                                                                setattr(self, "_retries", 0),
                                                            ),
                                                        )
                                                    )
                                                ),
                                            ),
                                            (
                                                lambda: self.state == NodeState.RECONNECTING
                                                and breaker is False
                                                and returner is False
                                            )
                                            and (yield from while_block()),
                                        ),
                                        (yield from while_block()),
                                    ),
                                )
                            ),
                        )
                    ),
                )
            ),
            "dispatch_reconnect": lambda self: [
                self.event_handler(
                    LavalinkIncomingOp.EVENT,
                    LavalinkEvents.WEBSOCKET_CLOSED,
                    {
                        "guildId": guild_id,
                        "code": 42069,
                        "reason": "Lavalink WS reconnected",
                        "byRemote": True,
                        "retries": self._retries,
                    },
                )
                for guild_id in self.guild_ids
            ],
            "update_state": lambda self, next_state: (
                ...
                if next_state == self.state
                else (
                    ws_ll_log.verbose(
                        "Changing node state: %s -> %s", self.state.name, next_state.name
                    ),
                    old_state := self.state,
                    setattr(self, "state", next_state),
                    (
                        ws_ll_log.debug("Event loop closed, not notifying state handlers.")
                        if is_loop_closed()
                        else tuple(
                            asyncio.create_task(handler(next_state, old_state))
                            for handler in self._state_handlers
                        )
                    ),
                )
            ),
            "register_state_handler": lambda self, func: (
                (
                    not asyncio.iscoroutinefunction(func)
                    and throw(ValueError("Argument must be a coroutine object."))
                ),
                func not in self._state_handlers and self._state_handlers.append(func),
            ),
            "unregister_state_handler": lambda self, func: self._state_handlers.remove(func),
            "create_player": coro(
                lambda self, channel, *, deafen=False: (
                    (
                        player := self.get_player(channel.guild.id),
                        (yield from player.move_to(channel, deafen=deafen)),
                    )
                    if self._already_in_guild(channel)
                    else (
                        player := (yield from channel.connect(cls=Player)),
                        deafen is True
                        and (
                            yield from player.guild.change_voice_state(
                                channel=player.channel, self_deaf=True
                            )
                        ),
                    ),
                    player,
                )[-1]
            ),
            "_already_in_guild": lambda self, channel: channel.guild.id in self._players_dict,
            "get_player": lambda self, guild_id: (
                self._players_dict[guild_id]
                if guild_id in self._players_dict
                else throw(NoPlayerFound("No such player for that guild."))
            ),
            "node_state_handler": coro(
                lambda self, next_state, old_state: (
                    ws_rll_log.debug(
                        "Received node state update: %s -> %s", old_state.name, next_state.name
                    ),
                    state := (
                        PlayerState.READY
                        if next_state == NodeState.READY
                        else PlayerState.DISCONNECTING
                        if next_state == NodeState.DISCONNECTING
                        else PlayerState.NODE_BUSY
                        if next_state in (NodeState.CONNECTING, NodeState.RECONNECTING)
                        else None
                    ),
                    state is not None and (yield from self.update_player_states(state)),
                )
            ),
            "update_player_states": coro(
                lambda self, state: (
                    i := (x for x in self.players),
                    b := coro(
                        lambda player: (
                            (yield from player.update_state(state)),
                            m := for_block(i),
                            m[0] and (yield from b(m[1])),
                        )
                    ),
                    (yield from b(next(i))),
                )
            ),
            "refresh_player_state": coro(
                lambda self, player: (
                    state := (
                        PlayerState.READY
                        if self.ready
                        else PlayerState.DISCONNECTING
                        if self.state == NodeState.DISCONNECTING
                        else PlayerState.NODE_BUSY
                    ),
                    (yield from player.update_state(state)),
                )
            ),
            "remove_player": lambda self, player: (
                (
                    log.error(
                        "Attempting to remove a player (%r) from player list with state %s",
                        player,
                        player.state.name,
                    )
                )
                if player.state != PlayerState.DISCONNECTING
                else (
                    guild_id := player.channel.guild.id,
                    guild_id in self._players_dict and self._players_dict.__delitem__(guild_id),
                )
            ),
            "disconnect": coro(
                lambda self: (
                    setattr(self, "_is_shutdown", True),
                    self._ready_event.clear(),
                    self._queue.clear(),
                    (
                        self.try_connect_task is not None
                        and not self.try_connect_task.cancelled()
                        and not is_loop_closed()
                    )
                    and self.try_connect_task.cancel(),
                    (
                        self.reconnect_task is not None
                        and not self.reconnect_task.cancelled()
                        and not is_loop_closed()
                    )
                    and self.reconnect_task.cancel(),
                    self.update_state(NodeState.DISCONNECTING),
                    (self._resuming_configured and not (self._ws is None or self._ws.closed))
                    and (yield from self.send(dict(op="configureResuming", key=None))),
                    setattr(self, "_resuming_configured", False),
                    (
                        i := (x for x in tuple(self.players)),
                        b := coro(
                            lambda p: (
                                (yield from p.disconnect(force=True)),
                                m := for_block(i),
                                m[0] and (yield from b(m[1])),
                            )
                        ),
                        (yield from b(next(i))),
                    ),
                    log.debug("Disconnected all players"),
                    (self._ws is not None and not self._ws.closed)
                    and (yield from self._ws.close()),
                    (
                        self._listener_task is not None
                        and not self._listener_task.cancelled()
                        and not is_loop_closed
                    )
                    and self._listener_task.cancel(),
                    (yield from self.session.close()),
                    setattr(self, "_state_handlers", []),
                    (globals().update(_nodes=[]) if len(_nodes) == 1 else _nodes.remove(self)),
                    ws_ll_log.info("Shutdown Lavalink WS"),
                )
            ),
            "send": coro(
                lambda self, data: (
                    self._queue.append(data)
                    if self._ws is None or self._ws.closed
                    else (
                        ws_ll_log.trace("Sending data to Lavalink node: %s", data),
                        (yield from self._ws.send_json(data)),
                    )
                )
            ),
            "send_lavalink_voice_update": coro(
                lambda self, guild_id, session_id, event: (
                    yield from self.send(
                        {
                            "op": LavalinkOutgoingOp.VOICE_UPDATE.value,
                            "guildId": str(guild_id),
                            "sessionId": session_id,
                            "event": event,
                        }
                    )
                )
            ),
            "destroy_guild": coro(
                lambda self, guild_id: (
                    yield from self.send(
                        {"op": LavalinkOutgoingOp.DESTROY.value, "guildId": str(guild_id)}
                    )
                )
            ),
            "no_event_stop": coro(
                lambda self, guild_id: (
                    yield from self.send(
                        {"op": LavalinkOutgoingOp.STOP.value, "guildId": str(guild_id)}
                    )
                )
            ),
            "stop": coro(
                lambda self, guild_id: (
                    (yield from self.no_event_stop(guild_id=guild_id)),
                    self.event_handler(
                        LavalinkIncomingOp.EVENT,
                        LavalinkEvents.QUEUE_END,
                        {"guildId": str(guild_id)},
                    ),
                )
            ),
            "no_stop_play": coro(
                lambda self, guild_id, track, replace=True, start=0, pause=False: (
                    yield from self.send(
                        {
                            "op": LavalinkOutgoingOp.PLAY.value,
                            "guildId": str(guild_id),
                            "track": track.track_identifier,
                            "noReplace": not replace,
                            "startTime": str(start),
                            "pause": pause,
                        }
                    )
                )
            ),
            "play": coro(
                lambda self, guild_id, track, replace=True, start=0, pause=False: (
                    yield from self.no_stop_play(
                        guild_id=guild_id, track=track, replace=replace, start=start, pause=pause
                    )
                )
            ),
            "pause": coro(
                lambda self, guild_id, paused: (
                    yield from self.send(
                        {
                            "op": LavalinkOutgoingOp.PAUSE.value,
                            "guildId": str(guild_id),
                            "pause": paused,
                        }
                    )
                )
            ),
            "volume": coro(
                lambda self, guild_id, _volume: (
                    yield from self.send(
                        {
                            "op": LavalinkOutgoingOp.VOLUME.value,
                            "guildId": str(guild_id),
                            "volume": _volume,
                        }
                    )
                )
            ),
            "seek": coro(
                lambda self, guild_id, position: (
                    yield from self.send(
                        {
                            "op": LavalinkOutgoingOp.SEEK.value,
                            "guildId": str(guild_id),
                            "position": position,
                        }
                    )
                )
            ),
        },
    ),
    get_node := lambda guild_id=None, *, ignore_ready_status=False: (
        guild_count := 1e10,
        least_used := None,
        breaker := False,
        [
            (
                guild_ids := node.guild_ids,
                (
                    ...
                    if ignore_ready_status is False and not node.ready
                    else (
                        (guild_count := len(guild_ids), least_used := node)
                        if len(guild_ids) < guild_count
                        else ...
                    )
                ),
                guild_id in guild_ids and (breaker := True, least_used := node),
            )
            for node in _nodes
            if breaker is not True
        ],
        least_used,
    )[-1],
    get_node_stats := lambda: [node.stats for node in _nodes],
    get_all_nodes := lambda: [node for node in _nodes],
    disconnect := coro(
        lambda: (
            i := (x for x in _nodes.copy()),
            b := coro(
                lambda node: (
                    (yield from node.disconnect()),
                    m := for_block(i),
                    m[0] and (yield from b(m[1])),
                )
            ),
            (yield from b(next(i))),
        )
    ),
    Player := type(
        "Player",
        (RESTClient, discord.voice_client.VoiceProtocol),
        {
            "__init__": lambda self, client, channel: (
                None,
                [
                    setattr(self, x, False)
                    for x in (
                        "_paused",
                        "repeat",
                        "shuffle",
                        "_is_autoplaying",
                        "_auto_play_sent",
                        "_connected",
                        "_is_playing",
                    )
                ],
                [
                    setattr(self, x, None)
                    for x in (
                        "current",
                        "connected_at",
                        "_con_delay",
                        "_last_resume",
                        "_session_id",
                        "_pending_server_update",
                    )
                ],
                setattr(self, "position", 0),
                setattr(self, "shuffle_bumped", True),
                setattr(self, "_metadata", {}),
                setattr(self, "queue", []),
                setattr(self, "_volume", 100),
                super(Player, self).__init__(client=client, channel=channel),
            )[0],
            "__repr__": lambda self: (
                f"<Player: state={self.state.name}, connected={self.connected}, guild={self.guild.name!r} ({self.guild.id}), channel={self.channel.name!r} ({self.channel.id}), playing={self.is_playing}, paused={self.paused}, volume={self.volume}, queue_size={len(self.queue)}, current={self.current!r}, position={self.position}, length={self.current.length if self.current else 0}, node={self.node!r}>"
            ),
            "is_auto_playing": property(
                lambda self: self._is_playing and not self._paused and self._is_autoplaying
            ),
            "is_playing": property(
                lambda self: self._is_playing and not self._paused and self._connected
            ),
            "paused": property(lambda self: self._paused),
            "volume": property(lambda self: self._volume),
            "ready": property(lambda self: self.node.ready),
            "connected": property(lambda self: self._connected),
            "on_voice_server_update": coro(
                lambda self, data: (
                    setattr(self, "_pending_server_update", data),
                    (yield from self._send_lavalink_voice_update()),
                )
            ),
            "on_voice_state_update": coro(
                lambda self, data: (
                    setattr(self, "_session_id", data["session_id"]),
                    (
                        (
                            ws_rll_log.info(
                                "Received voice disconnect from discord, removing player."
                            ),
                            ws_rll_log.verbose(
                                "Voice disconnect from discord: %s -  %r", data, self
                            ),
                            [
                                setattr(self, x, None)
                                for x in ("_session_id", "_pending_server_update")
                            ],
                            (yield from self.disconnect(force=True)),
                        )
                        if (channel_id := data["channel_id"]) is not None
                        else (
                            channel := self.guild.get_channel(int(channel_id)),
                            channel != self.channel
                            and (
                                self.channel
                                and setattr(self, "_last_channel_id", self.channel.id),
                                channel is None
                                and (
                                    [
                                        setattr(self, x, None)
                                        for x in ("_session_id", "_pending_server_update")
                                    ],
                                    ws_rll_log.verbose(
                                        "Voice disconnect from discord (Deleted VC): %s -  %r",
                                        data,
                                        self,
                                    ),
                                    setattr(self, "channel", channel),
                                ),
                            ),
                        )
                    ),
                    (yield from self._send_lavalink_voice_update()),
                )
            ),
            "_send_lavalink_voice_update": coro(
                lambda self: (
                    ...
                    if self._session_id is None or self._pending_server_update is None
                    else (
                        data := self._pending_server_update,
                        setattr(self, "_pending_server_update", None),
                        (
                            yield from self.node.send(
                                {
                                    "op": LavalinkOutgoingOp.VOICE_UPDATE.value,
                                    "guildId": str(self.guild.id),
                                    "sessionId": self._session_id,
                                    "event": data,
                                }
                            )
                        ),
                    )
                )
            ),
            "wait_until_ready": coro(
                lambda self, *, timeout=None, no_raise=False: (
                    True
                    if self.node.ready
                    else (
                        ret := {"ret": False},
                        maybe := (
                            yield from a_try(
                                coro(
                                    lambda: (
                                        yield from self.node.wait_until_ready(timeout=timeout)
                                    )
                                ),
                                f=lambda a: throw(a[1])
                                if not no_raise
                                else ret.__setitem__("ret", False),
                            )
                        ),
                        maybe or ret["ret"],
                    )[-1]
                )
            ),
            "connect": coro(
                lambda self, *, timeout=2.0, reconnect=False, deafen=False: (
                    [
                        setattr(self, x, datetime.datetime.now(datetime.timezone.utc))
                        for x in ("_last_resume", "connected_at")
                    ],
                    setattr(self, "_connected", True),
                    self.node._players_dict.__setitem__(self.guild.id, self),
                    (yield from self.node.refresh_player_state(self)),
                    (
                        yield from self.guild.change_voice_state(
                            channel=-self.channel, self_mute=False, self_deafen=deafen
                        )
                    ),
                )
            ),
            "move_to": coro(
                lambda self, channel, *, deafen=False: (
                    channel.guild != self.guild
                    and throw(TypeError(f"Cannot move {self!r} to a different guild.")),
                    self.channel and setattr(self, "_last_channel_id", self.channel.id),
                    setattr(self, "channel", channel),
                    (yield from self.connect(deafen=deafen)),
                    self.current
                    and (
                        yield from self.resume(
                            track=self.current,
                            replace=True,
                            start=self.position,
                            pause=self._paused,
                        )
                    ),
                )
            ),
            "disconnect": coro(
                lambda self, *, force=False: (
                    [
                        setattr(self, x, False)
                        for x in (
                            "_is_autoplaying",
                            "_is_playing",
                            "_auto_play_sent",
                            "_connected",
                        )
                    ],
                    ...
                    if self.state == PlayerState.DISCONNECTING
                    else (
                        (yield from self.update_state(PlayerState.DISCONNECTING)),
                        guild_id := self.guild.id,
                        force
                        and (
                            log.verbose(
                                "Forcing player disconnect for %r due to player manager request.",
                                self,
                            ),
                            self.node.event_handler(
                                LavalinkIncomingOp.EVENT,
                                LavalinkEvents.FORCED_DISCONNECT,
                                {
                                    "guildId": guild_id,
                                    "code": 42069,
                                    "reason": "Forced Disconnect - Do not Reconnect",
                                    "byRemote": True,
                                    "retries": -1,
                                },
                            ),
                        ),
                        not self.client.shards[self.guild.shard_id].is_closed()
                        and (yield from self.guild.change_voice_state(channel=None)),
                        (yield from self.node.destroy_guild(guild_id)),
                        self.node.remove_player(self),
                        self.cleanup(),
                    ),
                )
            ),
            "store": lambda self, key, value: self._metadata.__setitem__(key, value),
            "fetch": lambda self, key, default=None: self._metadata.get(key, default),
            "update_state": coro(
                lambda self, state: (
                    ...
                    if state == self.state
                    else (
                        ws_rll_log.trace(
                            "Player %r changing state: %s -> %s", self, self.state.name, state.name
                        ),
                        setattr(self, "state", state),
                        self._con_delay and setattr(self, "_con_delay", None),
                    )
                )
            ),
            "handle_event": coro(
                lambda self, event, extra: (
                    log.trace(
                        "Received player event for player: %r - %r - %r.", self, event, extra
                    ),
                    (extra == TrackEndReason.FINISHED and (yield from self.play()))
                    if event == LavalinkEvents.TRACK_END
                    else (
                        (
                            code := extra.get("code"),
                            (code in (4015, 4014, 4009, 4006, 4000, 1006) and not self._con_delay)
                            and setattr(
                                self, "_con_delay", discord.backoff.ExponentialBackoff(base=1)
                            ),
                        )
                        if event == LavalinkEvents.WEBSOCKET_CLOSED
                        else ...
                    ),
                )
            ),
            "handle_player_update": coro(
                lambda self, state: (
                    state.position > self.position and setattr(self, "_is_playing", True),
                    log.trace(
                        "Updated player position for player: %r - %ds.",
                        self,
                        state.position // 1000,
                    ),
                    setattr(self, "position", state.position),
                )
            ),
            "add": lambda self, requester, track: (
                setattr(track, "requester", requester),
                self.queue.append(track),
            ),
            "maybe_shuffle": lambda self, stick_songs=1: (self.shuffle and self.queue)
            and self.force_shuffle(stick_songs),
            "force_shuffle": lambda self, stick_songs=1: (
                ...
                if not self.queue
                else (
                    sticky := max(0, sticky_songs),
                    (
                        (to_keep := self.queue[:sticky], to_shuffle := self.queue[sticky:])
                        if sticky > 0
                        else (to_shuffle := self.queue, to_keep := [])
                    ),
                    not self.shuffle_bumped
                    and (
                        to_keep_bumped := [t for t in to_shuffle if t.extras.get("bumped", None)],
                        to_shuffle := [t for t in to_shuffle if not t.extras.get("bumped", None)],
                        to_keep.extend(to_keep_bumped),
                    ),
                    random.shuffle(to_shuffle),
                    to_keep.extend(to_shuffle),
                    setattr(self, "queue", to_keep),
                )
            ),
            "play": coro(
                lambda self: (
                    (self.repeat and self.current is not None) and self.queue.append(self.current),
                    setattr(self, "current", None),
                    setattr(self, "position", 0),
                    setattr(self, "_paused", False),
                    (yield from self.stop())
                    if not self.queue
                    else (
                        setattr(self, "_is_playing", True),
                        track := self.queue.pop(0),
                        setattr(self, "current", track),
                        log.verbose("Assigned current track for player: %r.", self),
                        (
                            yield from self.node.play(
                                self.guild.id, track, start=track.start_timestamp, replace=True
                            )
                        ),
                    ),
                )
            ),
            "resume": coro(
                lambda self, track, *, replace=True, start=0, pause=False: (
                    log.verbose("Resuming current track for player: %r.", self),
                    setattr(self, "_is_playing", False),
                    setattr(self, "_paused", True),
                    (
                        yield from self.node.play(
                            self.guild.id, track, start=start, replace=replace, pause=True
                        )
                    ),
                    (yield from self.set_volume(self.volume)),
                    (yield from self.pause(True)),
                    (yield from self.pause(pause, timed=1)),
                )
            ),
            "stop": coro(
                lambda self: (
                    (yield from self.node.stop(self.guild.id)),
                    setattr(self, "queue", []),
                    setattr(self, "current", None),
                    setattr(self, "position", 0),
                    [
                        setattr(self, x, False)
                        for x in ("_paused", "_is_autoplaying", "_auto_play_sent", "_is_playing")
                    ],
                )
            ),
            "skip": coro(lambda self: (yield from self.play())),
            "pause": coro(
                lambda self, pause=True, *, timed=None: (
                    timed is not None and (yield from asyncio.sleep(timed)),
                    setattr(self, "_paused", pause),
                    (yield from self.node.pause(self.guild.id, pause)),
                )
            ),
            "set_volume": coro(
                lambda self, volume: (
                    setattr(self, "_volume", max(min(volume, 150), 0)),
                    (yield from self.node.volume(self.guild.id, self.volume)),
                )
            ),
            "seek": coro(
                lambda self, position: (
                    self.current.seekable
                    and (
                        position := max(min(position, self.current.length), 0),
                        (yield from self.node.seek(self.guild.id, position)),
                    )
                )
            ),
        },
    ),
    parse_timestamps := lambda data: (
        data["tracks"]
        if data["loadType"] == LoadType.PLAYLIST_LOADED
        else (
            new_tracks := [],
            query := data["query"],
            query_url := s_try(urllib.parse.urlparse(query), f=lambda a: None, e=BaseException),
            data["tracks"]
            if not query_url
            else (
                [
                    (
                        start_time := {"start_time": 0},
                        s_try(
                            lambda: (
                                (
                                    all([query_url.scheme, query_url.netloc, query_url.path])
                                    or any(x in query for x in ["ytsearch:", "scsearch:"])
                                )
                                and (
                                    url_domain := ".".join(query_url.netloc.split(".")[-2:]),
                                    not query_url.netloc
                                    and (
                                        url_domain := ".".join(
                                            query_url.path.split("/")[0].split(".")[-2:]
                                        )
                                    ),
                                    (
                                        match := re.search(_re_youtube_timestamp, query),
                                        match
                                        and start_time.__setitem__(
                                            "start_time", int(match.group(1))
                                        ),
                                    )
                                    if (
                                        (
                                            url_domain in ["youtube.com", "youtu.be"]
                                            or "ytsearch:" in query
                                        )
                                        and any(x in query for x in ["&t=", "?t="])
                                        and not all(k in query for k in ["playlist", "&list="])
                                    )
                                    else (
                                        (
                                            (
                                                "/sets/" not in query
                                                or ("/sets/" in query and "?in=" in query)
                                            )
                                            and (
                                                match := re.search(
                                                    _re_soundcloud_timestamp, query
                                                ),
                                                match
                                                and start_time.__setitem__(
                                                    "start_time",
                                                    (int(match.group(1)) * 60)
                                                    + int(match.group(2)),
                                                ),
                                            )
                                        )
                                        if (
                                            (
                                                url_domain == "soundcloud.com"
                                                or "scsearch:" in query
                                            )
                                            and "#t=" in query
                                        )
                                        else (
                                            (url_domain == "twitch.tv" and "?t=" in query)
                                            and (
                                                match := re.search(_re_twitch_timestamp, query),
                                                match
                                                and start_time.__setitem__(
                                                    "start_time",
                                                    (int(match.group(1)) * 60 * 60)
                                                    + (int(match.group(2)) * 60)
                                                    + int(match.group(3)),
                                                ),
                                            )
                                        )
                                    ),
                                )
                            ),
                            f=lambda a: None,
                        ),
                        track["info"].__setitem__("timestamp", start_time["start_time"] * 1000),
                        new_tracks.append(track),
                    )
                    for track in data["tracks"]
                ],
                new_tracks,
            )[-1],
        )[-1]
    ),
    reformat_query := lambda query: (
        query := {"query": query},
        s_try(
            lambda: (
                query_url := urllib.parse.urlparse(query),
                (
                    all([query_url.scheme, query_url.netloc, query_url.path])
                    or any(x in query for x in ["ytsearch:", "scsearch:"])
                )
                and (
                    url_domain := ".".join(query_url.netloc.split(".")[-2:]),
                    not query_url.netloc
                    and (url_domain := ".".join(query_url.path.split("/")[0].split(".")[-2:])),
                    (
                        match := re.search(_re_youtube_timestamp, query),
                        match
                        and query.__setitem__("query", query.split("&t=")[0].split("?t=")[0]),
                    )
                    if (
                        (url_domain in ["youtube", "youtu.be"] or "ytsearch:" in query)
                        and any(
                            x in query
                            for x in ["&t=", "?t="]
                            and not all(k in query for k in ["playlist?", "&list="])
                        )
                    )
                    else (
                        (
                            match := re.search(_re_soundcloud_timestamp, query),
                            match and query.__setitem__("query", query.split("#t=")[0]),
                        )
                        if (
                            (url_domain == "soundcloud.com" or "scsearch:" in query)
                            and "#t=" in query
                        )
                        else (
                            (url_domain == "twitch.tv" and "?t=" in query)
                            and (
                                match := re.search(_re_twitch_timestamp, query),
                                match and query.__setitem__("query", query.split("?t=")[0]),
                            )
                        )
                    ),
                ),
            ),
            f=lambda a: None,
        ),
        query["query"],
    )[-1],
    Track := type(
        "Track",
        (),
        {
            "__init__": lambda self, data: (
                None,
                setattr(self, "requester", None),
                setattr(self, "_info", data.get("info", {})),
                [
                    setattr(self, x, self._info.get(y, z))
                    for x, y, z in (
                        ("seekable", "isSeekable", False),
                        ("author", "author", None),
                        ("length", "length", 0),
                        ("is_stream", "isStream", False),
                        ("position", "position", None),
                        ("title", "title", None),
                        ("uri", "uri", None),
                        ("start_timestamp", "timestamp", 0),
                    )
                ],
                setattr(self, "extras", data.get("extras", {})),
            )[0],
            "thumbnail": property(
                lambda self: ("youtube" in self.uri and "identifier" in self._info)
                and "https://img.youtube.com/vi/{}/mqdefault.jpg".format(self._info["identifier"])
            ),
            "__eq__": lambda self, other: (
                self.track_identifier == other.track_identifier
                if isinstance(other, Track)
                else NotImplemented
            ),
            "__ne__": lambda self, other: (
                x := self.__eq__(other),
                not x if x is not NotImplemented else NotImplemented,
            )[-1],
            "__hash__": lambda self: hash(
                tuple(sorted([self.track_identifier, self.title, self.author, self.uri]))
            ),
            "__repr__": lambda self: f"<Track: track_identifier={self.track_identifier!r}, author={self.author!r}, length={self.length}, is_stream={self.is_stream}, uri={self.uri!r}, title={self.title!r}>",
        },
    ),
    LoadResult := type(
        "LoadResult",
        (),
        {
            "__init__": lambda self, data: (
                None,
                setattr(self, "_raw", data),
                _fallback := {
                    "loadType": LoadType.LOAD_FAILED,
                    "exception": {
                        "message": "Lavalink API returned an unsupported response, Please report it.",
                        "severity": ExceptionSeverity.SUSPICIOUS,
                    },
                    "playlistInfo": {},
                    "tracks": [],
                },
                [
                    (
                        k not in data
                        and (
                            (
                                ...
                                if (
                                    k == "exception"
                                    and data.get("loadType", LoadType.LOAD_FAILED)
                                    != LoadType.LOAD_FAILED
                                )
                                else (
                                    v.__setitem__(
                                        "message",
                                        f"Timestamp: {self._raw.get('timestamp', 'Unknown')}\nStatus Code: {self._raw.get('status', 'Unknown')}\nError: {self._raw.get('error', 'Unknown')}\nQuery: {self._raw.get('query', 'Unknown')}\nLoad Type: {self._raw['loadType']}\nMessage: {self._raw.get('message', v['message'])}",
                                    )
                                )
                            ),
                            self._raw.update({k: v}),
                        )
                    )
                    for (k, v) in _fallback.items()
                ],
                setattr(
                    self,
                    "load_type",
                    LoadType(self._raw["loadType"]),
                    is_playlist := self._raw.get("isPlaylist")
                    or self.load_type == LoadType.PLAYLIST_LOADED,
                ),
                setattr(
                    self,
                    "is_playlist",
                    True if is_playlist is True else False if is_playlist is False else None,
                ),
                setattr(
                    self,
                    "playlist_info",
                    PlaylistInfo(**self._raw["playlistInfo"]) if is_playlist is True else None,
                ),
                _tracks := parse_timestamp(self._raw)
                if self._raw.get("query")
                else self._raw["tracks"],
                setattr(self, "tracks", tuple(Track(t) for t in _tracks)),
            )[0],
            "has_error": property(lambda self: self.load_type == LoadType.LOAD_FAILED),
            "exception_message": property(
                lambda self: (
                    (
                        exception_data := self._raw.get("exception", {}),
                        exception_data.get("message"),
                    )[-1]
                    if self.has_error
                    else None
                )
            ),
            "exception_severity": property(
                lambda self: (
                    ret := None,
                    self.has_error
                    and (
                        exception_data := self._raw("exception", {}),
                        severity := exception_data.get("severity"),
                        severity is not None and (ret := ExceptionSeverity(severity)),
                    ),
                    ret,
                )[-1]
            ),
        },
    ),
    format_time := lambda time: (
        d := divmod(time / 1000, 3600),
        n := divmod(d[1], 60),
        f"{d[0]:02d}:{n[0]:02d}:{n[1]:02d}",
    )[-1],
    is_loop_closed := lambda: (
        loop := {"loop": False},
        s_try(
            lambda: loop.__setitem__("loop", asyncio.get_running_loop().is_closed()),
            f=lambda a: loop.__setitem__("loop", True),
        ),
        loop["loop"],
    )[-1],
    set_logging_level(),
    __version__ := "0.11.0rc16",
    _S := type(
        "_S",
        (),
        {
            "__init__": lambda self, name, items: (
                None,
                setattr(self, "name", name),
                setattr(self, "items", items),
            )[0],
            "__getattr__": lambda self, item: (
                self.items[item]
                if item in self.items.keys()
                else throw(AttributeError(f"module '{self.name}' has no attribute '{item}'"))
            ),
        },
    ),
    enums := _S(
        "enums",
        {
            "LavalinkEvents": LavalinkEvents,
            "TrackEndReason": TrackEndReason,
            "LavalinkIncomingOp": LavalinkIncomingOp,
            "LavalinkOutgoingOp": LavalinkOutgoingOp,
            "NodeState": NodeState,
            "PlayerState": PlayerState,
            "LoadType": LoadType,
            "ExceptionSeverity": ExceptionSeverity,
        },
    ),
    errors := _S(
        "errors",
        {
            "RedLavalinkException": RedLavalinkException,
            "NodeException": NodeException,
            "PlayerException": PlayerException,
            "NodeNotFound": NodeNotFound,
            "AbortingNodeConnection": AbortingNodeConnection,
            "NodeNotReady": NodeNotReady,
            "PlayerNotFound": PlayerNotFound,
        },
    ),
    node := _S(
        "node",
        {
            "Stats": Stats,
            "Node": Node,
            "NodeStats": NodeStats,
            "get_node": get_node,
            "get_node_stats": get_node_stats,
            "get_all_nodes": get_all_nodes,
            "PositionTime": PositionTime,
            "MemoryInfo": MemoryInfo,
            "CPUInfo": CPUInfo,
        },
    ),
    player := _S("player", {"Player": Player}),
    rest_api := _S(
        "rest_api",
        {
            "LoadResult": LoadResult,
            "Track": Track,
            "RESTClient": RESTClient,
            "PlaylistInfo": PlaylistInfo,
            "LoadType": LoadType,
            "parse_timestamps": parse_timestamps,
            "reformat_query": reformat_query,
        },
    ),
)

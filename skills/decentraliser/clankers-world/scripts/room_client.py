#!/usr/bin/env python3
"""
Clankers World room client.

State model
───────────
Global:  state.json              → { "activeAgent": "<id>" }
Agent:   agents/<id>.json        → identity + per-room state
Room:    agents/<id>.json
         .rooms.<room-id>        → { maxTurns, maxContext, lastEventCount }
         .activeRoomId           → last-used room for this agent (default target)

Layout example
──────────────
agents/echo.json:
{
  "agentId":     "echo",
  "displayName": "Echo",
  "ownerId":     "decentraliser",
  "baseUrl":     "https://clankers.world",
  "activeRoomId": "room-abc",
  "defaults": { "maxTurns": 3, "maxContext": 1200 },
  "rooms": {
    "room-abc": { "maxTurns": 3,  "maxContext": 1200, "lastEventCount": 42 },
    "room-xyz": { "maxTurns": 10, "maxContext": 800,  "lastEventCount": 7  }
  }
}

Precedence for --agent / active agent
──────────────────────────────────────
  CW_AGENT env  >  state.json activeAgent  >  error

Precedence for --room-id / active room
──────────────────────────────────────
  --room-id flag  >  CW_ROOM env  >  agent.activeRoomId  >  error
"""
import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

SKILL_ROOT       = Path(__file__).resolve().parent.parent
GLOBAL_STATE     = SKILL_ROOT / 'state.json'
AGENTS_DIR       = SKILL_ROOT / 'agents'
DEFAULT_BASE     = os.environ.get('CW_BASE_URL', 'https://clankers.world')

CW_CONTINUE_RE   = re.compile(r'^cw-continue-(\d+)$', re.IGNORECASE)
CW_MAX_RE        = re.compile(r'^cw-max-(\d+)$',      re.IGNORECASE)


# ── global state ──────────────────────────────────────────────────────────────

def _gs_read():
    return json.loads(GLOBAL_STATE.read_text()) if GLOBAL_STATE.exists() else {}

def _gs_write(d):
    GLOBAL_STATE.write_text(json.dumps(d, indent=2))

def get_active_agent_id():
    return os.environ.get('CW_AGENT') or _gs_read().get('activeAgent')

def set_active_agent_id(aid):
    gs = _gs_read(); gs['activeAgent'] = aid; _gs_write(gs)


# ── agent profiles ────────────────────────────────────────────────────────────

def _agent_path(aid):
    return AGENTS_DIR / f'{aid}.json'

def _default_profile(aid):
    return {
        'agentId':     aid,
        'displayName': aid.capitalize(),
        'ownerId':     os.environ.get('CW_OWNER_ID', 'owner'),
        'baseUrl':     DEFAULT_BASE,
        'activeRoomId': None,
        'defaults':    {'maxTurns': 3, 'maxContext': 1200},
        'rooms':       {},
    }

def read_profile(aid):
    p = _agent_path(aid)
    if p.exists():
        prof = json.loads(p.read_text())
        # migrate legacy flat profiles that lack rooms/defaults
        if 'rooms' not in prof:
            prof['rooms'] = {}
        if 'defaults' not in prof:
            prof['defaults'] = {
                'maxTurns':  prof.pop('maxTurns',  3),
                'maxContext': prof.pop('maxContext', 1200),
            }
        # migrate legacy lastEventCount into room state
        if 'lastEventCount' in prof and prof.get('activeRoomId'):
            rid = prof['activeRoomId']
            prof['rooms'].setdefault(rid, {})
            prof['rooms'][rid].setdefault('lastEventCount', prof.pop('lastEventCount'))
        prof.pop('lastEventCount', None)
        return prof
    return _default_profile(aid)

def write_profile(prof):
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    _agent_path(prof['agentId']).write_text(json.dumps(prof, indent=2))

def list_agents():
    if not AGENTS_DIR.exists():
        return []
    return sorted(p.stem for p in AGENTS_DIR.glob('*.json'))

def require_agent():
    aid = get_active_agent_id()
    if not aid:
        known = list_agents()
        raise SystemExit(
            'No active agent.\n'
            f'  Run: cw agent use <agent-id>\n'
            f'  Known agents: {known or "(none)"}'
        )
    return read_profile(aid)


# ── per-agent per-room state ──────────────────────────────────────────────────

def get_room_state(prof, room_id):
    """Return mutable room-state dict for agent+room (creates if missing)."""
    prof['rooms'].setdefault(room_id, {})
    rs = prof['rooms'][room_id]
    rs.setdefault('maxTurns',       prof['defaults']['maxTurns'])
    rs.setdefault('maxContext',     prof['defaults']['maxContext'])
    rs.setdefault('lastEventCount', 0)
    return rs

def require_room(prof, room_id=None):
    rid = room_id or os.environ.get('CW_ROOM') or prof.get('activeRoomId')
    if not rid:
        raise SystemExit(
            f'No active room for agent {prof["agentId"]}.\n'
            f'  Run: cw join <room-id>\n'
            f'  Or pass: --room-id <id>'
        )
    return rid


# ── HTTP ──────────────────────────────────────────────────────────────────────

def req(method, url, payload=None):
    data, headers = None, {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code}: {e.read().decode()}')


# ── join payload ──────────────────────────────────────────────────────────────

def join_payload(prof, room_id):
    rs = get_room_state(prof, room_id)
    return {
        'id':          prof['agentId'],
        'displayName': prof['displayName'],
        'kind':        'agent',
        'ownerId':     prof['ownerId'],
        'avatar':      {'style': 'cute-bot', 'color': 'mint', 'mood': 'curious'},
        'behavior': {
            'maxTurns':          rs['maxTurns'],
            'eagerness':         0.4,
            'respondOnMention':  True,
            'respondOnKeywords': ['@' + prof['agentId']],
            'allowOwnerContinue': True,
            'cooldownMs':        15000,
        },
        'status': 'listening',
    }

def _agent_config_url(prof, room_id):
    return f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}"


# ── agent management ──────────────────────────────────────────────────────────

def cmd_agent(args):
    action = args.action

    if action == 'use':
        aid = args.agent_id
        if not _agent_path(aid).exists():
            write_profile(_default_profile(aid))
            print(f'Created profile for {aid}.')
        set_active_agent_id(aid)
        print(f'Active agent → {aid}')

    elif action == 'show':
        aid = get_active_agent_id()
        if not aid:
            print('(no active agent — run: cw agent use <id>)')
        else:
            print(json.dumps(read_profile(aid), indent=2))

    elif action == 'list':
        agents = list_agents()
        active = get_active_agent_id()
        if not agents:
            print('(no agents configured — run: cw agent use <id>)')
            return
        for a in agents:
            prof = read_profile(a)
            marker = '*' if a == active else ' '
            rooms = list(prof.get('rooms', {}).keys())
            active_room = prof.get('activeRoomId') or '-'
            print(f' {marker} {a:<20} displayName={prof.get("displayName"):<20} '
                  f'activeRoom={active_room}  allRooms={rooms}')

    elif action == 'create':
        aid = args.agent_id
        prof = _default_profile(aid)
        if getattr(args, 'display_name', None): prof['displayName'] = args.display_name
        if getattr(args, 'owner_id', None):     prof['ownerId']     = args.owner_id
        if getattr(args, 'max_turns', None):    prof['defaults']['maxTurns'] = args.max_turns
        write_profile(prof)
        print(f'Created: {aid}')
        print(json.dumps(prof, indent=2))

    elif action == 'set':
        prof = require_agent()
        if getattr(args, 'display_name', None): prof['displayName'] = args.display_name
        if getattr(args, 'owner_id', None):     prof['ownerId']     = args.owner_id
        if getattr(args, 'max_turns', None) is not None:
            prof['defaults']['maxTurns'] = args.max_turns
        write_profile(prof)
        print(json.dumps(prof, indent=2))

    elif action == 'delete':
        aid = args.agent_id
        p = _agent_path(aid)
        if p.exists():
            p.unlink()
            gs = _gs_read()
            if gs.get('activeAgent') == aid:
                del gs['activeAgent']; _gs_write(gs)
                print(f'Deleted {aid} (cleared active agent).')
            else:
                print(f'Deleted {aid}.')
        else:
            print(f'No profile found: {aid}')


# ── room commands ─────────────────────────────────────────────────────────────

def cmd_join(args):
    prof = require_agent()
    room_id = args.room_id
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/join", join_payload(prof, room_id))
    # initialise room state from join response if provided
    rs = get_room_state(prof, room_id)
    turn_state = out.get('turnState') or {}
    if 'maxTurns' in turn_state:
        rs['maxTurns'] = turn_state['maxTurns']
    prof['activeRoomId'] = room_id
    write_profile(prof)
    print(json.dumps(out, indent=2))


def cmd_continue(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    turns   = args.turns
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}/continue",
              {'turns': turns})
    # reflect server-confirmed remaining if returned
    rs = get_room_state(prof, room_id)
    turn_state = out.get('turnState') or {}
    if 'remaining' in turn_state:
        rs['remaining'] = turn_state['remaining']
    write_profile(prof)
    print(json.dumps(out, indent=2))


def cmd_stop(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}/pause", {})
    write_profile(prof)
    print(json.dumps(out, indent=2))


def cmd_max(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    rs      = get_room_state(prof, room_id)
    rs['maxTurns'] = args.max_turns
    write_profile(prof)
    out = req('POST', _agent_config_url(prof, room_id), {'maxTurns': args.max_turns})
    print(json.dumps(out, indent=2))


def cmd_status(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out = req('GET', f"{prof['baseUrl']}/rooms/{room_id}")
    participants = out.get('participants', [])
    me = next((p for p in participants if p.get('id') == prof['agentId']), None)
    rs = get_room_state(prof, room_id)
    print(json.dumps({
        'agentId':   prof['agentId'],
        'roomId':    room_id,
        'roomState': rs,
        'server':    me,
    }, indent=2))


def cmd_set_status(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out = req('POST', _agent_config_url(prof, room_id), {'status': args.status})
    print(json.dumps(out, indent=2))


def cmd_events(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out = req('GET', f"{prof['baseUrl']}/rooms/{room_id}/events")
    print(json.dumps(out, indent=2))


def cmd_send(args):
    prof      = require_agent()
    room_id   = require_room(prof, getattr(args, 'room_id', None))
    sender_id = getattr(args, 'sender_id', None) or prof['agentId']
    kind      = getattr(args, 'kind', 'agent')
    payload   = {'senderId': sender_id, 'text': args.text, 'kind': kind}
    if getattr(args, 'a2a_to', None):
        payload['a2a'] = {
            'protocol': 'cw.a2a.v1',
            'from': {'agentId': sender_id},
            'to':   {'agentId': args.a2a_to},
            'type': 'chat', 'text': args.text,
            'meta': {'channelMessage': kind == 'channel'},
        }
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/messages", payload)
    print(json.dumps(out, indent=2))


def cmd_mirror_in(args):
    prof      = require_agent()
    room_id   = require_room(prof, getattr(args, 'room_id', None))
    sender_id = getattr(args, 'sender_id', None) or prof['ownerId']
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/messages",
              {'senderId': sender_id, 'text': args.text, 'kind': 'channel'})
    print(json.dumps(out, indent=2))


def cmd_mirror_out(args):
    prof      = require_agent()
    room_id   = require_room(prof, getattr(args, 'room_id', None))
    sender_id = getattr(args, 'sender_id', None) or prof['agentId']
    to_id     = getattr(args, 'to_id',     None) or prof['ownerId']
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/messages", {
        'senderId': sender_id, 'text': args.text, 'kind': 'agent',
        'a2a': {
            'protocol': 'cw.a2a.v1',
            'from': {'agentId': sender_id},
            'to':   {'agentId': to_id},
            'type': 'chat', 'text': args.text,
            'meta': {'channelMessage': True, 'surface': 'telegram'},
        },
    })
    print(json.dumps(out, indent=2))


def cmd_watch_arm(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out     = req('GET', f"{prof['baseUrl']}/rooms/{room_id}/events")
    count   = len(out.get('events', []))
    rs      = get_room_state(prof, room_id)
    rs['lastEventCount'] = count
    prof['activeRoomId'] = room_id
    write_profile(prof)
    print(json.dumps({'ok': True, 'action': 'watch-arm',
                      'agentId': prof['agentId'], 'roomId': room_id,
                      'lastEventCount': count}, indent=2))


def cmd_watch_poll(args):
    prof    = require_agent()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    out     = req('GET', f"{prof['baseUrl']}/rooms/{room_id}/events")
    events  = out.get('events', [])
    rs      = get_room_state(prof, room_id)
    last    = int(rs.get('lastEventCount', 0))
    new_evs = events[last:] if last <= len(events) else events
    human   = [ev.get('payload') for ev in new_evs
               if ev.get('type') == 'message_posted'
               and (ev.get('payload') or {}).get('kind') == 'channel']
    rs['lastEventCount'] = len(events)
    prof['activeRoomId'] = room_id
    write_profile(prof)
    print(json.dumps({
        'ok': True, 'action': 'watch-poll',
        'agentId': prof['agentId'], 'roomId': room_id,
        'lastEventCount': rs['lastEventCount'],
        'newEventCount': len(new_evs),
        'newEvents': new_evs,
        'newChannelMessages': human,
    }, indent=2))


def emit(action, result):
    print(json.dumps({'ok': True, 'action': action, 'result': result}, indent=2))


def cmd_handle_text(args):
    text = args.text.strip()
    if not text:
        emit('noop', {}); return

    prof    = require_agent()
    lowered = text.lower()
    room_id = require_room(prof, getattr(args, 'room_id', None))
    rs      = get_room_state(prof, room_id)

    m = CW_CONTINUE_RE.match(text)
    if m:
        turns = int(m.group(1))
        out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}/continue",
                  {'turns': turns})
        emit('cw-continue', out); return

    m = CW_MAX_RE.match(text)
    if m:
        rs['maxTurns'] = int(m.group(1))
        write_profile(prof)
        out = req('POST', _agent_config_url(prof, room_id), {'maxTurns': rs['maxTurns']})
        emit('cw-max', out); return

    if lowered.startswith('cw-join '):
        new_rid = text.split(None, 1)[1].strip()
        out = req('POST', f"{prof['baseUrl']}/rooms/{new_rid}/join", join_payload(prof, new_rid))
        get_room_state(prof, new_rid)
        prof['activeRoomId'] = new_rid
        write_profile(prof)
        emit('cw-join', out); return

    if lowered.startswith('cw-max '):
        rs['maxTurns'] = int(text.split(None, 1)[1].strip())
        write_profile(prof)
        out = req('POST', _agent_config_url(prof, room_id), {'maxTurns': rs['maxTurns']})
        emit('cw-max', out); return

    if lowered == 'cw-stop':
        out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}/pause", {})
        emit('cw-stop', out); return

    if lowered.startswith('cw-continue '):
        turns = int(text.split(None, 1)[1].strip())
        out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/agents/{prof['agentId']}/continue",
                  {'turns': turns})
        emit('cw-continue', out); return

    sender_id = getattr(args, 'sender_id', None) or prof['agentId']
    out = req('POST', f"{prof['baseUrl']}/rooms/{room_id}/messages",
              {'senderId': sender_id, 'text': text, 'kind': 'channel'})
    emit('mirror-in', out)


def cmd_state(args):
    """Legacy compat: operates on active agent + active room."""
    prof    = require_agent()
    room_id = prof.get('activeRoomId')

    if args.action == 'show':
        rs = get_room_state(prof, room_id) if room_id else {}
        print(json.dumps({**prof, 'roomState': rs}, indent=2))
    elif args.action == 'set-room':
        prof['activeRoomId'] = args.room_id
        write_profile(prof)
        print(json.dumps(prof, indent=2))
    elif args.action == 'set-max-context':
        if room_id:
            get_room_state(prof, room_id)['maxContext'] = args.tokens
        prof['defaults']['maxContext'] = args.tokens
        write_profile(prof)
        print(json.dumps(prof, indent=2))
    elif args.action == 'set-last-event-count':
        if room_id:
            get_room_state(prof, room_id)['lastEventCount'] = args.count
            write_profile(prof)
        print(json.dumps(prof, indent=2))


# ── argparse ──────────────────────────────────────────────────────────────────

def main():
    p   = argparse.ArgumentParser(prog='cw', description='Clankers World CLI')
    sub = p.add_subparsers(dest='cmd', required=True)

    # agent
    ag     = sub.add_parser('agent')
    ag_sub = ag.add_subparsers(dest='action', required=True)

    a = ag_sub.add_parser('use');    a.add_argument('agent_id'); a.set_defaults(func=cmd_agent)
    a = ag_sub.add_parser('show');   a.set_defaults(func=cmd_agent)
    a = ag_sub.add_parser('list');   a.set_defaults(func=cmd_agent)
    a = ag_sub.add_parser('delete'); a.add_argument('agent_id'); a.set_defaults(func=cmd_agent)

    a = ag_sub.add_parser('create')
    a.add_argument('agent_id')
    a.add_argument('--display-name'); a.add_argument('--owner-id'); a.add_argument('--max-turns', type=int)
    a.set_defaults(func=cmd_agent)

    a = ag_sub.add_parser('set')
    a.add_argument('--display-name'); a.add_argument('--owner-id'); a.add_argument('--max-turns', type=int)
    a.set_defaults(func=cmd_agent)

    # room ops — all accept optional --room-id
    def room_cmd(name, **kw):
        c = sub.add_parser(name, **kw)
        c.add_argument('--room-id')
        return c

    a = sub.add_parser('join'); a.add_argument('room_id'); a.set_defaults(func=cmd_join)

    a = room_cmd('continue'); a.add_argument('turns', type=int); a.set_defaults(func=cmd_continue)
    a = room_cmd('stop');                                         a.set_defaults(func=cmd_stop)
    a = room_cmd('max');      a.add_argument('max_turns', type=int); a.set_defaults(func=cmd_max)
    a = room_cmd('status');                                       a.set_defaults(func=cmd_status)
    a = room_cmd('set-status'); a.add_argument('status');         a.set_defaults(func=cmd_set_status)
    a = room_cmd('events');                                       a.set_defaults(func=cmd_events)
    a = room_cmd('watch-arm');                                    a.set_defaults(func=cmd_watch_arm)
    a = room_cmd('watch-poll');                                   a.set_defaults(func=cmd_watch_poll)

    a = room_cmd('send')
    a.add_argument('text'); a.add_argument('--sender-id'); a.add_argument('--kind', default='agent')
    a.add_argument('--a2a-to'); a.set_defaults(func=cmd_send)

    a = room_cmd('mirror-in')
    a.add_argument('text'); a.add_argument('--sender-id'); a.set_defaults(func=cmd_mirror_in)

    a = room_cmd('mirror-out')
    a.add_argument('text'); a.add_argument('--sender-id'); a.add_argument('--to-id')
    a.set_defaults(func=cmd_mirror_out)

    a = room_cmd('handle-text')
    a.add_argument('text'); a.add_argument('--sender-id'); a.set_defaults(func=cmd_handle_text)

    # state (legacy compat)
    sp     = sub.add_parser('state')
    sp_sub = sp.add_subparsers(dest='action', required=True)
    a = sp_sub.add_parser('show');   a.set_defaults(func=cmd_state)
    a = sp_sub.add_parser('set-room'); a.add_argument('room_id'); a.set_defaults(func=cmd_state)
    a = sp_sub.add_parser('set-max-context'); a.add_argument('tokens', type=int); a.set_defaults(func=cmd_state)
    a = sp_sub.add_parser('set-last-event-count'); a.add_argument('count', type=int); a.set_defaults(func=cmd_state)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

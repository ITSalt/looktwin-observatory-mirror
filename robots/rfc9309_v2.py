"""RFC 9309 robots.txt evaluator for the observatory (LOO-44, ventures). v2, 02.11.2026.

v2 change (glitchfox e721d5f1, Q-068): percent-encoding normalisation, RFC 9309 2.2.2 / RFC 3986 6.2.2:
hex digits of %XX are upper-cased and %XX of unreserved characters (A-Z a-z 0-9 - . _ ~) are decoded,
in both the rule pattern and the path, before matching. %2A and %24 stay literal (not wildcard / anchor).

- Group match: user-agent value compared to the bot's product token, case-insensitive EQUALITY
  (not prefix, not substring: a "Bot" or "gpt" group does not apply to GPTBot). RFC 9309 2.2.1.
- Several groups for the same agent are merged; if none match, '*' groups are merged; if none, all allowed.
- Rules: '*' = any sequence; '$' is an end anchor only as the LAST character, elsewhere literal.
- Longest pattern wins; on a tie Allow wins; an empty Disallow/Allow matches nothing. RFC 9309 2.2.2.
- /robots.txt is always allowed.
"""
import re

_UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")

def norm(p):
    def f(m):
        c = chr(int(m.group(1), 16))
        return c if c in _UNRESERVED else "%" + m.group(1).upper()
    return re.sub(r"%([0-9A-Fa-f]{2})", f, p)

def parse(txt):
    groups, agents, rules, in_rules = [], [], [], False
    for line in txt.splitlines():
        s = line.split("#", 1)[0].strip()
        if ":" not in s:
            continue
        k, v = (x.strip() for x in s.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if in_rules:
                groups.append((agents, rules)); agents, rules, in_rules = [], [], False
            agents.append(v.lower())
        elif k in ("allow", "disallow"):
            if agents:
                rules.append((k, v)); in_rules = True
    if agents:
        groups.append((agents, rules))
    return groups

def rules_for(groups, token):
    t = token.lower()
    mine = [r for a, r in groups if t in a]
    if mine:
        return [x for r in mine for x in r]
    return [x for a, r in groups if "*" in a for x in r]

def _rx(pat):
    end = pat.endswith("$")
    body = pat[:-1] if end else pat
    return re.compile("".join(".*" if c == "*" else re.escape(c) for c in body) + ("$" if end else ""), re.S)

def allowed(txt, token, path):
    path = norm(path)
    if path == "/robots.txt":
        return True
    best_len, best_ok = -1, True
    for k, v in rules_for(parse(txt), token):
        if v == "":
            continue
        v = norm(v)
        if _rx(v).match(path):
            ok = (k == "allow")
            if len(v) > best_len or (len(v) == best_len and ok):
                best_len, best_ok = len(v), ok
    return best_ok

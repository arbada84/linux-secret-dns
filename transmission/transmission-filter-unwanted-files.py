#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.request


RPC_URL = "http://127.0.0.1:9091/transmission/rpc"
LOG_PATH = os.path.expanduser("~/.config/transmission/filter-unwanted-files.log")


def log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def rpc_call(payload, session_id=None):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["X-Transmission-Session-Id"] = session_id

    request = urllib.request.Request(RPC_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response), session_id
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            new_session_id = exc.headers.get("X-Transmission-Session-Id")
            if new_session_id and new_session_id != session_id:
                return rpc_call(payload, new_session_id)
        raise


def should_skip(name):
    lowered = name.lower()
    base = os.path.basename(lowered)
    return (
        "996gg.cc" in lowered
        or lowered.endswith(".url")
        or base == "offkab@sukebei.txt"
    )


def main():
    torrent_id = os.environ.get("TR_TORRENT_ID")
    torrent_name = os.environ.get("TR_TORRENT_NAME", "")
    if not torrent_id:
        log("skip: TR_TORRENT_ID is missing")
        return 1

    get_payload = {
        "method": "torrent-get",
        "arguments": {"ids": [int(torrent_id)], "fields": ["files"]},
    }
    response, session_id = rpc_call(get_payload)
    torrents = response.get("arguments", {}).get("torrents", [])
    if not torrents:
        log(f"skip: torrent not found id={torrent_id} name={torrent_name!r}")
        return 0

    files = torrents[0].get("files", [])
    unwanted = [index for index, item in enumerate(files) if should_skip(item.get("name", ""))]

    if unwanted:
        set_payload = {
            "method": "torrent-set",
            "arguments": {"ids": [int(torrent_id)], "files-unwanted": unwanted},
        }
        rpc_call(set_payload, session_id)
        log(f"filtered: id={torrent_id} name={torrent_name!r} unwanted={unwanted}")

    # Transmission이 토렌트 추가를 완전히 마칠 때까지 대기 후 시작
    time.sleep(2)
    start_payload = {
        "method": "torrent-start",
        "arguments": {"ids": [int(torrent_id)]},
    }
    rpc_call(start_payload, session_id)
    log(f"started: id={torrent_id} name={torrent_name!r}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"error: {exc}")
        sys.exit(1)

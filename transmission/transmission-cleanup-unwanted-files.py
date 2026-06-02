#!/usr/bin/env python3
# 토렌트 다운로드 완료 후 제외(unwanted)로 표시된 파일 자동 삭제

import json
import os
import sys
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


def main():
    torrent_id = os.environ.get("TR_TORRENT_ID")
    torrent_name = os.environ.get("TR_TORRENT_NAME", "")
    torrent_dir = os.environ.get("TR_TORRENT_DIR", "")
    if not torrent_id:
        log("cleanup skip: TR_TORRENT_ID is missing")
        return 1

    response, session_id = rpc_call({
        "method": "torrent-get",
        "arguments": {"ids": [int(torrent_id)], "fields": ["files", "fileStats"]},
    })
    torrents = response.get("arguments", {}).get("torrents", [])
    if not torrents:
        log(f"cleanup skip: torrent not found id={torrent_id}")
        return 0

    files = torrents[0].get("files", [])
    stats = torrents[0].get("fileStats", [])

    deleted = []
    for f, s in zip(files, stats):
        if s.get("wanted", True):
            continue
        filepath = os.path.join(torrent_dir, f["name"])
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                deleted.append(f["name"])
                # 빈 디렉토리면 함께 삭제
                parent = os.path.dirname(filepath)
                if parent != torrent_dir and os.path.isdir(parent):
                    if not os.listdir(parent):
                        os.rmdir(parent)
            except OSError as e:
                log(f"cleanup error: {filepath} — {e}")

    if deleted:
        log(f"cleanup deleted: id={torrent_id} name={torrent_name!r} files={deleted}")
    else:
        log(f"cleanup ok: id={torrent_id} name={torrent_name!r} nothing to delete")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"cleanup error: {exc}")
        sys.exit(1)

-- 플레이리스트에서 자막 파일 자동 제거
local subtitle_ext = {
    srt=true, ass=true, ssa=true, sub=true,
    vtt=true, smi=true, idx=true, sup=true, lrc=true
}

local function is_subtitle(filename)
    local ext = filename:match("%.([^.]+)$")
    return ext and subtitle_ext[ext:lower()]
end

local function filter_playlist()
    local count = mp.get_property_number("playlist-count", 0)
    local current = mp.get_property_number("playlist-pos", 0)

    for i = count - 1, 0, -1 do
        local filename = mp.get_property("playlist/" .. i .. "/filename", "")
        if is_subtitle(filename) then
            mp.commandv("playlist-remove", i)
            if i < current then
                current = current - 1
            end
        end
    end
end

mp.register_event("file-loaded", filter_playlist)

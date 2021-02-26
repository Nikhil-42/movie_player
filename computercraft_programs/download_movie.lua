-- A simple program to download / stream a video
-- from the specified ip. Requests are made in the 
-- form /movie_name/frame_#.nfp and answered by blit
-- blit-able string. 

-- Downloads a movie from the ip below
ip = "localhost"

-- Initialize starting point
movie_name = arg[1]
frame = tonumber(arg[2])
print(arg[3])
if arg[3] == "--silent" then
    silent = true
else
    silent = false
end

-- If the movie wasn't specified ask for it
if movie_name == nil then
    print("Which movie: ")
    movie_name = read()
end

movie_dir = "/disk/".. movie_name .."/"

-- If the frame wasn't specified start from the
-- cached position
if frame == nil then
    if fs.exists(movie_dir.. ".dwnld") then
        local file = io.open(movie_dir ..".dwnld")        
        frame = tonumber(file:read())
        file:close()
    end
    if frame == nil then frame = 0 end
end

-- Grab the screen
local scrn = peripheral.find("monitor")
scrn.setTextScale(0.5)

function drawImageFast(image)
    local y = 1
    for line in image do
        scrn.setCursorPos(1, y)
        scrn.blit(line, line, line)
        y = y + 1
    end
end

-- Download the frame at frame_index from ip
-- returns true on success
function downloadFrame(frame_idx)

    -- Download current frame
    local frame_str = "frame_".. tostring(frame_idx) ..".nfp"
    local request = http.get("http://".. ip .."/".. movie_name .."/".. frame_str)
    if request == nil then
        print("Couldn't download file: ".. frame_str)
        return false
    else
        -- Store to file
        local file = io.open(movie_dir .."/".. frame_str, "w")
        file:write(request.readAll())
        file:close()
        
        -- Print to screen
        if not silent then
            drawImageFast(io.lines(movie_dir..frame_str))
        end
        
        return true
    end
end

-- The main download loop
function runDownload()
    while true do
        if downloadFrame(frame) then
            frame = frame + 1
        end
        sleep(0)
    end
end

function checkExit()
    os.pullEvent("key")
end

-- Print specifications
print("Downloading ".. movie_name .." to ".. movie_dir)
print("Starting at frame: ".. frame)
print("Press any key to stop...")

-- Run main loop
parallel.waitForAny(runDownload, checkExit)

-- Save position to resume
file = io.open(movie_dir.. ".dwnld", "w")
file:write(tostring(frame))
file:close()
print("Stopped at frame: ".. frame)
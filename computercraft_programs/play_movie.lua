-- A simple program to play a video from the 
-- disk. Expects movies in the form 
-- disk/movie_name/frame_#.nfp and

-- Plays a movie from the disk.

-- Initialize starting point
movie_name = arg[1]
frame = tonumber(arg[2])

-- If the movie wasn't specified ask for it
if movie_name == nil then
    print("Which movie: ")
    movie_name = read()
end

movie_dir = "/disk/".. movie_name .."/"

-- If the frame wasn't specified start from the
-- cached position
if frame == nil then
    if fs.exists(movie_dir.. ".play") then
        local file = io.open(movie_dir.. ".play")
        frame = tonumber(file:read())
        file:close()
    end
    
    if frame == nil then frame = 0 end
end

frame_prefix = movie_dir .."frame_"

-- Wrap the screen
scrn = peripheral.find("monitor")
scrn.setTextScale(0.5)

-- A faster function to draw to the screen
-- WARNING: This is NOT STABLE
function drawImageFast(image)
    y = 1
    for line in image do
        scrn.setCursorPos(1, y)
        scrn.blit(line, line, line)
        y = y + 1
        
    end
end

-- Draw a single frame
function drawFrame(frame_idx)

    -- Read image from file
    image_path = frame_prefix..tostring(frame_idx)
     ..".nfp"
    file = io.open(image_path)

    -- Draw frame
    drawImageFast(file:lines())
    file:close()
end

-- The main play loop
function runDisplay()
    while true do
        parallel.waitForAll(
            function() drawFrame(frame) end,
            function() sleep(0.05) end
        )
        frame = frame + 1
    end
end

function checkScreenPress()
    os.pullEvent("monitor_touch")
end

function checkKeyPress()
    os.pullEvent("key")
end

-- Print specifications
print("Playing ".. movie_name)
print("Starting at frame: ".. frame)
print("Click or press any key to stop...")

-- Run main loop
parallel.waitForAny(runDisplay, checkScreenPress, checkKeyPress)

-- Show "THE END"
the_end = io.open(movie_dir..  "the_end.nfp")
drawImageFast(the_end:lines())
the_end:close()

-- Save position to resume
file = io.open(movie_dir.. ".play", "w")
file:write(tostring(frame))
file:close()
print("Stopped at frame: ".. frame)

-- Wait for user
print("Press any key to exit...")
os.pullEvent("key")
scrn.setTextColor(colors.white)
scrn.setBackgroundColor(colors.black)
scrn.clear()
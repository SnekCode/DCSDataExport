-- Data export script for DCS, version 1.2.
-- Copyright (C) 2006-2014, Eagle Dynamics.
-- See http://www.lua.org for Lua script system info 
-- We recommend to use the LuaSocket addon (http://www.tecgraf.puc-rio.br/luasocket) 
-- to use standard network protocols in Lua scripts.
-- LuaSocket 2.0 files (*.dll and *.lua) are supplied in the Scripts/LuaSocket folder
-- and in the installation folder of the DCS. 

-- Expand the functionality of following functions for your external application needs.
-- Look into Saved Games\DCS\Logs\dcs.log for this script errors, please.

local Tacviewlfs=require('lfs');dofile(Tacviewlfs.writedir()..'Scripts/TacviewGameExport.lua')
--dofile(lfs.writedir()..[[Scripts\DCS-ExportScript\ExportScript.lua]])



--[[	
-- Uncomment if using Vector class from the Scripts\Vector.lua file 
local lfs = require('lfs')
LUA_PATH = "?;?.lua;"..lfs.currentdir().."/Scripts/?.lua"
require 'Vector'
-- See the Scripts\Vector.lua file for Vector class details, please.
--]]

local default_output_file = nil
local previous_ouput_file = nil

function LuaExportStart()
    time = os.time(os.date("!*t"))
    filename = "/Logs/Export".. time ..".log"
    default_output_file = io.open(lfs.writedir()..filename, "w")
    UpdatePreviousLogWithDebreifData()

end

function LuaExportBeforeNextFrame()
-- Works just before every simulation frame.
    -- LoSetCommand(286)
end

function LuaExportAfterNextFrame()
-- Works just after every simulation frame.

    local t = LoGetModelTime()
    
    local sens = LoGetTWSInfo()
    
	local altRad = LoGetAltitudeAboveGroundLevel()
	local pitch, bank, yaw = LoGetADIPitchBankYaw()
    

-- Then send data to your file or to your receiving program:
-- 1) File
    if default_output_file then
        default_output_file:write(string.format("t = %.2f, altRad = %.2f, pitch = %.2f, bank = %.2f, yaw = %.2f", t, altRad, 57.3*pitch, 57.3*bank, 57.3*yaw))
        if sens == nil then
            default_output_file:write(", No Sensor Data")
        end
        if sens ~= nil then
            default_output_file:write(flatten(sens))
        end

    end

end


function OnGameEvent()
-- this needs to write in when what launched and when what killed
end

function UpdatePreviousLogWithDebreifData()
    local debrief = io.open(lfs.writedir().."/Logs/debrief.log", "rb")
    local state = io.open(lfs.writedir().."/Logs/state.log", "r")
    local previous_file_name = state:read()
    state:close()
    local previous_file = io.open(lfs.writedir()..previous_file_name, "a+")

    if previous_file ~= nil then
        previous_file:write(debrief:read("*all"))
    end
    previous_file:close()
end

function LuaExportStop()
-- Works once just after mission stop.
-- Close files and/or connections here.

-- 1) File

-- get debrief
local debrief = io.open(lfs.writedir().."/Logs/state.log", "w")
debrief:write(filename)
debrief:close()
default_output_file:write("\n\n\n")
default_output_file:write("#######################")
default_output_file:write("\n\n\n")
   if default_output_file then
        previous_output_file = filename
	    default_output_file:close()
	    default_output_file = nil
   end

end

function flatten(t)
    r = ""
    for k, v in pairs(t) do
        if type(v) == 'table' then
            r = r .. k .. "." .. flatten(v)
        end
        if type(v) ~= 'table' then
            r = r .. k .. ": " .. v .. " "
        end
    
    end
    return r
end


--[[
LoGetTWSInfo() -- return Threat Warning System status (result  the table )
result_of_LoGetTWSInfo =
{
	Mode = , -- current mode (0 - all ,1 - lock only,2 - launch only
	Emitters = {table of emitters}
}
emitter_table =
{
	ID =, -- world ID
	Type = {level1,level2,level3,level4}, -- world database classification of emitter
	Power =, -- power of signal
	Azimuth =,
	Priority =,-- priority of emitter (int)
	SignalType =, -- string with vlues: "scan" ,"lock", "missile_radio_guided","track_while_scan";
}
]]--

--[[ example
-- syntactic sugar => LoGetTWSInfo().Emitters.1.Power
lTWSInfo: { 
   [Emitters] = {
       [1] = {
           [Type] = {
               [level3] = number: "101"
               [level1] = number: "2"
               [level4] = number: "75"
               [level2] = number: "16"
           }
           [Azimuth] = number: "1.0060220956802"
           [Power] = number: "0.83987760543823"
           [iD] = number: "16777728"
           [Priority] = number: "140.83987426758"
           [signalType] = string: "scan"
       }
       [2] = {
           [Type] = {
               [level3] = number: "101"
               [level1] = number: "2"
               [level4] = number: "42"
               [level2] = number: "16"
           }
           [Azimuth] = number: "-0.60858452320099"
           [Power] = number: "0.73460388183594"
           [iD] = number: "16778240"
           [Priority] = number: "140.73460388184"
           [signalType] = string: "scan"
       }
   }
   [Mode] = number: "0"
}
]]--
-- Data export script for DCS, version 1.2.
-- Copyright (C) 2006-2014, Eagle Dynamics.
-- See http://www.lua.org for Lua script system info 
-- We recommend to use the LuaSocket addon (http://www.tecgraf.puc-rio.br/luasocket) 
-- to use standard network protocols in Lua scripts.
-- LuaSocket 2.0 files (*.dll and *.lua) are supplied in the Scripts/LuaSocket folder
-- and in the installation folder of the DCS. 
​
-- Expand the functionality of following functions for your external application needs.
-- Look into Saved Games\DCS\Logs\dcs.log for this script errors, please.
​
local Tacviewlfs=require('lfs');dofile(Tacviewlfs.writedir()..'Scripts/TacviewGameExport.lua')
​
​
--[[	
-- Uncomment if using Vector class from the Scripts\Vector.lua file 
local lfs = require('lfs')
LUA_PATH = "?;?.lua;"..lfs.currentdir().."/Scripts/?.lua"
require 'Vector'
-- See the Scripts\Vector.lua file for Vector class details, please.
--]]
​
local default_output_file = nil
​
function LuaExportStart()
   default_output_file = io.open(lfs.writedir().."/Logs/Export.log", "w")
​
end
​
function LuaExportBeforeNextFrame()
-- Works just before every simulation frame.
​
end
​
function LuaExportAfterNextFrame()
-- Works just after every simulation frame.
​
    local t = LoGetModelTime()
    local sens = LoGetTWSInfo()
    local lock = sens.Emitters.1.Power
	local altRad = LoGetAltitudeAboveGroundLevel()
	local pitch, bank, yaw = LoGetADIPitchBankYaw()
​
-- Then send data to your file or to your receiving program:
-- 1) File
    if default_output_file then
        default_output_file:write(string.format("t = %.2f, altRad = %.2f, pitch = %.2f, bank = %.2f, yaw = %.2f\n", t, altRad, 57.3*pitch, 57.3*bank, 57.3*yaw))
        default_output_file:write(string.format("Signal Power = %.2f\n", lock))
        -- ParseSensorData(sens)
      
    end
​
end
​
function ParseSensorData(sens)
-- copy/pasted TWSInfo sample output below
end
​
function OnGameEvent()
-- this needs to write in when what launched and when what killed
end
​
function LuaExportStop()
-- Works once just after mission stop.
-- Close files and/or connections here.
​
-- 1) File
   if default_output_file then
	  default_output_file:close()
	  default_output_file = nil
   end
​
end
​
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
​
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
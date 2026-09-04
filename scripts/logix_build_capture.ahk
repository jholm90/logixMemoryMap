; Logix Designer build/verify + Capacity capture loop (James, 2026-08-22).
; Companion to batch_memory_capture.ps1 -- that script writes the next ACD
; path to open (file existence at -OpenRequestPath = "go" signal, content +
; clipboard both carry the path) and polls for this script's results
; (-HandoffPath: error_count,warning_count,message_value,ocd_value,
; window_title, overwritten every cycle, consumed on read). This script
; never launches or closes Logix Designer -- it drives File > Open inside
; the same already-running instance (confirmed ~5s vs ~65s for a full
; close/reopen cycle).
;
; Update HANDOFF_PATH / OPEN_REQUEST_PATH below to match whatever you pass
; to batch_memory_capture.ps1's -HandoffPath / -OpenRequestPath.
;
; Confirmed empirically on James's machine (2026-08-22):
;   - Ctrl+O opens a dialog titled "Open Project" (not generic "Open").
;   - The save-changes prompt ("Project file '<name>.ACD' has been changed.
;     Save the changes?") actually fires AFTER pasting the new path + Enter,
;     not before the Open Project dialog -- dismissed with 'n' (discard),
;     since Build's cache write should never get persisted back into a
;     tracked sample file. A second save-prompt can also appear after the
;     Controller Properties/Capacity read, handled the same way.
;   - Controller Properties dialog title is "Controller Properties - <name>"
;     (dynamic per file), ahk_class #32770, ahk_exe LogixDesigner.Exe.
;   - Reading Edit3 (the Capacity/OCD value) can come back comma-formatted
;     by Studio 5000 (e.g. "99,999") -- stripped before it ever reaches the
;     handoff CSV, since an embedded comma would split into two columns.
;   - TODO (still needs verification): the "n" keystroke for the save
;     prompt, the exact ahk_exe/class for WinActivate, and a real "project
;     finished loading" signal to replace the fixed Sleep after Open.
;
; Ctrl+F1 starts the loop. Esc aborts. F9 is a standalone debug helper for
; checking what control text looks like on the active window.

#Requires AutoHotkey v2.0

SendMode "Event"
SetKeyDelay 50, 50

; scripts\ahk_runtime\ is gitignored (transient IPC files, never committed).
; A_ScriptDir resolves automatically as long as this file stays where it's
; tracked (scripts\logix_build_capture.ahk) -- matches
; batch_memory_capture.ps1's own $PSScriptRoot-relative defaults, so
; neither side needs a path typed in by hand.
HANDOFF_PATH := A_ScriptDir "\ahk_runtime\ahk_handoff.csv"        ; must match -HandoffPath
OPEN_REQUEST_PATH := A_ScriptDir "\ahk_runtime\open_request.txt"  ; must match -OpenRequestPath

; ahk_runtime\ won't exist until the PowerShell side creates it (or run
; this once by hand) -- FileExist below would just wait forever silently
; otherwise.
DirCreate A_ScriptDir "\ahk_runtime"
LOGIX_WIN := "ahk_exe LogixDesigner.exe"             ; confirmed via Window Spy, 2026-08-22

global OCDValue := ""
global ErrorValue := ""
global WarningValue := ""
global MessageValue := ""
global WindowTitle := ""
global BUILD_SKIP_CATALOGS := "*1769-*;*1756-L7*"

; Pulls the leading integer out of button/label text like "0 Warnings",
; "3 Errors", "1 Warning" -- handles singular/plural and any wording since
; it only looks for digits at the start. Returns "" (not "0") if nothing
; matched, so a bad ControlGetText read doesn't silently log a false zero.
ExtractCount(text) {
    if RegExMatch(Trim(text), "^(\d+)", &m)
        return m[1]
    return ""
}





BuildPopupExpected(title) {
    for pat in StrSplit(BUILD_SKIP_CATALOGS, ";") {
        pat := Trim(pat)
        if (pat = "")
            continue
        rx := "i)^" StrReplace(RegExReplace(pat, "([\\.^$|()\[\]{}+?])", "\$1"), "*", ".*") "$"
        if RegExMatch(title, rx)
            return false
    }
    return true
}


FindCountButtons() {
    counts := Map("Error", "", "Warning", "", "Message", "")
    seen := ""
    ctrls := ""
    try ctrls := WinGetControls("A")
    catch
        return {counts: counts, seen: "(WinGetControls failed)"}
    if !IsObject(ctrls)
        return {counts: counts, seen: "(no controls)"}

    for ctrl in ctrls {
        if !RegExMatch(ctrl, "^Button\d+$")
            continue
        txt := ""
        try txt := Trim(ControlGetText(ctrl, "A"))
        catch
            continue
        if (txt = "")
            continue
        seen .= (seen = "" ? "" : " | ") ctrl "=" txt
        for kind in ["Error", "Warning", "Message"] {
            if (counts[kind] = "") && RegExMatch(txt, "i)^(\d+)\b.*\b" kind, &m)
                counts[kind] := m[1]
        }
    }
    return {counts: counts, seen: seen}
}

; Studio 5000 formats some numeric fields (confirmed: the Capacity/OCD
; value) with thousands-separator commas -- e.g. "99,999" -- which would
; otherwise split into two columns once written into a comma-delimited
; handoff CSV. Strip commas from every value right before it's written,
; not just OCDValue, since any of these could pick one up.
StripCommas(text) {
    return StrReplace(text, ",", "")
}

; Window title is the one field that legitimately needs commas/other
; punctuation preserved (e.g. "Logix Designer - BoolPackBaseline in
; sample_0001...ACD [1756-L81E 35.11]") -- quote it for the CSV instead of
; stripping anything out of it.
CsvQuote(text) {
    return '"' StrReplace(text, '"', '""') '"'
}

StatusGui := Gui("+AlwaysOnTop +ToolWindow", "Loop Status.  Press ESC to Abort")
StatusGui.SetFont("s12 Bold")
StatusText := StatusGui.AddText("w320", "IDLE - press Ctrl+F1 in Logix window")
StatusGui.Show()

Status(msg) {
    global StatusText
    StatusText.Text := msg
}

^F1:: {
    Status("STARTED")
    Loop {
        global OCDValue := ""
        global ErrorValue := ""
        global WarningValue := ""
        global MessageValue := ""
        global WindowTitle := ""
				global ButtonTest := ""
				global active_title := ""

        ; --- Wait for PowerShell's next-file handoff (file existence = "go") ---
        Status("Waiting for next file from PowerShell...")
        while !FileExist(OPEN_REQUEST_PATH)
            Sleep 500
        FileDelete OPEN_REQUEST_PATH   ; consumed -- PowerShell won't write a new one until this is gone

        ; Explicitly grab focus onto Logix Designer -- whatever last had
        ; focus (PowerShell's console, most likely) doesn't matter after
        ; this. Without it, "A" (active window) below could target the
        ; wrong thing entirely.
        ;
        ; WinActivate itself doesn't return a testable success value in AHK
        ; v2 (it silently no-ops if nothing matches) -- WinExist is the one
        ; that actually returns a real HWND (truthy) or 0 (falsy), and sets
        ; the "last found window" that a bare WinActivate then acts on.
        if !WinExist(LOGIX_WIN) {
            MsgBox "Couldn't find the Logix Designer window (" LOGIX_WIN "). If it's definitely"
                . " running, check: (1) is this AHK script elevated (Run as administrator) while"
                . " Logix Designer is NOT? Windows blocks a higher-privilege process from seeing/"
                . " activating a lower one (UIPI) -- match their privilege levels. (2) is"
                . " LOGIX_WIN's exe name exactly right -- try Window Spy on the real window."
            continue
        }
        WinActivate
        Sleep 100

        Status("Opening next file (from clipboard)")
        Send "^o"

        if !WinWait("Open Project", , 5) {
            MsgBox "Open Project dialog didn't appear within 5s -- check the Ctrl+O shortcut."
            continue
        }
        Sleep 25
        Send "^v"   ; paste the path PowerShell put on the clipboard
        Sleep 100
        Send "{Enter}"
				
				sleep 1000

        ; Switching away from a Build-modified project can prompt to save
        ; first -- discard, never persist Build's cache write into the
        ; tracked sample file. TODO: confirm 'n' is really the access key
        ; for this dialog's "No"/"Don't Save" button.
        if WinWait(, "Save the changes?", 2)
            Send "n"

        ; Wait for the project to actually load. TODO: replace with a real
        ; "loaded" signal (e.g. WinWaitActive on a title pattern) once you
        ; know what changes on screen when load finishes -- file size will
        ; vary this just like Build does, same reasoning as the Build popup.
        Sleep 2000
				
				active_title := WinGetTitle("A")
				
				Status("Active Title: " active_title)
				
				sleep 100
				
				
				
				Timeout := 120000  ; 2 min
				Start := A_TickCount
				Loop {
						if WinExist("Logix Designer")
								break
						if (A_TickCount - Start > Timeout) {
								MsgBox "Timed out waiting for LogixDesigner window, dumbass."
								ExitApp
						}
						Sleep 250
				}
				; window found, continue here
				
				;ErrorValue := ExtractCount(ControlGetText("Button10", "A"))
				;WinActivate
				;sleep 20
				
				
				Timeout := 120000  ; 2 min
				Start := A_TickCount
				Loop {
						if WinExist("Logix Designer")
								break
						if (A_TickCount - Start > Timeout) {
								MsgBox "Timed out waiting for LogixDesigner window, dumbass."
								ExitApp
						}
						Sleep 250
				}
				; window found, continue here
				
				Sleep 100

        ; --- Build ---
        Status("Alt")
        Send "{Alt}"
        Sleep 50
        Status("l")
        Send "l"
        Sleep 50
        Status("b")


				Send "b"
				Sleep 300
				
				
				

				buildPopupTitle := "Building"
				maxAppearSeconds := 120   ; a big file can take minutes just to START
				maxWaitSeconds := 600     ; ceiling so a hung build doesn't loop forever

				Status("Waiting for build to start")
				if WinWait(buildPopupTitle, , maxAppearSeconds) {
						Status("Build started -- waiting for it to finish")
						if !WinWaitClose(buildPopupTitle, , maxWaitSeconds)
								MsgBox "Build popup didn't close within " maxWaitSeconds "s -- possible hang, check manually."
						else
								Status("Build finished")
				} else {
						Status("WARNING: build popup never seen within " maxAppearSeconds "s -- build may not have run, or finished too fast to catch. Counter values below are suspect.")
				}




        Sleep 50
				ErrorValue := ExtractCount(ControlGetText("Button10", "A"))
        ; Captured at the same moment as Error/Warning/Message -- the
        ; window title has the open .ACD filename baked in (James, 2026-08-22:
        ; "window title is valid there with the filename.acd present inside"),
        ; giving PowerShell an independent cross-check against the filename
        ; it actually requested, instead of just trusting the handshake blind.
        WindowTitle := WinGetTitle("A")
				found := FindCountButtons()
				ErrorValue   := found.counts["Error"]
				WarningValue := found.counts["Warning"]
				MessageValue := found.counts["Message"]
				
        Status("Errors/Warnings/Message: " ErrorValue ", " WarningValue ", " MessageValue " | " WindowTitle)

        ; --- Controller Properties -> Capacity (OCD value) ---
        Sleep 250
        Status("Alt")
        Send "{Alt}"
        Sleep 10
        Status("e")
        Send "e"
        Sleep 10
        Status("n")
        Send "n"

        ; Wait for the Controller Properties dialog itself instead of
        ; guessing a fixed delay -- title is "Controller Properties - <name>"
        ; (dynamic per file, confirmed via Window Spy: ahk_class #32770,
        ; ahk_exe LogixDesigner.Exe), so match on the stable leading text.
        Sleep 10
        if !WinWait("Controller Properties", , 5) {
            MsgBox "Controller Properties dialog didn't appear within 5s."
            continue
        }
        Sleep 250

        Status("Selecting tab")
        Send "+{Tab}"
        Sleep 50
        Send "{Up}"
        Sleep 50
        Send "{Right}"
        Sleep 250

        Status("Reading Edit3 value")
        Sleep 20
        OCDValue := StripCommas(Trim(ControlGetText("Edit3", "A")))
				ButtonTest := ControlGetText("Button1", "A")
        Status("Read OCD value: " OCDValue)
        Sleep 200
				Status("Read Test value: " ButtonTest)
        Sleep 250
				
				if OCDValue = "0" AND ButtonTest != "Redundancy Enabled"{
					Status("Reading 1769 Edit8 value")
											Sleep 50
							Send "{Tab}"
							Sleep 50
							Send "{Tab}"
							Sleep 50
							Send "{Enter}"
							Sleep 500
							OCDValue := StripCommas(Trim(ControlGetText("Edit8", "A")))
				}
				
				
				if OCDValue = "" OR OCDValue = "0" OR !IsNumber(OCDValue){
					Status("Reading Static23 value")
					Sleep 20
					OCDValue := StripCommas(Trim(ControlGetText("Static23", "A")))
					Status("Read Static23 value: {{" OCDValue "}}")
					
					Sleep 150
					
					; L7 or 1769
					if OCDValue = "" OR !IsNumber(OCDValue) OR OCDValue = "0" {
							Status("Read 1769 series Edit8 OCD value: " OCDValue)
							Sleep 2000
							Send "{Right}"
							Sleep 50   
							Send "{Right}"
							Sleep 50
							Send "{Tab}"
							Sleep 50
							Send "{Tab}"
							Sleep 50
							
							
							

								try isEnabled := ControlGetEnabled("Button2", "A")
								catch
										isEnabled := 0

								if (isEnabled) {
										Send("{Enter}")
								} 
						


							
							
							
							;Send "{Enter}"
							Sleep 500
							OCDValue := StripCommas(Trim(ControlGetText("Edit8", "A")))
					}					
				}
				
        Status("~ Read OCD value: " OCDValue)

        Send "!{F4}"
        Sleep 25

        ; A second save-changes prompt can appear here too, after closing
        ; Controller Properties -- same dismissal, discard and move on.
        ; Disabled 2026-08-22 -- James found it wasn't actually firing at
        ; this point in practice; left in place, commented, in case it
        ; resurfaces on a different file shape.
        ;if WinWait(, "Save the changes?", 2) {
        ;    Send "n"
        ;    Sleep 250
        ;}

        Status("Write Changes to manifest file")
        Sleep 5

        ; --- Hand results back to PowerShell ---
        handoffFile := FileOpen(HANDOFF_PATH, "w")
        handoffFile.Write("error_count,warning_count,message_value,ocd_value,window_title`n")
        handoffFile.Write(StripCommas(ErrorValue) "," StripCommas(WarningValue) "," StripCommas(MessageValue) "," OCDValue "," CsvQuote(WindowTitle) "`n")
        handoffFile.Close()

        Status("Looping -- waiting for next file...")
        ; Loop top handles the wait for PowerShell's next request -- no
        ; fixed sleep-and-alt-tab block needed anymore now that File|Open
        ; replaces close/reopen, and WinActivate replaces relying on
        ; whatever last had focus.
    }
}

Esc::ExitApp

F9:: {
    title := WinGetTitle("A")
    hwnd := ControlGetHwnd("Edit3", "A")
    txt := ControlGetText("Edit3", "A")
    MsgBox "Active window: " title "`nEdit3 HWND: " hwnd "`nEdit3 text: [" txt "]"
}

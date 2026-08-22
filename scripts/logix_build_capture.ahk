; Logix Designer build/verify + Capacity capture loop (James, 2026-08-22).
; Companion to batch_memory_capture.ps1 -- that script writes the next ACD
; path to open (file existence at -OpenRequestPath = "go" signal, content +
; clipboard both carry the path) and polls for this script's results
; (-HandoffPath: error_count,warning_count,message_value,ocd_value,
; overwritten every cycle, consumed on read). This script never launches or
; closes Logix Designer -- it drives File > Open inside the same already-
; running instance (confirmed ~5s vs ~65s for a full close/reopen cycle).
;
; Update HANDOFF_PATH / OPEN_REQUEST_PATH below to match whatever you pass
; to batch_memory_capture.ps1's -HandoffPath / -OpenRequestPath.
;
; Confirmed empirically on James's machine (2026-08-22):
;   - Ctrl+O opens a dialog titled "Open Project" (not generic "Open").
;   - Switching files after a Build can trigger a save prompt with the text
;     "Project file '<name>.ACD' has been changed. Save the changes?" --
;     dismissed with 'n' (discard) since Build's cache write should never
;     get persisted back into a tracked sample file.
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
LOGIX_WIN := "ahk_exe LogixDesigner.exe"             ; TODO: confirm via Window Spy

global OCDValue := ""
global ErrorValue := ""
global WarningValue := ""
global MessageValue := ""

; Pulls the leading integer out of button/label text like "0 Warnings",
; "3 Errors", "1 Warning" -- handles singular/plural and any wording since
; it only looks for digits at the start. Returns "" (not "0") if nothing
; matched, so a bad ControlGetText read doesn't silently log a false zero.
ExtractCount(text) {
    if RegExMatch(Trim(text), "^(\d+)", &m)
        return m[1]
    return ""
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

        ; Switching away from a Build-modified project can prompt to save
        ; first -- discard, never persist Build's cache write into the
        ; tracked sample file. TODO: confirm 'n' is really the access key
        ; for this dialog's "No"/"Don't Save" button.
        if WinWait(, "Save the changes?", 2)
            Send "n"

        if !WinWait("Open Project", , 5) {
            MsgBox "Open Project dialog didn't appear within 5s -- check the Ctrl+O shortcut."
            continue
        }
        Sleep 25
        Send "^v"   ; paste the path PowerShell put on the clipboard
        Sleep 100
        Send "{Enter}"

        ; Wait for the project to actually load. TODO: replace with a real
        ; "loaded" signal (e.g. WinWaitActive on a title pattern) once you
        ; know what changes on screen when load finishes -- file size will
        ; vary this just like Build does, same reasoning as the Build popup.
        Sleep 3000

        ; --- Build ---
        Status("Alt")
        Send "{Alt}"
        Sleep 50
        Status("l")
        Send "l"
        Sleep 50
        Status("b")
        Send "b"
        Sleep 250

        buildPopupTitle := "Building"
        if WinWait(buildPopupTitle, , 1) {
            maxWaitSeconds := 600   ; ceiling so a hung build doesn't loop forever
            if !WinWaitClose(buildPopupTitle, , maxWaitSeconds)
                MsgBox "Build popup didn't close within " maxWaitSeconds "s -- possible hang, check manually."
        }

        Sleep 1000
        ErrorValue := ExtractCount(ControlGetText("Button10", "A"))
        WarningValue := ExtractCount(ControlGetText("Button11", "A"))
        MessageValue := ExtractCount(ControlGetText("Button12", "A"))
        Status("Errors/Warnings/Message: " ErrorValue ", " WarningValue ", " MessageValue)

        ; --- Controller Properties -> Capacity (OCD value) ---
        Sleep 1000
        Status("Alt")
        Send "{Alt}"
        Sleep 50
        Status("e")
        Send "e"
        Sleep 50
        Status("n")
        Send "n"
        Sleep 250

        Status("Selecting tab")
        Send "+{Tab}"
        Sleep 50
        Send "{Up}"
        Sleep 50
        Send "{Right}"
        Sleep 50

        Status("Reading Edit3 value")
        Sleep 2000
        OCDValue := Trim(ControlGetText("Edit3", "A"))
        Status("Read OCD value: " OCDValue)
        Sleep 250

        Send "!{F4}"
        Sleep 250
        Send "!{F4}"
        Sleep 2000

        ; --- Hand results back to PowerShell ---
        handoffFile := FileOpen(HANDOFF_PATH, "w")
        handoffFile.Write("error_count,warning_count,message_value,ocd_value`n")
        handoffFile.Write(ErrorValue "," WarningValue "," MessageValue "," OCDValue "`n")
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

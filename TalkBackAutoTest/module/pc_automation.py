import sys
import time
import ctypes
from ctypes import wintypes

class KEYBDINPUT(ctypes.Structure):
    """Keyboard input structure for SendInput"""
    _fields_ = [
        ("wVk", wintypes.WORD),           # Virtual Key Code
        ("wScan", wintypes.WORD),         # Hardware scan code
        ("dwFlags", wintypes.DWORD),      # Flags (0 = press, KEYEVENTF_KEYUP = release)
        ("time", wintypes.DWORD),         # Timestamp (0 = use system)
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class INPUT(ctypes.Structure):
    """Input structure for SendInput"""
    _fields_ = [
        ("type", wintypes.DWORD),         # INPUT_KEYBOARD = 1
        ("ki", KEYBDINPUT),
        ("padding", ctypes.c_ubyte * 8)   # Padding for structure alignment
    ]

VK_TAB = 0x09           # Tab key
VK_RETURN = 0x0D        # Enter key
VK_CONTROL = 0x11       # Ctrl key
VK_LWIN = 0x5B          # Left Windows key

# Key event flags
KEYEVENTF_KEYUP = 0x0002

# CORE FUNCTIONS

def send_key_event(vk_code, is_key_up=False):
    """
    Send keyboard event using Windows SendInput API

    """
    try:
        # Create INPUT structure
        inputs = INPUT()
        inputs.type = 1  # INPUT_KEYBOARD
        inputs.ki.wVk = vk_code
        inputs.ki.wScan = 0
        inputs.ki.dwFlags = KEYEVENTF_KEYUP if is_key_up else 0
        inputs.ki.time = 0
        inputs.ki.dwExtraInfo = None
        
        # Call SendInput
        result = ctypes.windll.user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(inputs))
        return result
    except Exception as e:
        print(f"ERROR: send_key_event failed - {str(e)}", file=sys.stderr)
        return 0


def toggle_narrator():
    """
    Toggle Windows Narrator ON/OFF using Ctrl + Win + Enter shortcut

    """
    try:
        # Press keys in sequence: Ctrl -> Win -> Enter
        if send_key_event(VK_CONTROL, is_key_up=False) == 0:
            raise Exception("Failed to press Ctrl")
        
        if send_key_event(VK_LWIN, is_key_up=False) == 0:
            raise Exception("Failed to press Win")
        
        if send_key_event(VK_RETURN, is_key_up=False) == 0:
            raise Exception("Failed to press Enter")
        
        # Hold for system to recognize key combination
        time.sleep(0.1)
        
        # Release keys in reverse order: Enter -> Win -> Ctrl
        send_key_event(VK_RETURN, is_key_up=True)
        send_key_event(VK_LWIN, is_key_up=True)
        send_key_event(VK_CONTROL, is_key_up=True)
        
        print("OK: toggled ")
        return True
        
    except Exception as e:
        print(f"toggle failed - {str(e)}", file=sys.stderr)
        return False


def press_tab(times=1):
    """
    Press Tab key multiple times for UI navigation
  
    """
    delay_before = 2 # Delay before pressing Tab
    try:
        if times < 1:
            print("ERROR: times parameter must be >= 1")
            return False
        
        print(f"Pressing Tab {times} time(s)...")
        time.sleep(delay_before)  # Delay before starting to press Tab
        
        for i in range(times):
            # Press Tab
            if send_key_event(VK_TAB, is_key_up=False) == 0:
                raise Exception(f"Failed to press Tab at iteration {i+1}")
            
            time.sleep(0.05)  # Short delay while key is held
            
            # Release Tab
            if send_key_event(VK_TAB, is_key_up=True) == 0:
                raise Exception(f"Failed to release Tab at iteration {i+1}")
            
            # Delay between Tab presses
            time.sleep(0.2)
        
        print(f"OK: Tab pressed {times} time(s)")
        return True
        
    except Exception as e:
        print(f"ERROR: press_tab failed - {str(e)}", file=sys.stderr)
        return False

def main():
   
    # Check if action argument provided
    if len(sys.argv) < 2:
        print("ERROR: Missing action argument", file=sys.stderr)
        print_usage()
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    # Execute action
    if action == "narrator":
        success = toggle_narrator()
        sys.exit(0 if success else 1)
        
    elif action == "tab":
        # Parse optional count parameter
        times = 1
        if len(sys.argv) > 2:
            try:
                times = int(sys.argv[2])
                if times < 1:
                    print("ERROR: Tab count must be >= 1", file=sys.stderr)
                    sys.exit(1)
            except ValueError:
                print(f"ERROR: Invalid tab count '{sys.argv[2]}' - must be integer", file=sys.stderr)
                sys.exit(1)
        
        success = press_tab(times)
        sys.exit(0 if success else 1)
        
    else:
        print(f"Unknown action")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
    
    input()

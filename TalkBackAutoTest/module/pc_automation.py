import sys
import time
import ctypes
from ctypes import wintypes
import json
import uiautomation as auto
from uiautomation import ControlType, PatternId, PropertyId



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
VK_ESCAPE = 0x1B        # Escape key

# Key event flags
KEYEVENTF_KEYUP = 0x0002


# ELEMENT INSPECTION

# --- Constants: Enum to String Mappings ---
TOGGLE_STATE_NAMES = {
    0: 'Off',
    1: 'On',
}

EXPAND_COLLAPSE_STATE_NAMES = {
    0: 'Collapsed',
    1: 'Expanded',
}

# --- Pattern Handler Functions  ---

def _extract_value_pattern(element):
    """Extract Value from ValuePattern. Returns string or None."""
    if element.GetPattern(PatternId.ValuePattern):
        pattern = element.GetValuePattern()
        return pattern.Value
    return None


def _extract_toggle_pattern(element):
    """Extract ToggleState from TogglePattern. Returns 'On'/'Off'/etc or None."""
    if element.GetPattern(PatternId.TogglePattern):
            pattern = element.GetTogglePattern()
            state = pattern.ToggleState
            return TOGGLE_STATE_NAMES.get(state, str(state))

    return None


def _extract_expand_collapse_pattern(element):
    """Extract ExpandCollapseState. Returns 'Collapsed'/'Expanded'/etc or None."""
    if element.GetPattern(PatternId.ExpandCollapsePattern):
            pattern = element.GetExpandCollapsePattern()
            state = pattern.ExpandCollapseState
            return EXPAND_COLLAPSE_STATE_NAMES.get(state, str(state))
    return None



def _extract_selection_item_pattern(element):
    """Extract IsSelected from SelectionItemPattern. Returns 'selected'/'non-selected' or None."""
    if element.GetPattern(PatternId.SelectionItemPattern):
            pattern = element.GetSelectionItemPattern()
            return 'selected' if pattern.IsSelected else 'non-selected'
    return None


def _extract_position_in_set(element):
    """Extract PositionInSet and SizeOfSet properties.
    
    Returns dict { 'Index': pos, 'Total': size } if both values > 0.
    Returns None if properties are not set (value = 0).
    """
    pos = element.GetPropertyValue(PropertyId.PositionInSetProperty)
    size = element.GetPropertyValue(PropertyId.SizeOfSetProperty)
    
    if pos > 0 and size > 0:
        return {'Index': pos, 'Total': size}
    return None


# --- Control Type to Pattern Mapping ---
CONTROL_PATTERNS = {
    50004: ['Value'],                          # EditControl
    50030: ['Value'],                          # DocumentControl
    50002: ['ToggleState'],                    # CheckBoxControl
    50013: ['IsSelected'],                     # RadioButtonControl 
    50000: ['ToggleState'],                    # ButtonControl (toggle variant)
    50003: ['Value', 'ExpandCollapseState'],   # ComboBoxControl
    50007: ['IsSelected', 'ToggleState', 'ExpandCollapseState'],  # ListItemControl
    50024: ['ExpandCollapseState'],            # TreeItemControl
}

# Map pattern names to handler functions
PATTERN_HANDLERS = {
    'Value': _extract_value_pattern,
    'ToggleState': _extract_toggle_pattern,
    'ExpandCollapseState': _extract_expand_collapse_pattern,
    'IsSelected': _extract_selection_item_pattern,
}

# --- Main Function ---

def get_focused_element_info():
    """
    Get information about currently focused UI element.
    
    dict: Element info with base properties and control-specific patterns.
            Only includes fields that have values (no None fields).
            - Always: Name, LocalizedControlType
            - If set: Position, Value, ToggleState, ExpandCollapseState, IsSelected
        None: If no element focused or uiautomation unavailable.
    """
    if auto is None:
        print("ERROR: uiautomation library not available", file=sys.stderr)
        return None
    
    element = auto.GetFocusedControl()
    if element is None:
        print("ERROR: No focused element found", file=sys.stderr)
        return None
    
    # Base properties 
    result = {
        'Name': element.Name or '',
        'LocalizedControlType': element.LocalizedControlType or '',
    }
    
    # Position (only if set)
    position = _extract_position_in_set(element)
    if position:
        result['Position'] = position
    
    # Extract patterns for this control type (only include if not None)
    control_type_id = element.ControlType
    pattern_names = CONTROL_PATTERNS.get(control_type_id, [])
    
    for pattern_name in pattern_names:
        handler = PATTERN_HANDLERS.get(pattern_name)
        if handler:
            value = handler(element)
            if value is not None:
                result[pattern_name] = value
    
    return result
        

def send_key_event(vk_code, is_key_up=False):
    """
    Send keyboard event using Windows SendInput API

    """
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


def toggle_narrator():
    """
    Toggle Windows Narrator ON/OFF using Ctrl + Win + Enter shortcut

    """
    # Press keys in sequence: Ctrl -> Win -> Enter
    send_key_event(VK_CONTROL, is_key_up=False)
            
    send_key_event(VK_LWIN, is_key_up=False) 
            
    send_key_event(VK_RETURN, is_key_up=False) 
            
    # Hold for system to recognize key combination
    time.sleep(0.1)
        
    # Release keys in reverse order: Enter -> Win -> Ctrl
    send_key_event(VK_RETURN, is_key_up=True)
    send_key_event(VK_LWIN, is_key_up=True)
    send_key_event(VK_CONTROL, is_key_up=True)
        
    print("toggled ")
    return True
        
def press_tab():
    """
    Press Tab key one time for UI navigation
    """

    # Press Tab
    send_key_event(VK_TAB, is_key_up=False)
        
    time.sleep(0.05)  # Short delay while key is held
        
    # Release Tab
    send_key_event(VK_TAB, is_key_up=True) 
        
    time.sleep(0.3)  # Delay after Tab press
    return True


def is_escape_pressed():
    """
    Returns True if ESC is pressed
    """
    state = ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE)
    
    return (state & 0x8000) != 0 or (state & 0x0001) != 0


def run_tab_sequence():
    """
    Executes the tab navigation sequence with automatic cycle detection.
    Uses RuntimeId to detect when Tab loop returns to a previously-visited element.
    """
    print("Press ESC to stop", file=sys.stderr)
    time.sleep(1)
    
    count = 0
    seen_runtime_ids = set()
    
    while True:
        if is_escape_pressed():
            print("Stopped by user", file=sys.stderr)
            break
        
        if not press_tab():
            print(f"Failed at iteration {count + 1}", file=sys.stderr)
            return False
        count += 1
        
        element = auto.GetFocusedControl()
        if element is None:
            print("Focus lost", file=sys.stderr)
            break
        
        # Get RuntimeId 
        runtime_id = element.GetRuntimeId()
        
        if runtime_id in seen_runtime_ids:
            print(f"Total unique elements: {len(seen_runtime_ids)}", file=sys.stderr)
            break
        seen_runtime_ids.add(runtime_id)
        
        element_info = get_focused_element_info()
        if element_info:
            print(json.dumps(element_info, ensure_ascii=False))
        else:
            print(json.dumps(None))
        
    sys.stdout.flush()
    
    print(f"Tab pressed {count} time(s)", file=sys.stderr)
    print(f"Unique elements visited: {len(seen_runtime_ids)}", file=sys.stderr)
    return True


def main():
   
    # Check if action argument provided
    if len(sys.argv) < 2:
        print("ERROR: Missing action argument", file=sys.stderr)
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    # Execute action
    if action == "get_focused":
        result = get_focused_element_info()
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result is not None else 1)
    
    elif action == "narrator":
        success = toggle_narrator()
        sys.exit(0 if success else 1)
        
    elif action == "tab":
        success = run_tab_sequence()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
    input()

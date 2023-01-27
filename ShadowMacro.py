import time
import threading

from pynput import keyboard
from pynput import mouse

from playsound import playsound

keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()

f1 = keyboard.Key.f1,
f2 = keyboard.Key.f2
f3 = keyboard.Key.f3
f4 = keyboard.Key.f4
f5 = keyboard.Key.f5
f6 = keyboard.Key.f6
f7 = keyboard.Key.f7
f8 = keyboard.Key.f8
f9 = keyboard.Key.f9
f10 = keyboard.Key.f10
f11 = keyboard.Key.f11
f12 = keyboard.Key.f12

ctrl = keyboard.Key.ctrl_l
shift = keyboard.Key.shift

start_record_audio_path = "./audio_files/start_recording.wav"
stop_record_audio_path = "./audio_files/stop_recording.wav"
run_macro_audio_path = "./audio_files/run_macro.wav"
run_macro_loop_audio_path = "./audio_files/run_macro_loop.wav"
end_macro_audio_path = "./audio_files/end_macro.wav"
stop_macro_audio_path = "./audio_files/stop_macro.wav"
speed_up_macro_audio_path = "./audio_files/speed_up.wav"
slow_down_macro_audio_path = "./audio_files/slow_down.wav"
cant_do_that_macro_audio_path = "./audio_files/cant_do_that.wav"

recording = []
is_recording = False
time_last_input = 0

key_states = {}
key_states_recording = {}

mouse_states = {}
mouse_states_recording = {}

running_macro = 0
stop_macro = False
macro_speed = 1.0
loop_macro = False
D_SPEED_MACRO = 0.5


def stop_script():
    exit()

def on_key_press(key):
    global key_states, key_states_recording, recording, stop_macro, loop_macro
    
    k = None
    try:
        k = key.char
    except AttributeError:
        k = key
    
    if (k in key_states.keys() and key_states[k] == 1):
        return
    
    key_states[k] = 1
    
    
    if ((keyboard.Key.ctrl_l in key_states and key_states[keyboard.Key.ctrl_l] == 1) and (keyboard.Key.shift in key_states and key_states[keyboard.Key.shift] == 1)):
        
        if (k == f9):
            if (running_macro):
                print("Cannot record macro while a macro is running.")
                play_sound(cant_do_that_macro_audio_path)
            elif (not is_recording):
                start_recording()
            else:
                # don't record hotkeys that stopped the recording
                for action in reversed(recording):
                    if (action[1] == "key_press" and action[2] == keyboard.Key.ctrl_l):
                        recording.remove(action)
                        break
                for action in reversed(recording):
                    if (action[1] == "key_press" and action[2] == keyboard.Key.shift):
                        recording.remove(action)
                        break
                stop_recording()
            return
        
        if (k == f10 or k == f8):
            if (is_recording):
                print("Cannot play macro while recording.")
                play_sound(cant_do_that_macro_audio_path)
            elif (len(recording) <= 0):
                print("Must record macro before running it.")
                play_sound(cant_do_that_macro_audio_path)
            elif (not running_macro):
                loop_macro = (True, False)[k == f10]
                recording_thread = threading.Thread(target = run_macro)
                recording_thread.start()
            else:
                stop_macro = True
            return
        
        if (k == f11):
            if (running_macro):
                print("Cannot change macro speed while it's running.")
                play_sound(cant_do_that_macro_audio_path)
            elif (is_recording):
                print("Cannot change macro speed while recording.")
                play_sound(cant_do_that_macro_audio_path)
            else:
                slow_down_macro()
        if (k == f12):
            if (running_macro):
                print("Cannot change macro speed while it's running.")
                play_sound(cant_do_that_macro_audio_path)
            elif (is_recording):
                print("Cannot change macro speed while recording.")
                play_sound(cant_do_that_macro_audio_path)
            else:
                speed_up_macro()
    
    if (not is_recording):
        return
    if (k in key_states_recording.keys() and key_states_recording[k] == 1):
        return
    
    current_time = time.time()
    key_states_recording[k] = 1
    recording.append([current_time, "key_press", k, 1])
    
    
def on_key_release(key):
    global key_states, key_states_recording, recording
    
    k = None
    try:
        k = key.char
    except AttributeError:
        k = key
    
    if (not k in key_states.keys() or key_states[k] == 0):
        return
    
    key_states[k] = 0
    
    if (not is_recording):
        return
    if (not k in key_states_recording.keys() or key_states_recording[k] == 0):
        return
    
    current_time = time.time()
    key_states_recording[k] = 0
    recording.append([current_time, "key_press", k, 0])


def on_mouse_move(x, y):
    global recording
    
    if (not is_recording):
        return
    
    current_time = time.time()
    recording.append([current_time, "move_mouse", x, y])


def on_mouse_click(x, y, button, pressed):
    global recording, mouse_states, mouse_states_recording
    
    mouse_states[button.name] = pressed
    
    if (not is_recording):
        return
    
    if (pressed and button.name in mouse_states_recording.keys() and mouse_states_recording[button.name] == pressed):
        return
    if (not pressed and (not button.name in mouse_states_recording.keys() or mouse_states_recording[button.name] == pressed)):
        return
    
    current_time = time.time()
    mouse_states_recording[button.name] = pressed
    recording.append([current_time, "mouse_click", button, pressed, x, y])


def on_mouse_scroll(x, y, dx, dy):
    global recording
    
    if (not is_recording):
        return
    
    current_time = time.time()
    recording.append([current_time, "mouse_scroll", dx, dy, x, y])




def start_recording():
    global is_recording, recording
    
    keyboard_controller.release(keyboard.Key.ctrl_l)
    keyboard_controller.release(keyboard.Key.shift)
    keyboard_controller.release(keyboard.Key.f9)
    mouse_states[keyboard.Key.ctrl_l] = 0
    mouse_states[keyboard.Key.shift] = 0
    mouse_states[keyboard.Key.f9] = 0
    
    if (is_recording):
        return
    
    play_sound(start_record_audio_path)
    print("RECORDING STARTED")
    play_sound(start_record_audio_path)
    is_recording = True
    recording = []
    mouse_pos = mouse_controller.position
    on_mouse_move(mouse_pos[0], mouse_pos[1])
    
    
def stop_recording():
    global is_recording, macro_speed
    if (not is_recording):
        return
    print("RECORDING STOPPED")
    play_sound(stop_record_audio_path)
    macro_speed = 1.0
    is_recording = False


def speed_up_macro(amount = D_SPEED_MACRO):
    global macro_speed
    play_sound(speed_up_macro_audio_path)
    macro_speed += amount
    macro_speed = (round(macro_speed * 10)) / 10
    print(f"Speeding up macro by {amount}. New macro speed: {macro_speed}")
    if (macro_speed > 50.0):
        macro_speed = 50.0


def slow_down_macro(amount = D_SPEED_MACRO):
    global macro_speed
    play_sound(slow_down_macro_audio_path)
    macro_speed -= amount
    macro_speed = (round(macro_speed * 10)) / 10
    print(f"Slowing down macro by {amount}. New macro speed: {macro_speed}")
    if (macro_speed < 0.1):
        macro_speed = 0.1


def run_macro():
    global is_recording, recording, running_macro, stop_macro, loop_macro
    
    keyboard_controller.release(keyboard.Key.ctrl_l)
    keyboard_controller.release(keyboard.Key.shift)
    keyboard_controller.release(keyboard.Key.f10)
    mouse_states[keyboard.Key.ctrl_l] = 0
    mouse_states[keyboard.Key.shift] = 0
    mouse_states[keyboard.Key.f10] = 0
    
    pressed_keys = []
    pressed_buttons = []
    
    if (is_recording or len(recording) <= 0):
        return
    
    print("\nMACRO START" + ("", " (loop)\nPress CTRL + SHIFT + F10 to stop the macro.")[loop_macro])
    play_sound((run_macro_audio_path, run_macro_loop_audio_path)[loop_macro])
    running_macro = True
    played_once = False
    
    while(not (played_once) or loop_macro):
        played_once = True
        start_time = time.time()
        macro_start_time = recording[0][0]
        macro_time = 0
        
        action_num = 0
        for action in recording:
            current_time = time.time()
            macro_time = (current_time - start_time)
            action_time = action[0]
            action_time_rel = (action_time - macro_start_time) / macro_speed
            
            # wait until execution
            wait_time = action_time_rel - macro_time
            if (wait_time > 0):
                time.sleep(wait_time)
            
            if (action[1] == "move_mouse"):
                mouse_controller.position = (action[2], action[3])
                
            elif (action[1] == "mouse_click"):
                button = action[2]
                pressed = action[3]
                mouse_controller.position = (action[4], action[5])
                time.sleep(0.01)
                if (pressed):
                    mouse_controller.press(button)
                    if (not button in pressed_buttons):
                        pressed_buttons.append(button)
                else:
                    mouse_controller.release(button)
                    if (button in pressed_buttons):
                        pressed_buttons.remove(button)
                time.sleep(0.01)
                
            elif (action[1] == "key_press"):
                key = action[2]
                pressed = action[3]
                time.sleep(0.01)
                if (pressed):
                    keyboard_controller.press(key)
                    if (not key in pressed_keys):
                        pressed_keys.append(key)
                else:
                    keyboard_controller.release(key)
                    if (key in pressed_keys):
                        pressed_keys.remove(key)
                time.sleep(0.01)
                    
            elif (action[1] == "mouse_scroll"):
                mouse_controller.position = (action[4], action[5])
                mouse_controller.scroll(action[2], action[3])
                
            else:
                print(f"Error running macro. Found unregistered event: {action[1]}")
            
            action_num += 1
            if (stop_macro):
                loop_macro = False
                break
    
    # release keys/buttons so they don't stay pressed
    for key in pressed_keys:
        keyboard_controller.release(key)
    for button in pressed_buttons:
        mouse_controller.release(button)
    
    running_macro = False
    loop_macro = False
    if (stop_macro):
        print("MACRO STOPPED")
        play_sound(stop_macro_audio_path)
        stop_macro = False
    else:
        print("END MACRO")
        play_sound(end_macro_audio_path)


def play_sound(path):
    recording_thread = threading.Thread(target=playsound, args=(path,), daemon=True)
    recording_thread.start()


def main():
    print("Script started")
    print("Start/Stop recording macro: CTRL + SHIFT + F9")
    print("Play macro: CTRL + SHIFT + F10")
    print(f"Slow down macro ({D_SPEED_MACRO}x): CTRL + SHIFT + F11")
    print(f"Speed up macro ({D_SPEED_MACRO}x): CTRL + SHIFT + F12")
    
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click, on_scroll=on_mouse_scroll)
    
    keyboard_listener.start()
    mouse_listener.start()
    mouse_listener.join()
    
    





if (__name__ == "__main__"):
    main()

import os
import subprocess
import shutil
import filecmp
import tempfile
from tkinter import Tk, Button, Label, filedialog, Checkbutton, BooleanVar, messagebox, LabelFrame, NORMAL, DISABLED
from tkinter.ttk import Combobox
import time
import threading
import numpy as np

root = Tk()
root.title("Mass WAV to FLAC")
root.geometry("300x410")
settings_frame = LabelFrame(root, text="Settings", padx=10, pady=10)
settings_frame.pack(pady=10, padx=10, fill="both", expand=True)
# half gui at bottom hahahaha
script_dir = os.path.dirname(os.path.abspath(__file__))
local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
local_flaccl = os.path.join(script_dir, 'CUETools.FLACCL.cmd.exe')
command_ffmpeg = 'ffmpeg'
preserve_wav = BooleanVar()
preserve_wav.set(False)
selected_dir = None
allow_lossy = BooleanVar()
allow_lossy.set(False)
allow_overwrite = BooleanVar()
allow_overwrite.set(True)
delete_larger = BooleanVar()
delete_larger.set(True)
gpu_mode = BooleanVar()
gpu_mode.set(False)
cmd_mode = BooleanVar()
cmd_mode.set(True)
successful_conversions = 0
lossy_conversions = 0
lossy_converts = []
conversion_errors = 0
converted_errors = []
fileconflict_skip = 0
conflicted_skips = []
process = None
start_time = 0

def browse_directory():
    global selected_dir
    selected_dir = filedialog.askdirectory()
    directory_label.config(text=f"Directory: {selected_dir}")

def start_conversion(mode_var):
    global selected_dir, successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, process, start_time
    reset_conversion_statistics()
    allow_lossy_value = allow_lossy.get()
    allow_overwrite_value = allow_overwrite.get()
    delete_larger_value = delete_larger.get()
    if selected_dir:
        num_files = count_files(selected_dir, mode_var.get())
        if num_files > 0:
            message = f"Directory: {selected_dir}\n\nNumber of audio files to convert: {num_files}\n\nPlease ensure your settings and directory are correct, lost files are not recoverable. Are you sure you want to proceed?"
            response = messagebox.askquestion("Confirmation", message)
            if response == "yes":
                for widget in settings_frame.winfo_children():
                    widget.configure(state=DISABLED)
                browse_button.config(state=DISABLED)
                start_button.config(state=DISABLED)
                mode = mode_var.get()
                start_time = time.time()
                def run_conversion():
                    nonlocal allow_lossy_value, allow_overwrite_value, delete_larger_value
                    if mode == "WAV to FLAC":
                        convert_wav_to_flac(selected_dir, preserve_wav, allow_lossy_value, allow_overwrite_value, delete_larger_value)
                    elif mode == "FLAC to WAV":
                        convert_flac_to_wav(selected_dir, preserve_wav, allow_overwrite_value)
                    root.after(0, lambda: enable_widgets(settings_frame.winfo_children() + [browse_button] + [start_button]))
                    check_conversion()
                process = threading.Thread(target=run_conversion)
                process.start()
        else:
            message = f"Error: No audio files elligble for conversion could be found. Please check your directory and or permissions."
            messagebox.showinfo("Error: No files found", message)
            
def enable_widgets(widgets):
    for widget in widgets:
        widget.configure(state=NORMAL)

def check_conversion():
    global process, successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, start_time
    if process and process.is_alive():
        root.after(100, check_conversion)
    elif process:
        show_conversion_statistics(time.time() - start_time)

def count_files(directory, mode):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if mode == "WAV to FLAC" and file.endswith('.wav'):
                count += 1
            elif mode == "FLAC to WAV" and file.endswith('.flac'):
                count += 1
    return count

def reset_conversion_statistics():
    global successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, lossy_converts, converted_errors, conflicted_skips
    successful_conversions = 0
    lossy_conversions = 0
    conversion_errors = 0
    fileconflict_skip = 0
    lossy_converts = []
    converted_errors = []
    conflicted_skips = []

def convert_wav_to_flac(directory, preserve_wav, allow_lossy, allow_overwrite, delete_larger):
    global successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, lossy_converts, converted_errors, conflicted_skips
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.wav'):
                wav_file = os.path.join(root, file)
                flac_file = os.path.splitext(wav_file)[0] + '.flac'
                try:
                    if not allow_overwrite and os.path.exists(flac_file):
                        fileconflict_skip += 1
                        conflicted_skips.append(wav_file)
                        print(f"{wav_file} is being skipped as it already exists and overwrite is not enabled.")
                        continue
                    if os.path.exists(flac_file):
                        try:
                            os.remove(flac_file)
                        except FileNotFoundError:
                            print(f"Can't overwrite {flac_file} as it's not found, idk how you're even getting this error.")
                        except PermissionError:
                            print(f"Error overwriting {flac_file}: Permission not granted. Skipping.")
                            continue
                        except Exception as e:
                            print(f"Unexpected error overwriting {flac_file}, skipping")
                            continue
                    if cmd_mode.get():
                        ffmpeg_path = command_ffmpeg
                    else:
                        ffmpeg_path = local_ffmpeg
                        
                    if gpu_mode.get():
                        subprocess.run([local_flaccl, '--lax', '--fast-gpu', '--no-md5', '--cpu-threads', '2', wav_file], check=True)
                    else:
                        subprocess.run([ffmpeg_path, '-i', wav_file, '-compression_level', '12', flac_file], check=True)
                        # , '-strict', 'experimental'    (32 bit int lines?)
                    shutil.copystat(wav_file, flac_file)
                    wav_size = os.path.getsize(wav_file)
                    flac_size = os.path.getsize(flac_file)
                    if flac_size > wav_size and delete_larger:
                        fileconflict_skip += 1
                        conflicted_skips.append(wav_file)
                        try:
                            os.remove(flac_file)
                            print(f"Deleted {flac_file} as it has a larger file size than {wav_file}.")
                        except FileNotFoundError:
                            print(f"Smaller FLAC conversion detected but {flac_file} could not be delete as it's not found, idk how you're even getting this error.")
                        except PermissionError:
                            print(f"Smaller FLAC conversion detected but {flac_file} could not be removed: Permission not granted.")
                            continue
                        except Exception as e:
                            print(f"Smaller FLAC conversion detected but {flac_file} could not be removed")
                            continue
                        continue
                    if allow_lossy or is_lossless_conversion(wav_file, flac_file):
                        successful_conversions += 1
                        if not preserve_wav.get():
                            try:
                                os.remove(wav_file)
                                print(f"Successful conversion, source {wav_file} deleted.")
                            except FileNotFoundError:
                                print(f"Can't delete {wav_file} post conversion as it's not found, idk how you're even getting this error.")
                                continue
                            except PermissionError:
                                print(f"Error deleting {wav_file} post conversion: Permission not granted.")
                                continue
                            except Exception as e:
                                print(f"Unexpected error deleting {wav_file} post conversion")
                                continue
                        else:
                            print(f"Successful conversion, source {wav_file} preserved.")
                    else:
                        lossy_conversions += 1
                        lossy_converts.append(wav_file)
                        print(f"Warning: Lossy conversion detected for {wav_file} -> {flac_file}")
                        try:
                            os.remove(flac_file)
                            print(f"Deleted {flac_file} due to lossy conversion")
                        except FileNotFoundError:
                            print(f"Lossy FLAC conversion detected but {flac_file} could not be delete as it's not found, idk how you're even getting this error.")
                        except PermissionError:
                            print(f"Lossy FLAC conversion detected but {flac_file} could not be removed: Permission not granted.")
                            continue
                        except Exception as e:
                            print(f"Lossy FLAC conversion detected but {flac_file} could not be removed")
                            continue
                except Exception as e:
                    conversion_errors += 1
                    converted_errors.append(wav_file)
                    print(f"Error: {e}")

def convert_flac_to_wav(directory, preserve_wav, allow_overwrite):
    global successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, lossy_converts, converted_errors, conflicted_skips
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.flac'):
                flac_file = os.path.join(root, file)
                wav_file = os.path.splitext(flac_file)[0] + '.wav'
                try:
                    if allow_overwrite:
                        if os.path.exists(wav_file):
                            try:
                                os.remove(wav_file)
                            except FileNotFoundError:
                                conversion_errors += 1
                                converted_errors.append(flac_file)
                                print(f"Can't delete {wav_file} as it's not found, idk how you're even getting this error. Skipping")
                                continue
                            except PermissionError:
                                conversion_errors += 1
                                converted_errors.append(flac_file)
                                print(f"Error deleting {wav_file}: Permission not granted. Skipping conversion.")
                                continue
                            except Exception as e:
                                conversion_errors += 1
                                converted_errors.append(flac_file)
                                print(f"Unexpected error deleting {wav_file}, skipping conversion")
                                continue
                    else:
                        if os.path.exists(wav_file):
                          fileconflict_skip += 1
                          conflicted_skips.append(flac_file)
                          print(f"{wav_file} is being skipped as it already exists and overwrite is not enabled.")
                          continue
                    bit_depth_mapping = {'s16': '16', 's32': '24'}
                    bit_depth = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=sample_fmt', '-of', 'default=noprint_wrappers=1:nokey=1', flac_file], universal_newlines=True).strip()
                    subprocess.run(['ffmpeg', '-i', flac_file, '-c:a', 'pcm_s' + bit_depth_mapping.get(bit_depth, '16') + 'le', wav_file])
                    shutil.copystat(flac_file, wav_file)
                    successful_conversions += 1
                    if not preserve_wav.get():
                        try:
                            os.remove(flac_file)
                        except FileNotFoundError:
                            print(f"Can't delete {wav_file} post conversion as it's not found, idk how you're even getting this error.")
                            continue
                        except PermissionError:
                            print(f"Error deleting {wav_file} post conversion: Permission not granted.")
                            continue
                        except Exception as e:
                            print(f"Unexpected error deleting {wav_file} post conversion")
                            continue
                        print(f"Successful conversion, source {flac_file} deleted.")
                    else:
                        print(f"Successful conversion, source {flac_file} preserved.")
                except Exception as e:
                    conversion_errors += 1
                    converted_errors.append(flac_file)
                    print(f"Error converting {flac_file} to WAV: {e}")

def is_lossless_conversion(original_wav, converted_flac):
    try:
        identifier = os.path.basename(original_wav).split('.')[0]
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as original_temp:
            with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as converted_temp:
                original_temp_path = original_temp.name
                converted_temp_path = converted_temp.name

                # Convert to 32-bit float PCM for comparison
                subprocess.run(['ffmpeg', '-i', original_wav, '-f', 'f32le', '-y', original_temp_path], check=True)
                subprocess.run(['ffmpeg', '-i', converted_flac, '-f', 'f32le', '-y', converted_temp_path], check=True)

                # Read PCM data from temporary files
                original_data = np.fromfile(original_temp_path, dtype=np.float32)
                converted_data = np.fromfile(converted_temp_path, dtype=np.float32)

                # Compare PCM data
                if np.array_equal(original_data, converted_data):
                    print(f"Conversion is lossless: {original_wav} -> {converted_flac}")
                    return True
                else:
                    print(f"Warning: Lossy conversion detected for {original_wav} -> {converted_flac}")
                    return False

    except subprocess.CalledProcessError as e:
        print(f"Error during conversion check: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during lossless check: {e}")
        return False
    finally:
        try:
            os.unlink(original_temp_path)
            os.unlink(converted_temp_path)
        except (FileNotFoundError, PermissionError):
            pass

def show_conversion_statistics(elapsed_time):
    global successful_conversions, lossy_conversions, conversion_errors, fileconflict_skip, lossy_converts, converted_errors, conflicted_skips
    message = f"Conversion Statistics:\n\nSuccessful conversions: {successful_conversions}\nSkipped due to lossy conversion: {lossy_conversions}\nSkipped due to error: {conversion_errors}\nSkipped due to settings: {fileconflict_skip}\n\nElapsed time: {elapsed_time:.2f} seconds"
    messagebox.showinfo("Conversion Complete", message)
    #print(f"Batch complete!\n Files skipped due to lossy conversion:\n{lossy_converts}\n\nFiles skipped due to error:\n{converted_errors}\n\nFiles skipped due to settings:\n{conflicted_skips}")
    
    print(f"\n\n\nBatch complete!\n\nFiles skipped due to lossy conversion:")
    for item in lossy_converts:
        print(item)
    print(f"\nFiles skipped due to error:")
    for item in converted_errors:
        print(item)
    print(f"\nFiles skipped due to settings:")
    for item in conflicted_skips:
        print(item)

Checkbutton(settings_frame, text="Preserve original files", variable=preserve_wav).pack(anchor="w", pady=2)
Checkbutton(settings_frame, text="Skip lossless check", variable=allow_lossy).pack(anchor="w", pady=2)
Checkbutton(settings_frame, text="Allow overwriting", variable=allow_overwrite).pack(anchor="w", pady=2)
Checkbutton(settings_frame, text="Undo inefficient FLAC converts", variable=delete_larger).pack(anchor="w", pady=2)
Checkbutton(settings_frame, text="GPU mode (EXPERIMENTAL & BUGGY!!)", variable=gpu_mode).pack(anchor="w", pady=2)
Checkbutton(settings_frame, text="Command line ffmpeg", variable=cmd_mode).pack(anchor="w", pady=2)
modes = ["WAV to FLAC", "FLAC to WAV"]
mode_var = Combobox(settings_frame, values=modes, state="readonly")
mode_var.set("WAV to FLAC")
mode_var.pack(anchor="w", pady=2)
directory_label = Label(root, text="No directory selected", pady=5, wraplength=250)
directory_label.pack()
browse_button = Button(root, text="Browse", command=browse_directory)
browse_button.pack(pady=5)
start_button = Button(root, text="Start", command=lambda: start_conversion(mode_var))
start_button.pack(pady=10)
root.mainloop()
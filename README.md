# MassWAV2FLAC
Feature rich GUI batch WAV to FLAC converter in Python using ffmpeg and optionally FLACCL, prioritizing ease of use. Converts all applicable files in all subdirectories of selected folder.

**Please read carefully before using! This script has the potential to perform unwanted actions!**

## Features:
- Preserves file modification dates from input WAV
- Thorough lossless check
- Inefficient conversion detection
- Allows lossless converts of incompatible container bit depths with compatible content (ex: 32 bit float WAV file with only 24 bit content > 24 bit FLAC)
- FLAC > WAV mode
- Replaces input files upon successful conversion by default, option to keep them
- Extremely fast FLAC GPU encoding with FLACCL (Experimental, read)

## Installation

### Windows
1. Install python if it isn't installed already. On updated versions of windows 10/11, you can type "python" in CMD and it will lead you to install it.
2. Install numpy by entering this in CMD: ``pip install numpy``
3. Download the windows release, extract it to wherever you want, and double click "WAV2FLAC.py" to open (direct download link here)

### Anything else
1. Install python
2. Install numpy by entering this in whatever terminal or console your OS uses: ``pip install numpy``
3. Install ffmpeg
4. Download the universal release and launch "WAV2FLAC.py" however you normally do in your OS

## How to Use
This script is designed to be as easy to use as possible, and with fail safes in place. However, **use at your own risk**. You are responsible for your own files.

### Basic Function
Open the script, and you'll see the main GUI. By default, the settings are optimized for converting WAV to FLAC with intent to save space, replacing the input WAVs upon successful conversions. Overwriting existing files is also enabled by default. This should only be a concern if you already have a FLAC file with the same name as a WAV file in the same directory that you want to keep. These and more can be changed with the on-screen checkboxes. More info on these settings below. 

Next, click "Browse" to select your input directory. This script will convert all files inside the selected directory and its sub-directories. Click "Start", confirm the directory and number of files to be converted look correct, then click "Yes" if so. After the conversion is done, a pop-up with various info will appear, and (hopefully) you're done. Any files that caused an error will be listed in the console and logged.

Conversion can take a while if you have a lot of content. If the console seems stuck for a while, and no numbers are changing at all, click in the console, hold CTRL and press C, and it should continue appropriately.

### Conversion mode
By default, this script converts WAVs to FLAC. However, you can use the dropdown box to have it convert FLACs to WAV instead. The "Allow overwriting" setting may be more relevant under this mode, double check it is set to your liking.

### GPU mode (experimental)
**Read before using**. GPU mode uses FLACCL instead of ffmpeg to encode WAVs to FLAC. This can *encode* files tens of times faster, but with some serious potential drawbacks. FLACCL only likes immediately FLAC-compatible WAVs at common sample rates. It will refuse to convert many kinds of WAV files ffmpeg gladly will. It's much slower to start per file, stalls a bit upon an error, and some errors leave empty FLACs behind at the moment. It also doens't transfer metadata and tags like ffmpeg. This feature should only be used with a collection of generally large input WAVs you are confident will be supported (ex: 44.1kHz 16 bit WAV CD rips) that don't have metadata or tags you care about. This is not usable for something like a collection of short drum samples, or anything with unusual sample rates.

### Preserve Original Files
Checking this option will preserve all input files, rather than replacing them with the successful converted FLAC files. You may want this if you want to convert FLACs to use elsewhere but still want to keep the input WAVs. This is not checked by default since this script is intended to convert to save space.

### Skip Lossless Check
By default, this program compares the output converted FLAC against the input WAV to see if the FLAC conversion was truly lossless. Not only is this a nice sanity check, but it allows detection of "fake" bit depth WAV files, which are surprisingly common, to be converted to FLAC losslessly. This script by default only converts FLAC up to 24 bit, so if you have a 32 bit float WAV with only 24 bit content, it will convert it anyways not truly knowing it only has 24 bit content, and during the comparison it will see the conversion was lossless, and deem the 32 bit float WAV to 24 bit FLAC conversion a success.

This lossless check uses extra resources, and could cost a non-insignificant amount of time with very large collections. It can be disabled by checking the "Skip lossless check" box, but I **do not recommend this** unless you know all of your input WAVs will be lossless conversions. It will convert a 32 bit WAV with real 32 bit content to 24 bit FLAC with this check disabled.

Overall, I view this check as a fair investment of time for potential space gain and peace of mind.

### Allow overwriting
By default, this program will allow converted files to overwrite existing files of the same name and extension. This usually won't happen unless you already have a FLAC file with the same name as an input WAV file in the same directory. This could be useful to disable during FLAC to WAV mode, where you might not want any potential original WAVs to be overwritten.

This is on by default so if there is a pre-existing FLAC, it will simply overwrite it and delete the input WAV (if set to). Otherwise it won't delete (replace) the input WAV even if set to, which you probably want.

### Undo inefficient FLAC converts
Some WAV to FLAC conversions will result in a FLAC output that's a larger file size than the WAV input. This almost exclusively happens with very short WAV files. This setting will undo FLAC conversions that have a larger file size than their input WAV, good if space is your #1 priority.

### Command-line ffmpeg
This uses ffmpeg via command-line instead of using a windows executable in the same directory. Useful if you're not on windows or want to use a specific version of ffmpeg you already have installed.

## Concerns
While mass converting WAV files to FLAC to save space is generally a good idea, there *could* be some instances where you might lose important information. Like if a WAV had some kind of unusual custom data written to it, that would probably be lost. I'm not aware of anything like that, but it could exist. Most (if not all) normal tags and metadata are preserved when **not** using GPU mode.

This script *may* convert some lossy WAV files to FLAC, which cannot be restored back to their lossy WAV format. Since lossy audio, even primitive codecs, should be smaller than their output encoded in FLAC, this mostly is a risk with "Undo inefficient FLAC converts" unchecked.

I have tested this program on a large variety of unusual WAV files and formats, and while it should handle everything appropriately, I cannot rule out any unexpected behavior happening. Always use this script with caution, and consider running tests if you're unsure.

## Planned
- Better handling of FLACCL (GPU) errors
- Dynamic mix option using both ffmpeg and FLACCL based on file size and info
- Show size saved in pop-up box post conversion

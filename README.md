# MassWAV2FLAC
Feature rich GUI batch WAV to FLAC converter in Python using ffmpeg and optionally FLACCL, prioritizing ease of use.

**Please read carefully before using!**

## Features:
- Automatically preserves file modification dates from input WAV
- Converts all applicable files in all subdirectories of selected folder
- Thurough lossless check (optional)
- Inefficient conversion detection
- Allows converts of incompatible container bit depths with compatible content (ex: 32 bit WAV file with only 24 bit content > 24 bit FLAC)
- FLAC > WAV mode
- Replaces input files upon successful conversion by default, option to keep them
- Extremely fast FLAC GPU encoding with FLACCL* (Read)

## Installation

## How to Use
This script is designed to be as easy to use as possible, and with several fail safes in place. However, **use at your own risk**. You are responsible for your own files.

### Basic Function
Open the script, and you'll see the main GUI. By default, the program will perform a lossless check on each initially successful conversion, allow converted files to overwrite existing files, replace input files upon successful conversion, and undo FLAC converts larger than the input WAV. All of which can be changed with the on-screen checkboxes. For more info these settings, read below. 

Click "Browse" to select your input directory. The program will convert all files inside the selected directory, and all files in any sub-directories. Click "Start", and confirm the directory and number of files to be converted look correct, then click "Yes" if so. After the conversion is done, a pop-up with various info will appear, and (hopefully) you're done.

### Conversion mode
By default, this script converts WAVs to FLAC. However, you can use the dropdown box to have it convert FLACs to WAV instead. 

### GPU mode (experimental)
**Read this section carefully before using**. GPU mode uses FLACCL instead of ffmpeg to encode WAVs to FLAC. This does *encode* files tens of times faster, but with some serious potential drawbacks. FLACCL only likes immediately FLAC-compatible input WAVs at common sample rates. It will refuse to convert many kinds of WAV files ffmpeg gladly will. It's much slower to start and upon an error than ffmpeg, and some errors leave empty FLACs behind at the moment. It also doens't transfer metadata and tags like ffmpeg. This setting should only be used with a collection of generally large input WAVs you are confident will be supported (ex: 44.1kHz 16 bit WAV CD rip) that don't have metadata or tags you care about. This is not usable for something like a collection of short drum samples, or anything with unusual sample rates.

### Preserve Original Files
Checking this option will preserve all input files, rather than replacing them with the successful converted FLAC files. You may want this if you want to convert FLACs to use elsewhere but want to keep the input WAVs. This is not checked by default since generally the purpose of FLAC is to save space.

### Lossless Check
By default, this program compares the output converted FLAC against the input WAV to see if the FLAC conversion was truly lossless. Not only is this a nice sanity check, but it allows detection of "fake" bit depth WAV files to be converted to FLAC losslessly. FLAC only supports up to 24 bit, so if you have a 32 bit WAV with only 24 bit content, it will convert it anyways not truly knowing it only has 24 bit content, and during the comparison it will see the conversion was lossless, and deem the 32 bit WAV to 24 bit FLAC conversion a success.

This lossless check uses extra resources, and can add up with large collections. It can be disabled by checking the "Skip lossless check" box, but I **do not recommend this** unless you know all of your input WAVs will be lossless conversions. It will convert a 32 bit WAV (with real 32 bit content) to 24 bit FLAC with this check disabled.

Overall, I view this check as a fair investment of time for potential space gain and peace of mind.

### Allow overwriting
By default, this program will allow converted files to overwrite existing files of the same name and extension. This usually won't happen unless you already have a FLAC file with the same name as the input in the same directory. This can also more commonly happen during FLAC to WAV mode, where you might not want your original WAVs to be overwritten.

This is on by default so if there is a pre-existing FLAC, it will simply overwrite it and delete the input WAV (if set to). Otherwise it won't delete (replace) the input WAV, which you probably want.

### Undo inefficient FLAC converts
Some WAV to FLAC conversions will result in a FLAC output that's a larger file size than the WAV input. This almost exclusively happens with very short WAV files. This setting will undo FLAC conversions that have a larger file size than their input WAV, good if space is your #1 priority.


## Concerns
While mass converting WAV files to FLAC to save space is generally a good idea, there *could* be some instances where you might lose important information. Like if a WAV had some kind of unusual custom data written to it, that would probably be lost. I'm not aware of anything like that, but it could exist. Most (if not all) normal tags and metadata are preserved when **not** using GPU mode.

## Planned
- List all failed converts in console after batch completion
- Better handling of FLACCL (GPU) errors
- Dynamic mix of ffmpeg and FLACCL based on file size and info (optional)
- Manually transfer metadata and tags for GPU

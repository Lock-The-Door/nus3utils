import menu

import os
import shutil
import subprocess
from multiprocessing import Process
import wave
import ffmpeg

import menu
import youtube

# Create menus
# Audio source
menu_audioSource = menu.Menu(
    "Audio Source", 
    description="Choose where you want to get the audio from.",
    options=["Local Files", "Youtube"], 
    default=2
)
# Output format
menu_outputFormat = menu.Menu(
    "Output Format",
    options=[".brstm", ".idsp", ".nus3audio"],
    default=3
)
# Download mode
menu_downloadMode = menu.Menu(
    "Download Mode",
    options=["Single File", "Bulk Mode (Playlists/Folders)"],
    default=1
)

# Main
def main():
    print("Cool nus3audio stuff")

    # Ensure dependency exe's are in the current directory
    dependenciesFound = True
    if not os.path.exists("VGAudioCli.exe"):
        print("VGAudioCli.exe not found. Please place it in the current directory.")
        dependenciesFound = False
    if not os.path.exists("nus3audio.exe"):
        print("nus3audio.exe not found. Please place it in the current directory.")
        dependenciesFound = False
    if not dependenciesFound:
        input("Press enter to exit...")
        return

    source = menu_audioSource.Display()
    outputFormat = menu_outputFormat.Display()

    # Looping Point Option
    validInput = False
    while not validInput:
        loopOption = input("Enter a set of loop points (start-end), enter 'a' for auto-detection, or leave blank for no looping: ")
        # Input validation
        if loopOption != "" and loopOption != "a":
            try:
                loopOption = loopOption.split("-")
                loopOption[0] = int(loopOption[0])
                loopOption[1] = int(loopOption[1])
                validInput = True
            except:
                print("Invalid input, please try again.")
        else:
            validInput = True
    
    folderName = ""
    if source == 0: # Local Files
        print("Not implemented yet.")
        return
    else: # Youtube
        # Get the link
        validInput = False
        while not validInput:
            validInput = True
            link = input("Enter the link: ")
            isPlaylist = False
            # Get id from link
            if (link.find("youtube.com/watch?v=") != -1): # Single video
                id = link.split('=')[1]
            elif (link.find("youtu.be/") != -1): # Single video (Link shortener)
                id = link.split('/')[-1]
            elif (link.find("youtube.com/playlist?list=") != -1): # Playlist
                id = link.split('=')[1]
                isPlaylist = True
            else:
                validInput = False
                print("Invalid link")
        
        # Make temp folder
        path = os.path.join(os.getcwd(), id + "-temp")

        # Download the audio
        if not isPlaylist:
            sourceAudio = [youtube.DownloadAudio(id, path)]
        else:
            sourceAudio = youtube.DownloadPlaylist(id, path)
            folderName = youtube.GetPlaylistTitleFromId(id)

    jobs = []
    for audio in sourceAudio:
        p = Process(target=ConvertFile, args=(audio, loopOption, source, outputFormat))
        jobs.append(p)
        p.start()

    # Wait for all jobs to finish
    for job in jobs:
        job.join()

    #Cleanup
    tempFolder = path
    outputFolder = os.path.join(os.getcwd(), "Output")
    if (folderName != ""): # bulk mode
        outputName = RemoveIllegalCharacters(folderName)
        outputFolder = os.path.join(outputFolder, outputName)

    # Create output folder if it doesn't exist
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    # Copy files to output folder
    print("Copying result to output folder...")
    shutil.copytree(tempFolder, outputFolder, dirs_exist_ok=True)

    # Delete temp folder
    print("Deleting temp folder...")
    shutil.rmtree(tempFolder)

    # Done
    filesConverted = len(sourceAudio)
    outputFormat = menu_outputFormat.options[outputFormat]
    print("Done converting {} file(s) to {}.".format(filesConverted, outputFormat))
    input("Press enter to exit...")

def ConvertFile(audio, loopOption, source, outputFormat):
    # Remove extension
    audio = audio.removesuffix(".temp")

    # Get user friendly name if using yt
    if source == 1:
        outputName = youtube.GetTitleFromId(os.path.basename(audio))

    # Ensure output name is system friendly
    outputName = RemoveIllegalCharacters(outputName)

    # Convert to wav with audio rate of 48000
    print("Converting {} audio to wav...".format(outputName))
    ffmpeg.input(audio + ".temp").output(audio + ".wav", acodec="pcm_s16le", ar="48000").overwrite_output().run(quiet=True)

    # Get looping point arg
    loopingPointArg = "-l "
    if loopOption == "a": # Auto-detect
        loopingPointArg += "0-" + str(GetLoopingPoint(audio + ".wav"))
    elif loopOption != "": # Manual
        loopingPointArg += str(loopOption[0]) + "-" + str(loopOption[1])
    else: # No looping
        loopingPointArg = "--no-loop"

    # Convert to desired format
    if outputFormat == 0: # .brstm
        ConvertWithVGAudio(audio + ".wav", loopingPointArg, outputName + ".brstm")
    else: # .idsp/nus3audio
        ConvertWithVGAudio(audio + ".wav", loopingPointArg, audio + ".idsp", outputName)
        if outputFormat == 2: # .nus3audio
            ConvertToNus3audio(audio + ".idsp", outputName)
            os.remove(audio + ".idsp")
        else: # idsp
            shutil.move(audio + ".idsp", os.path.join(os.path.dirname(audio), outputName + ".idsp"))

    # Cleanup
    os.remove(audio + ".temp")
    os.remove(audio + ".wav")

# Removes bad characters from a string
badCharacters = "\\/:*?\"<>|"
def RemoveIllegalCharacters(string):
    for c in badCharacters:
        string = string.replace(c, '_')
    return string

# Calculate looping point
def GetLoopingPoint(filePath):
    audio = wave.open(filePath, 'rb')
    samples = audio.getnframes()
    return samples

# VG Audio converter
def ConvertWithVGAudio(inputFile, loopFlag, outputFile, outputName=None):
    splitFilename = os.path.splitext(outputFile)
    if outputName == None:
        outputName = splitFilename[0]
    print("Converting {} to {}...".format(outputName, splitFilename[1]))
    outputPath = os.path.join(os.path.dirname(inputFile), outputFile)
    subprocess.run("VGAudioCli.exe -i \"" + inputFile + "\" " + loopFlag + " -o \"" + outputPath + "\"", stdout=subprocess.DEVNULL)

# Nus3audio converter
def ConvertToNus3audio(inputFile, outputName):
    # make output path to temp folder
    outputPath = os.path.join(os.path.dirname(inputFile), outputName + ".nus3audio")

    print("Converting {} to nus3audio...".format(outputName))
    subprocess.run("nus3audio.exe -n -A \"" + outputName + "\" \"" + inputFile + "\" -w \"" + outputPath + "\"", stdout=subprocess.DEVNULL)

# Run main
if __name__ == '__main__':
    main()

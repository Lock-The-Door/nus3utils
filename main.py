import menu
# from convert import ConvertAudio

import os
import shutil

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
# nus3audio mode
menu_nus3audioMode = menu.Menu(
    "Do you want to combine all files to one nus3audio file?",
    options=["Yes", "No"],
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
    multifile = True

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

                # ask multifile if nus3audio
                if outputFormat == 2:
                    multifile = menu_nus3audioMode.Display()
                    multifile = multifile == 1
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

    if not multifile:
        multifile = folderName
    ConvertAudio(sourceAudio, loopOption, source, outputFormat, multifile)

    # Get output folder
    tempFolder = path
    outputFolder = os.path.join(os.getcwd(), "Output")
    if (folderName != "" and type(multifile) != str): # bulk mode
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

# Removes bad characters from a string
badCharacters = "\\/:*?\"<>|"
def RemoveIllegalCharacters(string):
    for c in badCharacters:
        string = string.replace(c, '_')
    return string

# Run main
if __name__ == '__main__':
    from convert import ConvertAudio
    main()
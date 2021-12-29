from main import RemoveIllegalCharacters

import os
from multiprocessing import Process, Array
import subprocess

import youtube
import ffmpeg
import wave

def ConvertAudio(sourceAudio, loopOption, source, outputFormat, multifile):
    # Reset progress
    totalConvertProcesses = len(sourceAudio)
    runningConvertProcesses = []
    finishedConvertProcesses = 0

    if type(sourceAudio) == str: # single file mode
        ConvertFile(sourceAudio, loopOption, source, outputFormat)
    else: # multi-file mode
        # Create conversion processes
        for audio in sourceAudio:
            p = Process(target=ConvertFile, args=(audio, loopOption, source, outputFormat, type(multifile) != str, Array("i", [totalConvertProcesses, finishedConvertProcesses])))
            runningConvertProcesses.append(p)
            p.start()
        # Wait for all jobs to finish
        for job in runningConvertProcesses:
            job.join()
        runningConvertProcesses.clear()

        # single nus3audio file mode
        if type(multifile) == str:
            # get files in temp folder
            files = os.listdir(os.path.dirname(sourceAudio[0]))
            # Merge idsp files into one nus3audio file
            ConvertToNus3audio(files, multifile, os.path.dirname(sourceAudio[0]))
            # Remove idsp files
            for file in files:
                if file.endswith(".idsp"):
                    os.remove(os.path.join(os.path.dirname(sourceAudio[0]), file))

def ConvertFile(audio, loopOption, source, outputFormat, multifile=None, convertProgress=None):
    # Remove extension
    audio = audio.removesuffix(".temp")

    # Get user friendly name if using yt
    if source == 1:
        outputName = youtube.GetTitleFromId(os.path.basename(audio))

    # Ensure output name is system friendly
    outputName = RemoveIllegalCharacters(outputName)

    # Convert to wav with audio rate of 48000
    print("Converting {} to wav...".format(outputName))
    ffmpeg.input(audio + ".temp").output(audio + ".wav", acodec="pcm_s16le", ar="48000").overwrite_output().run(quiet=True)
    print("Converted {} to wav.".format(outputName))

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
        ConvertWithVGAudio(audio + ".wav", loopingPointArg, outputName + ".idsp")
        if outputFormat == 2 and multifile: # .nus3audio (multi-file)
            idspFilePath = os.path.join(os.path.dirname(audio), outputName + ".idsp")
            ConvertToNus3audio(idspFilePath, outputName)
            os.remove(idspFilePath)

    # Cleanup
    os.remove(audio + ".temp")
    os.remove(audio + ".wav")

    # Update progress
    if convertProgress != None:
        convertProgress[1] += 1
        print("Converted {}/{} files.".format(convertProgress[1], convertProgress[0]))

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
    print("Converted {} to {}.".format(outputName, splitFilename[1]))

# Nus3audio converter
def ConvertToNus3audio(inputFile, outputName, workingDir=None):
    # create list of files to pack
    files = []
    if type(inputFile) == str: # signle file mode
        # make output path to temp folder
        outputPath = os.path.join(os.path.dirname(inputFile), outputName + ".nus3audio")

        print("Converting {} to nus3audio...".format(outputName))
        files.append("-A \"" + outputName + "\" \"" + inputFile + "\"")
    else: # multi-file mode
        # make output path to temp folder
        outputPath = os.path.join(workingDir, outputName + ".nus3audio")

        print("Packing {} files to {}.nus3audio...".format(len(inputFile), outputName))
        for file in inputFile:
            filename = os.path.splitext(file)[0]
            files.append("-A \"" + filename + "\"" + " \"" + os.path.join(workingDir, file) + "\"")

    # create nus3audio file
    subprocess.run("nus3audio.exe -n " + " ".join(files) + " -w \"" + outputPath + "\"", stdout=subprocess.DEVNULL)
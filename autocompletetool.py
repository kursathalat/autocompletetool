import string
import numpy as np
import nltk
from string import ascii_lowercase
import tkinter as tk
import json
import os
try:
    import win32com.client as win32
    noWord = False
except:
    noWord = True
    pass


# # # # # Main corpus creation

def corpora():
    """
    TO BE RUN ONLY ONCE

    This creates the base corpora for the application. Since the app comes with the base file, there is no need to run this.
    If no file named "base.json" found in the directory, then this function is run automatically.
    Two main sources are used for the corpora, Brown and Project Gutenberg selection by NLTK.
    While all the categories in Brown are used, only 12 out 18 texts in the Project Gutenberg selection are used.
    This is because some texts (like Shakespeare's) include quite old words, which is not an aim of this tool.
    Returns nothing.

    """
    from nltk.corpus import brown, gutenberg

    # Importing Brown corpus to a list
    baseCorpora = []
    for category in brown.categories():
        baseCorpora += brown.sents(categories=category)

    # Importing Project Gutenberg selections into the same list
    gutenbergTexts = [0, 1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 17]
    for work in gutenbergTexts:
        baseCorpora += list(gutenberg.sents(gutenberg.fileids()[work]))

    # Text with <s> and </s>, which is the main corpora
    textForBigrams = []
    for sentence in baseCorpora:
        textForBigrams.append("<s>")
        for word in sentence:
            if word.isalpha():
                textForBigrams.append(word.lower())
        textForBigrams.append("</s>")
    print("Corpus has been created.")
    # Saving the base corpora into a json file in the directory
    with open("base.json","w") as basecorpora:
        json.dump(textForBigrams, basecorpora)


# # # # # Functions for updating data


def updatecorpora(newtext):
    """
    TO BE RUN AFTER EVERY USE OF THE TOOL

    This opens the base file and adds the new text input to it.
    :param newtext: splitted text input with <s> and </s> for every sentence
    """
    with open("base.json","r") as base:
        textForBigrams = json.load(base)
        textForBigrams += newtext
    with open("base.json", "w") as base:
        json.dump(textForBigrams,base)


# # # Update unigrams and bigrams

def updateunigrams():
    """
    TO BE RUN WHEN "UPDATE" CLICKED BY THE updategrams() FUNCTION

    This can also be used to create the very first unigram file in the directory, if not existing.
    It opens the base file and creates a unigram list as a numpy array out of it, with words and their probabilities.
    Firstly, gets rid of the tags at the beginning and at the end of sentences.
    Creates a unigram frequency dictionary by NLTK.
    Creates an empty 3-dimensional numpy array, where stacks are every letter in English alphabet, first row in every stack
        is the word starting with respective letter, second row is the probability of that word, and columns are the words.
    To create arrays of equal length, stacks with less number of words than the max one are padded to the max number with empty values.

    The resulting array is saved into a npy file to load later for every use.
    """
    with open("base.json", "r") as base:
        textForBigrams = json.load(base)
    textForUnigrams = [word for word in textForBigrams if word not in ["<s>", "</s>"]]
    unigrams = nltk.FreqDist(textForUnigrams)
    abc = dict(zip(list(ascii_lowercase), list(range(26))))
    maxValue = maxValueFinder(abc, unigrams)
    dictionary = np.empty((26, 2, maxValue), dtype="U30")
    for char in abc.values():
        arrayKeys = padding(np.fromiter(dict(i for i in unigrams.items() if i[0].startswith(list(abc.keys())[char])).keys(), dtype="U30"), maxValue)
        arrayValues = padding(np.fromiter(dict(i for i in unigrams.items() if i[0].startswith(list(abc.keys())[char])).values(), dtype=float) / unigrams.N(), maxValue)
        dictionary[char] = np.array([arrayKeys, arrayValues])
    print("Unigrams have been created.")
    np.save("ug.npy", dictionary)


def maxValueFinder(abc,dictionary):
    """
    Finds the letter with the most number of words, given the alphabet and unigram list.
    :return: the number of the words appearing the most with a particular letter
    """
    maxValue = 0
    for char in abc.values():
        length = len(list(i for i in dictionary.keys() if i.startswith(list(abc.keys())[char])))
        if length > maxValue:
            maxValue = length
    return maxValue


def padding(array,maxvalue):
    """
    Pads the given array to the length of the max value.
    :return: a padded array
    """
    array = np.pad(array, (0, maxvalue-array.shape[0]), mode="empty")
    return array


def updatebigrams():
    """
    TO BE RUN WHEN "UPDATE" CLICKED BY THE updategrams() FUNCTION

    Opens the base file, update the bigrams with the new base, and saves it again to bg.json file
    """
    with open("base.json","r") as base:
        textForBigrams = json.load(base)
    bigrams = [(textForBigrams[index], textForBigrams[index + 1]) for index in range(len(textForBigrams) - 1)]
    print("Bigrams have been created.")
    with open("bg.json", "w") as outfile:
        json.dump(bigrams, outfile)


# # # # # Searching ngrams and retrieving the prediction


def findunigramlist(string):
    """
    Given the string being typed (after last space), it returns the unigram list and their probabilities.
    If the string involves something other than a letter, it returns None.
    If no word found, it returns None.
    Returned list is a 2-dimensional numpy array.

    :param string: the word being typed
    :return: unigram array with probabilities
    """
    if not string.isalpha():
        return None
    abc = dict(zip(list(ascii_lowercase), list(range(26))))
    try:
        if string == "n":
            wordsWithN = dictionary[13, 0].tolist()
            find = np.flatnonzero(np.char.startswith(dictionary[abc.get(string[0]), 0:2, 0:wordsWithN.index("")], string))
        else:
            find = np.flatnonzero(np.char.startswith(dictionary[abc.get(string[0])], string))
    except:
        return None
    unigramList = dictionary[abc.get(string[0]), 0:, find]
    # print(unigramList,"\n")
    return unigramList


def findbigramlist(word, char=""):
    """
    Given the word being typed and the previous one, returns probable bigrams according to the current word.
    It finds all the probabilities, creates a list out of them.
    Finds the number to multiply the minimum probability to 4.
    Then, multiplies all the probabilities by this number.
    These new numbers obtained will be used to multiply the unigram results.
    This way, the unigram results that also appear in the bigram results will have a higher chance to appear.

    :return: bigrams and probabilities as multipliers
    """
    bigramList = []
    allBigramProbabilities = []
    for secondWord in condProb[word].samples():
        if secondWord.startswith(char):
            allBigramProbabilities.append(condProb[word].prob(secondWord))
    if len(allBigramProbabilities) == 0:
        multiplier = 1
    else:
        multiplier = 10/min(allBigramProbabilities)
    for secondWord in condProb[word].samples():
        if secondWord.startswith(char):
            bigramList.append((secondWord, multiplier * condProb[word].prob(secondWord)))
    # print(bigramList,"\n")
    return bigramList


def finalizeunigrams(unigramresults, bigramresults):
    """
    Given the unigram results and bigram results, it adjust the unigrams with multipliers from bigrams.
    Probabilities will be higher for those words which appear in the bigram results.

    :return: finalized unigram results
    """
    for i in bigramresults:
        if i[0] in unigramresults.T[0]:
            for k in np.where(unigramresults == i)[0]:
                unigramresults[k][1] = float(unigramresults[k][1]) * i[1]
    # print(unigramresults,"\n")
    return unigramresults


def predictnextword(finalized_unigrams):
    """
    Given the finalized unigram list, it returns the word with the highest probability.
    If no word is found, it returns None.

    :return: the word with highest probability
    """
    probabilities = np.array(finalized_unigrams[0:, 1], dtype=float)
    if probabilities.shape[0] == 0:
        return ""
    else:
        return finalized_unigrams[probabilities.argmax()][0]

def predict(firstword, secondword=""):
    """
    Given the current word being written and the previous word, returns the word with highest probable.

    :return: the prediction
    """
    for char in firstword and secondword:
        if char not in list(string.ascii_lowercase):
            return ""
    return predictnextword(finalizeunigrams(findunigramlist(secondword), findbigramlist(firstword, secondword)))


def findTheWord(word, probabilitylist):
    """
    Given a word, it finds the most probable word after it.
    This is run when the user starts to write a new word (after a space, for example)
        since no clue can be used for the prediction regarding the word being typed.
    If no prediction is found, it returns None.
    If the prediction is the end of the sentence ("<s>"), it again returns None.

    :return: bigram prediction
    """
    try:
        nextWord = probabilitylist[word].max()
        if nextWord == "</s>":
            return ""
        else:
            return nextWord
    except:
        return ""


# # # # # Loading the files for the program

def loadfiles():
    """
    TO BE RUN ON EVERY USE

    Loads unigram (npy) and bigram (json) files.
    Since conditional probabilities cannot be saved into a json file,
        it loads the bigrams and calculates the conditional probabilities on every use.
    """
    global dictionary
    global condProb
    dictionary = np.load("ug.npy")
    with open("bg.json") as json_file:
        bigrams = json.load(json_file)
    condFreq = nltk.ConditionalFreqDist(bigrams)
    condProb = nltk.ConditionalProbDist(condFreq, nltk.MLEProbDist)
    return dictionary, condProb


# # # # # Tkinter Application

# # # Functions to be used in tkinter

def keypress(event):
    global firstKey
    startIndex = textBox.search("\S*\s\S*\s(\S*)?", tk.END, regexp=True, backwards=True)
    if startIndex == "":
        return
    lastTwoWords = textBox.get(startIndex, "insert").lower().split()
    if len(lastTwoWords) == 2:
        prediction.set(predict(lastTwoWords[0], lastTwoWords[1]))
        if len(lastTwoWords[-1]) < 2:
            labelInsert.configure(text="")
            return
        else:
            labelInsert.configure(text=prediction.get()[len(lastTwoWords[-1]):])
            if event.keysym == "Control_L":
                textBox.insert("insert", f"{prediction.get()[len(lastTwoWords[-1]):]} ")
                labelInsert.configure(text=findTheWord(prediction.get(), condProb))
                return
    elif len(lastTwoWords) == 1:
        prediction.set(findTheWord(lastTwoWords[0], condProb))
        if len(lastTwoWords[-1]) < 2:
            labelInsert.configure(text="")
            return
        else:
            labelInsert.configure(text=prediction.get())
            if event.keysym == "Control_L":
                textBox.insert("insert", f"{prediction.get()} ")
                labelInsert.configure(text=findTheWord(prediction.get(), condProb))
                return
    textBox.window_create(tk.END, window=labelInsert)
    while firstKey:
        textBox.mark_set("insert", "insert-1c")
        firstKey = False


def exitapp():
    """
    Exits app after saving all input to the base file.
    """
    newtext = []
    for sentence in textBox.get("1.0", "end-1c").split("."):
        newtext.append("<s>")
        for word in sentence.split():
            if word.isalpha():
                newtext.append(word)
        newtext.append("</s>")
    updatecorpora(newtext)
    window.destroy()


def updategrams():
    """
    Runs the update functions when "update" is clicked.
    """
    updateunigrams()
    updatebigrams()


def exporttoword():
    """
    Opens an Office Word document, pastes the input there.
    Only works if Office is already installed.
    """
    if noWord:
        return
    wordApp = win32.gencache.EnsureDispatch("Word.Application")
    newDoc = wordApp.Documents.Add()
    newDoc.Content.Text = textBox.get("1.0", "end-1c")
    wordApp.Visible = True


def evaluationscores():
    evalWindow = tk.Toplevel(window)
    evalWindow.config(bg="white")
    evalWindow.title("Evaluation Scores")
    evalWindow.geometry("1200x700")
    with open("evaluation.txt", "r", encoding="utf8") as base:
        evaluation = base.read()
    txtEval = tk.Text(master=evalWindow, font=("Helvetica", "12"), relief=tk.FLAT, padx=10, pady=10, spacing2=8, height=50, width=145)
    txtEval.insert(tk.END, evaluation)
    txtEval.configure(state=tk.DISABLED)
    txtEval.pack()


def readmewindow():
    readmeWindow = tk.Toplevel(window)
    readmeWindow.config(bg="white")
    readmeWindow.title("README")
    readmeWindow.geometry("1200x700")
    with open("readme.txt", "r") as base:
        readme = base.read()
    txtReadme = tk.Text(master=readmeWindow, height=40, font=("Helvetica", "14"), relief=tk.FLAT, padx=10, pady=10, spacing2=7, wrap=tk.WORD)
    txtReadme.insert(tk.END, readme)
    txtReadme.configure(state=tk.DISABLED)
    txtReadme.pack()


def infographics():
    infographicWindow = tk.Toplevel(window)
    infographicWindow.config(bg="white")
    infographicWindow.title("Infographics")
    infographicWindow.geometry("1200x700")
    infoFrame = tk.Frame(master=infographicWindow)
    infoFrame.pack()
    txtInfo = tk.Text(master=infoFrame, height=40, width=150, state=tk.DISABLED)
    txtInfo.image_create(tk.END, image=info)
    txtInfo.pack()

# # # Creating main window

window = tk.Tk()
window.geometry("1000x600")
window.config(bg="black")
window.title("Autocomplete")
window.grid_rowconfigure(0, weight=1, minsize=100)
window.grid_rowconfigure(1, weight=2)
window.grid_rowconfigure(2, weight=1, minsize=50)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=2)
window.grid_columnconfigure(2, weight=1, minsize=100)


# # # Frames

upperFrame = tk.Frame(bg="#778072")
mainFrame = tk.Frame(pady=10, bg="#778072")
menuFrame = tk.Frame(padx=10, pady=80, bg="#778072")
leftFrame = tk.Frame(bg="#778072")
bottomFrame = tk.Frame(bg="#778072")

mainFrame.grid_rowconfigure(0, weight=1)
mainFrame.grid_columnconfigure(0, weight=1)
leftFrame.grid_rowconfigure(0, weight=1)
leftFrame.grid_columnconfigure(0, weight=1)
menuFrame.grid_rowconfigure(0, weight=1)
menuFrame.grid_rowconfigure(1, weight=1)
menuFrame.grid_rowconfigure(2, weight=1)
menuFrame.grid_columnconfigure(0, weight=1)
upperFrame.grid_rowconfigure(0, weight=1)
upperFrame.grid_columnconfigure(0, weight=1)
bottomFrame.grid_rowconfigure(0, weight=1)
bottomFrame.grid_columnconfigure(0, weight=1)
bottomFrame.grid_columnconfigure(1, weight=1)
bottomFrame.grid_columnconfigure(2, weight=1)


# # # Widgets

buttonHeights = 5
buttonRelief = tk.GROOVE
lblTitle = tk.Label(master=upperFrame, bg="#464B43", fg="white", text="Autocomplete Tool",font=("Helvetica", "30"))
textBox = tk.Text(master=mainFrame, height=6, width=50, relief=tk.FLAT, font=("Helvetica", "20"))
textBox.tag_config("insertion", foreground="gray")
labelInsert = tk.Label(master=textBox, text="", font=("Helvetica","20"), fg="gray", bg="white", padx=0, bd=0)
btnUpdate = tk.Button(master=menuFrame, text="Update", height=buttonHeights, relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"), command=updategrams)
btnWord = tk.Button(master=menuFrame, text="Export to Word", height=buttonHeights, relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"), command=exporttoword)
btnExit = tk.Button(master=menuFrame, text="Exit", height=buttonHeights, relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"), command=exitapp)
evaluationButton = tk.Button(master=bottomFrame, text="Evaluation Scores", relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"), command=evaluationscores)
readmeButton = tk.Button(master=bottomFrame, text="README", relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"),command=readmewindow)
infoButton = tk.Button(master=bottomFrame, text="Infographics", relief=buttonRelief, bg="black", fg="white", font=("Helvetica", "18"),command=infographics)

# # # Mapping on window

upperFrame.grid(row=0, column=0, columnspan=3, sticky="nesw")
leftFrame.grid(row=1, column=0, sticky="nesw")
mainFrame.grid(row=1, column=1, sticky="nesw")
menuFrame.grid(row=1, column=2, sticky="nesw")
bottomFrame.grid(row=2, column=0, columnspan=3, sticky="nesw")
lblTitle.grid(row=0, column=0, sticky="nesw")
textBox.grid(row=0, column=0, sticky="nesw")
btnUpdate.grid(row=0, column=0, sticky="nesw")
btnWord.grid(row=1, column=0, sticky="nesw")
btnExit.grid(row=2, column=0, sticky="nesw")
evaluationButton.grid(row=0, column=0)
readmeButton.grid(row=0, column=1)
infoButton.grid(row=0, column=2)

textBox.bind("<KeyRelease>", keypress)
prediction = tk.StringVar()
firstKey = True
info = tk.PhotoImage(file="infographics.png").subsample(2)

# # # # # RUN

if "base.json" not in os.listdir():
    corpora()
if "ug.npy" not in os.listdir():
    updategrams()
if "bg.json" not in os.listdir():
    updategrams()

loadfiles()
window.mainloop()


Autocomplete Tool


This is an autocomplete tool that predicts the word you are typing or the next one, as you type. 

It is based on an n-gram language model, where the unigram and bigram probabilities are combined to predict the word.

It also keeps the user input and in time, it updates the predictions with the user input.


Getting Started


Just write! It features a basic GUI where you can type in and get predictions. The prediction will be in gray and when you press Left Control on your keyboard, the prediction will be added to your text.

There are some known issues with the interface. Rarely, it could get difficult to write, for example, it might keep deleting what you write. Also, one point to keep in mind is not to delete the prediction label. In such a case, it will not recreate the prediction label, resulting in no prediction at all. These will be addressed later.


How It Works


Corpus


The base corpora is created with texts from NLTK module. While the whole Brown corpus is used, some texts from the Project Gutenberg Selection are included, leaving the old ones like Shakespeare's.

The tool already comes with the corpus (base.json); however, if it is not found in the directory, it just creates it with the corpora() function. For this, you must have the dependencies (nltk.corpus).

This base file is also used for saving the user input. After every use (only when the "Exit" button is clicked), it adds the new input to this base file.


Unigrams and Bigrams


Unigrams and probabilities are created with the help of NLTK module. Then, this unigram dictionary is turned into a 3D numpy array for a more effective search. Only NLTK is used for the bigrams.

These two ngrams are stored in their respective files. While unigrams are in their final version with probabilities (ug.npy), bigrams are only the bigrams (bg.json), which are subsequently turned into conditional probabilities on every run. If you do not have either of these files, they are created at the beginning based on base.json.

The main point is that bigram probabilities affect the unigram probabilities for a given token according to the characters that have already been typed. Basically, among the bigram probabilities for a given incomplete token, the minimum one is increased to 10. Then, every bigram probability is multiplied by the multiplier of this operation, which then turns every probability into a multiplier. All the unigram probabilities are multiplied by their respective multipliers. This way, probable unigrams have a higher chance if they also exist in bigrams probabilities. You can adjust the number that all numbers are increased to (10) as you wish and see the impact it can have (in findbigramlist()).


Update


After every use, the input is saved into the base.json file. In order to adjust the predictions and probabilities according to newly acquired data, you need to click the "Update" button. This will recalculate the probabilities and you will be able to have them in the next run of the tool.


Office Word


If you are on Windows with MS Office and win32 module installed, you can export what you have written to a Word document, while it does not work with other OS.


Evaluation


For this n-gram based model, extrinsic evaluation methods were used. Upon using the tool, participants responded a survey about their experiences, indicating their like or dislike by scoring a scale out of 10. Evaluation results showed that it can be of help for many people who often write on computers and that participants liked the prediction power, though it needs further improvement. Survey questions and anonymous participant answers can be found in the tool.
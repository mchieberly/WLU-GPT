import pandas as pd
import matplotlib.pyplot as plt 
from collections import Counter
import re
import json

class TextDataEDA:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.DataFrame()
        self.load_data()
    
    def load_data(self):
        """Load data from a JSON Lines file and extract the 'note' field."""
        data = []
        # Define a simple regex for sentence splitting
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'

        with open(self.filepath, 'r') as f:
            for line in f:
                entry = json.loads(line)  # Parse the JSON string
                sentences = re.split(sentence_pattern, entry['note'])  # Split text into sentences
                for sentence in sentences:
                    if sentence.strip():  # Ensure the sentence is not just whitespace
                        data.append([sentence.strip(), entry['url']])  # Append each sentence with the same URL

        self.df = pd.DataFrame(data, columns=['note', 'url'])
    
    def data_overview(self):
        """Print basic information and the first few rows of the dataset."""
        print("\nData Overview:")
        print(self.df.head())
        # print(self.df.info()) 
    
    def word_count_analysis(self):
        """Analyze and print statistics about text length in the dataset."""
        self.df['word_count'] = self.df['note'].apply(lambda text: len(text.split()))
        print("\n\nText Length Summary Analysis:")
        print(self.df['word_count'].describe())
    
    def word_frequency_analysis(self, num_words=20):
        """Analyze and print the most common words in the dataset."""
        all_text = ' '.join(self.df['note'].tolist()).lower()
        words = re.findall(r'\b\S+\b', all_text)
        word_counts = Counter(words)
        print("\n\nTop {num_words} Most Common Words:")
        print(word_counts.most_common(num_words))
    
    def plot_histogram_word_count(self, sparse=True):
        """Plot a histogram of the text lengths."""
        self.df['word_count'].hist(bins=50, log=sparse)

        plt.title('Histogram of Text Lengths')
        plt.xlabel('Text Length')
        plt.ylabel('Frequency')
        plt.show()


    ### Data Filtering and Preperation Methods

    def filter_data(self, min_word_count=0, max_word_count=1000, keywords=[]):
        """Filter the dataset based on text length and keywords."""
        self.df = self.df[self.df['word_count'] >= min_word_count]
        self.df = self.df[self.df['word_count'] <= max_word_count]

        if keywords:
            self.df = self.df[self.df['note'].apply(lambda text: any(word in text for word in keywords))]

        print("\nFiltered Data Overview:")
        print(self.df.head())

   
    def save_data(self, savepath):
        """Save the filtered dataset to a new JSON Lines file."""
        self.df.to_json(savepath, orient='records', lines=True)

    
   



if __name__ == "__main__":
    
    filepath = 'raw/notes.jsonl' 
    eda = TextDataEDA(filepath)

    # Run EDA methods
    eda.word_count_analysis()
    eda.data_overview() 
    # eda.word_frequency_analysis()
    eda.plot_histogram_word_count(sparse=True)

    # Run Data Filtering method
    eda.filter_data(min_word_count=3, max_word_count=40, keywords=[])
    eda.save_data('raw/filtered_notes.jsonl')

    # Run Filtered Data Visualization methods
    eda.word_count_analysis()
    eda.plot_histogram_word_count(sparse=False)

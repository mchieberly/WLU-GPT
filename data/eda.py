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
        with open(self.filepath, 'r') as f:
            for line in f:
                entry = json.loads(line)  # Parse the JSON string
                data.append([entry['note'], entry['url']])  # Split 'note' and 'url' field
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
    
    def plot_histogram_word_count(self):
        """Plot a histogram of the text lengths."""
        self.df['word_count'].hist(bins=50, log=True)

        plt.title('Histogram of Text Lengths')
        plt.xlabel('Text Length')
        plt.ylabel('Frequency')
        plt.show()
    
   



if __name__ == "__main__":
    
    filepath = 'data/notes.jsonl' 
    eda = TextDataEDA(filepath)

    # Run EDA methods
    eda.word_count_analysis()
    eda.data_overview() 
    # eda.word_frequency_analysis()
    eda.plot_histogram_word_count()


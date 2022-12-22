# AmazonReview_Crawl_NLP
Built a tool to crawl Amazon reviews and classify review with CNN. This project use 2 methods of vectorize data: Tensorflow.Tokenizer and gensim.Word2Vec.

# Folder details:
- crawler:
  + exe tool
  + crawler python script
- data:
  + multiple data files in csv format
  + merge.ipynb: merge all above data files
- model_word2vec: 
  + data
  + word2vec model
  + CNN model
- model_tensorflowtokenizer:
  + data
  + CNN model
 
# Technologies:
- crawl: python BeautifulSoup, Selenium
- NLP: preprocessing, vectorize with Tensorflow.Tokenizer and gensim.Word2Vec
- Neural Network: tensorflow
 

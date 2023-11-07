from transformers import pipeline

def sentiment_analysis(text_path):
    # Read the text from the file
    with open(text_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Set up the inference pipeline using a model from the 🤗 Hub
    sentiment_analysis_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

    # Split the text into sentences using periods as delimiters
    sentences = text.split('.')

    # Initialize lists to store sentiment and confidence for each sentence
    sentence_sentiments = []
    sentence_confidences = []

    # Predict the sentiment for each sentence
    for sentence in sentences:
        # Remove leading and trailing spaces from the sentence
        sentence = sentence.strip()

        if sentence:
            # Predict the sentiment of the sentence
            result = sentiment_analysis_pipeline(sentence)

            # Access the sentiment prediction
            sentiment = result[0]["label"]
            confidence = result[0]["score"]

            # Append the sentiment and confidence to the lists
            sentence_sentiments.append(sentiment)
            sentence_confidences.append(confidence)

    # Print the sentiment and confidence for each sentence
    for i, sentence in enumerate(sentence_sentiments):
        print(f"Sentence {i + 1}:")
        print(f"Text: {sentences[i]}")
        print(f"Sentiment: {sentence_sentiments[i]}")
        print(f"Confidence: {sentence_confidences[i]}")
        print("\n")

from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer('stsb-roberta-large')

def similarity(text_file, options_file):
    with open(text_file, 'r') as file:
        text_content = file.read()
        
    with open(options_file, 'r') as file:
        options_content = file.read()

    # Split the options using the patterns "a)", "b)", "c)", etc.
    options = re.split(r'([a-z]\))', options_content)

    # Filter out empty strings and whitespace
    options = [option.strip() for option in options if option.strip()]

    max_similarity_score = -1  # Initialize with a low value
    most_similar_option = None
    similar_options = []

    for i in range(1, len(options), 2):
        option = options[i]  # Get the option text

        # Calculate the similarity between the text and the current option
        embeddings = model.encode([text_content, option], convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

        if similarity_score > max_similarity_score:
            max_similarity_score = similarity_score
            most_similar_option = option

        if similarity_score < 0.5:
            similar_options.append((option, similarity_score))

    print("Your input: ", text_content)

    if max_similarity_score >= 0.5:
        print(f"The most similar option to the text is: {most_similar_option}")
        print(f"Similarity Score: {max_similarity_score}")
    else:
        print("No similar option found.")

    if max_similarity_score < 0.5:
        for option, score in similar_options:
            print(f"Option: {option} : {score}")

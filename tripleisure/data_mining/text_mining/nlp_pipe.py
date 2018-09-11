import spacy

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')

# The text we want to examine
with open('blogs/Boiling Lake.txt', 'r') as f:
    text = f.read()

# Parse the text with spaCy. This runs the entire pipeline.
doc = nlp(text)

# 'doc' now contains a parsed version of text. We can use it to do anything we want!
# For example, this will print out all the named entities that were detected:
for entity in doc.ents:
    print(f"{entity.text} ({entity.label_})")



# import spacy
# import textacy.extract
#
# # Load the large English NLP model
# nlp = spacy.load('en_core_web_lg')
#
# # The text we want to examine
# with open('blogs/Boiling Lake.txt', 'r') as f:
#     text = f.read()
#
# # Parse the document with spaCy
# doc = nlp(text)
#
# # Extract semi-structured statements
# statements = textacy.extract.semistructured_statements(doc, "Lake")
#
# # Print the results
# print("Here are the things I know about Lake:")
#
# for statement in statements:
#     subject, verb, fact = statement
#     print(f" - {fact}")
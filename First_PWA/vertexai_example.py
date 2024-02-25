from vertexai.language_models import TextGenerationModel

def text_summarization(project_id:"educa-admin", location:"northamerica-northeast1") -> str:
    """Summarization Example with Vertex AI Gemini API"""
    # Initialize the client
    #client = vertexai.GeminiClient(project="educa-admin", location="northamerica-northeast1")
    #response = client.generate_text(text_to_summarize, model_name="gemini-1.0-pro-vision-001")
    client = TextGenerationModel.from_pretrained("gemini-1.0-pro-vision-001")

    # Define the text to summarize
    text_to_summarize = """
    Provide a very short summary, no more than three sentences, for the following article:
    Our quantum computers work by manipulating qubits in an orchestrated fashion that we call quantum algorithms.
    """

    # Generate the summary
    response = client.generate_text(text_to_summarize, temperature=0.2)

    # Extract the summary from the response
    summary = response.text

    return summary

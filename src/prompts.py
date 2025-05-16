"""Prompt for the presentation generator."""

# ruff: noqa: E501

generation_prompt_template = """You are a presentation designer. Your task is to generate a valid JSON to be used with the `python-pptx` library to create a PowerPoint presentation.

Topic: "{topic}"

You must follow exactly this JSON schema:
{json_schema_minified}

Here is an example of a valid JSON for the topic "La dieta mediterránea y sus beneficios":
{json_example_minified_1}

And this is another example for the topic "El impacto de la inteligencia artificial en la educación":
{json_example_minified_2}

And another example for the topic "Cambio climático y sus efectos globales":
{json_example_minified_3}

Do not reuse these examples or imitate their structure!

Instructions:
- The examples are provided only for illustration of the schema format. You must not copy their structure, slides, or content.
- You must create an original presentation with content that is consistent with the topic provided.
- Not all the fields in the schema are required. Only include the ones that are relevant to the topic and the design of the presentation.
- The output must strictly match the structure defined in the schema.
- The presentation must contain {count} slides where the first one is the title slide.
- Use realistic, varied, and relevant content based on the topic.
- Use paragraphs, bullet points, and a combination of different layouts.
- Include at least one chart and one table, as long as they are relevant to the topic.
- For any visual elements:
    - Use hex color codes that are visually coherent across the presentation.
    - For each image, provide a `pixabay_query` field with one, two or three English words related to the slide's content.
    - Do not repeat the same `pixabay_query` word across images.
- When generating charts:
    - The number of `categories` must match the number of values in each series.
    - Avoid naming series and categories with the same text.
- When positioning elements:
    - Avoid overlapping of textboxes or other visual elements.
    - Ensure that each element has a distinct vertical space (`top` + `height`) that does not intersect with others.
    - Use reasonable sizes and positions that fit within a 10x7.5 inch slide canvas.

Language: All slide content (titles, text, bullet points, captions, etc.) must be written in the same language as the topic.

Formatting:
- Check and ensure the JSON is valid.
- Output only the JSON.
- Do not include any additional text, explanation, or comments.
"""

fix_prompt_template = """You are a presentation designer and JSON repair assistant.

Your task is to fix the following broken or invalid JSON:
{json}

This JSON should follow the structure described by the following schema (do NOT copy this schema):
{json_schema_minified}

Instructions:
- Fix all syntax errors (e.g., missing commas, brackets, or quotes).
- Fix structural issues (e.g., wrong property names, missing required fields, invalid types).
- Ensure that the JSON follows the rules defined by the schema, but DO NOT copy the schema.
- DO NOT include any "$schema" field or the schema itself in the output.
- The output must be a **valid JSON object only**, with no explanation or additional text.
- If the output contains any "$schema" field, it is incorrect. Never include any JSON schema definitions.

Think carefully. Return only the corrected JSON.
"""

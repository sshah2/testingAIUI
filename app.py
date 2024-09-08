import markdown

# Sample Markdown text
markdown_text = """
# This is a Heading

Here is some basic text with **bold** and *italic* formatting.

## Subheading

- List item 1
- List item 2

[Link to OpenAI](https://www.openai.com/)
"""

# Converting Markdown text to HTML
html_output = markdown.markdown(markdown_text)

print(html_output)

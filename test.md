# Test Document

This is a test document to verify the Markdown to PDF conversion.

## Features

- **Bold text** and *italic text*
- [External link](https://www.example.com)
- Internal links to [Features](#features)

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

## Image

![Squirrel](squirrel--image_by_Sasha_matic_from_pixabay.jpg)
Image by Sasha matic from Pixabay

## Math Formula

The quadratic formula is:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$


## Mermaid Diagram

### Small Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Fix it]
    D --> B
```
### Large Mermaid Diagram

```mermaid
  flowchart LR;
      A[CI MULTI CHAPTCHA]-->B{Select captcha service by developer?};
      classDef green color:#022e1f,fill:#00f500;
      classDef red color:#022e1f,fill:#f11111;
      classDef white color:#022e1f,fill:#fff;
      classDef black color:#fff,fill:#000;
      B--YES-->C[How to use?]:::green;
      
      C-->U[I choose recaptcha.]:::green;
      U--Views-->Q["echo CIMC_JS('recaptcha');\n echo CIMC_HTML(['captcha_name'=>'recaptcha']);"]:::green;
      U--Controller-->W["CIMC_RULE('recaptcha');"]:::green;
      
      C-->I[I choose arcaptcha.]:::white;
      I--Views-->O["echo CIMC_JS('arcaptcha');\n echo CIMC_HTML(['captcha_name'=>'arcaptcha']);"]:::white;
      I--Controller-->P["CIMC_RULE('arcaptcha');"]:::white;
      
      C-->X[I choose bibot.]:::red;
      X--Views-->V["echo CIMC_JS('bibot');\n echo CIMC_HTML(['captcha_name'=>'bibot']);"]:::red;
      X--Controller-->N["CIMC_RULE('bibot');"]:::red;
      
      B--NO-->D[How to use?]:::black;
      D---Views:::black-->F["echo CIMC_JS('randomcaptcha');\n echo CIMC_HTML(['captcha_name'=>'randomcaptcha']);"]:::black; 
      D---Controller:::black-->T["CIMC_RULE('archaptcha,recaptcha,bibot');"]:::black;
```

## Blockquote

> This is a blockquote. Use it to highlight important notes, citations, or remarks.
> It can span multiple lines and will be styled with a left border.

## Table

| Name | Description |
|------|-------------|
| md2html | Converts Markdown to HTML |
| html2pdf | Converts HTML to PDF |
| md2pdf | Converts Markdown directly to PDF |
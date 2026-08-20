from unidoc.ir.models import Document


class MarkdownRenderer:
    def render(self, document: Document) -> str:
        output = []

        for page in document.pages:
            output.append(f"<!-- page: {page.physical_page_number} -->")

            for element in page.elements:
                if element.ignored:
                    continue

                if element.type == "heading":
                    output.append(f"# {element.text}")
                elif element.type == "paragraph":
                    output.append(element.text if element.text else "")
                elif element.type == "equation":
                    output.append(f"$$\n{element.latex}\n$$")
                # Table rendering would go here, skipping for MVP
                else:
                    if element.text:
                        output.append(element.text)

        return "\n\n".join(output)


def export_markdown(document: Document, path: str) -> None:
    renderer = MarkdownRenderer()
    md_content = renderer.render(document)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md_content)

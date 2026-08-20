from doctensor.ir.models import Document


def export_json(document: Document, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            document.model_dump_json(
                indent=2,
                exclude_none=True
            )
        )

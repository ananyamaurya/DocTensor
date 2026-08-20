import pytest
from doctensor.pipeline.context import PipelineContext
from doctensor.pipeline.pipeline import DocumentPipeline, PipelineStage


class DummyStage(PipelineStage):
    def run(self, context: PipelineContext) -> PipelineContext:
        context.debug["dummy_stage_run"] = True
        return context


def test_pipeline_execution():
    context = PipelineContext(
        source_path="dummy.pdf",
        source_type="pdf"
    )
    
    stage = DummyStage()
    pipeline = DocumentPipeline(stages=[stage])
    
    result_context = pipeline.run(context)
    
    assert result_context.source_path == "dummy.pdf"
    assert result_context.debug.get("dummy_stage_run") is True

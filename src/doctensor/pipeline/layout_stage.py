from doctensor.pipeline.pipeline import PipelineStage
from doctensor.pipeline.context import PipelineContext
from doctensor.layout.base import LayoutBackend


class LayoutStage(PipelineStage):
    def __init__(self, backend: LayoutBackend):
        self.backend = backend

    def run(self, context: PipelineContext) -> PipelineContext:
        self.backend.classify(context)
        return context

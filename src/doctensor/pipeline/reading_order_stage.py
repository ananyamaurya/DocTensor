from doctensor.pipeline.pipeline import PipelineStage
from doctensor.pipeline.context import PipelineContext
from doctensor.layout.reading_order import ReadingOrderReconstructor


class ReadingOrderStage(PipelineStage):
    def __init__(self, reconstructor: ReadingOrderReconstructor):
        self.reconstructor = reconstructor

    def run(self, context: PipelineContext) -> PipelineContext:
        self.reconstructor.reconstruct(context)
        return context

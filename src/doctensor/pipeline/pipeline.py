from abc import ABC, abstractmethod

from doctensor.pipeline.context import PipelineContext


class PipelineStage(ABC):
    @abstractmethod
    def run(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError


class DocumentPipeline:
    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages

    def run(self, context: PipelineContext) -> PipelineContext:
        for stage in self.stages:
            context = stage.run(context)
        return context

from doctensor.pipeline.context import PipelineContext

class ReadingOrderReconstructor:
    def reconstruct(self, context: PipelineContext) -> None:
        """
        Reconstructs the reading order of elements on each page.
        Modifies the page.elements list in-place.
        """
        for page in context.pages:
            if not page.elements:
                continue

            elements_with_bbox = [e for e in page.elements if e.bbox is not None]
            elements_without_bbox = [e for e in page.elements if e.bbox is None]
            
            if not elements_with_bbox:
                continue

            # Sort top to bottom initially
            elements_with_bbox.sort(key=lambda e: e.bbox.y0)
            
            # Very simplistic column grouping based on x-overlap or x-midpoint
            columns = []
            for element in elements_with_bbox:
                mid_x = (element.bbox.x0 + element.bbox.x1) / 2
                
                placed = False
                for col in columns:
                    col_avg_x = sum((e.bbox.x0 + e.bbox.x1)/2 for e in col) / len(col)
                    width_threshold = page.width * 0.2 if page.width else 100
                    if abs(mid_x - col_avg_x) < width_threshold:
                        col.append(element)
                        placed = True
                        break
                
                if not placed:
                    columns.append([element])
                    
            # Sort columns left to right based on their average x
            columns.sort(key=lambda col: sum((e.bbox.x0 + e.bbox.x1)/2 for e in col) / len(col))
            
            ordered_elements = []
            for col in columns:
                # Within column, sort top to bottom
                col.sort(key=lambda e: e.bbox.y0)
                ordered_elements.extend(col)
                
            page.elements = ordered_elements + elements_without_bbox

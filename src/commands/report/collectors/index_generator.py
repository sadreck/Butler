import os
from src.commands.report.collector_base import CollectorBase


class IndexGenerator(CollectorBase):
    generated_outputs: dict = None

    def generate_output_paths(self):
        self.outputs['html'] = os.path.join(self.output_path, f'index.html')

    def run(self) -> bool:
        if self.generated_outputs is None:
            raise NotImplementedError(f"generated_outputs is None")

        data = {
            'org': self.org.name,
            'workflows': self.generated_outputs.get('workflows', None),
            'third_party': self.generated_outputs.get('third_party', None),
            'variables': self.generated_outputs.get('variables', None),
            'runners': self.generated_outputs.get('runners', None),
            'errors': self.generated_outputs.get('errors', None),
        }

        self.render('index', self.org.name, data, self.outputs['html'])
        return True

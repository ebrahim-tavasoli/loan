from loan.base_forms import CommaSeparatedBaseForm
from guarantees import models


class CheckForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.Check
        fields = '__all__'
        

class PromissoryNoteForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.PromissoryNote
        fields = '__all__'

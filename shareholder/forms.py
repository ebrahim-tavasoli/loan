from loan.base_forms import CommaSeparatedBaseForm
from shareholder import models


class ShareForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.Share
        fields = '__all__'

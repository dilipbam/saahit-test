class VendorForms(object):
    CONTRACT_FORM = 'CONTRACT_FORM'
    SCHEDULE_FORM = 'SCHEDULE_FORM'

    def get_forms(self):
        return [self.CONTRACT_FORM,
                self.SCHEDULE_FORM]


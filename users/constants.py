from django.utils import timezone

GENDER = (
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
)

EMP_STATUS = (
    ('RECRUIT', 'Recruit'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('TERMINATED', 'Terminated'),

)

EMP_STATUS_APP_TER = (
    ('APPROVED', 'Approve'),
    ('TERMINATED', 'Terminate'),
)

EMP_APPROVE_OR_REJECT = (
    ('RECRUIT', 'Recruit'),
    ('APPROVED', 'Approve'),
    ('REJECTED', 'Reject'),
)

MARITAL_STATUS = (
    ('SINGLE', 'Single'),
    ('MARRIED', 'Married'),
    ('SEPARATED', 'Separated'),
    ('DIVORCED', 'Divorced'),
    ('WIDOWER', 'Widower')
)

YEARS = [year for year in range(1980, timezone.now().year)]

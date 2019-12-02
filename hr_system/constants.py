from django.utils import timezone


YES_OR_NO_TYPES = (
    ("YES", "Yes"),
    ("NO", "No")
)

YEARS = [year for year in range(1980, timezone.now().year)]

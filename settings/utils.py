from django.core.validators import RegexValidator

class PhoneNumbersValidator(RegexValidator):
    regex = r'^\+?1?\d{9,15}$'
    message = 'Phone number must be in the format +1234567890'
    code = 'invalid_phone_number'


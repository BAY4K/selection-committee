import secrets

from captcha.fields import CaptchaTextInput


def readable_challenge():
    # Avoid characters that are easily confused (0/O and 1/I/L).
    challenge = ''.join(secrets.choice('23456789ABCDEFGHJKMNPQRSTUVWXYZ') for _ in range(5))
    return challenge, challenge.lower()


class ApplicationCaptchaWidget(CaptchaTextInput):
    template_name = 'captcha/application_widget.html'

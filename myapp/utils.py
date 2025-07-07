# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

def send_activation_email(user, request):
    """Send activation email to user"""
    
    # Generate activation URL
    activation_url = request.build_absolute_uri(
        reverse('activate_account', kwargs={'token': user.activation_token})
    )
    
    # Email subject
    subject = 'Activate Your Account'
    
    # Render HTML email template
    html_message = render_to_string('emails/activation_email.html', {
        'user': user,
        'activation_url': activation_url,
        'site_name': 'Your Site Name'
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order
from django.http import HttpResponse
import re
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
from .models import ContactMessage, Product


def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Send email to admin
        full_message = f"Name: {name}\nEmail: {email}\n\nSubject: {subject}\n\nMessage:\n{message}"
        send_mail(
            subject=f"New Contact Form Submission: {subject}",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['your gmail'],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('home')
    products = Product.objects.all()
    context = {
      "products": products,
    }

    return render(request, 'index.html')


def signup(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']

        # Validate First Name and Last Name (only alphabets)
        if not fname.isalpha():
            messages.error(request, "First Name should only contain letters.")
            return redirect('signup')

        if not lname.isalpha():
            messages.error(request, "Last Name should only contain letters.")
            return redirect('signup')

        # Validate Passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # Validate password length
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('signup')

        # Validate Email format
        if not re.match(r'^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$', email):
            messages.error(request, "Invalid email format.")
            return redirect('signup')

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            user.first_name = fname
            user.last_name = lname
            user.save()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect('log_in')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')


def log_in(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Using email as the username field
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, "Invalid email or password")
            return redirect('log_in')

    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('home')


@login_required
def buynow(request):
    if request.method == 'POST':
        product_name = request.POST.get('productName', '')
        product_price = float(request.POST.get('productPrice', 0))
        quantity = int(request.POST.get('quantity', 1))
        address = request.POST.get('address', '')
        payment_method = request.POST.get('payment_method')
        total_price = product_price * quantity

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect('buynow')

        if payment_method == 'cod':
            order = Order.objects.create(
                user=request.user,
                product_name=product_name,
                product_price=product_price,
                quantity=quantity,
                total_price=total_price,
                address=address
            )

            # Send email
            subject = "Thank You for Your Order from MenTrend"
            message = f"""
            Dear {request.user.first_name} {request.user.last_name},

            Thank you for placing an order with MenTrend!

            You have ordered:
            Product: {product_name}
            Quantity: {quantity}
            Total Price: ₹{total_price}

            Your order will be delivered within 3-7 business days.

            Best regards,
            The MenTrend Team
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [request.user.email]
            send_mail(subject, message, from_email, recipient_list)

            messages.success(request, "Order placed successfully with Cash on Delivery!")
            return redirect('home')

        elif payment_method == 'online':
            request.session['buy_form_data'] = {
                'productName': product_name,
                'productPrice': product_price,
                'quantity': quantity,
                'address': address,
                'email': request.user.email,
                'name': f"{request.user.first_name} {request.user.last_name}"
            }
            return redirect('initiate_payment')

    # GET request
    product_name = request.GET.get('name', '')
    product_price = request.GET.get('price', '')

    user = request.user
    full_name = f"{user.first_name} {user.last_name}"
    email = user.email

    context = {
        'product_name': product_name,
        'product_price': product_price,
        'full_name': full_name,
        'email': email,
    }
    return render(request, 'buynow.html', context)
    

@login_required
def initiate_payment(request):
    form_data = request.session.get('buy_form_data')
    if not form_data:
        messages.error(request, "Session expired. Please try again.")
        return redirect('buynow')

    amount = float(form_data['productPrice']) * int(form_data['quantity']) * 100  # in paisa

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': int(amount), 'currency': 'INR', 'payment_capture': '1'})

    context = {
        'razorpay_order_id': payment['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': int(amount),
        'name': form_data['name'],
        'email': form_data['email'],
        'order_id': payment['id']
    }
    return render(request, 'payment.html', context)


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        form_data = request.session.get('buy_form_data')
        if form_data:
            total_price = float(form_data['productPrice']) * int(form_data['quantity'])
            Order.objects.create(
                user=request.user,
                product_name=form_data['productName'],
                product_price=float(form_data['productPrice']),
                quantity=int(form_data['quantity']),
                total_price=total_price,
                address=form_data['address']
            )
            send_mail("Order Confirmed", "Thanks for your order!", settings.DEFAULT_FROM_EMAIL, [form_data['email']])
            messages.success(request, "Payment successful and order placed.")
            return redirect('home')
    return redirect('home')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')

            send_mail(
                'Password Reset - MenTrend',
                f'Click the link to reset your password:\n{reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            messages.success(request, 'Password reset link sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'Email not found.')
    return render(request, 'forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST['password']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset. Please login.')
                return redirect('log_in')
            return render(request, 'reset_password.html')
        else:
            messages.error(request, 'Invalid or expired link.')
            return redirect('forgot_password')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid reset link.')
        return redirect('forgot_password')
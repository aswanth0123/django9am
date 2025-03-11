import requests
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # For testing purposes only - remove in production
def index(request):
    # Get credentials from session or POST data
    username = request.session.get('new_username', '')
    password = request.session.get('new_password', '')
    
    # Debug print to check if credentials are being passed correctly
    print(f"Index received session credentials: username={username}, password_length={len(password) if password else 0}")
    
    # If we have credentials from signup, attempt to log in automatically
    if username and password:
        try:
            # Build API request for authentication
            base_url = 'https://test.httpapi.com/api/resellers/v2/authenticate.xml'
            
            params = {
                'auth-userid': '1268935',
                'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
                'username': username,  # Use exactly what user entered
                'passwd': password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            print(f"Auto-login: Attempting to authenticate user '{username}'")
            response = requests.post(base_url, data=params, headers=headers, timeout=30)
            
            print(f"Auto-Login Status Code: {response.status_code}")
            print(f"Auto-Login Response Content: {response.text}")
            
            # Check for success in the response
            if '<status>Success</status>' in response.text or '<accessToken>' in response.text or response.status_code == 200:
                # Successful login
                request.session['is_authenticated'] = True
                request.session['username'] = username
                
                # Clear the credentials from session after successful login
                request.session.pop('new_username', None)
                request.session.pop('new_password', None)
                request.session.modified = True
                
                messages.success(request, "Login successful! Welcome to Start Reseller.")
                return render(request, 'index.html')
            else:
                # Don't clear credentials yet, let's manually populate the form
                print("Auto-login failed, will pre-fill form for manual login")
                messages.warning(request, "Please log in with your new account credentials.")
                # Don't clear session here, so the form can be pre-filled
        except Exception as e:
            print(f"Auto-login exception: {str(e)}")
            messages.warning(request, "Please log in with your new account credentials.")
            # Don't clear session here, so the form can be pre-filled
    
    # Handle manual login form submission
    if request.method == 'POST':
        form_username = request.POST.get('email', '')
        form_password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'
        
        print(f"Manual login attempt with username: {form_username}")
        
        if not form_username or not form_password:
            messages.error(request, "Please enter both email and password")
            return render(request, 'index.html', {
                'email': username  # Pre-fill the form with the email from session
            })
        
        # Here you would authenticate against your API
        try:
            # Build API request for authentication
            base_url = 'https://test.httpapi.com/api/resellers/v2/authenticate.xml'
            
            params = {
                'auth-userid': '1268935',
                'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
                'username': form_username,  # Use exactly what user entered
                'passwd': form_password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            print(f"Manual login: Attempting to authenticate user '{form_username}'")
            response = requests.post(base_url, data=params, headers=headers, timeout=30)
            
            print(f"Manual Login Status Code: {response.status_code}")
            print(f"Manual Login Response Content: {response.text}")
            
            # Check for success in the response - broader check for successful responses
            if '<status>Success</status>' in response.text or '<accessToken>' in response.text or response.status_code == 200:
                # Successful login
                request.session['is_authenticated'] = True
                request.session['username'] = form_username
                
                # Clear any remaining signup credentials
                request.session.pop('new_username', None)
                request.session.pop('new_password', None)
                request.session.modified = True
                
                # If remember_me is checked, extend session lifetime
                if remember_me:
                    request.session.set_expiry(86400 * 30)  # 30 days
                
                messages.success(request, "Login successful! Welcome to Start Reseller.")
                return render(request, 'index.html')
            else:
                messages.error(request, "Invalid username or password")
                # Pre-fill the form with the attempted username
                return render(request, 'index.html', {
                    'email': form_username
                })
        except Exception as e:
            print(f"Manual login exception: {str(e)}")
            messages.error(request, "Error connecting to authentication service. Please try again.")
            return render(request, 'index.html', {
                'email': form_username
            })
    
    # Pre-fill the form with the username from session if available
    return render(request, 'index.html', {
        'email': username
    })

@csrf_exempt  # For testing purposes only - remove in production
def signup2(request):
    if request.method == 'POST':
        # Get form data from the template fields
        name = request.POST.get('name', '')
        company = request.POST.get('company', '')
        gst_no = request.POST.get('gst_no', '')
        phone = request.POST.get('phone', '')
        country = request.POST.get('country', 'GB')
        state = request.POST.get('state', '')
        city = request.POST.get('city', '')
        zipcode = request.POST.get('zipcode', '')
        selling_currency = request.POST.get('selling_currency', 'GBP')
        accept_policy = request.POST.get('accept_policy') == 'on'
        
        # Get user-provided email and password
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        # Debug print
        print(f"Processing signup: name={name}, email={email}, phone={phone}, city={city}, zipcode={zipcode}")
        
        # Basic validation
        if not name or not phone or not city or not zipcode or not email or not password or not accept_policy:
            messages.error(request, "Please fill in all required fields")
            return render(request, 'signup2.html')
        
        # Password validation
        if len(password) < 9 or len(password) > 16:
            messages.error(request, "Password must be between 9-16 characters")
            return render(request, 'signup2.html')
            
        # Check for required character types in password
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[~*!@$#%_+.?:,{}]', password))
        
        if not (has_lower and has_upper and has_digit and has_special):
            messages.error(request, "Password must include at least one lowercase letter, one uppercase letter, one number, and one special character")
            return render(request, 'signup2.html')
        
        # UK Zipcode validation for GB country
        if country == 'GB':
            # Format UK postcode: ensure uppercase and proper spacing
            zipcode = zipcode.upper().replace(" ", "")
            
            # UK Postcode regex pattern
            uk_postcode_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}$|^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$'
            
            if not re.match(uk_postcode_pattern, zipcode):
                # Try to format it correctly with a space
                if len(zipcode) >= 5:
                    formatted_zipcode = zipcode[:-3] + " " + zipcode[-3:]
                    # Check if the formatted version matches
                    if not re.match(uk_postcode_pattern, formatted_zipcode):
                        messages.error(request, "Please enter a valid UK postcode (e.g., SW1A 1AA)")
                        return render(request, 'signup2.html')
                    zipcode = formatted_zipcode
                else:
                    messages.error(request, "Please enter a valid UK postcode (e.g., SW1A 1AA)")
                    return render(request, 'signup2.html')
        
        # Use the email directly as username - no prefix
        username = email
        
        # Prepare company name if not provided
        company_name = company if company else f"{name}'s Company"
        
        # Format address line 1
        address_line_1 = f"{city}, {state}" if state else city
        
        # Clean phone number
        clean_phone = ''.join(c for c in phone if c.isdigit())
        
        # Build API request
        base_url = 'https://test.httpapi.com/api/resellers/v2/signup.xml'
        params = {
            'auth-userid': '1268935',
            'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
            'username': username,  # Use exactly what user entered
            'passwd': password,
            'name': name,
            'company': company_name,
            'address-line-1': address_line_1,
            'city': city,
            'state': state if state else city,
            'country': country,
            'zipcode': zipcode,
            'phone-cc': '44',  # UK code
            'phone': clean_phone,
            'lang-pref': 'en',
            'accounting-currency-symbol': selling_currency,
            'selling-currency-symbol': selling_currency,
            'accept-policy': 'true',
            'auto-activate': 'true'
        }
        
        # Add VAT ID if provided
        if gst_no:
            params['vat-id'] = gst_no
        
        try:
            # Set headers and longer timeout
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            print(f"Sending API signup request with username: '{username}':", params)
            response = requests.post(base_url, data=params, headers=headers, timeout=60)
            
            # Print response for debugging
            print(f"Signup Status Code: {response.status_code}")
            print(f"Signup Response Content: {response.text}")
            
            # Check for success in the response
            if '<status>Success</status>' in response.text or '<string>Success</string>' in response.text:
                # Store credentials in session for the login page
                request.session['new_username'] = username
                request.session['new_password'] = password
                request.session.modified = True
                
                print(f"Account created successfully. Storing credentials in session: username={username}, password_length={len(password)}")
                
                # Add a flash message that will be displayed after redirect
                messages.success(request, "Account created successfully! You'll be logged in automatically.")
                
                # Redirect to the index page
                return redirect('index')
            elif '<message>' in response.text:
                # Extract error message
                start_tag = '<message>'
                end_tag = '</message>'
                start_pos = response.text.find(start_tag) + len(start_tag)
                end_pos = response.text.find(end_tag, start_pos)
                
                if start_pos > len(start_tag) and end_pos > start_pos:
                    error_message = response.text[start_pos:end_pos]
                    messages.error(request, f"API Error: {error_message}")
                else:
                    messages.error(request, "Could not process your request. Please try again.")
            else:
                messages.error(request, f"Error: API returned status code {response.status_code}")
                
        except Exception as e:
            print(f"Signup exception occurred: {str(e)}")
            messages.error(request, f"Error connecting to API: {str(e)}")
            
    return render(request, 'signup2.html')





def signup_page(request):
    return render(request, 'signup.html')





import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # For testing purposes only - remove in production
def forgot_password(request):
    if request.method == 'POST':
        # Get the username/email from the form
        username = request.POST.get('email', '')
        
        # Basic validation
        if not username:
            messages.error(request, "Please enter your email address")
            return render(request, 'forgot_password.html')
        
        try:
            # Build API request for forgot password
            base_url = 'https://test.httpapi.com/api/customers/forgot-password.xml'
            
            params = {
                'auth-userid': '1268935',
                'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
                'username': username
            }
            
            print(f"Forgot password: Attempting to send reset email for user '{username}'")
            response = requests.get(base_url, params=params, timeout=30)
            
            print(f"Forgot Password Status Code: {response.status_code}")
            print(f"Forgot Password Response Content: {response.text}")
            
            # Check for success in the response
            if 'true' in response.text.lower() or response.status_code == 200:
                messages.success(request, "Password reset email has been sent to your email address. Please check your inbox.")
                return redirect('index')
            else:
                messages.error(request, "We couldn't find an account with that email address. Please try again.")
                return render(request, 'forgot_password.html', {'email': username})
                
        except Exception as e:
            print(f"Forgot password exception: {str(e)}")
            messages.error(request, "Error connecting to password reset service. Please try again later.")
            return render(request, 'forgot_password.html', {'email': username})
    
    # If GET request, just show the form
    return render(request, 'forgot_password.html')




def coming_soon(request):
    return render(request, 'comingsoon.html') 
 
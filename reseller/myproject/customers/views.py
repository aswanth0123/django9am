import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # For testing purposes only - remove in production
def index(request):
    # Check if there are credentials from a recent signup
    new_username = request.session.get('new_username', '')
    new_password = request.session.get('new_password', '')
    
    # If we have credentials from signup, attempt to log in automatically
    if new_username and new_password:
        try:
            # Clear the session variables after retrieving them
            del request.session['new_username']
            del request.session['new_password']
            
            # Build API request for authentication
            base_url = 'https://test.httpapi.com/api/resellers/v2/authenticate.xml'
            params = {
                'auth-userid': '1268935',
                'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
                'username': new_username,
                'passwd': new_password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(base_url, data=params, headers=headers, timeout=30)
            
            print(f"Auto-Login Status Code: {response.status_code}")
            print(f"Auto-Login Response Content: {response.text}")
            
            # Check for success in the response
            if '<status>Success</status>' in response.text or '<string>Success</string>' in response.text:
                # Successful login
                request.session['is_authenticated'] = True
                request.session['username'] = new_username
                messages.success(request, "Login successful! Welcome to Start Reseller.")
                # You could redirect to a dashboard here if you want
                # return redirect('dashboard')
            else:
                messages.error(request, "Automatic login failed. Please log in manually with your new credentials.")
        except Exception as e:
            print(f"Auto-login exception: {str(e)}")
            messages.error(request, f"Error during automatic login: {str(e)}")
    
    # Handle manual login form submission
    if request.method == 'POST':
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'
        
        if not username or not password:
            messages.error(request, "Please enter both email and password")
            return render(request, 'index.html')
        
        # Here you would authenticate against your API
        try:
            # Build API request for authentication
            base_url = 'https://test.httpapi.com/api/resellers/v2/authenticate.xml'
            params = {
                'auth-userid': '1268935',
                'api-key': 'pDKU0MlZ4H16YgYxDpGX7wZIpsYJTVHx',
                'username': username,
                'passwd': password
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(base_url, data=params, headers=headers, timeout=30)
            
            print(f"Login Status Code: {response.status_code}")
            print(f"Login Response Content: {response.text}")
            
            # Check for success in the response
            if '<status>Success</status>' in response.text or '<string>Success</string>' in response.text:
                # Successful login
                request.session['is_authenticated'] = True
                request.session['username'] = username
                
                # If remember_me is checked, extend session lifetime
                if remember_me:
                    request.session.set_expiry(86400 * 30)  # 30 days
                
                messages.success(request, "Login successful! Welcome to Start Reseller.")
                # You could redirect to a dashboard here if you want
                # return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password")
        except Exception as e:
            print(f"Login exception: {str(e)}")
            messages.error(request, f"Error connecting to authentication service: {str(e)}")
    
    # Render the login page with any new credentials
    return render(request, 'index.html', {
        'new_username': new_username,
        'new_password': new_password
    })



import requests
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

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
        
        # Use the user-provided email as username instead of generating one
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
            'username': username,
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
            
            print("Sending API request with params:", params)
            response = requests.post(base_url, data=params, headers=headers, timeout=60)
            
            # Print response for debugging
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            
            # Check for success in the response
            if '<status>Success</status>' in response.text or '<string>Success</string>' in response.text:
                # Store credentials in session for the login page
                request.session['new_username'] = username
                request.session['new_password'] = password
                messages.success(request, f"Account created successfully! Please login with your credentials.")
                return redirect('index')  # Redirect to the login page
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
            print(f"Exception occurred: {str(e)}")
            messages.error(request, f"Error connecting to API: {str(e)}")
            
    return render(request, 'signup2.html')


def signup_page(request):
    return render(request, 'signup.html')
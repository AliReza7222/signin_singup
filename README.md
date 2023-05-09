# signin_singup
<p style="font-size: large">
    a mini project for sign_in and sign_up User with Django .
</p>

<p>
  This project has the following property :
</p>

<pre style="font-size: large">
    The user first enters his mobile number.
    If the user has already registered, he will be authenticated by entering the password.
    Otherwise, a one-time 6-digit code will be generated for the user, which will be sent to him via SMS.
    By entering the code, the user is registered and then personal information such as first and last name and email is taken from him
    In the login process, if the user enters the wrong user name three times or enters the wrong combination of username and password   three times from the same IP, he will be blocked for 1 hour.
    In the same way, in the registration process, if three SMS requests come from the same IP but the entered code is wrong, or a number enters the wrong code three times, it will be blocked for 1 hour.
</pre>

Title: What Happens When You Connect to Starbucks Wi-Fi
Date: 2019-09-16T12:15:00-0400
Category: programming
Tags: networking starbucks scripts

Back in the day, if you wanted to use Wi-Fi at Starbucks all you had to do was
click the big green "Accept & Connect" button.

![Starbucks Wi-Fi from Google by Chris Messina](/images/starbucks_captive.jpg)
_[Image by Chris Messina](https://www.flickr.com/photos/factoryjoe/22127717262)_

However, if you were running GNU/Linux like I was at the time, you wouldn't see
the fancy captive portal pop-up as you would see on macOS. Instead, you would
be redirected to the captive portal page within your browser after trying to
visit a website. 

There were a few problems though. I was using the [HTTPS
Everywhere](https://www.eff.org/https-everywhere) browser add-on which needed
to be disabled before I could proceed to the "Accept & Connect" page. Sometimes
I forgot to re-enable the add-on after connecting. Other times I booted up my
machine and jumped right into a terminal only to realize I didn't authenticate
to the Wi-Fi yet. This was all very annoying. I decided to automate the
process with a shell script and a bit of `curl` so I could authenticate from
the comfort of my own terminal.

After poking around in the markup of the portal page I saw that it contained a
simple form which takes parameters from the URL, such as your MAC address and
the access point name, and POSTs the data to
`http://sbux-portal.appspot.com/submit`. Funny thing, I noticed that the MAC
address wasn't even required, only the AP name. Neat.

The important bits of the script looked like:

```
APNAME=`curl -s -o /dev/null -w "%{redirect_url}\n" http://www.google.com | grep -o "apname.*"`
SUBMIT_URL=http://sbux-portal.appspot.com/submit
AUTHENTICATED=`curl -s -F $APNAME $SUBMIT_URL | grep -oh "sbux-portal-authenticated"`
```
Boom. I was authenticated and could go about my business.

But then things changed.

## Google Starbucks

Sometime last year Starbucks introduced "Google Starbucks" Wi-Fi. They now
require your first name, last name, email, and zip code in order to
authenticate to their network. 

![Google Starbucks signup page](/images/google_starbucks_signup.png)

No worries, I thought. I just need to tweak my script with some random data in
order to appease the googly sirens. Turns out that I was wrong. The whole
process now uses a bunch of redirects and JavaScript. Fun.

## What Happens Behind the Scenes

Making the first request.

```
$ curl -v http://www.duckduckgo.com/

*   Trying 184.72.104.138...
* TCP_NODELAY set
* Connected to duckduckgo.com (184.72.104.138) port 80 (#0)
> GET / HTTP/1.1
> Host: duckduckgo.com
> User-Agent: curl/7.54.0
> Accept: */*
> 
< HTTP/1.1 302 Captive Portal
< Server:
< Date: Sun, 15 Sep 2019 22:31:17 GMT
< Cache-Control: no-cache,no-store,must-revalidate,post-check=0,pre-check=0
< Location: https://sbux-portal.globalreachtech.com:443/?cmd=login&mac=xx:xx:xx:xx:xx:xx&essid=Google%20Starbucks&ip=172.31.98.111&apname=18%3A64%3A72%3Ace%3Ae3%3Ab1&apmac=18%3A64%3A72%3Ace%3Ae3%3Ab1&vcname=S00772-VC&switchip=aruba.odyssys.net&url=http%3A%2F%2Fduckduckgo.com%2F
< Connection: close
< 
* Closing connection 0

```

Which wants to redirect us to:

```
https://sbux-portal.globalreachtech.com:443/?cmd=login&mac=xx:xx:xx:xx:xx:xx&essid=Google%20Starbucks&ip=172.31.98.111&apname=18%3A64%3A72%3Ace%3Ae3%3Ab1&apmac=18%3A64%3A72%3Ace%3Ae3%3Ab1&vcname=S00772-VC&switchip=aruba.odyssys.net&url=http%3A%2F%2Fduckduckgo.com%2F
```

Ok, what happens when we request that?

```
> GET /?cmd=login&mac=xx:xx:xx:xx:xx:xx&essid=Google%20Starbucks&ip=172.31.98.111&apname=18%3A64%3A72%3Ace%3Ae3%3Ab1&apmac=18%3A64%3A72%3Ace%3Ae3%3Ab1&vcname=S00772-VC&switchip=aruba.odyssys.net&url=http%3A%2F%2Fduckduckgo.com%2F HTTP/1.1
> Host: sbux-portal.globalreachtech.com
> User-Agent: curl/7.54.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Accept-Ranges: bytes
< Access-Control-Allow-Origin: https://sbux-portal.globalreachtech.com
< Content-Type: text/html
< Date: Sun, 15 Sep 2019 22:37:25 GMT
< ETag: "5ab11893-22c"
< Last-Modified: Tue, 20 Mar 2018 14:20:03 GMT
< Server: openresty
< Strict-Transport-Security: max-age=31536000
< X-Content-Type-Options: nosniff
< X-Frame-Options: SAMEORIGIN
< X-XSS-Protection: 1; mode=block
< Content-Length: 556
< Connection: keep-alive
< 
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
        <title></title>
        <script type="text/javascript">
      window.location.href = '/check' + document.location.search;
      document.getElementById('fallbackLink').href = '/check' + document.location.search;
    </script>
</head>
<body>
<center>
<h1 style="margin-top: 200px; font-size: 90;">Please wait, you are being redirected. If you are not redirected, please <a id="fallbackLink" href="#">click here</a></h1>
</center>
</body>
</html>
* Connection #0 to host sbux-portal.globalreachtech.com left intact
```

Alright, this is just another redirect but in the form of JavaScript. It wants us to go to `/check` while retaining the parameters.

```
https://sbux-portal.globalreachtech.com:443/check?cmd=login&mac=xx:xx:xx:xx:xx:xx&essid=Google%20Starbucks&ip=172.31.98.111&apname=18%3A64%3A72%3Ace%3Ae3%3Ab1&apmac=18%3A64%3A72%3Ace%3Ae3%3Ab1&vcname=S00772-VC&switchip=aruba.odyssys.net&url=http%3A%2F%2Fduckduckgo.com%2F
```

Ok, what happens when we request that?

```
> GET /check?cmd=login&mac=xx:xx:xx:xx:xx:xx&essid=Google%20Starbucks&ip=172.31.98.111&apname=18%3A64%3A72%3Ace%3Ae3%3Ab1&apmac=18%3A64%3A72%3Ace%3Ae3%3Ab1&vcname=S00772-VC&switchip=aruba.odyssys.net&url=http%3A%2F%2Fduckduckgo.com%2F HTTP/1.1
> Host: sbux-portal.globalreachtech.com
> User-Agent: curl/7.54.0
> Accept: */*
> 
< HTTP/1.1 302 Moved Temporarily
< Access-Control-Allow-Origin: https://sbux-portal.globalreachtech.com
< Content-Type: text/html
< Date: Sun, 15 Sep 2019 22:38:39 GMT
< Location: /signup?data=CTx0BMW%2FoKy7yMRAYcKD8Bs%2Bnggy0mPOlILmmhDroh2tAF7buSPIJABsASKvRhwdejvMzywSVTvbJQj92jaWFbz127bgNyNy54Q7TeOxkIqIcbY7d5B3%2FtfFXoIEtuibv%2BVPyP2Cno4%2FZMeV2twc3s2CtE2W2cmVArOOJafM9Fs%3D
< Server: openresty
< Strict-Transport-Security: max-age=31536000
< X-Content-Type-Options: nosniff
< X-Frame-Options: SAMEORIGIN
< X-XSS-Protection: 1; mode=block
< Content-Length: 142
< Connection: keep-alive
< 
<html>
<head><title>302 Found</title></head>
<body>
<center><h1>302 Found</h1></center>
<hr><center>openresty</center>
</body>
</html>
* Connection #0 to host sbux-portal.globalreachtech.com left intact
```

Oh, look, another redirect. This time to a new location `/signup` with a rather
long `data` parameter slapped on the end.

```
https://sbux-portal.globalreachtech.com:443/signup?data=CTx0BMW%2FoKy7yMRAYcKD8Bs%2Bnggy0mPOlILmmhDroh2tAF7buSPIJABsASKvRhwdejvMzywSVTvbJQj92jaWFbz127bgNyNy54Q7TeOxkIqIcbY7d5B3%2FtfFXoIEtuibv%2BVPyP2Cno4%2FZMeV2twc3s2CtE2W2cmVArOOJafM9Fs%3D
```

Ok, what happens when we request that?

```
> GET /signup?data=CTx0BMW%2FoKy7yMRAYcKD8Bs%2Bnggy0mPOlILmmhDroh2tAF7buSPIJABsASKvRhwdejvMzywSVTvbJQj92jaWFbz127bgNyNy54Q7TeOxkIqIcbY7d5B3%2FtfFXoIEtuibv%2BVPyP2Cno4%2FZMeV2twc3s2CtE2W2cmVArOOJafM9Fs%3D HTTP/1.1
> Host: sbux-portal.globalreachtech.com
> User-Agent: curl/7.54.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: https://sbux-portal.globalreachtech.com
< Content-Type: text/html
< Date: Sun, 15 Sep 2019 22:39:52 GMT
< Server: openresty
< Strict-Transport-Security: max-age=31536000
< X-Content-Type-Options: nosniff
< X-Frame-Options: SAMEORIGIN
< X-XSS-Protection: 1; mode=block
< Content-Length: 4113
< Connection: keep-alive
< 
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="GlobalReach Technology">
    <meta name="copyright" content="GlobalReach Technology (2018)">
    <meta name="robots" content="noindex">
    <meta name="description" content="Solution Powered by GlobalReach Technology">
    <meta property="og:title" content="Starbucks WiFi">
    <meta property="og:description" content="Solution Powered by GlobalReach Technology">
    <meta property="og:image" content="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/img/og-image.png">
    <link rel="shortcut icon" href="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/img/favicon.ico" type="image/x-icon" />
    <link rel="apple-touch-icon" href="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/img/og-image.png">
    <title>Starbucks Wi-Fi</title>

    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-P93LDX');</script>

    <link rel="stylesheet" href="https://cdn.sbux-portal.globalreachtech.com/assets/bootstrap/bootstrap.min.css?v=100">
    <link rel="stylesheet" href="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/css/fonts.css?v=100">
    <link rel="stylesheet" href="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/css/styles.css?v=100">

    <script src="https://cdn.sbux-portal.globalreachtech.com/assets/js/jquery.min.js?v=100"></script>
    <script src="https://cdn.sbux-portal.globalreachtech.com/assets/js/signup.js?v=100"></script>
</head>

<body class="bkground">
<div class="login-dark" role="main">
    <form id="auth-form" method="post" class="centered">
        <img class="img-fluid centered sbux-logo" alt="Starbucks logo" src="https://cdn.sbux-portal.globalreachtech.com/assets/greendot/img/siren_2x.png">
        <p class="text-center centered wifi-title"><strong>Wi-Fi + Coffee =&nbsp; 💚</strong></p>
        <p class="text-center centered wifi-desc">Welcome to Starbucks<br>Log on to our network once, and this device will automatically connect at participating &nbsp;Starbucks<sup>®</sup> stores everywhere you go.</p>
        <div class="form-group centered">
            <input class="form-control" type="text" id="fname" name="fname" placeholder="First name" maxlength="50" autocomplete="off" aria-label="First name" autofocus>
            <div id="fname-err" class="form-err" aria-live="assertive"></div>
            <input class="form-control" type="text" id="lname" name="lname" placeholder="Last name" autocomplete="off" maxlength="50" aria-label="Last name">
            <div id="lname-err" class="form-err" aria-live="assertive"></div>
            <input class="form-control" type="text" id="email" name="email" placeholder="Email address" autocomplete="off" maxlength="255" aria-label="Email address">
            <div id="email-err" class="form-err" aria-live="assertive"></div>
            <input class="form-control" type="text" id="postcode" name="postcode" autocomplete="off" placeholder="Postal code" maxlength="12" aria-label="Postal code">
            <div id="postcode-err" class="form-err" aria-live="assertive"></div>
            <p class="text-center centered accept-line">By accepting, I agree to receive emails about Starbucks news, promotions and offers.</p>
            <input class="btn btn-primary btn-block" type="submit" value="Accept &amp; Connect">
        </div>
        <p class="text-center centered terms-line">Starbucks <a href="https://globalassets.starbucks.com/assets/8E9005FEDE0249F086CF8283EA445595.pdf" aria-label="Privacy Statement">Privacy Statement</a></p>
        <p class="text-center centered terms-line"><a href="terms.html" aria-label="Terms of Service">Terms of Service</a></p>
    </form>
</div>
</body>

* Connection #0 to host sbux-portal.globalreachtech.com left intact
```

Ah-ha! We finally made it the signup form. Looks like this just POSTs the input
fields `fname`, `lname`, `email`, and `postcode` to the current URL which
starts with `/signup?data=`. We'll store that in `$SIGNUP_URL`.

So lets POST some fake generated data.

```
$ curl --data-urlencode fname="Mattie" \
       --data-urlencode lname="Parker" \
       --data-urlencode email="MattieRParker@jourrapide.com" \
       --data-urlencode postcode="20036" "$SIGNUP_URL"
```

Hmm, we hit a login page with a hidden form ...

```
> POST /signup?data=CTx0BMW%2FoKy7yMRAYcKD8Bs%2Bnggy0mPOlILmmhDroh2tAF7buSPIJABsASKvRhwdejvMzywSVTvbJQj92jaWFbz127bgNyNy54Q7TeOxkIqIcbY7d5B3%2FtfFXoIEtuibv%2BVPyP2Cno4%2FZMeV2twc3s2CtE2W2cmVArOOJafM9Fs%3D HTTP/1.1
> Host: sbux-portal.globalreachtech.com
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Length: 77
> Content-Type: application/x-www-form-urlencoded
> 
* upload completely sent off: 77 out of 77 bytes
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: https://sbux-portal.globalreachtech.com
< Content-Type: text/html
< Date: Sun, 15 Sep 2019 22:42:49 GMT
< Server: openresty
< Strict-Transport-Security: max-age=31536000
< X-Content-Type-Options: nosniff
< X-Frame-Options: SAMEORIGIN
< X-XSS-Protection: 1; mode=block
< Content-Length: 1259
< Connection: keep-alive
< 
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Initial Login</title>
<!-- Global Site tag (gtag.js) - Google Analytics -->
<!--         Starbucks - Google Analytics         -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-P93LDX');</script>
    </head>
    <body>
        <form id="apForm" action="https://aruba.odyssys.net/cgi-bin/login" method="post">
            <input type="hidden" name="cmd" value="authenticate">
            <input type="hidden" name="user" value="vQOqhNXDWbf1HWNm"> <!-- Generated device-specific credentials -->
            <input type="hidden" name="password" value="O07Pytzh0oLwU6I7zbES0nLsDYU=">
            <input type="hidden" name="url" value="https://wifi.starbucks.com/">
        </form>
        <script>
        window.onload = function() {
          setTimeout(function(){
            document.getElementById("apForm").submit();
          }, 500);
        }
        </script>
    </body>
</html>
* Connection #0 to host sbux-portal.globalreachtech.com left intact
```

The interesting bits on this page are the "generated device-specific"
credentials in the `user` and `password` fields. These values indeed change
when you modify the `mac` parameter in the first redirect URL. I've tried this
whole process multiple times with completely random data in the `mac`
parameter, no `mac` parameter, and with a fake MAC address. Neither worked
when submitting this form. The values change but you hit an error page when you
try to POST them. 

```
> POST /cgi-bin/login HTTP/1.1
> Host: aruba.odyssys.net
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Length: 118
> Content-Type: application/x-www-form-urlencoded
> 
* upload completely sent off: 118 out of 118 bytes
< HTTP/1.1 200 OK
< Content-Type:text/html; charset=utf-8
< Pragma: no-cache
< Cache-Control: max-age=0, no-store
* no chunk, no close, no size. Assume close to signal end
< 
<html>
 <head>
 <meta http-equiv="refresh" content="0; url=https://sbux-portal.globalreachtech.com:443?url=https://wifi.starbucks.com/&mac=xx:xx:xx:xx:xx:xx&ip=172.31.98.111&essid=Google Starbucks&apname=18:64:72:ce:e3:b1&apgroup=S00772-VC&errmsg=Login error. Please retry.">
 </head><body></body>
</html>
* Closing connection 0
* TLSv1.2 (OUT), TLS alert, Client hello (1):
```

I suspect there's some server side validation that validates the `mac` parameter
against the MAC address making the requests. Obviously you should be spoofing
your MAC even before you connect to to the network in the first place. I was
just curious if it made a difference.

Alright, lets just POST the "correct" login credentials to
`https://aruba.odyssys.net/cgi-bin/login`. We'll store the user name in
`$LOGIN_USER`, the password in `$LOGIN_PASSWORD`, and the URL in `$LOGIN_URL`.

```
$ curl --data-urlencode "cmd=authenticate" \
       --data-urlencode "user=$LOGIN_USER" \
       --data-urlencode "password=$LOGIN_PASSWORD" \
       --data-urlencode "url=https://wifi.starbucks.com/" \
       $LOGIN_URL
```

Phew. Finally we're authenticated.

## Recap

1. Select "Google Starbucks" Wi-Fi network.
2. Make a request to any site.
3. Redirect to `?cmd=login` URL.
4. Hit page that uses a JavaScript redirect to `/check?cmd=login` URL.
5. If you've previously logged in, skip to hidden login form with "generated device-specific credentials".
5. If not, redirect to `/signup?data=` URL.
6. POST first name, last name, email, postal code.
7. Hit hidden login form page with "generated device-specific credentials". 
8. POST credentials.
9. Authenticated.

## Some Notes

* I believe the `/check` redirect checks if you've previously signed up before.
  If so, it skips the `/signup` redirect and takes you directly to the hidden
  login form page. Probably has something to do with that long `data` parameter.
* Modifying the parameters in the first redirect changes the device-specific
  credentials. Using those credentials on the final login form sends you to an
  error page.
* You'll need to disable the captive portal control on macOS if you want to try
  these steps out for yourself. If you have already authenticated before you'll
  want to modify the `mac` parameter in the first redirect URL to proceed.

How to disable the captive portal pop-up on macOS:

```
defaults write /Library/Preferences/SystemConfiguration/com.apple.captive.control Active -bool false
```

## coffeeconnect

If you would like to automate this process and authenticate without opening a
browser then please check out my
[coffeeconnect](https://github.com/imwally/coffeeconnect) script.



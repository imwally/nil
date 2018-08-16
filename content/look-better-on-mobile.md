Title: This Site Should Look Better On Mobile Devices
Date: 2018-06-12T23:06:25-0400
Category: meta

Is mobile first design still a thing? Either way, this site should be
easier to read on a mobile device. Font sizes have been slightly
reduces on smaller screens and a little extra padding has been added
for a bit more breathing room. The diff below shows the changes. It's
on
[github](https://github.com/imwally/niltheme/commit/278e44ae3938100166a60393ae18ab1800f6c04e)
as well.

```
:::dpatch
diff --git a/static/css/main.css b/static/css/main.css                                              
index 9566def..f27cc03 100644
--- a/static/css/main.css
+++ b/static/css/main.css
@@ -3,6 +3,11 @@ html, body {
 }


+header, main, footer {
+    box-sizing: border-box;
+}
+
+
 header {
     color: #262E2E;
     width: 600px;
@@ -128,17 +133,23 @@ footer a {

 /* Responsive Stuff */
 @media only screen and (max-width: 600px) {
-    html, body {
-       padding: 0px 20px;
-    }
-
     header,
     main,
     footer {
        width: 100%;
     }

+    h1 {
+       font-size: 24px;
+    }
+
+    main {
+       padding: 10px 15px;
+       font-size: 16px;
+    }
+
     header {
        padding: 0;
     }
+
 }
```

Slowly this little site is taking shape. Even though I'm categorizing
these posts the theme bit is unfinished. Pelican comes with a
[categories](/categories.html) page out of the box, and the theme
seems to handle it well, but I think it could use some work. Also,
what's the difference between categories and tags? I'll have to read
up more on that. Maybe
[this](http://pirsquared.org/blog/pelican-tags-vs-categories.html)
would be a good starting point.

Also, I need to read more about [S3](https://aws.amazon.com/s3/) and
how to get this site behind TLS for great good. Perhaps that's for a
future meta post. 

I think most of this is going to be a lot me thinking out loud but
hopefully some structure will arrive in the midst. Recently I finished
the [Algorithmic
Toolbox](https://www.coursera.org/learn/algorithmic-toolbox) course
with a grade of 85.8%. Not terrible but not great either. The
important part is that I learned a few things of which should be
written down before I forget.

Title: Counting "Characters" In Go
Date: Sun, 03 Mar 2019 20:21:24 -0500
Tags: golang

Even though I have been using macOS full-time for the last 3 years I still like
to use the same command line utilities I used when running Linux and OpenBSD.
Indeed [mutt](http://www.mutt.org) is one of those utilities. Once you master
navigation it's hard to use anything else. There are however some downsides
when living in the terminal, like dealing with HTML emails. 
 
There are a couple options though. You can pipe the email to your favorite
terminal based web browser such as [lynx](https://lynx.browser.org),
[links](http://links.twibright.com), or even [elinks](http://www.elinks.cz).
You can even just save the html file and open it up in your favorite desktop
browser. But what if you just need to access a single link within the email
such as a verification or unsubscribe link? There's a handy little utility
called [urlview](https://github.com/sigpipe/urlview) that makes this task
easier. I really like `urlview` but I don't like that I can't tell what the
context of the link is. Since the world is obsessed with tracking and analytics
it's almost impossible to tell where a link points to in some cases. 

Here's an example of `urlview` on a new music notification email from Apple Music:

```
UrlView 0.9: (99 matches) Press Q or Ctrl-C to Quit!

->    1 http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd
      2 http://www.w3.org/1999/xhtml
      3 https://new.applemusic.com/img/APPLE_EMAIL_LINK/spacer2.gif?v=2&a=aDOTAYkFZd5DLnage3eJb%2FpW
      4 https://new.applemusic.com/r?v=2&la=en&lc=usa&a=TGTVS9fyLweNj90vV5N4BdZQgzKk%2BdLiNUPJ0ZBgdV
      5 http://static-its-images.apple.com/images/applemusic/apple-music-logo.png
      6 https://new.applemusic.com/r?v=2&la=en&lc=usa&a=TGTVS9fyLweNj90vV5N4BdZQgzKk%2BdLiNUPJ0ZBgdV
      7 https://new.applemusic.com/r?v=2&la=en&lc=usa&a=NdC6z1KzllRaGq4wOYsjvGc1Pf%2BJ1im1VCK6ObUhIh
      8 https://is4-ssl.mzstatic.com/image/thumb/Features128/v4/e3/85/a0/e385a03e-4158-0345-8bf9-748
      9 https://new.applemusic.com/r?v=2&la=en&lc=usa&a=NdC6z1KzllRaGq4wOYsjvGc1Pf%2BJ1im1VCK6ObUhIh
     10 http://static-its-images.apple.com/images/applemusic/rt-arrow-fd3159.png

``` 

Not very helpful. I have no idea where most of those links are pointing to. So
I wrote a replacement called [linkview](https://github.com/imwally/linkview)
that does something similar but is positioned more towards links within an HTML
document.

Here's the same example from above but using `linkview`:

```
h: help   q: quit   (1 of 79)

https://new.applemusic.com/r?v=2&la=en&lc=usa&a=TGTVS9fyLweNj90vV5N4BdZQgzKk%2BdLiNUPJ0ZBgdVZwdH20X5N4AQkPUylShu%2Beb%

-> Apple Music
   This just in.
   Here’s a selection of the hottest new music.
   New in Electronic
   Electronic Daily
   Electronic Daily
   Listen now
   Nosso
   Nosso     
   Branko             
   Listen now         
   The Weight
   The Weight
   Weval                       
   Listen now                  

```

As I scroll down the list the URL at the top will show me what the text points
to. Hitting tab will show the full URL or I can simply call `open` on the URL to
open up my default desktop browser by hitting return. 

## Counting Characters

A problem started to appear on a few emails though. I noticed that certain
links had gaps between the characters. Here's an example (with a lot of links
trimmed out) of using Hacker News:

```
-> The password “  ji32k7au4a83”   has been seen over a hundred times           
   China’  s Plan to Build the World’  s Biggest Supergrid                      
   Show HN: Wdio –   Docker setup for WebdriverIO                               
   Designing a package manager from the ground up                               
```

Clearly there's an issue with characters like `“`,`’`, and `–`. But why? 

First I should mention how the program renders a line of text in the terminal.
Using the [termbox-go](https://github.com/nsf/termbox-go) package you can write
to the terminal at any column or row with:

```
termbox.SetCell(x, y, char, termbox.ColorDefault, termbox.ColorDefault)
```

To simply writing a line I wrapped this in a function using a for loop that
would range over a string which incremented the x position on each loop.

```
func (t *Terminal) Println(x int, y int, s string) {
        for col, char := range s {
                termbox.SetCell(col+x, y, char, termbox.ColorDefault, termbox.ColorDefault)
        }
}
```

This seems pretty straightforward but obviously something is off since gaps are
appearing within the strings. Let's do some simple testing in the Go Playground
to figure out what's going on.

```
package main

import (
    "fmt"
)

func main() {
    s := "The password “ji32k7au4a83” has been seen over a hundred times"
    for i, char := range s {
        fmt.Printf("%d:\t%c\n", i, char)
    }
}
```
[Run on Go Playground](https://play.golang.org/p/ioMvcs8IBr-)

```
12:  
13: “
16: j
17: i
18: 3
19: 2
20: k
21: 7
22: a
23: u
24: 4
25: a
26: 8
27: 3
28: ”
31:  
```

Sure enough, there's a jump in the index when the `“` character appears.

One from 13 to 16 and then again from 28 to 31. Where are those 2 digits
disappearing to? Maybe Rob Pike has something to say about [Strings, bytes,
runes and characters in Go](https://blog.golang.org/strings).

> One way to approach this topic is to think of it as an answer to the frequently asked question, "When I index a Go string at position n, why don't I get the nth character?" As you'll see, this question leads us to many details about how text works in the modern world.

...

> To answer the question posed at the beginning: Strings are built from bytes so indexing them yields bytes, not characters. A string might not even hold characters. In fact, the definition of "character" is ambiguous and it would be a mistake to try to resolve the ambiguity by defining that strings are made of characters.

Knowing this now made it apparent what the issue was. Since runes have varying
widths you shouldn't depend on the index of a range over a string to count
sequentially. A rune made of multiple bytes will cause the `terminal.Println`
function to write blanks for each additional byte. A simple fix is to use an
auxiliary index counter initialized outside of the `for` loop and incremented
within it.

```
func main() {
    s := "The password “ji32k7au4a83” has been seen over a hundred times"
    i := 0
    for _, char := range s {
        fmt.Printf("%d:\t%c\n", i, char)
        i++
    }
}
```
[Run On Go Playground](https://play.golang.org/p/nBLslbrHnxi)

```
12:
13: “
14: j
15: i
16: 3
17: 2
18: k
19: 7
20: a
21: u
22: 4
23: a
24: 8
25: 3
26: ”
27:  
```

Now that's what I was looking for. Here's the updated `terminal.Println()` function:

```
func (t *Terminal) Println(x int, y int, s string) {
    i := 0
    for _, char := range s {
        termbox.SetCell(i+x, y, char, termbox.ColorDefault, termbox.ColorDefault)
        i++
    }
}
```

And what the output now looks like:

```
-> The password “ji32k7au4a83” has been seen over a hundred times
   China’s Plan to Build the World’s Biggest Supergrid
   Show HN: Wdio – Docker setup for WebdriverIO                                 
   Designing a package manager from the ground up                               
```
## What is a String?

- A string is a slice of bytes.
- A "character" isn't necessarily made of a single byte.
- A `for range` on a string loops over one UTF-8 code point or what is called
  a rune in Go on each iteration.
- Each time around the loop, the index of the loop is the starting position
  of the current rune, measured in bytes, and the code point is its value.

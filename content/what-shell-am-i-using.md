Title: What Shell Am I Using?
Date: 2020-01-13T21:19:05-0500
Category: unix

I wanted to install the latest version of zsh on my MacBook Pro. This is
usually the first thing I install when setting up a new machine. A `brew
install zsh` and a `chsh` later and I'm good to go (well, technically I had to
add the homebrew location of zsh to `/etc/shells` as well). Close out
Terminal.app and reopen to make sure my changes took effect, and sure enough,
there's my zsh prompt. 

Yes, I know macOS Catalina ships with zsh as the default shell, but I want to
make sure I have the latest... just because.

Curiosity strikes in and I wonder, even though the homebrew location of zsh is
configured as my shell, am I actually using it?

## which

```
~ % which zsh
/usr/local/bin/zsh
```

Hold on. I want the full location.

```
~ % ls -la $(which zsh)
lrwxr-xr-x  1 wally  admin  27 Dec 28 20:28 /usr/local/bin/zsh -> ../Cellar/zsh/5.7.1/bin/zsh
```

Yup, that looks about right. 

But wait... that only told me the location of zsh the executable which is only
correct because I added homebrew's `/usr/local/bin` location to my `PATH`. That is literally
the first line of the man page for `which`.

```
WHICH(1)                  BSD General Commands Manual                 WHICH(1)

NAME
     which -- locate a program file in the user's path
```

That means that if I were to execute `zsh` from my current shell a new instance
of zsh from `/usr/local/bin/zsh` would begin. This doesn't tell me the location
of the shell I'm currently typing in which started after opening Terminal.app.

## $SHELL

```
~ % echo $SHELL
/usr/local/bin/zsh
```

Eh, I don't know. That tells me that it's configured as my shell but does not
necessarily tell me the location of the shell I'm currently typing in.

## ps

Maybe I can find the currently running process of the instance of zsh I'm in right now.

```
~ % ps 
  PID TTY           TIME CMD
78525 ttys003    0:00.11 -zsh
```

Well that still doesn't give me the full path. And is that even the right
process? How do I get the PID of the shell I'm currently typing in? Turns out
there's a convenient shell variable `$$`.

```
~ % echo $$
78525
```

Hmm, that's good I suppose, but I still don't know if the process with PID
`78525`, the one I'm currently typing in, is the correct zsh.

## lsof

Oh yeah, I probably should have used `lsof` a long time ago but knowing how to
get the PID of the current shell makes things a bit easier.

```
~ % lsof -p $$
COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF                NODE NAME
zsh     78525 wally  cwd    DIR    1,5     1120              362897 /Users/wally
zsh     78525 wally  txt    REG    1,5   614404             1052389 /usr/local/Cellar/zsh/5.7.1/bin/zsh

... trimmed output ...

```

Ahhh, finally! Not a single of instance of `/bin/zsh` in the output. I think
I'm pretty happy with this result.

## Are There Other Ways? 

But now I'm even more curious. Are there other ways to find this same
information? Turns out `apropos process` returned a few results but of the
bunch the only interesting find was `fuser`. 

## fuser

```
~ % fuser /usr/local/Cellar/zsh/5.7.1/bin/zsh             
/usr/local/Cellar/zsh/5.7.1/bin/zsh: 78525
```

Neat. That PID matches `$$`.

```
~ % fuser /bin/zsh
/bin/zsh: 
```

And no results for the pre-installed macOS version of `/bin/zsh`. 

## macOS Activity Monitor

If you want a more point-and-click way of finding the same information then
Activity Monitor has you covered. Make sure View > Applications in last 12
hours is selected. Expand Terminal.app and double click zsh. Clicking the
Sample button on the bottom left gives you some detailed information about that
running process. 

![Screen shot showing layered windows of macOS Activity Monitor and a process sample output of zsh](/images/activity-monitor-zsh.png)

Fun fact: you can use the `sample` command for the same information.

## Conclusion

Finding the shell you're _actually_ using isn't all that simple at first. You
can find the location of the executable of the shell. You can find all
the processes currently running with that shell name. But gathering information
about the shell you're typing all those commands in to find the shell you're
using requires a little more poking around. The two easiest solutions, on macOS
at least, are `lsof` and `fuser`. Activity Monitor also offers up a GUI for
finding the same information but you need to how to dig into it.

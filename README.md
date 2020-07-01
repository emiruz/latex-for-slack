# latex-for-slack

This is the code for the recently deceased LaTeX for Slack bot. It enables the /latex slash command
and renders any latest passed to it as a JPG image which is then attached to a message in the channel.

    /latex e=mc^2

It tries to be a little bit secure by:

* Using the [latex-container](https://github.com/emiruz/latex-container) project to (little bit) securely render LaTeX.

* Retaining as little user information as possible and running everything in memory. 

* Running the web service as a regular user.

* Using signed communication with Slack.

* Invoking the LaTeX rendering container (via latex.sh) as a sudoer with no further permissions.


External Python package required:

    webpy
    slackclient

Running:

     CLI_SIG="%CLI_SIG%" SUPPORT_URL="%SUPPORT_URL%" uwsgi \
     --master \
     --socket 127.0.0.1:8080 \
     --enable-threads \
     --processes=2 -w serve

Before you run it you need to give the running user sudoer permission just for the execution
of latex.sh because docker has to run as root.

Endpoints provided:

   /cmd - slash command handling
   /auth - oauth authorisation handling
   /install - app installation handling

To run it yourself, you need a Slack account and you need to register a Slack app. Instructions on how to do so are here: https://api.slack.com/start

GPL v3, please see the LICENSE file for more information on licensing.

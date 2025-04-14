# Issues with OpenAI Client

So I was cruising along thinking that I could knock this out but started having issues with OpenAI. WHilst I thought the error was my code somewhere's it turned out that alas, apparently OpenAI was having some issues and everyone was recieving the same error which I did at least get through my email as a notification. So that was nice. 

## Reviewing the Scripts

So there was a few issues getting the script to work and not sure if it was me running it through a DevContainer in VS Code or the AI giving me outdated scripts. Turns out that there seems to be something amis running these scripts and getting the response which was actually locking up my MacBook. Granted it is just an Air with a whopping 8GB of furry and an M2 chip, but still. My VS Code was locking up and reading the old files and not savinbg them correctly. Could be me, could be Copilot having issues who knows.... The point is I reworked the code a bit after I went down the Python rabbit hole of pip-tools vs Poetry and which path to go with. 

## Python dependency hell

So yes, I am old and started with just the basic requirements.txt like a neanderthal but seenig how it is 2024 I may as well get with the hot-n-fresh kids of today and use some real tools. I started looking at pip-tools as it locks down the requirements and seems nifty as I do not need to specify every single import but as I kept adding in more I noticed that either I was doing something wrong or did not read the docs. The latter more likely. So I read up on Poetry and wanted to give that a spin. 

## What the hell is wrong with you tool developers?

Like seriously if I wanted to remember everything that I installed, imported and jacked around with I'd go back to using punh cards or ripping apart Yahoo to learn the YUI library. When you tell me there's a new tool please do us a favor and make the conversion easier. Seriously, I should be able to just export my environment to the new tool and call it a f'ing day. Luckily I did come across this post:  https://danielms.site/blog/requirements-txt-to-poetry-pyproject-toml/ and kudos to you human for sharing this as it literally just went through my requirments and updated what needed to be f'ing updated in the TOML. 

## Watch your secrets genius

Yup even though I did make my classic `secrets` folder for my local development work I did not variablize the file name which after looking does not actually provide the access key for Google API but could probably be figured out by someone smarter than I. So will need to go and update that to ensure someone does not use it nefariously. Luckily it is just the client ID which according to the all mighty google:

"No, your Google client ID is not a secret:
Explanation
A Google client ID is a public value that identifies an application, while a client secret is a confidential value that's used to prove the application's identity. A client secret is only required for server-side operations.
"

So yippity skippity for that. 

#always-check-your-API-key-usage

With that I off to using poetry but may circle back to pip-tools depending on if I get pissed or not. For now though I am going to create a new branch, verify that I am not pusing any secrets and commit some friggin code. tata.
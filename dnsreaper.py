#!/usr/bin/env python3
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from bs4 import *
from bs4.element import Comment
import discord
from discord import Webhook, RequestsWebhookAdapter, File

""" 
    To surpress any errors related to the requests library.
"""
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
    Define ANSII colors for more bearable output
"""

YELLOW="\u001b[33m"
BLUE="\u001b[34m"
RED="\u001b[31m"
RESET="\u001b[0m"

"""
  Webhook IDs and Tokens (for Telegram and Discord)
"""

DISCORD_WEBHOOK_ID = "INSERT_YOUR_WEBHOOK_ID"
DISCORD_WEBHOK_TOKEN = "_INSERT_YOUR_WEBHOOK_TOKEN"

"""
    Print our fancy banner
"""

def showBanner():
  banner = """              ...                            
             ;::::;                           
           ;::::; :;                          
         ;:::::'   :;                         
        ;:::::;     ;.                         
       ,:::::'       ;           OOO\         
       ::::::;       ;          OOOOO\                __           ____                            
       ;:::::;       ;         OOOOOOOO          ____/ /___  _____/ __ \___  ____ _____  ___  _____
      ,;::::::;     ;'         / OOOOOOO        / __  / __ \/ ___/ /_/ / _ \/ __ `/ __ \/ _ \/ ___/
    ;:::::::::`. ,,,;.        /  / DOOOOOO     / /_/ / / / (__  ) _, _/  __/ /_/ / /_/ /  __/ /   
  .';:::::::::::::::::;,     /  /     DOOOO    \__,_/_/ /_/____/_/ |_|\___/\__,_/ .___/\___/_/     
 ,::::::;::::::;;;;::::;,   /  /        DOOO                                   /_/   
;`::::::`'::::::;;;::::: ,#/  /          DOOO 
:`:::::::`;::::::;;::: ;::#  /            DOOO
::`:::::::`;:::::::: ;::::# /              DOO
`:`:::::::`;:::::: ;::::::#/               DOO
 :::`:::::::`;; ;:::::::::##                OO
 ::::`:::::::`;::::::::;:::#                OO
 `:::::`::::::::::::;'`:;::#                O 
  `:::::`::::::::;' /  / `:#                  
   ::::::`:::::;'  /  /   `#              
"""
  return banner

"""
    Check if subdomain is vulnerable to takeover, if it is, it will return 'True'
    Format should be in http(s)://<domain>/
"""

vulnerableDomains = [] # list to save vulnerable domains to
def checkIfVulnerable(url,outputFileName):
    global vulnerableDomains
    file = open(outputFileName, "a+")
    req = requests.get(url, verify=False, allow_redirects=True, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"})
    # Credit to EdOverflow (https://github.com/EdOverflow/can-i-take-over-xyz) for fingerprints
    fingerprints = ["<strong>Trying to access your account", 
    "Use a personal domain name", 
    "The request could not be satisfied", 
    "Sorry, We Couldn't Find That Page", 
    "Fastly error: unknown domain", 
    "The feed has not been found", 
    "You can claim it now at", 
    "Publishing platform",                        
    "There isn't a GitHub Pages site here",                       
    "No settings were found for this company",
    "Heroku | No such app", 
    "<title>No such app</title>",                        
    "You've Discovered A Missing Link. Our Apologies!", 
    "Sorry, couldn&rsquo;t find the status page",                        
    "NoSuchBucket", 
    "Sorry, this shop is currently unavailable", 
    "<title>Hosted Status Pages for Your Company</title>", 
    "data-html-name=\"Header Logo Link\"",                        
    "<title>Oops - We didn't find your site.</title>",
    "class=\"MarketplaceHeader__tictailLogo\"",                        
    "Whatever you were looking for doesn't currently exist at this address", 
    "The requested URL was not found on this server", 
    "The page you have requested does not exist", 
    "This UserVoice subdomain is currently available!", 
    "but is not configured for an account on our platform", 
    "Help Center Closed",
    "Oops, this help center no longer exists",
    "<title>Help Center Closed | Zendesk</title>", 
    "Sorry, We Couldn't Find That Page Please try again"
    ]

    
    for fingerprint in fingerprints:
      if fingerprint in req.text:
              vulnerableDomains.append(url)
              print(BLUE+"VULNERABLE!:", url, YELLOW+"Message:", RED+fingerprint, RESET)
              file.write(url+"\n")
              return  BLUE+"VULNERABLE!:", url, YELLOW+"Message:", RED+fingerprint, RESET

parser = argparse.ArgumentParser(description="DNSReaper, automate subdomain and DNS hijacking discovery.", epilog="Reaping DNS records since 2021.")
parser.add_argument('list', type=str, help="a text file with the domains in sequential order")
parser.add_argument('output', type=str, help="Filename to write the results to")
#parser.add_argument('-v', '--verbose', action='store_true', help="Make output more verbose")
arguments = parser.parse_args()

print(showBanner())
print(BLUE,"<- [!] automate subdomain and DNS hijacking discovery [!] ->",RESET)


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    try:
        for domains in open(arguments.list, 'r').read().splitlines():
            futures.append(executor.submit(checkIfVulnerable, url=domains, outputFileName=arguments.output))
        for future in concurrent.futures.as_completed(futures):
            """
            if future != "None":
                #print(future.result())
              pass
            """
            
    except Exception as e:
        print("Error:", e)
        print("Filename either does not exist, or it can't be read. Or, you haven't formatted your domains file correctly.")
        exit(1)

"""
  Send results to Discord Webhook
"""

webhook = Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOK_TOKEN, adapter=RequestsWebhookAdapter())
webhook.send("```css\n[!] [Vulnerable domains found] [!]\n```\n```fix\n" +'\n'.join(vulnerableDomains) + "\n\n```")

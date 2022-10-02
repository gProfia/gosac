
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from bs4 import BeautifulSoup

import pandas as pd

import getopt, sys, time, os
from pathlib import Path


firefox_opt = Options()
firefox_opt.headless = True

def clean_text(text) -> str:
    ct = text
    chars = "\\;:/`*_{}[]()><#+-.,!@#$%\"'\"&'´?"
    for c in chars:
        ct = ct.replace(c, "")
    return ct.lower()


def main():
    args_in = sys.argv[1:]    
    options = "f:nyried:h"
    long_options = ["file", "not-log", "yes-log", "real-name", "iter-save", "end-save", "delay", "help"]
    ai=an=ay=ar=ae=False
    delay=3
    author_file = None 
    try:
        #parse args
        args, values = getopt.getopt(args_in, options, long_options)
        for curr_arg, curr_value in args:
            if curr_arg in ("-f", "--file"):
                author_file = curr_value
            elif curr_arg in ("-n", "--not-log"):
                an = True
            elif curr_arg in ("-y", "--yes-log"):
                ay = True
            elif curr_arg in ("-r", "--real-name"):
                ar = True
            elif curr_arg in ("-i", "--iter-save"):
                ai = True
            elif curr_arg in ("-e", "--end-save"):
                ae = True
            elif curr_arg in ("-d", "--delay"):
                try:
                    delay = int(curr_value)
                except ValueError:
                    print("opt err: --delay must be a integer")
                    sys.exit(1)
            elif curr_arg in ("-h", "--help"):
                print("""
[-f filename] INPUT FILE 
[-n] LOG NOT FOUND AUTHOR TO STDOUT
[-y] LOG FOUND AUTHOR DO STDOUT 
[-r] SAVE THE AUTHOR NAME SCRAPPED TO FINAL RESULT DATAFRAME CSV 
[-i] SAVE DATA IN DATAFRAME CSV WHILE IT IS BEEN CAPTURED [default]
[-e] COLLECT ALL DATA AND SAVE AT THE END
[-d] REQUESTS DELAY
[-h] THIS MESSAGE
                        """)
                sys.exit(0)
            else:
                print("opt err: undefined option " + str(curr_arg))
                sys.exit(1)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    
    #args conditions
    if not author_file:
        print("file err: author file not present in argv")
        sys.exit(3)
    if ai and ae:
        print("opt err: Can't use --iter-save and --end-save simultaneously")
        sys.exit(4)
    if not ae:
        ai = True

    authors = []
    with open(author_file) as file:
        authors = [ line.strip() for line in file ]
    if len(authors) == 0:
        print("empty err: empty file provided")
        sys.exit(5)
    driver = webdriver.Firefox(options=firefox_opt, service=FirefoxService(GeckoDriverManager().install()))
    result_lines = {"Author":[], "AuthorSN": [], "Citations": []} if ar else {"Author": [], "Citations": []} 

    for author in authors: 
        outer_url = "https://scholar.google.com/citations?view_op=search_authors&mauthors=" + author + "&hl=en-US"
        driver.get(outer_url)
        time.sleep(delay)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        author_candidates = soup.find_all("h3", {"class":"gs_ai_name"})
        #match author name
        author_found = ""
        tag = None
        for ac in author_candidates:
            if author == ac.text.strip() or clean_text(author) == clean_text(ac.text):
               author_found = ac.text.strip()
               tag  = ac
               if ay:
                   print("FOUND: "+ author + " --> " + author_found)
               break       
        if not author_found:
            if an:
                print("NOT FOUND: "+ author)
        else:
            inner_url = "https://scholar.google.com"+tag.find('a')['href']
            driver.get(inner_url)
            time.sleep(delay)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            metric_lines = soup.find("table", {"id": "gsc_rsb_st"}).find_all("tr")
            
            for ml in metric_lines:
                if "citations" in ml.text.lower():
                    if ae:
                        result_lines["Author"].append(author)
                        if ar:
                            result_lines["AuthorSN"].append(tag.text.strip())
                        result_lines["Citations"].append(ml.find_all("td")[1].text.strip())
                    else:
                        result_line = {"Author":[author], "AuthorSN": [tag.text.strip()], "Citations": [ml.find_all("td")[1].text.strip()]} if ar else {"Author": [author], "Citations": [m1.find_all("td")[1].text.strip()]} 
                        df = pd.DataFrame(result_line)
                        if os.path.exists(Path(author_file).stem+"_out.csv"):
                            df.to_csv(Path(author_file).stem+'_out.csv', index=False, mode='a', header=False)
                        else:
                            df.to_csv(Path(author_file).stem+'_out.csv',index=False, mode='w')
                    break
    if ae:
        df = pd.DataFrame(result_lines)
        df.to_csv(Path(author_file).stem+'_out.csv',index=False, mode='w')
        
    driver.quit()


print("""
 ██████   ██████  ███████  █████   ██████ 
██       ██    ██ ██      ██   ██ ██      
██   ███ ██    ██ ███████ ███████ ██      
██    ██ ██    ██      ██ ██   ██ ██      
 ██████   ██████  ███████ ██   ██  ██████  v0.1                                                                             
        """)       
main()

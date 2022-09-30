
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import getopt, sys 



options = Options()
#options.headless = True

def main():
    args_in = sys.argv[1:]    
    options = "f:nyrieh"
    long_options = ["file", "not-log", "yes-log", "real-name", "iter-save", "end-save", "help"]
    ai=an=ay=ar=ae=False
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
            elif curr_arg in ("-h", "--help"):
                print("""
[-f filename] INPUT FILE 
[-n] LOG NOT FOUND AUTHOR TO STDOUT
[-y] LOG FOUND AUTHOR DO STDOUT 
[-r] SAVE THE AUTHOR NAME SCRAPPED TO FINAL RESULT DATAFRAME CSV 
[-i] SAVE DATA IN DATAFRAME CSV WHILE IT IS BEEN CAPTURED [default]
[-e] COLLECT ALL DATA AND SAVE AT THE END
                        """)
                sys.exit(0)
            else:
                print("opt err: "+str(curr_arg))
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


main()

import pickle
import os
import argparse

from src.scraper import AstraScraper
from src.utils.adminlink import string_filter

def crawly_go_crawl(args):
    scraper = AstraScraper()

    scraper.crawl_page(
        write_dir=args.write_dir, 
        write=args.write,
        verbose=args.verbose, 
        filter_function=args.filter_function, 
        filter_string=args.filter_string, 
        begin=args.begin,
    )

    with open(os.path.join(args.write_dir, 'overview', 'scraper_class.pkl'), 'wb') as con:
        pickle.dump(scraper, con)


if __name__ == "__main__":
    # add parser
    parser = argparse.ArgumentParser(description='Arguments')

    parser.add_argument("--write_dir",
                        type=str)
    parser.add_argument("--write",
                        type=bool,
                        default=True)
    parser.add_argument('--verbose',
                        type=bool,
                        default=True)
    parser.add_argument('--filter_function',
                        type=function,
                        default=string_filter)
    parser.add_argument('--filter_string',
                        type=str,
                        default='astra/de|classified-compilation|fedlex')
    parser.add_argument('--begin', type=bool, default=False)


    args = parser.parse_args()

    crawly_go_crawl(args)